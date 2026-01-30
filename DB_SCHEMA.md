# MentorMind Database Schema Documentation

Bu dosya MentorMind projesinin veritabanı yapısını, tablolar arası ilişkileri ve veri modellerini en ince ayrıntısına kadar dokümante eder.

## 📌 Genel Bakış
MentorMind; soru üretimi, model yanıtları, kullanıcı değerlendirmeleri ve iki aşamalı judge (hakem) sistemini yönetmek için ilişkisel (PostgreSQL) ve vektör tabanlı (ChromaDB) hibrit bir yapı kullanır.

---

## 🗄️ İlişkisel Tablolar (PostgreSQL)

### 1. Özel Veri Tipleri (ENUMs)
Sistemde tutarlılığı sağlamak için kullanılan sabit değer listeleri:

*   **`metric_type`**: `Truthfulness`, `Helpfulness`, `Safety`, `Bias`, `Clarity`, `Consistency`, `Efficiency`, `Robustness`
*   **`difficulty_level`**: `easy`, `medium`, `hard`

### 2. `question_prompts` Tablosu
Claude'un soru üretirken kullandığı ana şablonları (templates) tanımlar.

| Sütun | Veri Tipi | Özellikler | Açıklama |
| :--- | :--- | :--- | :--- |
| `id` | SERIAL | PRIMARY KEY | Otomatik artan benzersiz kimlik. |
| `primary_metric` | `metric_type` | NOT NULL | Şablonun odaklandığı ana metrik. |
| `bonus_metrics` | JSONB | NOT NULL, DEFAULT '[]' | Gizli değerlendirilecek yan metrikler listesi. |
| `question_type` | TEXT | NOT NULL | Soru kategorisi (örn: `hallucination_test`). |
| `user_prompt` | TEXT | NOT NULL | Claude'a gönderilecek ham şablon metni. |
| `golden_examples` | JSONB | NOT NULL, DEFAULT '[]' | Few-shot öğrenme için örnek soru-cevaplar. |
| `difficulty` | `difficulty_level` | NOT NULL | Sorunun zorluk seviyesi. |
| `category_hints` | JSONB | NOT NULL, DEFAULT '["any"]' | Kategori tercihleri (örn: `["Math", "Coding"]`). |
| `is_active` | BOOLEAN | DEFAULT TRUE | Şablonun kullanımda olup olmadığını belirler. |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Kayıt oluşturulma tarihi. |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Son güncelleme tarihi (Otomatik güncellenir). |

### 3. `questions` Tablosu
Şablonlardan üretilen veya havuza eklenen somut soruları tutar.

| Sütun | Veri Tipi | Özellikler | Açıklama |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | PRIMARY KEY | Format: `q_YYYYMMDD_HHMMSS_randomhex`. |
| `question` | TEXT | NOT NULL | Sorunun metni. |
| `category` | TEXT | NOT NULL | Sorunun kategorisi (Math, Coding, vb.). |
| `difficulty` | `difficulty_level` | NOT NULL | Sorunun zorluk seviyesi (ENUM). |
| `reference_answer` | TEXT | - | Claude tarafından üretilen ideal cevap. |
| `expected_behavior` | TEXT | - | Modelin sergilemesi beklenen davranış notu. |
| `rubric_breakdown` | JSONB | NOT NULL | 1-5 puan arası değerlendirme kriterleri. |
| `primary_metric` | `metric_type` | NOT NULL | Sorunun ana metriği (Denormalize ENUM). |
| `bonus_metrics` | JSONB | NOT NULL, DEFAULT '[]' | Yan metrikler (Denormalize). |
| `question_prompt_id` | INTEGER | FK (SET NULL) | Kaynak şablon referansı. |
| `times_used` | INTEGER | DEFAULT 0 | Sorunun kaç kez seçildiği. |
| `first_used_at` | TIMESTAMP | - | İlk kullanım tarihi. |
| `last_used_at` | TIMESTAMP | - | Son kullanım tarihi. |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Kayıt oluşturulma tarihi. |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Son güncelleme tarihi (Otomatik güncellenir). |

### 4. `model_responses` Tablosu
K modellerinin (denek modeller) sorulara verdiği ham yanıtları saklar.

| Sütun | Veri Tipi | Özellikler | Açıklama |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | PRIMARY KEY | Format: `resp_YYYYMMDD_HHMMSS_randomhex`. |
| `question_id` | TEXT | FK (CASCADE) | Yanıtın ait olduğu soru. |
| `model_name` | TEXT | NOT NULL | Yanıtı veren modelin ismi (Örn: `gpt-3.5-turbo`). |
| `response_text` | TEXT | NOT NULL | Modelin ürettiği yanıt metni. |
| `evaluated` | BOOLEAN | DEFAULT FALSE | Kullanıcı tarafından puanlanıp puanlanmadığı. |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Kayıt oluşturulma tarihi. |

### 5. `user_evaluations` Tablosu
Kullanıcının model yanıtlarına verdiği puanları ve gerekçeleri saklar.

| Sütun | Veri Tipi | Özellikler | Açıklama |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | PRIMARY KEY | Format: `eval_YYYYMMDD_HHMMSS_randomhex`. |
| `response_id` | TEXT | FK (CASCADE) | Değerlendirilen model yanıtı. |
| `evaluations` | JSONB | NOT NULL | 8 metrik için puan ve gerekçeleri içeren nesne. |
| `judged` | BOOLEAN | DEFAULT FALSE | GPT-4o tarafından işlenip işlenmediği. |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Değerlendirme tarihi. |

### 6. `judge_evaluations` Tablosu
GPT-4o tarafından yapılan iki aşamalı mentörlük analizlerini ve gap (sapma) verilerini saklar.

| Sütun | Veri Tipi | Özellikler | Açıklama |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | PRIMARY KEY | Format: `judge_YYYYMMDD_HHMMSS_randomhex`. |
| `user_evaluation_id` | TEXT | FK (CASCADE) | İlgili kullanıcı değerlendirmesi. |
| `independent_scores` | JSONB | NOT NULL | Stage 1: GPT-4o'nun bağımsız puanları. |
| `alignment_analysis` | JSONB | NOT NULL | Stage 2: Kullanıcı-Judge kıyaslaması ve geri bildirimler. |
| `judge_meta_score` | INTEGER | CHECK (1-5) | Değerlendirme kalitesi puanı. |
| `overall_feedback` | TEXT | NOT NULL | Genel mentörlük mesajı. |
| `improvement_areas` | JSONB | DEFAULT '[]' | Geliştirilmesi gereken alanlar listesi. |
| `positive_feedback` | JSONB | DEFAULT '[]' | Başarılı bulunan noktalar listesi. |
| `vector_context` | JSONB | - | ChromaDB'den çekilen geçmiş hata bağlamı. |
| `primary_metric` | `metric_type` | NOT NULL | Odaklanılan ana metrik (ENUM). |
| `primary_metric_gap` | REAL | NOT NULL | Ana metriğe ait puan farkı. |
| `weighted_gap` | REAL | NOT NULL | Ağırlıklı genel sapma puanı. |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Kayıt oluşturulma tarihi. |

**Kısıtlamalar & İndeksler:**
*   **INDEX:** `idx_judge_evaluations_meta_score` - Performans takibi için.
*   **INDEX:** `idx_judge_evaluations_metric` - Metrik bazlı başarı analizi için.

---

---

## 🧠 Vektör Hafıza Yapısı (ChromaDB)

*(Detaylar konuşulduktan sonra buraya eklenecektir)*

---

## 🔄 Veri Akış Şeması

*(Detaylar konuşulduktan sonra buraya eklenecektir)*

---

**Son Güncelleme:** 29 Ocak 2026
**Durum:** Taslak Aşamasında (Detaylı görüşme bekleniyor)
