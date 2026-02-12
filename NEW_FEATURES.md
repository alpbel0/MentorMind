# MentorMind — Phase 3: Coach Chat + Evidence Spec

> Purpose: turn evaluations from "scorecards" into an actionable coaching flow.
> This spec captures the agreed MVP design for **Evidence/"Kanıt"** generation and **metric-scoped chat**.

---

## Goals

After an evaluation, users typically ask:
- "Ben niye 3 verdim, judge niye 2 verdi?"
- "Şu cevapta hangi cümle hangi metriği bozdu?"
- "Bir dahaki sefer daha iyi olması için neyi değiştirmeliyim?"

We will answer these with:
1) **Evidence (Kanıt)** per metric (quotes + why + suggested fix)
2) **Coach Chat** scoped to selected metrics (1–3 metrics), to avoid conversations drifting.

---

## Architectural Decisions — Index

| # | Karar | Özet |
|---|-------|------|
| AD-1 | Evidence Generation in Stage 1 | Kanıtlar Stage 1'de (blind) toplanır, Stage 2'de yorumlanır |
| AD-2 | 5-Stage Self-Healing Verification | Exact → Substring → Anchor → Whitespace(safe) → Fallback |
| AD-3 | New Snapshot Table | `evaluation_snapshots` + `chat_messages` tabloları |
| AD-4 | SSE + DB Chat + Turn Limit | Streaming, reconnect, shared turn ID, token windowing, init greeting |
| AD-5 | Coach Model Selection | GPT-4o-mini, config'den değiştirilebilir |
| AD-6 | Slug-Based Metric Keys | `Truthfulness` → `truthfulness`, explicit mapping |
| AD-7 | Snapshot Timing — Atomic Write | Stage 2 bitince tek transaction'da yaz |
| AD-8 | Evidence Graceful Degradation | Evidence parse hatası pipeline'ı kırmaz |
| AD-9 | Chat Turn Limit — Read-Only | 15 user mesaj, dolunca read-only + yönlendirme |
| AD-10 | Strict Evidence Usage | Coach kendi alıntı üretmez, sadece Stage 1 evidence'a referans |
| AD-11 | Snapshot — Otomatik Kayıt | Stage 2 bitince otomatik, kullanıcı aksiyonu gerekmez |
| AD-12 | Concurrent Sessions | MVP'de kısıtlama yok, snapshot başına limit yeterli |
| AD-13 | Retention Policy — Soft Delete | `deleted_at` + `status: archived` altyapısı hazır |

---

### AD-1: Evidence Generation in Stage 1

**Karar:** Evidence (Kanıt/Alıntı) üretimi, Judge akışının **Stage 1 (Bağımsız Değerlendirme)** sırasında gerçekleştirilecektir.

**Gerekçeler:**

1. **Nesnellik (Objectivity):** Evidence, modelin cevabına dair somut bir "bulgudur". Bu bulgu kullanıcının puanından bağımsız bir gerçektir. Judge, Stage 1'de herhangi bir dış etki altında kalmadan hataları yerinde tespit eder. Bu, kanıtın tarafsızlığını garanti altına alır.

2. **Bağlamsal Tazelik (Contextual Freshness):** Judge, Stage 1'de cevabı satır satır okuyup puan takdir eder. Kanıtın bu aşamada JSON çıktısına eklenmesi, Judge'ın "sıcağı sıcağına" bulguları kaydetmesini sağlar. Stage 2'ye bırakılan bir kanıt arama süreci, modelin kendi verdiği puanı sonradan rasyonalize etmeye çalışmasına (post-hoc justification) ve halüsinasyon riskinin artmasına neden olabilir.

3. **Token Verimliliği (Efficiency):** Stage 2 prompt'u zaten kullanıcı puanları, metrik şemaları ve geçmiş verilerle yüklüdür. Kanıt arama görevini de buraya yüklemek hem token maliyetini artırır hem de modelin asıl görevi olan "mentörlük ve kıyaslama"ya odaklanmasını zorlaştırır. Stage 1'de kanıtları toplamak, Stage 2'ye sadece bu hazır kanıtları yorumlama görevini bırakır.

4. **Eğitim Materyali:** Kullanıcı Judge ile aynı puanı vermiş olsa bile (Gap = 0), Judge'ın hangi cümleleri "kritik" gördüğünü görmek öğreticidir. Stage 1'de üretilen kanıtlar, sadece "hataları düzeltmek" için değil, "iyi uygulamaları pekiştirmek" için de birer eğitim materyaline dönüşür.

> **Analoji:** Deliller "suç mahallinde" (Stage 1) toplanır; "mahkemede" (Stage 2) ise sadece bu deliller üzerinden tartışılır.

---

### AD-2: 5-Stage Self-Healing Evidence Verification

**Karar:** Judge'dan gelen evidence verisi, veritabanına kaydetmeden önce 5 aşamalı bir doğrulama + düzeltme döngüsünden geçirilecektir. Aşamalar **en yüksek güvenilirlikten en düşüğe** doğru sıralanmıştır.

**Aşamalar:**

#### Aşama 1: Exact Slice (Hızlı Kontrol)
```python
model_answer[start:end] == quote
```
- Eşleşirse → `verified: true`, `start`/`end` korunur. İşlem tamam.
- **Güvenilirlik:** En yüksek. Doğrudan verilen indeksler doğru.

#### Aşama 2: Substring Search (Tam Alıntı Araması)
```python
idx = model_answer.find(quote)
```
- Bulunursa → `start` ve `end` değerlerini yeni pozisyonlara güncelle, `verified: true`.
- **Güvenilirlik:** Yüksek. Alıntı birebir doğru ama indeksler kaymış.
- Neden önce: Tam alıntı araması, parçalı (anchor) aramaya göre çok daha temiz ve güvenilir bir düzeltme sağlar. Önce tam olanı bulmak, sistemin hata yapma riskini azaltır.

#### Aşama 3: Anchor-Based Search (Çapa Araması)
```python
ANCHOR_LEN = 25
head_anchor = quote[:ANCHOR_LEN]
tail_anchor = quote[-ANCHOR_LEN:]

head_idx = model_answer.find(head_anchor)
if head_idx >= 0:
    # Güvenlik penceresi: head'den itibaren alıntı uzunluğu + tolerans
    search_window = len(quote) + 2000
    search_end = min(head_idx + search_window, len(model_answer))
    tail_idx = model_answer.find(tail_anchor, head_idx, search_end)

    if tail_idx >= 0:
        new_start = head_idx
        new_end = tail_idx + len(tail_anchor)
```
- Alıntının baş ve son 25 karakterlik "çapa" (anchor) metinleri orijinal metinde aranır.
- **Search Window:** Tail araması tüm metinde değil, head'den itibaren `len(quote) + 2000` karakterlik pencerede yapılır. Uzun model cevaplarında tail'in başka bir yerde geçmesi durumunda false positive riski ortadan kalkar.
- Her iki anchor bulunursa → `start`/`end` değerleri düzeltilir, `verified: true`.
- **Güvenilirlik:** Orta-yüksek. LLM alıntıyı kısaltmış veya ortasını değiştirmiş olabilir, ama baş ve son genellikle doğrudur.

#### Aşama 4: Whitespace-Insensitive Match (Boşluk Toleransı — Safe Mode)
```python
normalized_answer = normalize(model_answer)  # fazla boşluk/newline temizle
normalized_quote = normalize(quote)
found = normalized_answer.find(normalized_quote) >= 0
```
- Hem `quote` hem `model_answer` normalize edilir (fazla boşluklar, yeni satırlar temizlenir).
- Bulunursa → `verified: true` **ama `start`/`end` güncellenmez** (Safe Mode).
- **Safe Mode Gerekçesi:** Normalize edilmiş metindeki indeksleri orijinal metne geri haritalamak (reverse mapping) çok karmaşık ve hata payı yüksektir. Yanlış yeri boyamak yerine, doğruluğu onaylayıp highlight'ı pas geçmek kullanıcı güveni için daha sağlıklıdır.
- **UI/UX Protokolü (Aşama 4 özel davranış):**
  1. **Highlight İptali:** Model cevabı üzerinde herhangi bir boyama (highlight) yapılmaz.
  2. **Quote Gösterimi:** Kanıt, metrik kartı üzerinde sadece metin alıntısı olarak gösterilmeye devam eder.
  3. **Bilgilendirme Etiketi:** Kanıtın yanında küçük bir info label gösterilir: *"Pozisyon tespit edilemedi, highlight kapalı"*
- **Neden:** Kullanıcı, kanıtın "doğru" bulunduğunu bilir ancak teknik kısıtlar nedeniyle metin üzerinde tam yerinin gösterilemediğini de anlar. "Neden bazı yerler boyanıyor da burası boyanmıyor?" sorusu ortadan kalkar.

#### Aşama 5: Fallback (Başarısızlık)
- Hiçbir aşamada bulunamazsa → `verified: false`, orijinal `start`/`end` değerleri korunur.
- UI'da uyarı gösterilir: **"Kanıt doğrulanamadı"**

**Neden Bu Yaklaşım:**
- **Efficiency First:** Aşamalar en güvenilirden en az güvenilire sıralı. Çoğu durumda Aşama 1-2'de çözülür, maliyetli aşamalara gerek kalmaz.
- **UI Tutarlılığı:** Frontend highlighter bileşeni `start`/`end` değerlerine güvenir. Self-healing ile highlighter'ın her zaman doğru yeri boyaması garanti edilir. Aşama 4'te indeks güncellemesi yapılmayarak yanlış boyama riski sıfırlanır.
- **Kullanıcı Güveni:** "Kanıt doğrulanamadı" uyarısı ne kadar az görünürse, sisteme güven o kadar artar.
- **False Positive Koruması:** Anchor search'te search window ile, whitespace match'te safe mode ile false positive'ler engellenir.

---

### AD-3: New Snapshot Table (evaluation_snapshots)

**Karar:** Mevcut tablolara `evidence_json` eklemek yerine, yeni bir **snapshot tablo** oluşturulacaktır.

**Gerekçeler:**

1. **Hafıza ve Bağlam Bütünlüğü (Context Integrity):** Bir coaching session bir anlık görüntüdür. Soru bankasından o soru silinse veya değişse bile, o gün yapılan değerlendirme ve Judge sohbeti bozulmamalıdır. Veriyi kopyalayarak bu oturum ölümsüzleştirilir.

2. **LLM Verimlilik (LLM Efficiency):** Chat başlattığında 4 farklı tabloya JOIN atmak yerine, tek bir ID ile o satırı çekip direkt LLM'e göndermek hem daha hızlı hem de kodun daha temiz kalmasını sağlar.

3. **Separation of Concerns:** Mevcut tablolar (questions, user_evaluations vb.) "Veri Bankası" ve "Genel İstatistikler" odaklıdır. Yeni tablo tamamen "Eğitim ve Geri Bildirim" odaklı olacaktır. İki dünyayı ayırmak gelecekte sistemi büyütürken işleri kolaylaştırır.

4. **Veri Yapısı Karmaşıklığı:** `evidence_json` çok zengin bir veri. Tüm aktörlerin (Kullanıcı, Judge, Model) bilgisinin olduğu bir "Final Report" tablosunda tutmak çok daha profesyonel durur.

**Yeni Tablolar:**

#### evaluation_snapshots
| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT | PK. Format: `snap_YYYYMMDD_HHMMSS_randomhex` |
| `created_at` | TIMESTAMP | Snapshot oluşturulma zamanı |
| `question_id` | TEXT | Orijinal soru ID'si (referans, FK değil) |
| `question` | TEXT | Soru metni (snapshot) |
| `model_answer` | TEXT | Model cevabı (snapshot) |
| `model_name` | TEXT | Cevaplayan model adı |
| `judge_model` | TEXT | Judge model adı (default: gpt-4o) |
| `primary_metric` | TEXT | Birincil metrik |
| `bonus_metrics` | JSONB | Bonus metrikler |
| `category` | TEXT | Soru kategorisi |
| `user_scores_json` | JSONB | Kullanıcı skorları (8 metrik + reasoning) |
| `judge_scores_json` | JSONB | Judge skorları (8 metrik + rationale). Stage 1'den gelen `independent_scores` objesi direkt kullanılır, dönüşüm gerekmez. |
| `evidence_json` | JSONB | Kanıt verisi (8 metrik, her biri 1-3 evidence) |
| `judge_meta_score` | INTEGER | 1-5 meta skor |
| `weighted_gap` | REAL | Ağırlıklı fark |
| `overall_feedback` | TEXT | Judge genel geri bildirimi |
| `user_evaluation_id` | TEXT | Orijinal user_evaluation ID'si (referans) |
| `judge_evaluation_id` | TEXT | Orijinal judge_evaluation ID'si (referans) |
| `chat_turn_count` | INTEGER | Kullanılan **kullanıcı** mesaj sayısı (default: 0). Sadece user role mesajları sayılır. |
| `max_chat_turns` | INTEGER | Maksimum kullanıcı mesaj hakkı (default: 15) |
| `status` | TEXT | active, completed, archived (Bkz: Retention Policy) |
| `deleted_at` | TIMESTAMP | Soft delete zamanı (nullable, default: null). Retention policy altyapısı. |

#### chat_messages
| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT | PK. Format: `msg_YYYYMMDD_HHMMSS_randomhex` |
| `client_message_id` | TEXT | Shared Turn ID (**NOT NULL**). Aynı konuşma turundaki user ve assistant mesajları aynı ID'yi paylaşır. Client-side UUID olarak üretilir. |
| `is_complete` | BOOLEAN | Mesaj tamamlandı mı? (default: user→true, assistant→false). SSE streaming bitince assistant mesajı true olur. Reconnect'te yarım kalan cevaplar bu alanla tespit edilir. |
| `snapshot_id` | TEXT | FK → evaluation_snapshots.id |
| `role` | TEXT | user, assistant |
| `content` | TEXT | Mesaj içeriği |
| `selected_metrics` | JSONB | Seçilen metrikler (ilk mesajda set edilir, oturum boyunca immutable) |
| `token_count` | INTEGER | Mesaj token sayısı (maliyet takibi) |
| `created_at` | TIMESTAMP | Mesaj zamanı |

**Constraints & Indexes:**
- `UNIQUE (snapshot_id, client_message_id, role)` — Aynı tur (ID) içinde sadece bir user ve bir assistant mesajı olabilir.
- `INDEX (snapshot_id, created_at)` — Sohbet geçmişi sorgularında performans.

**Shared Interaction ID Modeli:**
```
Turn 1: client_message_id = "abc_001"
  ├─ role: "user",      content: "Neden Clarity'de 4 verdin?"
  └─ role: "assistant",  content: "Clarity metriğinde şu kanıtlara baktığımda..."

Turn 2: client_message_id = "abc_002"
  ├─ role: "user",      content: "Peki nasıl düzeltebilirim?"
  └─ role: "assistant",  content: "Şu cümleyi yeniden yazarsan..."
```
- User mesajı ve assistant cevabı aynı `client_message_id`'yi taşır → doğal eşleşme, FK gerekmez.
- User mesajı `is_complete: true` ile yazılır (anlık). Assistant mesajı `is_complete: false` ile başlar, streaming bitince `true` olur.

---

### AD-4: Streaming SSE + DB-Backed Chat + Turn Limit

**Karar:** Coach Chat, **Server-Sent Events (SSE)** ile streaming olacak, sohbet geçmişi veritabanında tutulacak ve mesaj limiti uygulanacaktır.

#### Streaming (SSE)
- FastAPI `StreamingResponse` kullanılacak.
- Kelime kelime akış, modern UX hissi verir.
- Kullanıcı okumaya erkenden başlayabilir.

#### SSE Reconnect & Idempotency

İki farklı ID, iki farklı sorumluluk:

| ID | Yön | Sorumluluk |
|----|-----|------------|
| `client_message_id` | Client → Server | Yeni mesaj gönderiminde **idempotency** (duplicate engeli) |
| `last_event_id` (SSE) | Server → Client | Bağlantı kopmasında **resume** (kaldığı yerden devam) |

**Idempotency (client_message_id — Shared Turn ID):**
- Her konuşma turu için client-side UUID üretilir (**NOT NULL**, DB'de zorunlu).
- Aynı `client_message_id` ile hem user hem assistant mesajı yazılır (Shared Interaction ID).
- `UNIQUE (snapshot_id, client_message_id, role)` constraint ile DB seviyesinde dedup garanti.
- Aynı `client_message_id` tekrar gelirse → mevcut cevap döner, sayaç artmaz, LLM çağrılmaz.

**Reconnect (last_event_id):**
- Frontend SSE bağlantısı koparsa, `last_event_id` (son alınan SSE event'in `msg_id`'si) ile tekrar bağlanır.
- Backend bu ID'den sonraki mesajları DB'den çeker:
  - Assistant cevabı `is_complete: true` ise → DB'deki cevabı döner (LLM'e gitmez).
  - Assistant cevabı `is_complete: false` ise → **Update-In-Place:** Mevcut satır silinmez, `content` sıfırlanır ve `is_complete: false` kalır. LLM üretimi baştan başlatılıp aynı satırın üzerine yazılır.
    - **Neden DELETE değil?** (1) `UNIQUE (snapshot_id, client_message_id, role)` ihlal edilmez, (2) `msg_id` değişmez → frontend state (React key) bozulmaz, (3) Tek UPDATE, DELETE+INSERT'e göre daha az indeks maliyeti.
  - Assistant kaydı **hiç yoksa** (mesaj alınmadan bağlantı kopmuş) → Yeni assistant satırı `INSERT` edilir (aynı `client_message_id`, `role: assistant`).

**Turn Counter Sıralaması (Önce Dedup, Sonra Sayaç):**
```
1. (snapshot_id, client_message_id, "user") kontrol et (DB lookup)
   └─ Zaten var? → Mevcut assistant cevabını dön, ÇIKIŞ
2. chat_turn_count < max_chat_turns atomik kontrol + artırım
   └─ Limit dolmuş? → HTTP 429, ÇIKIŞ
3. User mesajı DB'ye yaz (is_complete: true)
4. Assistant mesajı DB'ye yaz (is_complete: false, content: "")
5. LLM streaming başlat → assistant content'i güncelle
6. Streaming bitince assistant is_complete: true güncelle
```
Bu sıralama, retry edilen mesajların sayacı haksız yere artırmasını engeller.

#### Chat History → Database
- `chat_messages` tablosunda saklanacak.
- Kullanıcı geri dönüp "Hoca o gün ne demişti?" diye bakabilir.
- Sayfa yenilenmesi sohbeti silmez.

#### Chat History Token Windowing
- LLM'e her zaman gönderilen: **Snapshot context (evidence)** + **Son 6 mesaj** (3 user + 3 assistant).
- Eski mesajlar DB'de kalır ama LLM context'ine dahil edilmez.
- Coach zaten anlık evidence üzerinden konuştuğu için 10 mesaj öncesini hatırlamasına gerek yok.
- Token tasarrufu: ~15 mesajlık full history yerine ~6 mesaj, context window'u %60 küçültür.

#### Endpoint Yapısı

**Chat Endpoint:**
```
POST /api/snapshots/{snapshot_id}/chat
```
- **Girdi:** `{ "message": "...", "client_message_id": "uuid-v4", "selected_metrics": ["truthfulness", "clarity"], "is_init": false }`
- **Çıktı:** SSE stream (Coach'un cevabı)
- **Arka Plan:** `evaluation_snapshots` tablosundan bağlamı çeker, `chat_messages`'dan son 6 mesajı ekler, LLM'e gönderir.
- `selected_metrics` sadece ilk mesajda gönderilir, sonraki mesajlarda ignore edilir (immutable).

**Init Greeting (Selamlama Modu):**
- `is_init: true` flag'i veya boş `message` gönderildiğinde Coach "Selamlama Modu"na geçer.
- Coach, seçilen metriklerdeki gap ve evidence verilerini analiz ederek otomatik açılış mesajı üretir.
- Bu mesaj kullanıcının 15 mesajlık limitinden **düşmez** (bonus mesaj, `chat_turn_count` artmaz).
- DB'ye `client_message_id: "init_{snapshot_id}"` sabit kimlikle kaydedilir (idempotent — tekrar çağrılırsa aynı greeting döner).
- **Shared Turn ID İstisnası:** Init greeting, Shared Interaction ID modelinin tek istisnasıdır. Bu turn'de sadece `role: assistant` mesajı vardır, eşleşen `role: user` mesajı yoktur. `UNIQUE (snapshot_id, client_message_id, role)` constraint'i buna izin verir.
- Akış: Kullanıcı metrik seçer → "Sohbeti Başlat" → Frontend `is_init: true` gönderir → Coach açılış yapar → Kullanıcı oradan devam eder.

**CRUD Endpoint'leri:**
```
GET  /api/snapshots/                    — Tüm snapshot listesi (geçmiş oturumlar)
GET  /api/snapshots/{snapshot_id}       — Snapshot detayı (evaluation result screen)
GET  /api/snapshots/{snapshot_id}/messages — Chat geçmişi (sayfa reload'da)
```

> **Not:** Endpoint path `/api/snapshots/` kullanır, `/api/evaluations/` değil. Resource = snapshot, URL = snapshot. (REST convention)

#### Turn Limit (Maliyet Kontrolü)
- Her değerlendirme için **maksimum 15 kullanıcı mesajı** hakkı (configurable).
- **Sadece user role mesajları sayılır.** Coach'un cevapları limite dahil değildir. Toplam ~30 mesaj (15 user + 15 assistant).
- Limit dolunca: "Bu değerlendirme üzerine yeterince konuştuk, hadi yeni bir soruya geçelim."
- Hem maliyeti korur hem sohbetin konu dışına çıkmasını azaltır.
- `evaluation_snapshots.chat_turn_count` ile takip edilir.

---

### AD-5: Coach Model Selection

**Karar:** MVP'de coach chat modeli olarak **GPT-4o-mini** kullanılacaktır.

**Gerekçeler:**
- **Maliyet:** GPT-4o'ya kıyasla ~10x ucuz
- **Hız:** Streaming için daha düşük latency
- **Yeterlilik:** Coaching (mevcut evidence üzerinden açıklama) için yeterli zeka seviyesi
- **Türkçe:** Yeterli Türkçe kalitesi

**Config:** `settings.py`'de `COACH_MODEL` olarak tanımlanacak, ileride GPT-4o veya başka modele geçiş config değişikliğiyle yapılabilir.

---

### AD-6: Slug-Based Metric Keys

**Karar:** JSON içindeki metrik anahtarları (keys) **küçük harf slug** formatında saklanacaktır.

**Mapping:**
| Display Name | Slug Key |
|-------------|----------|
| Truthfulness | `truthfulness` |
| Helpfulness | `helpfulness` |
| Safety | `safety` |
| Bias | `bias` |
| Clarity | `clarity` |
| Consistency | `consistency` |
| Efficiency | `efficiency` |
| Robustness | `robustness` |

**Gerekçeler:**
- **i18n Hazırlığı:** Yarın UI Türkçeleştiğinde (Label: "Doğruluk") veritabanı yapısı bozulmaz. Slug sabit kalır, display name değişir.
- **Kod Güvenliği:** Büyük harf, boşluk veya özel karakter içeren key'ler case-sensitivity hataları yaratır. Slug'lar bu riski ortadan kaldırır.
- **Frontend-Backend Contract:** Her iki taraf aynı slug'ları kullanır, mapping hatası olmaz.

**Uygulama:**
- `evidence_json`, `user_scores_json`, `judge_scores_json` → slug key'ler
- `selected_metrics` (chat) → slug array: `["truthfulness", "clarity"]`
- Backend'de `METRIC_SLUGS` constant'ı ve `display_name_to_slug()` / `slug_to_display_name()` helper fonksiyonları

**Migration Stratejisi (Code-Level, DB Dokunulmaz):**
- Mevcut tablolara (user_evaluations, judge_evaluations) **dokunulmaz**. Eski veriler `"Truthfulness"` key'leriyle kalır.
- Snapshot oluşturulurken (Stage 2 bitişinde) **explicit dictionary** ile slug dönüşümü yapılır.
- Sadece `evaluation_snapshots` tablosu temiz slug kullanır. Geriye dönük uyumluluk korunur.

**Explicit Slug Mapping (otomatik `lower()` yerine):**
```python
METRIC_SLUG_MAP = {
    "Truthfulness": "truthfulness",
    "Helpfulness": "helpfulness",
    "Safety": "safety",
    "Bias": "bias",
    "Clarity": "clarity",
    "Consistency": "consistency",
    "Efficiency": "efficiency",
    "Robustness": "robustness",
}

SLUG_DISPLAY_MAP = {v: k for k, v in METRIC_SLUG_MAP.items()}  # reverse lookup
```
- **Neden explicit?** Otomatik `lower()` güvenilir değil. İleride "Safety & Policy" gibi karmaşık isimler gelirse kod kırılır. Sabit dictionary ile her zaman doğru mapping garanti edilir.

---

### AD-7: Snapshot Timing — Stage 2 Completion (Atomic Write)

**Karar:** `evaluation_snapshots` kaydı, **Stage 2 tamamlandıktan sonra** tek bir atomik işlemle oluşturulacaktır.

**Akış:**
```
Stage 1 (bağımsız değerlendirme + evidence) → Stage 2 (mentorluk karşılaştırma)
    → Her ikisi başarılı ise → Snapshot atomik yazım
```

**Gerekçeler:**
- **Veri Bütünlüğü:** Yarım snapshot (evidence var ama meta_score yok, veya tersi) oluşması engellenir.
- **Basitlik:** Tek bir "create snapshot" fonksiyonu, Stage 1 + Stage 2 sonuçlarını birleştirir ve yazar. İki ayrı yazım + güncelleme yerine tek transaction.
- **Hata Yönetimi:** Stage 1 veya Stage 2 başarısız olursa snapshot oluşturulmaz. Kullanıcıya "judge işlemi başarısız" mesajı gösterilir, bozuk veri oluşmaz.

**Orchestration:**
```python
# judge_task.py içinde (pseudo-code)
stage1_result = judge_service.stage1_independent_evaluation(...)  # scores + evidence
stage2_result = judge_service.stage2_mentoring_comparison(...)     # alignment + feedback

# Her ikisi başarılı → atomik snapshot yazımı
snapshot = create_evaluation_snapshot(
    stage1=stage1_result,
    stage2=stage2_result,
    user_eval=user_eval,
    question=question,
    model_response=model_response
)
db.add(snapshot)
db.commit()
```

---

### AD-8: Evidence Graceful Degradation

**Karar:** Stage 1 sırasında evidence JSON parse başarısız olursa, tüm işlem iptal **edilmeyecektir**.

**Davranış:**
- Sistem, `evidence_json` alanını boş (`null` veya `{}`) olarak kaydedip yoluna devam eder.
- Skorlar ve Judge yorumları asıl değerdir, evidence "bonus"tur.
- Chat ve rapor ekranı yine çalışır, sadece "Kanıt" butonları/bölümleri görünmez.
- Log'a `WARNING` seviyesinde kayıt düşer: `"Evidence parse failed for eval {id}, continuing without evidence"`

**Neden:**
- Kullanıcı değerlendirmesini tamamlamış, Stage 1 + Stage 2 skorları üretilmiş. Evidence olmadan da mentörlük değerli.
- Tüm pipeline'ı evidence parse hatası yüzünden kırmak kullanıcı deneyimini bozar.

---

### AD-9: Chat Turn Limit — Read-Only Termination & Guide

**Karar:** Mesaj limiti dolduğunda chat kutusu **read-only** moda geçecek ve kullanıcı yeni değerlendirmeye yönlendirilecektir.

**Davranış:**
1. Kullanıcı 15 mesaja (configurable) ulaştığında:
   - Chat input kutusu **kilitlenir** (disabled)
   - Geçmiş mesajlar **okunabilir** kalır (scroll, kopyalama)
   - UI'da yönlendirme mesajı gösterilir:
     > "Bu değerlendirme üzerine yeterince konuştuk! Öğrendiklerini pekiştirmek için yeni bir soru çözmeye ne dersin?"
   - **"Yeni Değerlendirme Başlat"** butonu gösterilir

2. Backend kontrolü (Atomik Turn Limit):
   - Her mesajda atomik SQL ile kontrol + artırım tek işlemde yapılır:
     ```sql
     UPDATE evaluation_snapshots
     SET chat_turn_count = chat_turn_count + 1
     WHERE id = :id AND chat_turn_count < max_chat_turns
     ```
   - `rows_affected == 0` ise limit dolmuş → `HTTP 429` döner: `{"error": "turn_limit_reached", "message": "..."}`
   - Atomik olması, hızlı art arda gelen mesajların (veya botların) limiti delmesini engeller.
   - Frontend bu response'u handle edip read-only moda geçer.

**Gerekçeler:**
- **Maliyet Kontrolü:** Sonsuz sohbet = sonsuz API maliyeti. Turn limit bütçeyi korur.
- **Pedagojik:** Kullanıcıyı "konuşmak" yerine "uygulamak"a teşvik eder. Yeni soru çözmek daha öğretici.
- **Jailbreak Riski:** Uzun sohbetlerde LLM'in konu dışına çıkma olasılığı artar. Kısa sohbetler daha güvenli.
- **UX:** Hard stop yerine read-only + yönlendirme, kullanıcı frustrasyonunu azaltır.

---

### AD-10: Strict Evidence Usage — Coach Halüsinasyon Koruması

**Karar:** Coach Chat modeli (GPT-4o-mini), konuşma sırasında **asla yeni kanıt (alıntı) üretmeyecek**; sadece Judge tarafından Stage 1'de bulunmuş ve veritabanına kaydedilmiş mevcut kanıtlar üzerinden mentörlük yapacaktır.

**Kural:**
- Coach, evidence listesindeki `quote`, `why`, `better` alanlarına referans verebilir.
- Coach, model cevabından kendi alıntılarını **üretemez**.
- Coach prompt'unda bu kural açıkça belirtilir:
  > "You must ONLY reference evidence items provided in the context. Do NOT quote from the model answer directly. If no evidence exists for a topic, say so honestly."

**Gerekçeler:**
- **Halüsinasyon Riski:** Chat modeli konuşma akışında kendi alıntı yapmaya çalışırsa, olmayan şeyi varmış gibi gösterebilir. Sistemin "tek doğrusu" Judge'ın ilk tespiti olmalıdır.
- **Tutarlılık:** Kullanıcı UI'daki highlight'ları ve chat'teki referansları karşılaştırabilir. İkisi aynı kaynaktan (Stage 1 evidence) geliyorsa tutarlılık sağlanır.
- **Güven Zinciri:** Stage 1 (Judge) → Evidence (doğrulanmış) → Coach (sadece referans). Bu zincir kırılmaz.

---

### AD-11: Snapshot Oluşturma — Otomatik Kayıt

**Karar:** Snapshot kaydı, **Stage 2 işlemi başarıyla biter bitmez otomatik olarak** oluşturulacaktır. Kullanıcı aksiyonu gerekmez.

**Gerekçe:**
- "Rapor Oluştur" butonuna basılmasını beklemek veri kaybı riski yaratır (kullanıcı sayfayı kapatabilir).
- Her tamamlanan değerlendirme potansiyel bir mentörlük seansıdır ve DB'de hazır beklemelidir.
- Kullanıcı istediği zaman `GET /api/snapshots/` ile geçmiş oturumlarını görür, istediğinde chat'e girer.

**Akış:**
```
Judge Task tamamlanır → Snapshot atomik yazılır (AD-7) → Kullanıcı feedback ekranını görür
    → İstediği zaman "Sohbet Başlat" → Chat init → Coach açılış mesajı
```

---

### AD-12: Concurrent Sessions — Serbest Bırakma

**Karar:** MVP'de kullanıcının aynı anda kaç farklı snapshot üzerinde sohbet açabileceğine dair **kısıtlama getirilmeyecektir**.

**Davranış:**
- Kullanıcı dilerse 3 farklı sekmede 3 farklı soruyu tartışabilir.
- Maliyet kontrolü zaten "snapshot başına 15 kullanıcı mesajı" kuralıyla sağlanmaktadır.
- Locking mekanizması gereksiz karmaşıklık yaratır, MVP'de değer katmaz.

---

### AD-13: Retention Policy — Soft Delete Altyapısı

**Karar:** MVP'de veri sonsuz saklanacak, ancak soft delete altyapısı hazır olacaktır.

**MVP Davranışı:**
- Tüm snapshot ve chat verileri süresiz saklanır.
- Aktif silme job'ı (cron) yazılmaz, veri boyutu MVP'de yönetilebilir.

**Altyapı (şimdiden hazır):**
- `evaluation_snapshots.deleted_at` kolonu (nullable TIMESTAMP)
- `evaluation_snapshots.status` → `archived` değeri
- Query'lerde `WHERE deleted_at IS NULL` filtresi
- Gelecekte 1 yıllık retention policy uygulanabilir (cron job ile `deleted_at` set edilir)

**Neden Şimdiden:**
- Sonradan `deleted_at` kolonu eklemek migration gerektirir. Baştan koymak bedava.
- `status: archived` kullanıcıya "bu oturum arşivlendi" göstermek için yeterli.

---

## UX Flow

### A) Evaluation Result Screen
1. Judge değerlendirmesi tamamlandıktan sonra UI **8 metric card** gösterir.
2. Her metric card:
   - `user_score` (1–5)
   - `judge_score` (1–5)
   - `gap = |user_score - judge_score|` (kart üzerinde gösterilir)
   - Evidence preview (kısa snippet) veya "Kanıt" bölümü
3. Aksiyonlar:
   - **Sohbet Başlat** (Coach Chat)
   - (Opsiyonel) **Yeni soru üret**

### B) Sohbet Başlat (Metrik Seçimi)
- **Sohbet Başlat** tıklanınca modal/panel açılır, **8 metrik checkbox/buton** olarak gösterilir.
- Kullanıcı tartışmak istediği metrikleri seçer (önerilen: 1–3).
- Chat, **sadece seçilen metriklerin** context'i ile başlar.
- **Immutable:** Seçilen metrikler oturum boyunca değiştirilemez. Farklı metrikler tartışmak için yeni sohbet başlatılmalıdır.

### C) Coach Chat
- Tek coach modu. Sohbet evaluation snapshot'a bağlıdır:
  - question
  - model answer
  - sadece seçilen metrikler
  - her seçilen metrik için: scores + reasons + evidence + fix suggestions
- Coach ilk mesajda otomatik açılış yapar: seçilen metriklerdeki farkları özetler.

---

## Evidence ("Kanıt") Generation

### When
Evidence, **Stage 1 (Bağımsız Değerlendirme)** sırasında üretilir. (Bkz: AD-1)

### What
Her metrik için Judge şunları döndürür:
- 1–3 evidence span (alıntı) — model cevabından verbatim
- `why`: Rubrik bağlamında neden önemli olduğu (kısa)
- `better`: Düzeltme önerisi (bir örnek cümle veya kısa rewrite)
- `start`/`end`: Karakter pozisyonları (doğrulama için)

### Verification
Backend, 5 aşamalı self-healing doğrulama uygular. (Bkz: AD-2)

### Marketing Language
UI'da "Evidence / Kanıt" kullanılır ("RAG" değil).

---

## Evidence JSON Schema (per evaluation)

Tüm metrikler `evidence_json` içinde saklanır.

```json
{
  "truthfulness": {
    "user_score": 2,
    "judge_score": 2,
    "metric_gap": 0,
    "user_reason": "Yanlış bilgi içeriyor",
    "judge_reason": "Factual error detected in Nobel prize claim",
    "evidence": [
      {
        "start": 120,
        "end": 168,
        "quote": "Einstein 1921'de Nobel Kimya Ödülü aldı",
        "why": "Einstein Nobel Fizik Ödülü aldı, Kimya değil. Factual hallucination.",
        "better": "Einstein 1921'de Nobel Fizik Ödülü'nü fotoelektrik etki üzerine çalışmalarıyla aldı.",
        "verified": true,
        "highlight_available": true
      }
    ]
  },
  "clarity": {
    "user_score": 5,
    "judge_score": 4,
    "metric_gap": 1,
    "user_reason": "Gayet açık",
    "judge_reason": "Minor redundancy in explanation",
    "evidence": [
      {
        "start": 12,
        "end": 50,
        "quote": "Kısacası, özetle söylemek gerekirse",
        "why": "'Kısacası' ve 'özetle söylemek gerekirse' aynı anlama gelir, redundancy.",
        "better": "Kısacası, fotoelektrik etki...",
        "verified": true,
        "highlight_available": true
      }
    ]
  }
}
```

**Field Notes:**
- `metric_gap` = `abs(user_score - judge_score)`, backend'de hesaplanır.
- `user_reason` ve `judge_reason` opsiyonel, mevcut olduğunda dahil edilir.
- Evidence items:
  - `start`/`end` **zorunlu** (Judge prompt'unda enforce edilir).
  - `verified` **backend tarafında** self-healing algoritmasıyla hesaplanır (Bkz: AD-2).
  - `highlight_available` **backend tarafında** hesaplanır. Frontend'in highlight kararı bu alana bağlıdır:
    | `verified` | `highlight_available` | UI Davranışı |
    |------------|----------------------|--------------|
    | `true` | `true` | Highlight aktif, boyama yapılır (Aşama 1-3) |
    | `true` | `false` | Quote gösterilir, highlight yapılmaz, info label: *"Pozisyon tespit edilemedi"* (Aşama 4) |
    | `false` | `false` | "Kanıt doğrulanamadı" uyarısı (Aşama 5) |

---

## Chat Payload Schema (to LLM)

Kullanıcı sohbet başlatıp metrik seçtiğinde, sadece seçilen metrikler gönderilir.

```json
{
  "snapshot_id": "snap_20260210_143052_abc123",
  "question": "2024 Nobel Kimya Ödülü'nü kim aldı?",
  "model_answer": "Einstein 1921'de Nobel Kimya Ödülü aldı...",
  "model_name": "mistralai/mistral-nemo",
  "selected_metrics": ["truthfulness", "clarity"],
  "metrics": {
    "truthfulness": {
      "user_score": 2,
      "judge_score": 2,
      "metric_gap": 0,
      "user_reason": "Yanlış bilgi içeriyor",
      "judge_reason": "Factual error detected",
      "evidence": [
        {
          "start": 120,
          "end": 168,
          "quote": "Einstein 1921'de Nobel Kimya Ödülü aldı",
          "why": "Einstein Nobel Fizik Ödülü aldı, Kimya değil.",
          "better": "Einstein 1921'de Nobel Fizik Ödülü'nü aldı.",
          "verified": true,
          "highlight_available": true
        }
      ]
    },
    "clarity": {
      "user_score": 5,
      "judge_score": 4,
      "metric_gap": 1,
      "evidence": [
        {
          "start": 12,
          "end": 50,
          "quote": "Kısacası, özetle söylemek gerekirse",
          "why": "Redundancy",
          "better": "Kısacası, ...",
          "verified": true,
          "highlight_available": true
        }
      ]
    }
  },
  "chat_history": [
    {"role": "assistant", "content": "Merhaba! Truthfulness ve Clarity metrikleri hakkında..."},
    {"role": "user", "content": "Neden Clarity'de 4 verdin?"}
  ]
}
```

**Kurallar:**
- Chat context'e seçilmeyen 5-7 metrik dahil **edilmez**.
- LLM, seçilen metrikler ve sağlanan evidence içinde kalması için talimatlandırılır.
- `chat_history` DB'den çekilir, **sadece son 6 mesaj** (3 user + 3 assistant) dahil edilir. Eski mesajlar token verimliliği için kesilir (Bkz: AD-4, Token Windowing).

---

## Prompting Notes (Implementation Guidance)

### Judge Prompt (Stage 1) — Evidence Eklentisi
- Mevcut Stage 1 prompt'una evidence output talimatı eklenir.
- Output: strict JSON, Evidence schema'ya uygun.
- Evidence alıntıları `model_answer`'dan **verbatim** alınmalı.
- `start`/`end` karakter indeksleri zorunlu.
- `why` (rubrik bağlantılı açıklama) ve `better` (düzeltme önerisi) zorunlu.
- Score null olan metrikler için evidence boş array `[]` olabilir.

### Coach Chat Prompt
- Tek coach modu (GPT-4o-mini).
- Metrik bazlı coaching:
  - Gap'i açıkla
  - Evidence'a referans ver
  - 1–2 somut iyileştirme öner
  - Opsiyonel: kullanıcıdan yeniden yazmayı ve değerlendirmeyi iste
- İlk mesajda otomatik açılış: seçilen metriklerdeki farkları özetle.
- Sohbet Türkçe, teknik terimler İngilizce kalabilir.
- Seçilmeyen metrikler hakkında konuşmayı **reddet**.
- **Strict Evidence Usage (AD-10):** Model cevabından kendi alıntılarını üretemez. Sadece Stage 1'de üretilmiş evidence'lara referans verebilir. Evidence yoksa bunu dürüstçe belirtir.

---
