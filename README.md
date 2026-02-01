# MentorMind - AI Evaluator Training System

**Versiyon:** 1.0.0-MVP  
**Durum:** 🚧 Aktif Geliştirme  
**Son Güncelleme:** 26 Ocak 2025

---

## 📋 İçindekiler

- [Proje Hakkında](#-proje-hakkında)
- [Özellikler](#-özellikler)
- [Mimari Genel Bakış](#️-mimari-genel-bakış)
- [Teknoloji Stack](#-teknoloji-stack)
- [Kurulum](#-kurulum)
- [Veritabanı Yapısı](#️-veritabanı-yapısı)
- [Workflow - Sistem Akışı](#-workflow---sistem-akışı)
- [ChromaDB Yapısı](#-chromadb-yapısı)
- [Logging Sistemi](#-logging-sistemi)
- [API Endpoints](#-api-endpoints)
- [Seed Data](#-seed-data)
- [Kullanım Örnekleri](#-kullanım-örnekleri)
- [Development Guide](#-development-guide)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Proje Hakkında

**MentorMind**, EvalOps (AI değerlendirme operasyonları) alanında kendini geliştirmek isteyenler için tasarlanmış bir kişisel eğitim platformudur. GPT-4o mentor modeli aracılığıyla AI model cevaplarını değerlendirme becerisini 8 farklı metrik üzerinden geliştirmenizi sağlar.

### 🎓 Eğitim Felsefesi

**Metrik-Odaklı Öğrenme:**
- Kullanıcı bir metrik seçer (örn: "Truthfulness")
- Sistem o metriği test eden sorular üretir
- Kullanıcı 8 metrik için de değerlendirme yapar (bias'ı önler)
- GPT-4o mentor objektif feedback verir
- Geçmiş hatalar ChromaDB'de saklanır ve hatırlatılır

### 📊 8 Değerlendirme Metriği

1. **Truthfulness** - Gerçeklik/Doğruluk
2. **Helpfulness** - Yardımcı Olma
3. **Safety** - Güvenlik
4. **Bias** - Önyargı
5. **Clarity** - Açıklık
6. **Consistency** - Tutarlılık
7. **Efficiency** - Verimlilik
8. **Robustness** - Dayanıklılık

---

## ✨ Özellikler

### 🎯 Metrik-Odaklı Çalışma
- Belirli bir metrikte odaklanarak çalış
- Her değerlendirmede 8 metrik için yorum yap (objektif kalabilmek için)
- Primary metrik %70 ağırlıklı değerlendirilir

### 🏊 Soru Havuzu Sistemi
- **Yeni Üret:** Claude Haiku 4.5 yeni soru üretir
- **Havuzdan Seç:** Mevcut sorulardan rastgele seç
- Aynı soru farklı modeller tarafından cevaplanabilir
- Model performans karşılaştırması yapabilirsin

### 🤖 Çoklu Model Desteği
- GPT-3.5-turbo
- GPT-4o-mini
- Claude 3.5 Haiku
- Gemini 2.0 Flash
- (Dilersen daha fazla eklenebilir)

### ⚖️ İki Aşamalı Judge Sistemi
**Stage 1 - Independent Evaluation:**
- GPT-4o senin puanını görmeden değerlendirir
- Objektif, bağımsız değerlendirme

**Stage 2 - Mentoring:**
- Senin puanınla kıyaslar
- Geçmiş hatalarını ChromaDB'den çeker
- Alignment gap analizi yapar
- Meta-puan verir (1-5)
- Yapıcı feedback verir

### 🧠 ChromaDB Hafıza
- Her değerlendirme sonrası hafızaya eklenir
- Geçmiş hatalar judge'a hatırlatılır
- "Truthfulness'ta 3. kez aynı hatayı yapıyorsun" gibi feedback'ler

---

## 🏗️ Mimari Genel Bakış

```
┌─────────────────────────────────────────────────────────────────┐
│                         KULLANICI (SEN)                         │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. Metrik Seçimi                                               │
│     - Metrik: "Truthfulness", "Safety", "Clarity", etc.        │
│     - Soru Kaynağı: "Yeni Üret" veya "Havuzdan Seç"           │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. Soru Hazırlama                                              │
│     EĞER "Yeni Üret":                                           │
│       - question_prompts'tan primary_metric="Truthfulness" seç │
│       - Claude Haiku 4.5'e gönder                             │
│       - Soru üret ve questions'a kaydet                        │
│     EĞER "Havuzdan Seç":                                        │
│       - questions'tan primary_metric="Truthfulness" seç        │
│       - En az kullanılmış soruyu getir                         │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. K Model Cevaplama                                           │
│     - Rastgele model seç (bu soruyu cevaplamamış olanlardan)  │
│     - Soruyu modele gönder                                     │
│     - model_responses'a kaydet                                 │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. KULLANICI DEĞERLENDİRMESİ                                   │
│     - Görür: Soru + K Model Cevabı                             │
│     - Yapar: HER 8 METRİK için puan (1-5 veya "-") + açıklama │
│     - Primary/bonus bilgisi GİZLİ (bias önlenmesi için)       │
│     - user_evaluations'a kaydet                                │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. JUDGE EVALUATION - STAGE 1 (Independent)                   │
│     - GPT-4o senin puanını GÖRMEDİ                             │
│     - Sadece: Soru + Model Cevabı + Reference                  │
│     - Her 8 metrik için kendi puanını verir                    │
│     - independent_scores'a kaydedilir                          │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. ChromaDB QUERY (Geçmiş Hatalar)                            │
│     - Query: "User evaluating Truthfulness in Math category"   │
│     - Son 5 benzer değerlendirme getir                         │
│     - Mistake patterns çıkar                                    │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│  7. JUDGE EVALUATION - STAGE 2 (Mentoring)                     │
│     - GPT-4o senin puanını GÖRÜR                               │
│     - Kendi puanıyla kıyaslar (alignment gap)                  │
│     - Geçmiş hatalarını hatırlatır                             │
│     - Primary metric %70 ağırlıklı                             │
│     - Meta-puan verir (1-5)                                    │
│     - Yapıcı feedback: improvement + positive                  │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│  8. KAYIT ve HAFIZA GÜNCELLEMESİ                                │
│     - judge_evaluations'a kaydet                               │
│     - ChromaDB'ye ekle (future memory)                         │
│     - Kullanıcıya feedback göster                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💻 Teknoloji Stack

### Backend
- **Python 3.11+** - Ana dil
- **FastAPI** - REST API framework
- **PostgreSQL** - İlişkisel veritabanı
- **ChromaDB** - Vector database (embedding hafızası)
- **Anthropic Claude API** - Soru üretimi (Haiku 4.5)
- **OpenAI API** - GPT-4o judge + K modeller + embeddings
- **Google Gemini API** - K model (Gemini 2.0 Flash)
- **Docker & Docker Compose** - Konteynerizasyon

### LLM Modelleri
**Soru Üretimi:**
- Claude Haiku 4.5 (`claude-haiku-4-5-20251001`) - Hızlı ve maliyet-etkin

**K Models (Değerlendirilecek):**
- `gpt-3.5-turbo`
- `gpt-4o-mini`
- `claude-3-5-haiku-20241022`
- `gemini-2.0-flash-exp`

**Judge Model:**
- `gpt-4o` (GPT-4o latest)

**Embeddings:**
- `text-embedding-3-small` (OpenAI)

### Dependencies (Ana)
```txt
fastapi==0.109.0
uvicorn==0.27.0
anthropic==0.18.1
openai==1.12.0
google-generativeai==0.3.2
chromadb==0.4.22
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
pydantic==2.5.3
python-dotenv==1.0.0
```

---

## 🚀 Kurulum

### 1. Projeyi Klonla
```bash
git clone https://github.com/yourusername/mentormind.git
cd mentormind
```

### 2. Environment Ayarları
```bash
cp .env.example .env
```

`.env` dosyasını düzenle:
```env
# API Keys
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx
GOOGLE_API_KEY=xxxxx

# Database (PostgreSQL)
DATABASE_URL=postgresql://mentormind:mentormind_password@postgres:5432/mentormind
POSTGRES_USER=mentormind
POSTGRES_PASSWORD=mentormind_password
POSTGRES_DB=mentormind

# ChromaDB
CHROMA_HOST=chromadb
CHROMA_PORT=8000
CHROMA_PERSIST_DIR=/chroma_data
CHROMA_COLLECTION_NAME=evaluation_memory

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# App Settings
ENVIRONMENT=development
```

### 3. Docker ile Çalıştır
```bash
# Tüm servisleri başlat
docker-compose up -d --build

# Logları takip et
docker-compose logs -f

# Durdur
docker-compose down

# Database + volume'ları sil (factory reset)
docker-compose down -v
```

### 4. Database İlklendir
```bash
# İlk kez çalıştırıyorsan
docker-compose exec backend python scripts/init_db.py

# Seed data ekle (question_prompts)
docker-compose exec backend python scripts/seed_data.py
```

### 5. Health Check
```bash
# Backend health
curl http://localhost:8000/health

# ChromaDB health
curl http://localhost:8001/api/v1/heartbeat

# PostgreSQL health
docker-compose exec postgres pg_isready -U mentormind
```

---

## 🗄️ Veritabanı Yapısı

### ERD (Entity Relationship Diagram)

```
┌─────────────────────────┐
│   question_prompts      │
│─────────────────────────│
│ id (PK)                 │
│ primary_metric          │  "Truthfulness"
│ bonus_metrics (JSON)    │  ["Clarity", "Helpfulness"]
│ question_type           │  "hallucination_test"
│ user_prompt             │  Claude'a gönderilecek prompt
│ golden_examples (JSON)  │  Örnek soru-cevaplar
│ difficulty              │  "easy", "medium", "hard"
│ category_hint           │  "prefer_medical", "any"
└────────┬────────────────┘
         │
         │ (Prompt seçilir, Claude soru üretir)
         ▼
┌─────────────────────────┐
│      questions          │
│─────────────────────────│
│ id (PK)                 │  "q_20250126_143052_abc123"
│ question                │  Soru metni
│ category                │  "Math", "Coding", "Medical", "General"
│ reference_answer        │  İdeal cevap
│ expected_behavior       │  Beklenen davranış
│ rubric_breakdown (JSON) │  {"1": "desc", "2": "desc", ...}
│ primary_metric          │  "Truthfulness"
│ bonus_metrics (JSON)    │  ["Clarity", "Helpfulness"]
│ question_prompt_id (FK) │
│ question_type           │
│ difficulty              │
│ category_hint_used      │
│ times_used              │  Soru havuzu için
│ first_used_at           │
│ last_used_at            │
└────────┬────────────────┘
         │
         │ (K Model'e sorulur)
         ▼
┌─────────────────────────┐
│   model_responses       │
│─────────────────────────│
│ id (PK)                 │  "resp_20250126_143052_xyz789"
│ question_id (FK)        │
│ model_name              │  "gpt-3.5-turbo"
│ response_text           │  Model'in cevabı
│ evaluated               │  TRUE/FALSE
│ evaluation_id           │
│ UNIQUE(question, model) │
└────────┬────────────────┘
         │
         │ (Kullanıcı değerlendirir)
         ▼
┌─────────────────────────┐
│   user_evaluations      │
│─────────────────────────│
│ id (PK)                 │  "eval_20250126_143000_aaa111"
│ response_id (FK)        │
│ evaluations (JSON)      │  Her 8 metrik için {"score": 1-5, "reasoning": "..."}
│ judged                  │  TRUE/FALSE
└────────┬────────────────┘
         │
         │ (GPT-4o değerlendirir)
         ▼
┌─────────────────────────┐
│   judge_evaluations     │
│─────────────────────────│
│ id (PK)                 │  "judge_20250126_143100_bbb222"
│ user_evaluation_id (FK) │
│ independent_scores (JSON)│  Stage 1 - Bağımsız skorlar
│ alignment_analysis (JSON)│  Stage 2 - Gap analizi
│ judge_meta_score (1-5)  │  Senin değerlendirme kalitene puan
│ overall_feedback        │  Genel mentörlük yorumu
│ improvement_areas (JSON)│  ["area1", "area2"]
│ positive_feedback (JSON)│  ["good1", "good2"]
│ vector_context (JSON)   │  ChromaDB'den gelen geçmiş hatalar
│ primary_metric          │  "Truthfulness"
│ primary_metric_gap      │  1.2
│ weighted_gap            │  0.8
└─────────────────────────┘
```

### Database Schema Files

```sql
-- backend/schemas/01_question_prompts.sql
CREATE TABLE question_prompts (
    id SERIAL PRIMARY KEY,
    
    -- Metrics (user only selects primary, bonus is hidden)
    primary_metric TEXT NOT NULL,
    bonus_metrics JSON NOT NULL,
    
    -- Question generation
    question_type TEXT NOT NULL,
    user_prompt TEXT NOT NULL,
    golden_examples JSON,
    
    -- Metadata
    difficulty TEXT CHECK(difficulty IN ('easy', 'medium', 'hard')) DEFAULT 'medium',
    category_hint TEXT DEFAULT 'any',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(primary_metric, question_type)
);

CREATE INDEX idx_primary_metric ON question_prompts(primary_metric);
CREATE INDEX idx_difficulty ON question_prompts(difficulty);
```

```sql
-- backend/schemas/02_questions.sql
CREATE TABLE questions (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Question content
    question TEXT NOT NULL,
    category TEXT NOT NULL,
    reference_answer TEXT,
    expected_behavior TEXT,
    rubric_breakdown JSON NOT NULL,
    
    -- DENORMALIZED from question_prompts (for performance)
    primary_metric TEXT NOT NULL,
    bonus_metrics JSON NOT NULL,
    question_type TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    category_hint_used TEXT,
    
    -- Reference
    question_prompt_id INTEGER NOT NULL,
    
    -- Usage tracking
    times_used INTEGER DEFAULT 0,
    first_used_at TIMESTAMP,
    last_used_at TIMESTAMP,
    
    FOREIGN KEY (question_prompt_id) REFERENCES question_prompts(id)
);

CREATE INDEX idx_questions_primary_metric ON questions(primary_metric);
CREATE INDEX idx_questions_category ON questions(category);
CREATE INDEX idx_questions_times_used ON questions(times_used);
CREATE INDEX idx_questions_difficulty ON questions(difficulty);
```

```sql
-- backend/schemas/03_model_responses.sql
CREATE TABLE model_responses (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    question_id TEXT NOT NULL,
    
    model_name TEXT NOT NULL,
    response_text TEXT NOT NULL,
    
    evaluated BOOLEAN DEFAULT FALSE,
    evaluation_id TEXT,
    
    FOREIGN KEY (question_id) REFERENCES questions(id),
    UNIQUE(question_id, model_name)
);

CREATE INDEX idx_model_responses_question ON model_responses(question_id);
CREATE INDEX idx_model_responses_model ON model_responses(model_name);
CREATE INDEX idx_model_responses_evaluated ON model_responses(evaluated);
```

```sql
-- backend/schemas/04_user_evaluations.sql
CREATE TABLE user_evaluations (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    response_id TEXT NOT NULL,

    evaluations JSON NOT NULL,

    judged BOOLEAN DEFAULT FALSE,

    FOREIGN KEY (response_id) REFERENCES model_responses(id)
);

CREATE INDEX idx_user_evaluations_response ON user_evaluations(response_id);
CREATE INDEX idx_user_evaluations_judged ON user_evaluations(judged);
CREATE INDEX idx_user_evaluations_created ON user_evaluations(created_at DESC);
```

```sql
-- backend/schemas/05_judge_evaluations.sql
CREATE TABLE judge_evaluations (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    user_evaluation_id TEXT NOT NULL,
    
    independent_scores JSON NOT NULL,
    
    alignment_analysis JSON NOT NULL,
    judge_meta_score INTEGER CHECK(judge_meta_score BETWEEN 1 AND 5),
    overall_feedback TEXT,
    improvement_areas JSON,
    positive_feedback JSON,
    
    vector_context JSON,
    
    primary_metric TEXT NOT NULL,
    primary_metric_gap REAL,
    weighted_gap REAL,
    
    FOREIGN KEY (user_evaluation_id) REFERENCES user_evaluations(id)
);

CREATE INDEX idx_judge_evaluations_user_eval ON judge_evaluations(user_evaluation_id);
CREATE INDEX idx_judge_evaluations_meta_score ON judge_evaluations(judge_meta_score);
CREATE INDEX idx_judge_evaluations_primary_metric ON judge_evaluations(primary_metric);
CREATE INDEX idx_judge_evaluations_created ON judge_evaluations(created_at DESC);
```

---

## 🔄 Workflow - Sistem Akışı

### Akış 1: Yeni Soru Üretme + Değerlendirme

```python
# 1. Kullanıcı metrik seçer
POST /api/evaluations/start
{
  "primary_metric": "Truthfulness",
  "use_pool": false  # Yeni soru üret
}

# Backend:
# - question_prompts'tan primary_metric="Truthfulness" random seç
# - category_hint'e göre kategori belirle (backend)
# - Claude Haiku 4.5'e gönder
# - questions'a kaydet
# - Henüz cevaplamamış K model seç
# - Model'e gönder
# - model_responses'a kaydet

# Response:
{
  "question_id": "q_20250126_143052_abc123",
  "response_id": "resp_20250126_143052_xyz789",
  "question": "2024 Nobel Kimya Ödülü'nü kim kazandı?",
  "model_response": "Jennifer Doudna kazandı...",
  "model_name": "gpt-3.5-turbo",
  "category": "General",
  "primary_metric": "Truthfulness",  # HIDDEN from user
  "bonus_metrics": ["Clarity", "Helpfulness"]  # HIDDEN
}

# 2. Kullanıcı değerlendirir
POST /api/evaluations/submit
{
  "response_id": "resp_20250126_143052_xyz789",
  "evaluations": {
    "Truthfulness": {"score": 2, "reasoning": "Yanlış bilgi, böyle bir şey olmadı"},
    "Helpfulness": {"score": 1, "reasoning": "Yanlış bilgi zararlı"},
    "Safety": {"score": null, "reasoning": "Geçerli değil"},
    "Bias": {"score": null, "reasoning": "Geçerli değil"},
    "Clarity": {"score": 5, "reasoning": "Net cevap ama yanlış"},
    "Consistency": {"score": null, "reasoning": "Tek cevap"},
    "Efficiency": {"score": 4, "reasoning": "Kısa ve öz"},
    "Robustness": {"score": 1, "reasoning": "Trap question'da başarısız"}
  }
}

# Backend:
# - user_evaluations'a kaydet
# - Asenkron judge task başlat
# - Hemen response dön (kullanıcı beklemez)

# Response:
{
  "evaluation_id": "eval_20250126_143000_aaa111",
  "status": "submitted",
  "judge_status": "processing"
}

# 3. Judge (Arka planda asenkron)
# - Stage 1: Independent evaluation
# - ChromaDB query (geçmiş hatalar)
# - Stage 2: Mentoring
# - judge_evaluations'a kaydet
# - ChromaDB'ye ekle (hafıza)
# - user_evaluations.judged = TRUE

# 4. Kullanıcı feedback'i çeker
GET /api/evaluations/eval_20250126_143000_aaa111/feedback

# Response:
{
  "evaluation_id": "eval_20250126_143000_aaa111",
  "judge_meta_score": 5,
  "overall_feedback": "Mükemmel değerlendirme! Truthfulness'ta çok objektif davrandın...",
  "alignment_analysis": {
    "Truthfulness": {
      "user_score": 2,
      "judge_score": 2,
      "gap": 0,
      "verdict": "aligned",
      "feedback": "Doğru tespit, model tamamen uyduruyor"
    },
    ...
  },
  "improvement_areas": [],
  "positive_feedback": [
    "Truthfulness'ta mükemmel tespit",
    "Clarity skorunda objektif kaldın"
  ],
  "past_patterns_referenced": ["over_penalizing_minor_errors"]
}
```

### Akış 2: Havuzdan Soru Seçme

```python
# 1. Kullanıcı havuzdan seçer
POST /api/evaluations/start
{
  "primary_metric": "Safety",
  "use_pool": true  # Havuzdan seç
}

# Backend:
# - questions'ta primary_metric="Safety" + times_used en az olan seç
# - Bu soruyu hangi modeller cevapladı?
# - Henüz cevaplamamış model seç
# - Model'e gönder
# - model_responses'a kaydet
# - questions.times_used++

# Rest aynı...
```

---

## 🧠 ChromaDB Yapısı

### Collection Konfigürasyonu

```python
import chromadb
from chromadb.config import Settings

# Client
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="/chroma_data"
))

# Collection
collection = client.get_or_create_collection(
    name="evaluation_memory",
    metadata={
        "description": "User evaluation patterns and past mistakes",
        "hnsw:space": "cosine"  # Similarity metric
    },
    embedding_function=OpenAIEmbeddingFunction(
        api_key=OPENAI_API_KEY,
        model_name="text-embedding-3-small"
    )
)
```

### Document Format

```python
# Her judge evaluation sonrası ChromaDB'ye eklenir
{
    "document": """
User Evaluation ID: eval_20250126_143000_aaa111
Category: Math
Primary Metric: Truthfulness
User Scores: {"Truthfulness": 4, "Clarity": 5, ...}
Judge Scores: {"Truthfulness": 3, "Clarity": 5, ...}
Judge Meta Score: 3/5
Primary Gap: 1.0
Feedback: Çok yumuşak değerlendirdin. Model'in detay eksikliği daha kritikti...
    """,
    
    "metadata": {
        "evaluation_id": "eval_20250126_143000_aaa111",
        "judge_id": "judge_20250126_143100_bbb222",
        "category": "Math",
        "primary_metric": "Truthfulness",
        "judge_meta_score": 3,
        "alignment_gap": 1.0,
        "mistake_pattern": "over_estimating_minor_errors",
        "timestamp": "2025-01-26T14:31:00Z"
    },
    
    "id": "eval_20250126_143000_aaa111"
}
```

### Query (Judge tarafından)

```python
def get_past_mistakes(primary_metric, category, n_results=5):
    query_text = f"User evaluating {primary_metric} in {category} category"
    
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results,
        where={
            "$and": [
                {"primary_metric": primary_metric},
                {"category": category}
            ]
        }
    )
    
    return results
```

**Example Query Result:**
```json
{
  "ids": [["eval_001", "eval_042", "eval_089"]],
  "documents": [["User Evaluation...", "...", "..."]],
  "metadatas": [[
    {
      "evaluation_id": "eval_001",
      "primary_metric": "Truthfulness",
      "alignment_gap": 1.2,
      "mistake_pattern": "over_estimating_minor_errors",
      "timestamp": "2025-01-20T10:30:00Z"
    },
    {...},
    {...}
  ]],
  "distances": [[0.12, 0.18, 0.25]]
}
```

---

## 📝 Logging Sistemi

### Log Yapısı

MentorMind kapsamlı bir logging sistemi kullanır:

```
data/
└── logs/
    ├── mentormind.log         # Tüm loglar (DEBUG+)
    ├── mentormind.log.1       # Rotated backup
    ├── mentormind.log.2
    ├── mentormind.log.3
    ├── mentormind.log.4
    ├── mentormind.log.5
    ├── errors.log             # Sadece hatalar (ERROR+)
    ├── errors.log.1
    └── llm_calls.jsonl        # LLM API çağrıları (JSON Lines)
```

### Log Seviyeleri

- **DEBUG:** Detaylı debugging bilgileri
- **INFO:** Normal operasyonlar (API requests, workflow steps)
- **WARNING:** Potansiyel sorunlar
- **ERROR:** Hatalar
- **CRITICAL:** Sistem seviyesi başarısızlıklar

### Log Formatı

**Console (stdout):**
```
2025-01-26 14:30:52 - mentormind.api - INFO - → POST /api/evaluations/start
```

**File (detailed):**
```
2025-01-26 14:30:52 - mentormind.judge_service - DEBUG - [judge_service.py:45] - Starting Stage 1 evaluation for eval_001
```

### LLM API Call Tracking

Her LLM API çağrısı `llm_calls.jsonl` dosyasına kaydedilir:

```json
{
  "timestamp": "2025-01-26T14:30:55",
  "provider": "anthropic",
  "model": "claude-haiku-4-5-20251001",
  "purpose": "question_generation",
  "prompt_tokens": 450,
  "completion_tokens": 320,
  "total_tokens": 770,
  "duration_seconds": 2.14,
  "success": true,
  "error": null
}
```

**Tracked providers:**
- `anthropic` - Claude Haiku 4.5 (soru üretimi)
- `openai` - GPT-4o (judge), GPT-3.5/4o-mini (K models), embeddings
- `google` - Gemini 2.0 Flash (K model)

### Log Rotation

- **Max file size:** 10MB
- **Backup count:** 5 files
- Eski loglar otomatik olarak `.1`, `.2`, vb. ile yedeklenir

### Logları Görüntüleme

```bash
# Tüm logları canlı takip et
docker-compose logs -f backend

# Son 100 satır
docker-compose logs --tail=100 backend

# Sadece hatalar
docker-compose exec backend tail -f /app/data/logs/errors.log

# LLM call tracking
docker-compose exec backend tail -f /app/data/logs/llm_calls.jsonl

# Belirli bir pattern ara
docker-compose exec backend grep "judge_stage1" /app/data/logs/mentormind.log

# Son 1 saatin logları
docker-compose exec backend find /app/data/logs -name "*.log" -mmin -60 -exec tail {} \;
```

### Log Analizi

```bash
# LLM maliyet analizi
docker-compose exec backend python scripts/analyze_llm_costs.py

# Output:
# LLM Usage Stats:
# anthropic/claude-haiku-4-5-20251001:
#   Calls: 42
#   Total Tokens: 32,450
#   Avg Duration: 2.14s
#   Est. Cost: $0.65
# 
# openai/gpt-4o:
#   Calls: 84 (42 stage1 + 42 stage2)
#   Total Tokens: 156,800
#   Avg Duration: 5.82s
#   Est. Cost: $3.92
```

### Log Levels Environment Variable

```bash
# .env dosyasında
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Development için
LOG_LEVEL=DEBUG

# Production için
LOG_LEVEL=INFO
```

### Debugging

**Problem:** Bir evaluation neden başarısız oldu?

```bash
# 1. Evaluation ID'yi bul
docker-compose exec backend grep "eval_20250126_143000" /app/data/logs/mentormind.log

# 2. O evaluation'a ait tüm logları göster
docker-compose exec backend grep "eval_20250126_143000" /app/data/logs/mentormind.log | less

# 3. Hata detaylarını kontrol et
docker-compose exec backend grep "eval_20250126_143000" /app/data/logs/errors.log
```

**Problem:** Claude API neden timeout veriyor?

```bash
# LLM call loglarını incele
docker-compose exec backend grep "anthropic" /app/data/logs/llm_calls.jsonl | jq '.'

# Başarısız çağrıları filtrele
docker-compose exec backend grep "anthropic" /app/data/logs/llm_calls.jsonl | jq 'select(.success == false)'
```

### Log Cleanup

```bash
# Eski logları temizle (30 günden eski)
docker-compose exec backend find /app/data/logs -name "*.log.*" -mtime +30 -delete

# LLM call logs'u arşivle
docker-compose exec backend gzip /app/data/logs/llm_calls.jsonl
docker-compose exec backend mv /app/data/logs/llm_calls.jsonl.gz /app/data/logs/archive/
```

---

## 🔌 API Endpoints

### Base URL: `http://localhost:8000/api`

#### 1. Health Check
```bash
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "chromadb": "connected"
}
```

#### 2. Start Evaluation
```bash
POST /evaluations/start
Content-Type: application/json

{
  "primary_metric": "Truthfulness",
  "use_pool": false
}
```
**Response:**
```json
{
  "question_id": "q_...",
  "response_id": "resp_...",
  "question": "...",
  "model_response": "...",
  "model_name": "gpt-3.5-turbo",
  "category": "Math"
}
```

#### 3. Submit User Evaluation
```bash
POST /evaluations/submit
Content-Type: application/json

{
  "response_id": "resp_...",
  "evaluations": {
    "Truthfulness": {"score": 4, "reasoning": "..."},
    "Helpfulness": {"score": 3, "reasoning": "..."},
    ...
  }
}
```
**Response:**
```json
{
  "evaluation_id": "eval_...",
  "status": "submitted",
  "judge_status": "processing"
}
```

#### 4. Get Judge Feedback
```bash
GET /evaluations/{evaluation_id}/feedback
```
**Response:**
```json
{
  "evaluation_id": "eval_...",
  "judge_meta_score": 4,
  "overall_feedback": "...",
  "alignment_analysis": {...},
  "improvement_areas": [...],
  "positive_feedback": [...]
}
```

#### 5. Statistics
```bash
GET /stats/overview
```
**Response:**
```json
{
  "total_evaluations": 42,
  "average_meta_score": 3.8,
  "metrics_performance": {
    "Truthfulness": {"avg_gap": 0.8, "count": 15},
    "Clarity": {"avg_gap": 0.3, "count": 12},
    ...
  },
  "improvement_trend": "+0.3 (last 10)"
}
```

#### 6. Questions Pool Stats
```bash
GET /questions/pool/stats
```
**Response:**
```json
{
  "total_questions": 127,
  "by_metric": {
    "Truthfulness": 18,
    "Safety": 15,
    ...
  },
  "by_category": {
    "Math": 32,
    "Coding": 28,
    ...
  },
  "avg_times_used": 2.4
}
```

---

## 🌱 Seed Data

### Initial question_prompts (24 satır)

**Truthfulness (3 types):**
- `hallucination_test` - Model uydurmaya meyilli
- `factual_accuracy` - Kesin doğru cevap
- `edge_case` - Tricky durumlar

**Clarity (3 types):**
- `explain_like_5` - Basit anlatım
- `technical_jargon` - Teknik terim açıklama
- `step_by_step` - Adım adım açıklama

**Safety (3 types):**
- `harmful_content` - Zararlı içerik riski
- `medical_advice` - Yanlış medikal bilgi
- `illegal_activity` - Yasadışı aktivite

**Bias (3 types):**
- `stereotype_check` - Stereotip tespiti
- `implicit_bias` - Örtük önyargı
- `fairness_test` - Adalet testi

**Helpfulness (3 types):**
- `practical_guidance` - Pratik yardım
- `example_provision` - Örnek sunma
- `actionable_advice` - Uygulanabilir öneri

**Consistency (3 types):**
- `multi_part_question` - Çok parçalı soru
- `repeated_query` - Tekrarlanan sorgu
- `contradiction_check` - Çelişki kontrolü

**Efficiency (3 types):**
- `concise_explanation` - Kısa ve öz
- `time_complexity` - Zaman karmaşıklığı
- `resource_optimization` - Kaynak optimizasyonu

**Robustness (3 types):**
- `edge_case` - Kenar durumlar
- `adversarial_input` - Karşıt girdi
- `stress_test` - Stres testi

**Seed Script:**
```bash
# Seed question_prompts (24 satır)
docker-compose exec backend python scripts/seed_data.py
```

**NOT:** Judge prompt'ları artık database'de değil, `backend/prompts/judge_prompts.py` dosyasında hardcoded olarak tutuluyor.

---

## 🖥️ CLI Testing Interface

MentorMind, manual integration testing için bir CLI aracı sağlar. Bu araç, API endpoint'lerini test etmek ve tam workflow'u manuel olarak çalıştırmak için kullanılır.

### CLI Kullanımı

```bash
# Yardım
python3 -m backend.cli --help

# Full workflow test (interactive)
python3 -m backend.cli full --metric Truthfulness

# Sadece soru üret
python3 -m backend.cli generate --metric Safety --pool

# Sadece evaluation submit (interactive)
python3 -m backend.cli evaluate --response-id resp_123

# Judge feedback polling
python3 -m backend.cli judge --evaluation-id eval_123 --timeout 120
```

### CLI Komutları

| Komut | Açıklama |
|-------|----------|
| `full` | Tam workflow: soru üret → değerlendir → judge feedback |
| `generate` | Sadece soru üret ve K model cevabı al |
| `evaluate` | Mevcut response_id için evaluation submit (interactive) |
| `judge` | Judge feedback polling (timeout belirtebilirsin) |

### Full Workflow Örneği

```bash
python3 -m backend.cli full --metric Truthfulness --pool
```

**Output:**
```
======================================================================
                    FULL WORKFLOW INTEGRATION TEST
======================================================================

ℹ Step 1: Generating question and K model response...
ℹ Generating question for metric: Truthfulness
ℹ Using pool: True
✓ Question generated successfully!

Question ID: q_20260201_120000_abc123
Response ID: resp_20260201_120000_xyz789
Category: General
Model: mistralai/mistral-nemo

Question: What is 2+2?
Response: The answer is 5.

✓ Step 2: Submitting user evaluation...
Enter scores (1-5) or null for each metric:

Truthfulness (1-5 or null): 1
  Reasoning: Wrong answer
Helpfulness (1-5 or null): 2
  Reasoning: Misleading
Safety (1-5 or null): 5
  Reasoning: No issues
Bias (1-5 or null): null
  Reasoning: N/A
Clarity (1-5 or null): 5
  Reasoning: Clear
Consistency (1-5 or null): null
  Reasoning: N/A
Efficiency (1-5 or null): 5
  Reasoning: Concise
Robustness (1-5 or null): 2
  Reasoning: Factually wrong

✓ Evaluation submitted successfully!

Evaluation ID: eval_20260201_120000_aaa111
Status: submitted
Message: Evaluation submitted successfully. Judge evaluation running in background.

✓ Step 3: Waiting for judge evaluation...
ℹ Attempt 1: Still processing... (2.3s elapsed)
ℹ Attempt 2: Still processing... (4.5s elapsed)
✓ Judge evaluation completed in 12.3s!

Result:
{
  "evaluation_id": "eval_20260201_120000_aaa111",
  "status": "completed",
  "message": "Judge evaluation completed. Full feedback will be available in Week 4."
}

======================================================================
                           TEST SUMMARY
======================================================================
✓ Response ID: resp_20260201_120000_xyz789
✓ Evaluation ID: eval_20260201_120000_aaa111
ℹ Check the database to verify:
  - user_evaluations.judged = TRUE
  - (Week 4) judge_evaluations record created
```

### Docker ile CLI Kullanımı

```bash
# Full workflow test
docker-compose exec backend python -m backend.cli full --metric Clarity

# Generate test
docker-compose exec backend python -m backend.cli generate --metric Robustness --pool
```

---

## 💡 Kullanım Örnekleri

### Senaryo 1: İlk Değerlendirme

```bash
# 1. Yeni soru üret + değerlendirme başlat
curl -X POST http://localhost:8000/api/evaluations/start \
  -H "Content-Type: application/json" \
  -d '{
    "primary_metric": "Truthfulness",
    "use_pool": false
  }'

# Response:
{
  "question_id": "q_001",
  "response_id": "resp_001",
  "question": "2024 Nobel Kimya Ödülü'nü kim kazandı?",
  "model_response": "Jennifer Doudna kazandı.",
  "model_name": "gpt-3.5-turbo"
}

# 2. Değerlendir
curl -X POST http://localhost:8000/api/evaluations/submit \
  -H "Content-Type: application/json" \
  -d '{
    "response_id": "resp_001",
    "evaluations": {
      "Truthfulness": {"score": 1, "reasoning": "Tamamen yanlış, böyle bir şey olmadı"},
      "Helpfulness": {"score": 1, "reasoning": "Yanlış bilgi zararlı"},
      "Safety": {"score": null, "reasoning": "Geçerli değil"},
      "Bias": {"score": null, "reasoning": "Geçerli değil"},
      "Clarity": {"score": 5, "reasoning": "Net ama yanlış"},
      "Consistency": {"score": null, "reasoning": "Tek cevap"},
      "Efficiency": {"score": 4, "reasoning": "Kısa"},
      "Robustness": {"score": 1, "reasoning": "Trap question başarısız"}
    }
  }'

# Response:
{
  "evaluation_id": "eval_001",
  "status": "submitted",
  "judge_status": "processing"
}

# 3. Feedback al (30 saniye sonra)
curl http://localhost:8000/api/evaluations/eval_001/feedback

# Response:
{
  "judge_meta_score": 5,
  "overall_feedback": "Mükemmel! İlk değerlendirmen çok objektif...",
  "alignment_analysis": {
    "Truthfulness": {
      "gap": 0,
      "verdict": "aligned",
      "feedback": "Doğru tespit"
    }
  },
  "improvement_areas": [],
  "positive_feedback": ["Truthfulness'ta mükemmel"]
}
```

### Senaryo 2: Tekrar Eden Hata

```bash
# 5. değerlendirme - Yine Truthfulness'ta yumuşak
{
  "judge_meta_score": 2,
  "overall_feedback": "BU 5. KEZ! Truthfulness'ta tutarlı olarak yumuşak değerlendiriyorsun...",
  "alignment_analysis": {
    "Truthfulness": {
      "gap": 2.0,
      "verdict": "significantly_over_estimated"
    }
  },
  "improvement_areas": [
    "Truthfulness - detay eksikliklerini daha sert değerlendir"
  ]
}
```

### Senaryo 3: Gelişme Trendi

```bash
# İstatistik çek
curl http://localhost:8000/api/stats/overview

# Response:
{
  "total_evaluations": 50,
  "average_meta_score": 4.1,
  "metrics_performance": {
    "Truthfulness": {
      "avg_gap": 0.4,  # Başta 1.5'ti, gelişiyor! ✅
      "count": 18,
      "trend": "improving"
    }
  },
  "improvement_trend": "+1.2 (last 10)"
}
```

---

## 👨‍💻 Development Guide

### Project Structure

```
mentormind/
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── routers/
│   │   ├── evaluations.py      # /api/evaluations/*
│   │   ├── questions.py        # /api/questions/*
│   │   └── stats.py            # /api/stats/*
│   ├── services/
│   │   ├── claude_service.py   # Soru üretimi
│   │   ├── model_service.py    # K model manager
│   │   ├── judge_service.py    # GPT-4o judge (2-stage)
│   │   └── chromadb_service.py # Vector DB
│   ├── prompts/                # ← Judge prompts (hardcoded)
│   │   └── judge_prompts.py
│   ├── models/
│   │   ├── database.py         # SQLAlchemy models
│   │   └── schemas.py          # Pydantic schemas
│   ├── config/
│   │   ├── settings.py         # Environment config
│   │   └── logging_config.py   # Logging setup
│   ├── middleware/
│   │   └── logging_middleware.py  # Request/Response logging
│   ├── schemas/                # SQL table schemas
│   │   ├── 01_question_prompts.sql
│   │   ├── 02_questions.sql
│   │   ├── 03_model_responses.sql
│   │   ├── 04_user_evaluations.sql
│   │   └── 05_judge_evaluations.sql
│   ├── scripts/
│   │   ├── init_db.py          # Database initialization
│   │   ├── seed_data.py        # Seed question_prompts
│   │   └── analyze_llm_costs.py # LLM cost analysis
│   └── requirements.txt
│
├── data/                       # Volume mount
│   └── logs/
│       ├── mentormind.log
│       ├── errors.log
│       └── llm_calls.jsonl
│
├── docker-compose.yml
├── Dockerfile
├── .env.example
└── README.md
```

### Docker Development

```bash
# Build ve run
docker-compose up --build

# Sadece rebuild (cache kullan)
docker-compose build

# Logs
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f chromadb

# Shell'e gir
docker-compose exec backend bash
docker-compose exec postgres psql -U mentormind -d mentormind

# Database reset
docker-compose down -v
docker-compose up -d
docker-compose exec backend python scripts/init_db.py
docker-compose exec backend python scripts/seed_data.py
```

### Testing

```bash
# Unit tests
docker-compose exec backend pytest tests/unit/

# Integration tests
docker-compose exec backend pytest tests/integration/

# Specific test
docker-compose exec backend pytest tests/test_judge_service.py -v

# Coverage
docker-compose exec backend pytest --cov=backend --cov-report=html
```

---

## 🔧 Troubleshooting

### Database Issues

**Problem: PostgreSQL connection refused**

```bash
# Check PostgreSQL
docker-compose exec postgres pg_isready -U mentormind

# Check credentials
docker-compose exec postgres psql -U mentormind -d mentormind -c "SELECT 1;"

# Reset database
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend python scripts/init_db.py
```

**Problem: Database tables missing**

```bash
# Check if tables exist
docker-compose exec postgres psql -U mentormind -d mentormind -c "\dt"

# Re-initialize
docker-compose exec backend python scripts/init_db.py
```

### ChromaDB Issues

**Problem: ChromaDB connection failed**

```bash
# Check ChromaDB container
docker-compose ps

# Restart ChromaDB
docker-compose restart chromadb

# Check logs
docker-compose logs chromadb

# Health check
curl http://localhost:8001/api/v1/heartbeat
```

### API Key Errors

```bash
# Verify .env file
cat .env | grep API_KEY

# Check environment in container
docker-compose exec backend env | grep API_KEY

# Restart after .env change
docker-compose down
docker-compose up -d
```

### Logging Issues

**Problem: Loglar görünmüyor**

```bash
# Log directory var mı?
docker-compose exec backend ls -la /app/data/logs

# Permissions kontrol et
docker-compose exec backend ls -la /app/data

# Manuel log dizini oluştur
docker-compose exec backend mkdir -p /app/data/logs
```

**Problem: Disk doldu**

```bash
# Log dosyalarının boyutunu kontrol et
docker-compose exec backend du -sh /app/data/logs/*

# Eski logları temizle
docker-compose exec backend rm -f /app/data/logs/*.log.*
docker-compose exec backend rm -f /app/data/logs/errors.log.*
```

**Problem: LLM calls JSONL bozuk**

```bash
# Geçerli JSON satırlarını kontrol et
docker-compose exec backend cat /app/data/logs/llm_calls.jsonl | jq empty

# Hatalı satırları bul
docker-compose exec backend cat /app/data/logs/llm_calls.jsonl | while read line; do echo "$line" | jq empty || echo "Invalid: $line"; done
```

### Judge Issues

**Problem: Judge evaluation çok yavaş**

```bash
# Check if async task is running
docker-compose logs backend | grep "judge_task"

# Monitor GPT-4o API latency
docker-compose exec backend tail -f /app/data/logs/llm_calls.jsonl | grep gpt-4o

# (Judge 2-stage usually takes 10-30 seconds)
```

**Problem: Judge timeout**

```bash
# Increase timeout in settings
# backend/config/settings.py
JUDGE_TIMEOUT_SECONDS = 60  # Default: 30

# Check error logs
docker-compose exec backend tail -f /app/data/logs/errors.log
```

---

## 📊 Roadmap

### ✅ MVP 
- [] Database schema (PostgreSQL)
- [] Question generation (Claude)
- [] K Model integration (4 models)
- [] User evaluation API
- [] Judge evaluation (2-stage)
- [] ChromaDB integration
- [] Logging system
- [] Docker setup

### 🚧 Phase 2 (Next 2 Weeks)
- [ ] Frontend UI (React/Vue/Svelte)
- [ ] Real-time judge progress updates
- [ ] Advanced statistics dashboard
- [ ] Export evaluations (CSV, JSON)

### 📅 Phase 3 (Future)
- [ ] Multi-user support
- [ ] Leaderboard (kendinle yarış)
- [ ] Custom prompt creation UI
- [ ] A/B testing different judge prompts
- [ ] ML-based mistake pattern detection
- [ ] Discord/Slack bot integration

---

## 📄 Lisans

MIT License - Bu projeyi istediğin gibi kullanabilirsin!

---

## 📞 İletişim

Sorular için: [GitHub Issues](https://github.com/yourusername/mentormind/issues)

---

**Son güncelleme:** 26 Ocak 2025  
**Versiyon:** 1.0.0-MVP  
**Durum:** 🚧 Aktif Geliştirme

---

**MentorMind** ile EvalOps yolculuğunda başarılar! 🚀