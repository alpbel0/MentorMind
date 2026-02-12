# Frontend Design Sorunları

**Tarih:** 6 Şubat 2026  
**Sayfa:** `/evaluate` - Evaluation Flow  
**Durum:** 🔴 İyileştirme Gerekiyor

---

## 📋 Tespit Edilen Sorunlar

### 1. Soru ve Cevap Görünürlüğü Sorunu

**Mevcut Durum:**
- Question bölümü çok küçük bir alana sıkıştırılmış
- Model response (K model'in cevabı) tam olarak görünmüyor
- "View Full" butonu ile açılması gerekiyor
- Kullanıcı soru ve cevabı rahatça okuyamıyor

**Neden Sorun:**
- Değerlendirme yaparken soru ve cevap sürekli görünür olmalı
- Kullanıcı her metrik için soru/cevaba bakarak değerlendirme yapacak
- "View Full" butonuna tıklamak ekstra adım ve UX açısından kötü
- Soru ve cevap, değerlendirmenin temelini oluşturuyor - gizli olmamalı

**Beklenen Davranış:**
- Soru ve model cevabı sayfanın üst kısmında **açık ve net** görünmeli
- Minimum 300-400px yükseklikte bir alan olmalı
- Scroll edilebilir olabilir ama **default olarak açık** durmalı
- "View Full" butonu yerine **daima görünür** olmalı

---

### 2. Puan Verme (Scoring) UI Sorunu

**Mevcut Durum:**
- 1-5 arası sayı butonları düz, basit bir grid layout'ta
- N/A butonu sağ üstte küçük
- "Very Poor" ve "Excellent" etiketleri var ama vurgulanmamış
- **KRİTİK SORUN**: 3'e bastığında 3 gözükmüyor - seçilen buton vurgulanmıyor
- Hangi puanı seçtiğini anlayamıyor kullanıcı

**Neden Sorun:**
- Butonlar arasında active/selected state yok
- Seçilen buton ile seçilmeyen buton arasında görsel fark yok
- Kullanıcı "3'e bastım mı basmadım mı?" diye düşünüyor
- Her metrik için 8 kere bu kafa karışıklığını yaşıyor
- N/A opsiyonu yeterince görünür değil

**Beklenen Davranış:**
- **Sayı butonları kalsın** (1, 2, 3, 4, 5) - slider veya star rating OLMAYACAK
- Butonların görsel durumları (states) net olmalı:
  - **Default state** (seçilmemiş): Gri border, beyaz background
  - **Hover state**: Hafif mavi background, cursor pointer
  - **Active/Selected state**: 
    - Koyu mavi background + beyaz text (örn: bg-indigo-600)
    - Veya kalın border + scale efekti
    - Veya shadow efekti
    - **ÖNEMLİ**: Seçili buton NET bir şekilde diğerlerinden farklı görünmeli
  - **Disabled state** (N/A seçiliyse): Gri ve tıklanamaz

- N/A opsiyonu daha belirgin olmalı:
  - Toggle switch veya checkbox şeklinde
  - "Bu metrik uygulanamaz" metni yanında
  - N/A seçilince tüm butonlar disable olmalı

- Ek görsel iyileştirmeler:
  - Her buton için tooltip (hover'da "Excellent", "Good", "Fair", "Poor", "Very Poor")
  - Seçilen puan altında "Puan: 3/5" gibi text feedback
  - Smooth transition animasyonları (color, scale değişimlerinde)

---

### 3. 8 Metrik Grid Layout Sorunu

**Mevcut Durum:**
- 8 metrik 2 sütun halinde, 4x2 grid
- Her kart çok sıkışık görünüyor
- Aynı anda çok fazla bilgi ekranda
- Scroll gerekiyor

**Neden Sorun:**
- Kullanıcı aynı anda 8 metrik görmek zorunda
- Cognitive overload (bilgi yükü fazla)
- Her kartın içinde: başlık, açıklama, 5 buton, N/A, textarea var
- Ekran karmaşık ve bunaltıcı görünüyor

**Öneriler:**
- **Accordion/Collapse yaklaşımı**: Her metrik kapalı başlasın, tıklanınca açılsın
- **Stepper/Wizard yaklaşımı**: Metrikleri tek tek göster, "Next" butonu ile ilerle
- **Tabs yaklaşımı**: 8 tab, her metrik bir tab'de
- **Vertical list**: 2 sütun yerine tek sütun, daha geniş kartlar

---

## 🎨 Öncelikli İyileştirmeler

### Yüksek Öncelik (P0)
1. ✅ **Soru ve cevap görünürlüğünü artır**
   - Default olarak açık, geniş alan
   - "View Full" butonunu kaldır veya modal yerine expand yap
   
2. ✅ **Puan verme UI'ını yeniden tasarla**
   - Daha modern, interaktif bir component
   - Görsel feedback (hover, active states)
   - Net puan açıklamaları

### Orta Öncelik (P1)
3. ⚠️ **8 metrik layout'unu iyileştir**
   - Grid yerine daha iyi bir yaklaşım (stepper/accordion)
   - Cognitive load'u azalt

### Düşük Öncelik (P2)
4. 📝 **Reasoning textarea'sını iyileştir**
   - Auto-resize (büyüyen textarea)
   - Character counter
   - Placeholder metinleri daha açıklayıcı

---

## 💡 Design Inspiration Önerileri

### Modern Scoring UI Örnekleri
- **Google Forms** - Star rating ve slider
- **App Store Reviews** - 5 yıldız sistemi
- **SurveyMonkey** - Likert scale with labels
- **Typeform** - Tek soru, büyük butonlar, smooth geçişler

### Multi-step Form Örnekleri
- **Typeform** - Her soru ayrı ekran, smooth transitions
- **Linear** - Issue creation wizard, step-by-step
- **Stripe Checkout** - Progress bar + stepper

---

## 📊 Kullanıcı Deneyimi Hedefleri

**Mevcut Durum:**
- Kullanıcı soruyu görmekte zorlanıyor ❌
- Puan vermek mekanik ve sıkıcı ❌
- 8 metrik aynı anda bunaltıcı ❌

**Hedef Durum:**
- Kullanıcı soru ve cevabı rahatça okuyor ✅
- Puan vermek görsel ve eğlenceli ✅
- Değerlendirme akışı doğal ve odaklı ✅

---

## 🔄 Sonraki Adımlar

1. Bu sorunları inceleyip hangi çözümün en uygun olduğuna karar ver
2. Seçilen design approach için wireframe/mockup hazırla (opsiyonel)
3. Component'leri yeniden tasarla
4. Kullanıcı testine al (kendin kullan ve feedback topla)

---

**Not:** Bu dokümanda kod yok, sadece sorunlar ve öneriler belgelendi. Implementation aşaması ayrı bir task.
