# MentorMind - Phase 1 MVP Roadmap

**Proje:** MentorMind - AI Evaluator Training System  
**Phase:** 1 - MVP (Minimum Viable Product)  
**Hedef:** Temel sistemin çalışır hale getirilmesi  
**Tahmini Süre:** 4 hafta  
**Başlangıç:** 27 Ocak 2025  

---

## 📋 İçindekiler

- [Phase 1 Overview](#-phase-1-overview)
- [Week 1: Database & Infrastructure](#-week-1-database--infrastructure)
- [Week 2: Question Generation & K Models](#-week-2-question-generation--k-models)
- [Week 3: User Evaluation & Judge Stage 1](#-week-3-user-evaluation--judge-stage-1)
- [Week 4: Judge Stage 2 & End-to-End Testing](#-week-4-judge-stage-2--end-to-end-testing)
- [Success Metrics](#-success-metrics)

---

## 🎯 Phase 1 Overview

### Scope

**Dahil:**
- PostgreSQL database (5 tablo)
- Docker infrastructure
- Claude API soru üretimi
- 4 K model entegrasyonu (GPT-3.5, GPT-4o-mini, Claude Haiku, Gemini Flash)
- User evaluation API
- GPT-4o judge (2-stage)
- ChromaDB hafıza sistemi
- Comprehensive logging
- CLI testing interface

**Hariç:**
- Frontend UI
- Multi-user support
- Advanced analytics
- Production deployment

### Definition of Done

Phase 1 tamamlanmış sayılır eğer:
- [ ] Tüm database tabloları oluşturuldu
- [ ] Docker container'lar çalışıyor
- [ ] Claude ile soru üretilebiliyor
- [ ] 4 K model soru cevaplayabiliyor
- [ ] Kullanıcı değerlendirmesi kaydedilebiliyor
- [ ] Judge 2-stage workflow çalışıyor
- [ ] ChromaDB hafıza aktif
- [ ] CLI üzerinden end-to-end test başarılı
- [ ] Documentation güncel

---

## 📅 Week 1: Database & Infrastructure

**Tarih:** 27 Ocak - 2 Şubat 2025  
**Hedef:** Database, Docker, logging altyapısı

---

### Task 1.1: Project Setup

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (26 Ocak 2025)

**Yapılacaklar:**
- [x] GitHub repository oluştur
- [x] Ana klasör yapısını oluştur:
  ```
  mentormind/
  ├── backend/
  ├── data/
  ├── chroma_data/
  ├── .gitignore
  ├── .env.example
  ├── README.md
  └── ROADMAP.md
  ```
- [x] `.gitignore` dosyası ekle
- [x] Initial commit yap (commit: 3bf9c3b)

---

### Task 1.2: Environment Configuration

**Tahmini Süre:** 1 saat

**Durum:** ✅ **TAMAMLANDI** (26 Ocak 2025)

**Yapılacaklar:**
- [x] `.env.example` oluştur (tüm environment variables ile)
- [x] `.env` dosyası oluştur
- [x] API key'leri ekle:
  - [x] ANTHROPIC_API_KEY
  - [x] OPENAI_API_KEY
  - [x] GOOGLE_API_KEY
- [x] Database credentials ayarla
- [x] `.env` dosyasının `.gitignore`'da olduğunu doğrula

---

### Task 1.3: Docker Setup

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (26 Ocak 2025)

**Yapılacaklar:**
- [x] `Dockerfile` oluştur (Python 3.11-slim base image)
- [x] `docker-compose.yml` oluştur (3 service: backend, postgres, chromadb)
- [x] `.dockerignore` oluştur
- [x] `requirements.txt` oluştur (dependency conflict fixed: pytest==7.4.4)
- [x] `docker-compose build` ile build al
- [x] `docker-compose up -d` ile container'ları başlat
- [x] `docker-compose ps` ile durumları kontrol et
- [x] `curl http://localhost:8000` ile backend'e erişimi test et

**Notlar:**
- pytest 8.0.0 ve pytest-asyncio 0.23.4 arası conflict çözüldü (pytest downgrade edildi)
- env_file directive eklendi (.env dosyasından otomatik okuma)
- Environment variables docker-compose'a taşındı

---

### Task 1.4: Python Backend Foundation

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (26 Ocak 2025)

**Yapılacaklar:**
- [x] `backend/requirements.txt` oluştur (Task 1.3'te yapıldı)
- [x] Backend klasör yapısını oluştur:
  ```
  backend/
  ├── config/
  ├── middleware/
  ├── models/
  ├── routers/
  ├── schemas/
  ├── scripts/
  ├── services/
  ├── prompts/
  ├── tests/
  └── main.py
  ```
- [x] `backend/config/settings.py` oluştur (environment loader with Pydantic Settings)
- [x] `backend/config/__init__.py` oluştur
- [x] `backend/main.py` oluştur (minimal FastAPI app with 4 endpoints)
- [x] `backend/__init__.py` oluştur
- [x] FastAPI app'in çalıştığını test et
- [x] Hot-reload aktif (--reload flag)

**Endpoints:**
- `GET /` - Root endpoint (API info)
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed system status
- `GET /info` - Development-only config info

**Swagger UI:** http://localhost:8000/docs
**ReDoc:** http://localhost:8000/redoc

---

### Task 1.5: Database Models - SQLAlchemy Setup

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (26 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/models/database.py` oluştur:
  - [x] SQLAlchemy Base
  - [x] Database engine
  - [x] SessionLocal
  - [x] get_db() dependency
- [x] `backend/config/database.py` oluştur (DB connection config)
- [x] Database connection'ı test et

**Notlar:**
- SQLAlchemy 2.0 text() fonksiyonu kullanıldı (raw SQL için)
- Connection pool: pool_size=3, max_overflow=5
- Health endpoint'leri database status ile güncellendi
- Test script: `backend/scripts/test_db_connection.py`

---

### Task 1.6: SQL Schema - question_prompts

**Tahmini Süre:** 1 saat

**Durum:** ✅ **TAMAMLANDI** (26 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/schemas/01_question_prompts.sql` oluştur
- [x] Tablo tanımını yaz (id, primary_metric, bonus_metrics, question_type, user_prompt, golden_examples, difficulty, category_hints JSONB, timestamps)
- [x] UNIQUE constraint ekle (primary_metric, question_type)
- [x] Indexes ekle (primary_metric, difficulty)

---

### Task 1.7: SQL Schema - questions

**Tahmini Süre:** 1 saat

**Durum:** ✅ **TAMAMLANDI** (26 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/schemas/02_questions.sql` oluştur
- [x] Tablo tanımını yaz (id, question, category, reference_answer (nullable), expected_behavior (nullable), rubric_breakdown, denormalized fields, usage tracking)
- [x] Foreign key ekle (question_prompt_id nullable)
- [x] Indexes ekle (primary_metric, category, times_used, pool_selection composite)

---

### Task 1.8: SQL Schema - model_responses

**Tahmini Süre:** 1 saat

**Durum:** ✅ **TAMAMLANDI** (26 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/schemas/03_model_responses.sql` oluştur
- [x] Tablo tanımını yaz (id, question_id, model_name, response_text, evaluated, evaluation_id)
- [x] Foreign key ekle (question_id)
- [x] UNIQUE constraint ekle (question_id, model_name)
- [x] Indexes ekle (question_id, model_name, evaluated, pending_evaluations partial)

---

### Task 1.9: SQL Schema - user_evaluations

**Tahmini Süre:** 1 saat

**Durum:** ✅ **TAMAMLANDI** (26 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/schemas/04_user_evaluations.sql` oluştur
- [x] Tablo tanımını yaz (id, response_id, evaluations JSONB, judged)
- [x] Foreign key ekle (response_id)
- [x] Indexes ekle (response_id, judged, created_at_desc)

---

### Task 1.10: SQL Schema - judge_evaluations

**Tahmini Süre:** 1 saat

**Durum:** ✅ **TAMAMLANDI** (26 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/schemas/05_judge_evaluations.sql` oluştur
- [x] Tablo tanımını yaz (id, user_evaluation_id, independent_scores, alignment_analysis, judge_meta_score, overall_feedback, improvement_areas, positive_feedback, vector_context, primary_metric, gaps)
- [x] Foreign key ekle (user_evaluation_id)
- [x] CHECK constraint ekle (judge_meta_score BETWEEN 1 AND 5)
- [x] Indexes ekle (user_evaluation_id, meta_score, primary_metric, created_at_desc, metric_score composite)

---

### Task 1.11: SQLAlchemy Models

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (26 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/models/question_prompt.py` oluştur (QuestionPrompt model)
- [x] `backend/models/question.py` oluştur (Question model)
- [x] `backend/models/model_response.py` oluştur (ModelResponse model)
- [x] `backend/models/user_evaluation.py` oluştur (UserEvaluation model)
- [x] `backend/models/judge_evaluation.py` oluştur (JudgeEvaluation model)
- [x] `backend/models/__init__.py` oluştur (tüm modelleri export et)

---

### Task 1.12: Pydantic Schemas

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (26 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/models/schemas.py` oluştur
- [x] QuestionPrompt schemas (Base, Create, Response)
- [x] Question schemas (Base, Create, Response)
- [x] ModelResponse schemas (Base, Create, Response)
- [x] UserEvaluation schemas (Base, Create, Response)
- [x] JudgeEvaluation schemas (Base, Create, Response)
- [x] Validation logic ekle

---

### Task 1.13: Database Initialization Script

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (26 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/scripts/init_db.py` oluştur
- [x] Tüm SQL schema dosyalarını okuma logic'i ekle
- [x] Sırayla execute et (01 → 05)
- [x] Error handling ekle
- [x] Script'i test et: `docker-compose exec backend python scripts/init_db.py`
- [x] Tabloları kontrol et: `docker-compose exec postgres psql -U mentormind -d mentormind -c "\dt"`

---

### Task 1.14: Logging Infrastructure

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (29 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/config/logging_config.py` oluştur:
  - [x] Log formatters (default, detailed)
  - [x] Handlers (console, file, error_file)
  - [x] Loggers (mentormind, root)
  - [x] RotatingFileHandler (10MB, 5 backups)
- [x] `backend/services/llm_logger.py` oluştur:
  - [x] LLMCallLogger class
  - [x] log_call() method (provider, model, purpose, tokens, duration, success)
  - [x] JSONL format
- [x] `backend/middleware/logging_middleware.py` oluştur:
  - [x] RequestLoggingMiddleware class
  - [x] Request/Response logging
  - [x] Duration tracking
- [x] `backend/main.py`'a logging ekle
- [x] Test: `curl http://localhost:8000` ve logları kontrol et

**Notlar:**
- 3 log dosyası oluşturuluyor: mentormind.log, errors.log, llm_calls.jsonl
- Log dosyaları 10MB'da rotate olur, 5 backup tutar
- Request logging middleware tüm HTTP request'leri loglar

---

### Task 1.15: Health Check Endpoints

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (29 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/routers/health.py` oluştur
- [x] `GET /api/health` endpoint (basic health)
- [x] `GET /api/health/detailed` endpoint:
  - [x] Database connection check
  - [x] ChromaDB connection check
  - [x] Status response (healthy/degraded)
- [x] `backend/main.py`'a router'ı ekle
- [x] Test: `curl http://localhost:8000/api/health`
- [x] Test: `curl http://localhost:8000/api/health/detailed`

**Notlar:**
- Implementation done directly in main.py (no separate router needed)
- Database connection testing working
- Latency measurement working
- Pool status reporting working

---

### Task 1.16: Testing Infrastructure

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (29 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/tests/conftest.py` oluştur:
  - [x] Test database setup (PostgreSQL: mentormind_test)
  - [x] db fixture
  - [x] client fixture (TestClient)
- [x] `backend/pytest.ini` oluştur
- [x] `backend/tests/test_health.py` oluştur (örnek test)
- [x] Tests çalıştır: `docker-compose exec backend pytest`
- [x] Coverage report kontrol et

**Notlar:**
- PostgreSQL test database kullanılıyor (SQLite değil)
- SQLAlchemy create_all() ENUM ve Trigger'ları oluşturamaz, bu yüzden ham SQL dosyaları sırayla çalıştırılıyor
- 5 test geçiyor (test_health.py)
- Test coverage: 46% (backend genel)

---

### Task 1.17: Seed Data Script (Skeleton)

**Tahmini Süre:** 1 saat

**Durum:** ✅ **TAMAMLANDI** (29 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/scripts/seed_data.py` oluştur
- [x] seed_question_prompts() fonksiyonu (skeleton, Week 2'de doldurulacak)
- [x] verify_prompts() fonksiyonu
- [x] reset_prompts() fonksiyonu
- [x] main() fonksiyonu (CLI with --verify, --reset, --dry-run flags)
- [x] Error handling
- [x] Script çalıştırılabilir durumda (skeleton mode)

**Notlar:**
- CLI flags: `--verify` (mevcut promptları kontrol et), `--reset` (tüm promptları sil), `--dry-run` (ne yapılacağını göster)
- Normal mode: Week 2'de 24 şablon eklenecek (8 metrik × 3 zorluk)
- Exit code 1 when incomplete (expected behavior)

---

### Task 1.18: LLM Cost Analysis Script

**Tahmini Süre:** 1 saat

**Yapılacaklar:**
- [ ] `backend/scripts/analyze_llm_costs.py` oluştur
- [ ] JSONL log okuma logic'i
- [ ] Provider/model bazında grouping
- [ ] İstatistik hesaplama (calls, tokens, duration, est. cost)
- [ ] Pretty print output
- [ ] Script'i test et (boş log ile)

---

### ✅ Week 1 Checklist

- [x] Docker container'lar çalışıyor (backend, postgres, chromadb)
- [x] Database tabloları oluşturuldu (5 tablo) (Completed: 26 Ocak 2026)
- [x] SQLAlchemy models hazır (Completed: 26 Ocak 2026)
- [x] Pydantic schemas hazır (Completed: 26 Ocak 2026)
- [x] Logging sistemi çalışıyor (3 log dosyası: mentormind.log, errors.log, llm_calls.jsonl) (Completed: 29 Ocak 2026)
- [x] Health check endpoints çalışıyor (Completed: 29 Ocak 2026)
- [x] Test infrastructure kurulu (Completed: 29 Ocak 2026)
- [ ] Scripts hazır (init_db.py, seed_data.py, analyze_llm_costs.py)

---

## 📅 Week 2: Question Generation & K Models

**Tarih:** 3 - 9 Şubat 2025  
**Hedef:** Soru üretimi ve K model entegrasyonu

---

 ### Task 2.1: Master Question Prompts & Golden Examples Preparation

**Tahmini Süre:** 4 saat

**Durum:** ✅ **TAMAMLANDI** (30 Ocak 2026)

**Açıklama:** 24 ayrı prompt yazmak yerine, her metrik için 1 adet "Master Prompt" hazırlanacak. Çeşitlilik
      veritabanındaki `question_type` değişkeni ve o tipe özel `golden_examples` (few-shot) ile sağlanacak.

**Yapılacaklar:**
- [x] 8 metrik için dinamik "Master Prompt" şablonlarını oluştur.
- [x] 24 farklı `question_type` senaryosu için kaliteli "Golden Examples" verilerini hazırla.

**Metrik Grupları (Her biri 1 Master Prompt + 3 Tip Örnek):**
- [x] **Truthfulness:** (hallucination_test, factual_accuracy, edge_case)
- [x] **Clarity:** (explain_like_5, technical_jargon, step_by_step)
- [x] **Safety:** (harmful_content, medical_advice, illegal_activity)
- [x] **Bias:** (stereotype_check, implicit_bias, fairness_test)
- [x] **Helpfulness:** (practical_guidance, example_provision, actionable_advice)
- [x] **Consistency:** (multi_part_question, repeated_query, contradiction_check)
- [x] **Efficiency:** (concise_explanation, time_complexity, resource_optimization)
- [x] **Robustness:** (edge_case, adversarial_input, stress_test)

---

### Task 2.2: Seed Data Implementation

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (30 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/scripts/seed_data.py`'daki seed_question_prompts() fonksiyonunu tamamla
- [x] promptlar'u dictionary formatında ekle
- [x] bonus_metrics'i belirle (her primary metric için 2 bonus)
- [x] difficulty ve category_hint ekle
- [x] Script'i çalıştır: `docker-compose exec backend python scripts/seed_data.py`
- [x] Database'i kontrol et: `SELECT COUNT(*) FROM question_prompts;` (24 kayıt doğrulandı) 

---

### Task 2.3: Claude Service - Setup

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (30 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/services/claude_service.py` oluştur
- [x] Anthropic client initialize et
- [x] API key'i environment'tan al
- [x] Basic error handling ekle
- [x] Logger setup
- [x] `claude_api_timeout` configuration (settings.py)

---

### Task 2.4: Claude Service - Dynamic Category Selection

**Tahmini Sure:** 2 saat (Mantik genisletildi)

**Durum:** TAMAMLANDI (30 Ocak 2026)

**Aciklama:** Soru kategorilerini 4 ana baslikla sinirlamak yerine, veritabanindaki `category_hints`
  alanina tam uyum saglayan ve "any" durumunda genis bir yelpazeden secim yapan dinamik bir yapilandi.

**Yapilacaklar:**
- [x] `backend/services/claude_service.py` icinde genis kapsamli bir `DEFAULT_CATEGORY_POOL` (21 kategori) tanimlandi.
- [x] `select_category(category_hints: list[str]) -> str` fonksiyonu yazildi:
  - [x] Eger `category_hints` ozel konular iceriyorsa (orn: `["React", "SQL"]`), bunlardan birini sec.
  - [x] Eger `category_hints` `["any"]` iceriyorsa veya bossa, `DEFAULT_CATEGORY_POOL`'dan rastgele sec.
  - [x] Legacy category mapping (Math->Mathematics, Coding->Programming, vb.) eklendi.
- [x] `backend/services/__init__.py` export'lari guncellendi.

**Notlar:**
- 21 kategorilik DEFAULT_CATEGORY_POOL olusturuldu (Akademik, Teknoloji, Profesyonel, Sanat)
- Legacy kategoriler (Math, Coding, Medical, General) yeni kategorilere map edildi


### Task 2.5: Claude Service - Prompt Template

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (30 Ocak 2026 - Kod analizi ile tespit edildi)

**Açıklama:** `render_user_prompt()` fonksiyonu `backend/prompts/master_prompts.py` dosyasında uygulanmış durumda. Fonksiyon template'taki placeholder'ları doldurur ve tam prompt döndürür.

**Yapılacaklar:**
- [x] `render_user_prompt(primary_metric, question_type, category, difficulty) -> str` fonksiyonu mevcut (master_prompts.py:947)
- [x] Template render et (user_prompt'ta placeholder'ları replace)
- [x] Golden examples formatla (format_golden_example fonksiyonu mevcut)
- [x] Return full prompt

---

### Task 2.6: Claude Service - Question Generation

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (30 Ocak 2026 - Kod analizi ile tespit edildi + Model güncellendi)

**Açıklama:** `_generate_new_question()` ve `generate_question()` fonksiyonları `backend/services/claude_service.py` dosyasında uygulanmış durumda. Model güncellemesi yapıldı.

**Yapılacaklar:**
- [x] `generate_question(primary_metric: str, use_pool: bool) -> Question` fonksiyonu mevcut (claude_service.py:407)
  - [x] use_pool=True ise havuzdan seç (_select_from_pool fonksiyonu mevcut)
  - [x] use_pool=False ise yeni üret (_generate_new_question fonksiyonu mevcut)
- [x] Yeni üretim logic'i:
  - [x] question_prompts'tan random seç (WHERE primary_metric=?)
  - [x] Category belirle (select_category fonksiyonu mevcut)
  - [x] Prompt render et (render_user_prompt ile master_prompts'dan alıyor)
  - [x] Claude API'ya gönder (claude-haiku-4-5-20251001 - YENİ MODEL!)
  - [x] Response parse et (JSON)
  - [x] Question object oluştur (ID: q_YYYYMMDD_HHMMSS_randomhex)
  - [x] Database'e kaydet
- [x] LLM call logging ekle (log_llm_call ile loglanıyor)
- [x] Error handling (timeout, invalid JSON, API error)

---

### Task 2.7: Claude Service - Response Parsing

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (30 Ocak 2026 - Kod analizi ile tespit edildi)

**Açıklama:** `_parse_claude_response()` ve `_parse_json()` fonksiyonları `backend/services/claude_service.py` dosyasında uygulanmış durumuda. Markdown code block içindeki JSON'ı çıkarabilir.

**Yapılacaklar:**
- [x] `_parse_claude_response(content: str) -> dict` fonksiyonu mevcut (claude_service.py:343)
- [x] Expected fields validate et:
  - [x] question (str)
  - [x] reference_answer (str)
  - [x] expected_behavior (str)
  - [x] rubric_breakdown (dict: 1-5 → descriptions)
- [x] Validation errors handle et (ValueError fırlatıyor)
- [x] Return parsed data

---

### Task 2.8: Claude Service - Tests

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (30 Ocak 2026 - Canlı API testleri yazıldı)

**Açıklama:** `backend/tests/test_claude_service.py` oluşturuldu. Unit testler ve canlı API testleri (mock yok) içeriyor.

**Yapılacaklar:**
- [x] `backend/tests/test_claude_service.py` oluştur
- [x] test_select_category() (all category_hint variations)
- [x] test_parse_claude_response() (valid JSON, markdown, invalid)
- [x] test_claude_service_initialization() (model check)
- [x] test_generate_question_live_api() (CANLI API - gerçek Claude çağrısı)
- [x] Tests çalıştır

---

### Task 2.9: K Model Service - Setup (OpenRouter Implementation)

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (30 Ocak 2026)

**Not:** OpenRouter kullanılarak 6 model entegrasyonu yapıldı.

**Yapılacaklar:**
- [x] `backend/services/model_service.py` oluştur
- [x] K_MODELS constant tanımla (6 model via OpenRouter):
  ```python
  K_MODELS = [
      "mistralai/mistral-nemo",
      "qwen/qwen-2.5-7b-instruct",
      "deepseek/deepseek-chat",
      "google/gemini-flash-1.5",
      "openai/gpt-4o-mini",
      "openai/gpt-3.5-turbo",
  ]
  ```
- [x] OpenAI client initialize et (base_url=https://openrouter.ai/api/v1)
- [x] Logger setup

---

### Task 2.10: K Model Service - Model Selection

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (30 Ocak 2026)

**Yapılacaklar:**
- [x] `select_model(question_id: str, db: Session) -> str` fonksiyonu yaz:
  - [x] Bu soruyu hangi modeller cevapladı? (query model_responses)
  - [x] Cevaplamamış modeller listele
  - [x] Eğer tümü cevaplamış → random seç
  - [x] Eğer bazıları cevaplamamış → onlardan random seç
- [x] Test fonksiyonu

---

### Task 2.11: K Model Service - OpenRouter Integration

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (30 Ocak 2026)

**Not:** OpenRouter unified API gateway kullanıldı.

**Yapılacaklar:**
- [x] `_call_openrouter(model_name: str, question: str) -> str` fonksiyonu yaz
- [x] OpenAI client ile OpenRouter API call (base_url=https://openrouter.ai/api/v1)
- [x] Messages format: `[{"role": "user", "content": question}]`
- [x] Response parse et (choices[0].message.content)
- [x] LLM call logging ekle
- [x] Error handling
- [x] Test (mock API)

---

### Task 2.12: K Model Service - (Skipped - Merged into 2.11)

**Tahmini Süre:** 2 saat

**Durum:** ⏭️ **ATLANDI** (OpenRouter ile birleştirildi)

**Not:** OpenRouter sayesinde ayrı Anthropic entegrasyonuna gerek kalmadı.

---

### Task 2.13: K Model Service - (Skipped - Merged into 2.11)

**Tahmini Süre:** 2 saat

**Durum:** ⏭️ **ATLANDI** (OpenRouter ile birleştirildi)

**Not:** OpenRouter sayesinde ayrı Google entegrasyonuna gerek kalmadı.

---

### Task 2.14: K Model Service - Unified Interface

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (30 Ocak 2026)

**Yapılacaklar:**
- [x] `answer_question(question_id: str, model_name: str, db: Session) -> ModelResponse` fonksiyonu yaz:
  - [x] Question'ı database'den getir
  - [x] OpenRouter API call yap (_call_openrouter)
  - [x] ModelResponse object oluştur (ID: resp_YYYYMMDD_HHMMSS_randomhex)
  - [x] Database'e kaydet
  - [x] Return response
- [x] Error handling

---

### Task 2.15: K Model Service - Tests

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (30 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/tests/test_model_service.py` oluştur
- [x] test_select_model()
- [x] test_call_openrouter() (mock)
- [x] test_answer_question() (mock)
- [x] Tests çalıştır (11 passed)

---

### Task 2.16: Questions Router - Setup

**Tahmini Süre:** 1 saat

**Durum:** ✅ **TAMAMLANDI** (30 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/routers/questions.py` oluştur
- [x] APIRouter oluştur
- [x] Logger setup

---

### Task 2.17: Questions Router - Generate Endpoint

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (30 Ocak 2026)

**Yapılacaklar:**
- [x] `POST /api/questions/generate` endpoint yaz:
  - [x] Request schema: `{primary_metric: str, use_pool: bool}`
  - [x] Claude service'i çağır (generate_question)
  - [x] Model seç (select_model)
  - [x] Model service'i çağır (answer_question)
  - [x] Response format: `{question_id, response_id, question, model_response, model_name, category}`
  - [x] Error handling
- [x] Pydantic request/response schemas
- [x] Test endpoint (integration test - manual curl successful)

---

### Task 2.18: Questions Router - Pool Stats Endpoint

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (30 Ocak 2026)

**Yapılacaklar:**
- [x] `GET /api/questions/pool/stats` endpoint yaz:
  - [x] Total questions count
  - [x] By metric breakdown
  - [x] By category breakdown
  - [x] By difficulty breakdown
  - [x] Average times_used
- [x] Response schema
- [x] Test endpoint (curl successful)

---

### Task 2.19: Router Integration

**Tahmini Süre:** 1 saat

**Durum:** ✅ **TAMAMLANDI** (30 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/main.py`'a questions router'ı ekle
- [x] Prefix: `/api/questions`
- [x] Tags: `["questions"]`
- [x] Test: `curl -X POST http://localhost:8000/api/questions/generate -d '{"primary_metric": "Truthfulness", "use_pool": false}'`

---

### Task 2.20: End-to-End Test (Week 2)

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (30 Ocak 2026)

**Yapılacaklar:**
- [x] Manuel test senaryosu çalıştır:
  1. [x] Seed data yükle (24 prompts)
  2. [x] Yeni soru üret (Truthfulness) - Başarılı
  3. [x] K model cevapladı (mistralai/mistral-nemo)
  4. [x] Pool stats kontrol et - Başarılı
  5. [x] Database'de question ve model_response kayıtlarını kontrol et
- [x] Logları incele (mentormind.log, llm_calls.jsonl) - Her şey loglanıyor
- [x] Bug'ları tespit et ve fix'le

---

### ✅ Week 2 Checklist

- [x] 24 question_prompt seeded (30 Ocak 2026)
- [x] Claude service soru üretebiliyor (Önceki tasks'te yapıldı)
- [x] 6 K model soru cevaplayabiliyor (30 Ocak 2026)
- [x] Question pool sistemi çalışıyor
- [x] API endpoints çalışıyor (generate, pool stats)
- [x] LLM call logging aktif
- [ ] Integration tests geçiyor

---

## 📅 Week 3: User Evaluation & Judge Stage 1

**Tarih:** 10 - 16 Şubat 2025  
**Hedef:** User evaluation API ve judge'ın independent evaluation'ı

---

### Task 3.1: Evaluation Router - Setup

**Tahmini Süre:** 1 saat

**Durum:** ✅ **TAMAMLANDI** (30 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/routers/evaluations.py` oluştur
- [x] APIRouter oluştur
- [x] Logger setup

---

### Task 3.2: Evaluation Schemas

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (30 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/models/schemas.py`'ye ekle:
  - [x] MetricEvaluation schema (score: 1-5 or null, reasoning: str)
  - [x] EvaluationSubmitRequest schema (response_id, evaluations: Dict[str, MetricEvaluation])
  - [x] EvaluationSubmitResponse schema (evaluation_id, status, message)
- [x] Validation logic:
  - [x] 8 metrik olmalı
  - [x] Score 1-5 veya null
  - [x] Reasoning required if score given

---

### Task 3.3: Evaluation Submit Endpoint

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (30 Ocak 2026)

**Yapılacaklar:**
- [x] `POST /api/evaluations/submit` endpoint yaz:
  - [x] Request validate et
  - [x] UserEvaluation object oluştur (ID: eval_YYYYMMDD_HHMMSS_randomhex)
  - [x] evaluations JSON'u serialize et
  - [x] Database'e kaydet
  - [x] Async judge task başlat (arka planda) → ✅ **TAMAMLANDI** (1 Şubat 2026)
  - [x] Immediate response dön: `{evaluation_id, status: "submitted", message}`
- [x] Error handling
- [x] Router integration (main.py)
- [x] Unit tests (test_evaluations.py)

---

### Task 3.4: Evaluation Update Endpoint

**Tahmini Süre:** 1 saat

**Durum:** ✅ **TAMAMLANDI** (30 Ocak 2026)

**Not:** Dairesel ilişki (circular dependency) nedeniyle `evaluation_id` maddesi iptal edildi, diğer işlemler Task 3.3 ile birleştirildi.

**Yapılacaklar:**
- [x] model_responses tablosunda evaluated flag'i update et
- [x] evaluation_id'yi set et (iptal - circular dependency)
- [x] Endpoint çağrısında bu update'i yap (Task 3.3'te yapıldı)

---

### Task 3.5: Judge Prompts - Hardcoded

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (30 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/prompts/judge_prompts.py` oluştur
- [x] JUDGE_PROMPTS dictionary:
  - [x] "stage1" key:
    - [x] system_prompt (5048 chars - 6+ paragraphs)
    - [x] user_prompt_template (7 placeholders)
  - [x] "stage2" key:
    - [x] system_prompt (5363 chars - 6+ paragraphs)
    - [x] user_prompt_template (6 placeholders)
- [x] Prompt'ları yaz (detaylı, net instruction'lar)
- [x] Helper functions: render_stage1_prompt(), render_stage2_prompt()
- [x] Tests: 29 passed (test_judge_prompts.py)

**Notlar:**
- System prompts: İngilizce, 5000+ karakter (çok detaylı)
- Output language: Türkçe (promptlarda belirtilmiş)
- Few-shot examples: Her iki stage'de de mevcut
- Export constants: JUDGE_STAGE1_VERDICTS, META_SCORE_THRESHOLDS, WEIGHTED_GAP_WEIGHTS

---

### Task 3.6: Judge Service - Setup

**Tahmini Süre:** 1 saat

**Durum:** ✅ **TAMAMLANDI** (31 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/services/judge_service.py` oluştur
- [x] OpenAI client initialize et (GPT-4o için)
- [x] Logger setup
- [x] Import judge_prompts
- [x] THE_EIGHT_METRICS constant ekle
- [x] Global judge_service instance
- [x] Export to services/__init__.py

---

### Task 3.7: Judge Service - Data Fetching

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (31 Ocak 2026)

**Yapılacaklar:**
- [x] `fetch_evaluation_data(user_eval_id: str, db: Session) -> dict` fonksiyonu yaz:
  - [x] user_evaluation getir
  - [x] model_response getir (response_id üzerinden)
  - [x] question getir (question_id üzerinden)
  - [x] Return: `{user_eval, model_response, question, user_scores: dict}`
- [x] Validate 8 metrics present
- [x] Error handling for missing data

---

### Task 3.8: Judge Service - Stage 1 Implementation

**Tahmini Süre:** 4 saat

**Durum:** ✅ **TAMAMLANDI** (31 Ocak 2026)

**Yapılacaklar:**
- [x] `stage1_independent_evaluation(user_eval_id: str, db: Session) -> dict` fonksiyonu yaz:
  - [x] Evaluation data fetch et
  - [x] Prompt render et (JUDGE_PROMPTS["stage1"]["system_prompt"] + render_stage1_prompt())
  - [x] GPT-4o'ya gönder (temperature=0.3)
  - [x] Response parse et (JSON)
  - [x] Validate: 8 metrik, her biri {score (1-5 or null), rationale (str)}
  - [x] Return independent_scores dict
- [x] LLM call logging ekle (log_llm_call with token tracking)
- [x] Error handling (APITimeoutError, RateLimitError, APIConnectionError, APIError)

---

### Task 3.9: Judge Service - Response Parsing

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (31 Ocak 2026)

**Yapılacaklar:**
- [x] `parse_judge_response(response: str) -> dict` fonksiyonu yaz
- [x] Direct JSON parsing (try first)
- [x] Markdown code blocks (```json ... ```)
- [x] Generic code blocks (``` ... ```)
- [x] Nested brace extraction (count braces manually)
- [x] Validate structure (independent_scores key exists)
- [x] Return parsed dict
- [x] Tests: 11 passed (test_judge_service.py)

**Notlar:**
- Live API tests use actual GPT-4o API calls
- All 11 tests passing (init, fetch, parse, live API)
- LLM logging working (1622-1686 tokens per evaluation)

---

### Task 3.10: Async Task Infrastructure - Setup

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (1 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/tasks/__init__.py` oluştur
- [x] `backend/tasks/judge_task.py` oluştur
- [x] Background task decorator kullan (FastAPI BackgroundTasks)
- [x] Logger setup

---

### Task 3.11: Async Task - Judge Task

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (1 Şubat 2026)

**Yapılacaklar:**
- [x] `run_judge_evaluation(user_eval_id: str)` async fonksiyonu yaz:
  - [x] Try/except wrapper
  - [x] Stage 1 çağır
  - [x] (Stage 2 Week 4'te eklenecek)
  - [x] user_evaluations.judged = TRUE set et
  - [x] Errors handle et ve logla
- [x] Task'ı evaluation submit endpoint'ten çağır (BackgroundTasks)

---

### Task 3.12: Judge Feedback Endpoint - Basic

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (1 Şubat 2026)

**Yapılacaklar:**
- [x] `GET /api/evaluations/{evaluation_id}/feedback` endpoint yaz:
  - [x] user_evaluation getir
  - [x] judged flag kontrol et
  - [x] Eğer FALSE → return `{status: "processing"}`
  - [x] Eğer TRUE → return `{status: "completed"}` (Stage 2 Week 4'te eklenecek)
- [x] Response schema
- [x] Test endpoint
- [x] `POST /api/evaluations/{evaluation_id}/retry` endpoint (ekstra - retry için)

---

### Task 3.13: Judge Service - Tests

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (31 Ocak 2026)

**Yapılacaklar:**
- [x] `backend/tests/test_judge_service.py` oluştur
- [x] test_fetch_evaluation_data()
- [x] test_parse_judge_response()
- [x] test_stage1_independent_evaluation() (mock GPT-4o)
- [x] Tests çalıştır (11 passed)

---

### Task 3.14: Integration Test (Week 3)

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (1 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/cli.py` oluştur (CLI testing interface)
- [x] Interactive evaluation submission (8 metrik)
- [x] Judge feedback polling with timeout
- [x] Full workflow test command (generate → evaluate → judge)
- [x] Colored terminal output
- [x] Error handling for API failures
- [x] README.md'ye CLI kullanım instructions ekle
- [x] Test ve doğrula

---

### ✅ Week 3 Checklist

- [x] User evaluation API çalışıyor (30 Ocak 2026)
- [x] Evaluation validation doğru (30 Ocak 2026)
- [x] Judge prompts hazır (hardcoded) (30 Ocak 2026)
- [x] Judge Stage 1 (independent) çalışıyor (31 Ocak 2026)
- [x] Async task infrastructure kurulu (1 Şubat 2026)
- [x] Judge feedback endpoint çalışıyor (1 Şubat 2026)
- [x] LLM logging GPT-4o call'larını kaydediyor (31 Ocak 2026)
- [x] Judge service tests (11 passed) (31 Ocak 2026)
- [x] Integration tests geçiyor (1 Şubat 2026)
- [x] CLI testing interface (1 Şubat 2026)

---

## 📅 Week 4: Judge Stage 2 & End-to-End Testing

**Tarih:** 17 - 23 Şubat 2025  
**Hedef:** ChromaDB entegrasyonu, judge Stage 2, end-to-end test

---

### Task 4.1: ChromaDB Service - Setup

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (1 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/services/chromadb_service.py` oluştur
- [x] ChromaDB client initialize et
- [x] Collection oluştur ("evaluation_memory")
- [x] Embedding function setup (OpenAI text-embedding-3-small)
- [x] Logger setup
- [x] Health check entegrasyonu (/health ve /health/detailed)
- [x] Unit tests (10 test passed)

---

### Task 4.2: ChromaDB Service - Add to Memory

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (1 Şubat 2026)

**Yapılacaklar:**
- [x] `add_to_memory(db_session, user_eval_id: str, judge_eval_id: str) -> None` fonksiyonu yaz:
  - [x] Evaluation data fetch et (4-table join)
  - [x] Judge evaluation fetch et
  - [x] Document text oluştur (balanced format ~500 chars)
  - [x] Metadata oluştur:
    - evaluation_id
    - judge_id
    - category
    - primary_metric
    - difficulty
    - judge_meta_score
    - primary_metric_gap
    - weighted_gap
    - model_name
    - timestamp
    - mistake_pattern
  - [x] ChromaDB'ye add et
- [x] Error handling (ValueError for missing data, RuntimeError for ChromaDB failures)
- [x] Test fonksiyonu (inline test data, 8 tests passed)

---

### Task 4.3: ChromaDB Service - Query Past Mistakes

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (1 Şubat 2026)

**Yapılacaklar:**
- [x] `query_past_mistakes(primary_metric: str, category: str, n: int = 5) -> dict` fonksiyonu yaz:
  - [x] Query text oluştur: "User evaluating {primary_metric} in {category} category"
  - [x] ChromaDB query (where filter: $and operator for primary_metric & category)
  - [x] n_results parameter
  - [x] Return simplified format: `{evaluations: [{evaluation_id, category, judge_meta_score, primary_gap, feedback, mistake_pattern, timestamp}]}`
- [x] Empty result handling (returns empty list)
- [x] Error handling (RuntimeError for ChromaDB failures)
- [x] Test fonksiyonu (query tests with n parameter, filters)

---

### Task 4.4: Judge Service - Comparison Table Generator

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (2 Şubat 2026)

**Yapılacaklar:**
- [x] `generate_comparison_table(user_scores: dict, judge_scores: dict) -> str` fonksiyonu yaz:
  - [x] Markdown table oluştur
  - [x] Columns: Metric, User Score, Judge Score, Gap, Verdict
  - [x] Her 8 metrik için satır
  - [x] Gap hesapla (user - judge)
  - [x] Verdict belirle (over_estimated, under_estimated, aligned, not_applicable)
  - [x] Return markdown string
- [x] Test fonksiyonu (3 tests passed)

---

### Task 4.5: Judge Service - Weighted Gap Calculation

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (2 Şubat 2026)

**Yapılacaklar:**
- [x] `calculate_weighted_gap(user_scores: dict, judge_scores: dict, primary_metric: str, bonus_metrics: list) -> float` fonksiyonu yaz:
  - [x] Primary gap hesapla (abs)
  - [x] Bonus gaps hesapla (avg)
  - [x] Other gaps hesapla (avg)
  - [x] Weighted gap: primary*0.7 + bonus*0.2 + other*0.1
  - [x] Return weighted_gap
- [x] Test fonksiyonu (5 tests passed)

---

### Task 4.6: Judge Service - Meta Score Mapping

**Tahmini Süre:** 1 saat

**Durum:** ✅ **TAMAMLANDI** (2 Şubat 2026)

**Yapılacaklar:**
- [x] `weighted_gap_to_meta_score(weighted_gap: float) -> int` fonksiyonu yaz:
  - [x] <= 0.5 → 5
  - [x] <= 1.0 → 4
  - [x] <= 1.5 → 3
  - [x] <= 2.0 → 2
  - [x] else → 1
- [x] Test fonksiyonu (6 tests passed)

---

### Task 4.7: Judge Service - Stage 2 Implementation

**Tahmini Süre:** 4 saat

**Yapılacaklar:**
- [x] `stage2_mentoring_comparison(user_eval_id: str, stage1_scores: dict, vector_context: dict) -> dict` fonksiyonu yaz:
  - [x] Evaluation data fetch et
  - [x] Question data getir (primary_metric, bonus_metrics)
  - [x] Comparison table oluştur (Task 4.4 helper kullan)
  - [x] User scores serialize et
  - [x] Past mistakes formatla (vector_context'ten - `_format_past_mistakes`)
  - [x] Prompt render et (judge_prompts["stage2"])
  - [x] GPT-4o'ya gönder
  - [x] Response parse et (parse_stage2_response + _validate_stage2_response)
  - [x] Weighted gap hesapla (Task 4.5 helper kullan)
  - [x] Meta score hesapla (Task 4.6 helper kullan)
  - [x] Return: alignment_analysis, judge_meta_score, overall_feedback, improvement_areas, positive_feedback, primary_metric_gap, weighted_gap
- [x] LLM call logging (judge_stage2_comparison)
- [x] Error handling (timeout, rate limit, connection error, API error)
- [x] Test yaz (TestFormatPastMistakes, TestParseStage2Response, TestStage2MentoringComparison)

✅ **TAMAMLANDI** (2 Şubat 2026)

---

### Task 4.8: Judge Service - Full Flow Integration

**Tahmini Süre:** 3 saat

**Yapılacaklar:**
- [x] `full_judge_evaluation(user_eval_id: str) -> str` fonksiyonu yaz:
  - [x] Stage 1: independent evaluation
  - [x] ChromaDB: query past mistakes
  - [x] Stage 2: mentoring comparison
  - [x] Judge ID oluştur (judge_YYYYMMDD_HHMMSS_randomhex)
  - [x] judge_evaluations'a kaydet
  - [x] ChromaDB: add to memory (log-only on failure)
  - [x] user_evaluations.judged = TRUE
  - [x] Return judge_id
- [x] Error handling (rollback on failure)
- [x] Test yaz (TestFullJudgeEvaluation)

✅ **TAMAMLANDI** (2 Şubat 2026)

---

### Task 4.9: Async Task - Full Judge

**Tahmini Süre:** 1 saat

**Yapılacaklar:**
- [x] `backend/tasks/judge_task.py`'daki run_judge_evaluation() fonksiyonunu güncelle:
  - [x] full_judge_evaluation() çağır
  - [x] Success/failure logla
  - [x] Docstring güncelle (full flow reference)
- [x] Test async task

✅ **TAMAMLANDI** (2 Şubat 2026)

---

### Task 4.10: Judge Feedback Endpoint - Complete

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (2 Şubat 2026)

**Yapılacaklar:**
- [x] `GET /api/evaluations/{evaluation_id}/feedback` endpoint'i güncelle:
  - [x] Complete response format:
    - evaluation_id
    - judge_meta_score
    - overall_feedback
    - alignment_analysis (full dict)
    - improvement_areas
    - positive_feedback
    - past_patterns_referenced (ChromaDB'den)
  - [x] Response schema güncelle (AlignmentMetric.gap: int | float)
- [x] Test endpoint (7 new tests added)
- [x] Fix tests (UserEvaluation flush before JudgeEvaluation)

---

### Task 4.11: Statistics Router - Setup

**Tahmini Süre:** 1 saat

**Durum:** ✅ **TAMAMLANDI** (2 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/routers/stats.py` oluştur
- [x] APIRouter oluştur
- [x] Logger setup

---

### Task 4.12: Statistics - Overview Endpoint

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (2 Şubat 2026)

**Yapılacaklar:**
- [x] `GET /api/stats/overview` endpoint yaz:
  - [x] Total evaluations (COUNT user_evaluations)
  - [x] Average meta score (AVG judge_meta_score)
  - [x] Metrics performance:
    - [x] Her metrik için: avg primary_metric_gap, count
    - [x] Trend hesapla (son 10 vs önceki 10)
  - [x] Improvement trend (overall)
  - [x] Response format
- [x] Database queries optimize et (indexes kullan)
- [x] Test endpoint (8 tests passing)

---

### Task 4.13: CLI Testing Interface

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (2 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/cli.py` güncelle:
  - [x] `start_evaluation(primary_metric, use_pool)` → API call (zaten mevcut)
  - [x] `submit_evaluation(response_id, evaluations)` → API call (zaten mevcut)
  - [x] `get_feedback(evaluation_id)` → API call (zaten mevcut)
  - [x] `get_stats()` → API call (yeni eklendi)
  - [x] Pretty print results
- [x] Interactive CLI (input prompts) (zaten mevcut)
- [x] Test CLI

---

### Task 4.14: End-to-End Test Suite

**Tahmini Süre:** 4 saat

**Durum:** ✅ **TAMAMLANDI** (2 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/tests/test_e2e.py` oluştur
- [x] Test Scenario 1: Yeni soru üretme → değerlendirme → judge → feedback
- [x] Test Scenario 2: Havuzdan soru seçme → değerlendirme → judge → feedback
- [x] Test Scenario 3: Tekrar eden hata (ChromaDB hafıza)
- [x] Test Scenario 4: İstatistikler
- [x] Assert conditions:
  - [x] Database records created
  - [x] Judge meta score calculated
  - [x] ChromaDB document added
  - [x] Feedback returned
- [x] Tests çalıştır (7 tests passing)

---

### Task 4.15: Manual Testing Session

**Tahmini Süre:** 3 saat

**Yapılacaklar:**
- [ ] Manuel test senaryoları çalıştır (CLI kullanarak):
  1. [ ] **İlk değerlendirme (Truthfulness):**
     - Soru üret
     - Model cevaplasın
     - Değerlendirme yap (8 metrik)
     - Judge feedback al
     - Meta score kontrol et
  2. [ ] **Havuzdan seç (Safety):**
     - Havuzdan soru seç
     - Değerlendirme yap
     - Feedback al
  3. [ ] **Tekrar eden hata:**
     - Aynı metrikte (Truthfulness) 3 farklı değerlendirme yap
     - Her birinde biraz yumuşak/sert değerlendir
     - 3. değerlendirmede judge'ın "past patterns" referans ettiğini kontrol et
  4. [ ] **İstatistikler:**
     - Stats endpoint çağır
     - Metrics performance kontrol et
     - Improvement trend kontrol et
- [ ] Logları incele (mentormind.log, errors.log, llm_calls.jsonl)
- [ ] Bug'ları tespit et ve fix'le

---

### Task 4.16: Performance Testing

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] Judge duration ölç (Stage 1 + Stage 2)
- [ ] Database query performance kontrol et
- [ ] ChromaDB query latency ölç
- [ ] Bottleneck'leri belirle
- [ ] Optimization notları al (Phase 2 için)

---

### Task 4.17: Documentation Update

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] README.md güncelle:
  - [ ] Installation instructions doğru mu?
  - [ ] API endpoints listesi ekle
  - [ ] Example usage ekle (CLI)
- [ ] API documentation kontrol et (FastAPI auto-gen)
- [ ] Code comments ekle (missing parts)

---

### Task 4.18: Bug Fixes & Cleanup

**Tahmini Süre:** 3 saat

**Yapılacaklar:**
- [ ] Tespit edilen bug'ları fix'le
- [ ] Dead code sil
- [ ] Unused imports temizle
- [ ] Code formatting (black)
- [ ] Linting (flake8)
- [ ] Type hints ekle (mypy)

---

### Task 4.19: Final Verification

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] Tüm tests çalıştır: `pytest`
- [ ] Coverage kontrol et (target: 80%+)
- [ ] Docker build: `docker-compose build`
- [ ] Docker run: `docker-compose up -d`
- [ ] Health check: All services healthy
- [ ] End-to-end workflow: Baştan sona çalışıyor mu?

---

### Task 4.20: Enhancement - question_type Denormalization

**Tahmini Süre:** 1 saat

**Durum:** ✅ **TAMAMLANDI** (2 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/schemas/07_add_question_type_to_questions.sql` oluştur:
  - [x] `question_type` column ekle (TEXT, nullable)
  - [x] Existing data migrate et (question_prompts'tan questions'a)
  - [x] Index oluştur (idx_questions_question_type)
- [x] `backend/models/question.py` güncelle:
  - [x] `question_type: Mapped[Optional[str]]` field ekle
  - [x] String(50), nullable=True for backward compatibility
- [x] `backend/models/schemas.py` güncelle:
  - [x] QuestionBase'e `question_type: Optional[str]` field ekle
  - [x] Field description ekle
- [x] `backend/services/claude_service.py` güncelle:
  - [x] `_generate_new_question()` fonksiyonuna `question_type=question_type` ekle
- [x] `backend/routers/questions.py` güncelle:
  - [x] QuestionGenerateResponse'a `question_type: Optional[str]` field ekle
  - [x] Return statement'a `question_type=question.question_type` ekle
  - [x] Optional import ekle
- [x] SQL migration execute et:
  - [x] Column added (ALTER TABLE)
  - [x] Data migrated (15 questions updated)
  - [x] Index created
- [x] Test API response:
  - [x] `/api/questions/generate` returns `question_type`
  - [x] Pool selection works with `question_type`
  - [x] New generation populates `question_type`

**Notlar:**
- question_type denormalized from question_prompts for query performance
- Backward compatible (nullable column)
- All existing questions migrated (15 rows)

---

### ✅ Week 4 Checklist

- [x] ChromaDB entegrasyonu çalışıyor
- [x] Judge Stage 2 (mentoring) çalışıyor
- [x] Full judge workflow (Stage 1 + ChromaDB + Stage 2) çalışıyor
- [x] Past mistakes judge'a hatırlatılıyor
- [x] **Judge Feedback Endpoint Complete** (Task 4.10) (2 Şubat 2026)
- [ ] Statistics API çalışıyor
- [ ] CLI testing interface hazır
- [x] End-to-end tests geçiyor (16 tests + 7 new = 23 tests passed)
- [ ] Manual test senaryoları başarılı
- [x] Documentation güncel
- [ ] Code clean ve formatlanmış

---

## 🎯 Success Metrics

### Technical Metrics

- [ ] **Test Coverage:** 80%+ (backend)
- [ ] **API Response Time:** < 200ms (non-LLM endpoints)
- [ ] **Judge Duration:** 10-30 seconds (2-stage)
- [ ] **Database Queries:** Optimized (indexes kullanılıyor)
- [ ] **Docker Build:** < 5 dakika
- [ ] **Container Startup:** < 30 saniye (all services)

### Functional Metrics

- [ ] **Question Generation:** 100% success rate
- [ ] **K Model Answers:** 4/4 model çalışıyor
- [ ] **User Evaluation:** Validation %100 doğru
- [ ] **Judge Evaluation:** 2-stage workflow %100 başarılı
- [ ] **ChromaDB Memory:** Past mistakes doğru retrieve ediliyor
- [ ] **End-to-End:** Full workflow hiçbir hata vermeden çalışıyor

### Quality Metrics

- [ ] **Code Quality:** Linting errors yok (flake8)
- [ ] **Code Format:** Black formatlanmış
- [ ] **Type Hints:** Critical functions'larda mevcut
- [ ] **Documentation:** README + API docs güncel
- [ ] **Logging:** Comprehensive (3 log types)
- [ ] **Error Handling:** Try/except blokları mevcut

---

## 🎉 Phase 1 Completion

**Phase 1 tamamlandığında elimizde şunlar olacak:**

✅ **Çalışan Backend API** (FastAPI)  
✅ **5 Database Tablosu** (PostgreSQL)  
✅ **Soru Üretimi** (Claude Sonnet 4.5)  
✅ **4 K Model Entegrasyonu** (GPT-3.5, GPT-4o-mini, Claude Haiku, Gemini)  
✅ **User Evaluation System**  
✅ **2-Stage Judge System** (GPT-4o)  
✅ **ChromaDB Hafıza**  
✅ **Comprehensive Logging**  
✅ **CLI Testing Interface**  
✅ **Docker Infrastructure**  

**Sonraki adım:** Phase 2 - Frontend UI 🚀

---

## 📅 Phase 2: Frontend UI (6 Weeks)

**Tarih:** 24 Şubat - 7 Nisan 2025
**Hedef:** Next.js 14+ frontend ile kullanıcı dostu arayüz

---

## 🎯 Phase 2 Overview

### Scope

**Dahil:**
- Next.js 14+ (App Router) frontend
- shadcn/ui component library
- TanStack Query + Zustand state management
- Evaluation flow UI
- Judge feedback display (polling)
- Statistics dashboard
- Responsive design
- TypeScript

**Hariç:**
- User authentication (MVP single-user)
- Real-time features (SSE/WebSocket)
- PWA support
- Advanced analytics

### Definition of Done

Phase 2 tamamlandığında:
- [ ] Next.js proje kurulumu tamamlandı
- [ ] Tüm sayfalar render ediliyor
- [ ] Evaluation flow çalışıyor
- [ ] Judge feedback polling çalışıyor
- [ ] Statistics dashboard görüntüleniyor
- [ ] Responsive tasarım (mobile-friendly)
- [ ] Type-safe kod (TypeScript)
- [ ] Test suite hazır

---

## 📅 Week 5: Foundation & Setup

**Tarih:** 24 Şubat - 2 Mart 2025
**Hedef:** Next.js proje kurulumu ve temel yapı

---

### Task 5.1: Project Initialization

**Tahmini Süre:** 2 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] `frontend/` klasörünü oluştur
- [ ] Next.js 14+ initialize et (`npx create-next-app@latest`)
- [ ] TypeScript seç
- [ ] Tailwind CSS seç
- [ ] App Router seç
- [ ] `frontend/` klasör yapısını oluştur
- [ ] `.gitignore` güncelle (frontend-specific)

---

### Task 5.2: shadcn/ui Setup

**Tahmini Süre:** 2 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] shadcn/ui initialize et (`npx shadcn-ui@latest init`)
- [ ] Component library kurulumu
- [ ] Temel component'leri ekle:
  - [ ] button
  - [ ] card
  - [ ] input
  - [ ] label
  - [ ] slider
  - [ ] textarea
  - [ ] badge
  - [ ] progress
  - [ ] skeleton
  - [ ] alert
  - [ ] dialog
- [ ] `components/ui/` klasör yapısını oluştur

---

### Task 5.3: TanStack Query + Zustand Setup

**Tahmini Süre:** 2 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] `@tanstack/react-query` kur
- [ ] `zustand` kur
- [ ] `axios` kur
- [ ] Query client setup (`lib/query/client.ts`)
- [ ] Query keys tanımla (`lib/query/keys.ts`)
- [ ] Zustand store'ları oluştur:
  - [ ] evaluation store
  - [ ] UI store
- [ ] Provider setup (`app/providers.tsx`)

---

### Task 5.4: API Client Setup

**Tahmini Süre:** 2 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] API client oluştur (`lib/api/client.ts`)
- [ ] Axios instance konfigürasyonu
- [ ] Error handling middleware
- [ ] Request/response interceptor'lar
- [ ] Environment variables setup
- [ ] API base URL konfigürasyonu

---

### Task 5.5: Routing Structure

**Tahmini Süre:** 2 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] App Router yapısını oluştur:
  - [ ] `app/(auth)/` - Auth route group (future)
  - [ ] `app/dashboard/` - Dashboard
  - [ ] `app/evaluation/` - Evaluation flow
  - [ ] `app/statistics/` - Statistics
- [ ] Layout component'leri oluştur
- [ ] Navigation component'i oluştur
- [ ] Route guards ekle (future auth)

---

### Task 5.6: Design System Setup

**Tahmini Süre:** 3 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] Tailwind config güncelle (design tokens)
- [ ] Color palette ekle (LCH-based)
- [ ] Type scale ekle (Perfect Fourth)
- [ ] Spacing system ekle (8-point grid)
- [ ] Border radius tokens ekle
- [ ] Shadow system ekle
- [ ] `globals.css` güncelle
- [ ] Custom utility classes ekle

---

### ✅ Week 5 Checklist

- [ ] Next.js proje hazır
- [ ] shadcn/ui component'leri yüklü
- [ ] TanStack Query + Zustand kurulu
- [ ] API client hazır
- [ ] Routing yapısı kuruldu
- [ ] Design system tanımlandı

---

## 📅 Week 6: Evaluation Flow

**Tarih:** 3 - 9 Mart 2025
**Hedef:** Değerlendirme akışı UI

---

### Task 6.1: Dashboard Page

**Tahmini Süre:** 4 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] Dashboard page component'i oluştur (`app/dashboard/page.tsx`)
- [ ] Metric selector card (8 metrik kartları)
- [ ] "Start Evaluation" butonu
- [ ] Quick stats display (toplam değerlendirme, ortalama meta score)
- [ ] Recent evaluations listesi
- [ ] Responsive layout

---

### Task 6.2: Start Evaluation Page

**Tahmini Süre:** 3 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] Evaluation start page (`app/evaluation/page.tsx`)
- [ ] Primary metric selection
- [ ] Use pool toggle (havuzdan seç / yeni üret)
- [ ] Start button with loading state
- [ ] Error handling
- [ ] API integration (`POST /api/questions/generate`)

---

### Task 6.3: Question Card Component

**Tahmini Süre:** 3 saat

**Durum:** ⏳ **PLANLANDI`

**Yapılacaklar:**
- [ ] QuestionCard organism component'i
- [ ] Question display (formatted text)
- [ ] Category badge
- [ ] Model response display
- [ ] Model name badge
- [ ] Reference answer (collapsible)
- [ ] Loading skeleton

---

### Task 6.4: Evaluation Form Component

**Tahmini Süre:** 6 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] EvaluationForm organism component'i
- [ ] 8 metric card (accordion-style):
  - [ ] Metric name + icon
  - [ ] Score slider (1-5)
  - [ ] N/A checkbox
  - [ ] Reasoning textarea
- [ ] Form validation (tüm metrikler doldurulmalı)
- [ ] Draft auto-save (localStorage)
- [ ] Submit button with loading state
- [ ] Progress indicator (doldurulan metrikler)

---

### Task 6.5: Evaluation Page Integration

**Tahmini Süre:** 4 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] Evaluation page component'i (`app/evaluation/[id]/page.tsx`)
- [ ] QuestionCard + EvaluationForm entegrasyonu
- [ ] State management (Zustand)
- [ ] API integration (`POST /api/evaluations/submit`)
- [ ] Success state → redirect to feedback
- [ ] Error handling
- [ ] Loading states

---

### ✅ Week 6 Checklist

- [ ] Dashboard page hazır
- [ ] Start evaluation page hazır
- [ ] Question card component hazır
- [ ] Evaluation form component hazır
- [ ] Evaluation page entegrasyonu tamam
- [ ] API endpoint'leri entegre

---

## 📅 Week 7: Judge Feedback Display

**Tarih:** 10 - 16 Mart 2025
**Hedef:** Judge feedback polling ve display

---

### Task 7.1: Feedback Polling Hook

**Tahmini Süre:** 3 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] `useJudgeFeedback` hook oluştur
- [ ] TanStack Query ile polling implement et
- [ ] 3 saniyede bir poll et
- [ ] Status check (processing vs completed)
- [ ] Error handling
- [ ] Retry mechanism

---

### Task 7.2: Processing State Component

**Tahmini Süre:** 2 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] Processing state component'i
- [ ] Loading animation (Framer Motion)
- [ ] Estimated time display
- [ ] Progress steps (Stage 1 → Stage 2)
- [ ] Status messages

---

### Task 7.3: Judge Feedback Panel

**Tahmini Süre:** 6 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] JudgeFeedbackPanel organism component'i
- [ ] Meta score display (1-5 stars)
- [ ] Overall feedback section
- [ ] Alignment analysis (8 metrik için):
  - [ ] User score vs Judge score
  - [ ] Gap indicator
  - [ ] Verdict badge (aligned/over/under)
  - [ ] Feedback text
- [ ] Improvement areas list
- [ ] Positive feedback list
- [ ] Past patterns section (ChromaDB)

---

### Task 7.4: Feedback Page Integration

**Tahmini Süre:** 4 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] Feedback page component'i (`app/evaluation/[id]/feedback/page.tsx`)
- [ ] Processing state → Feedback state transition
- [ ] JudgeFeedbackPanel entegrasyonu
- [ ] Retry button (failed judge için)
- [ ] Back to dashboard navigation
- [ ] Error handling

---

### Task 7.5: Animations (Framer Motion)

**Tahmini Süre:** 3 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] Feedback item stagger animation
- [ ] Score comparison animation
- [ ] Progress bar animation
- [ ] Page transition animations
- [ ] Micro-interactions (hover, tap)

---

### ✅ Week 7 Checklist

- [ ] Feedback polling hook hazır
- [ ] Processing state component hazır
- [ ] Judge feedback panel hazır
- [ ] Feedback page entegrasyonu tamam
- [ ] Animalar implement edildi

---

## 📅 Week 8: Statistics Dashboard

**Tarih:** 17 - 23 Mart 2025
**Hedef:** İstatistik dashboard ve grafikler

---

### Task 8.1: Stats Overview Page

**Tahmini Süre:** 3 saat

**Durum:** ⏳ **PLANLANDI`

**Yapılacaklar:**
- [ ] Stats overview page (`app/statistics/page.tsx`)
- [ ] Total evaluations counter
- [ ] Average meta score display
- [ ] Trend indicator (improving/declining)
- [ ] Quick stats cards
- [ ] Responsive layout

---

### Task 8.2: Metric Performance Cards

**Tahmini Süre:** 4 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] MetricPerformanceCard component'i
- [ ] 8 metrik için card'lar
- [ ] Average gap display
- [ ] Evaluation count
- [ ] Trend indicator (arrow + color)
- [ ] Metric-specific color theming

---

### Task 8.3: Chart Library Setup

**Tahmini Süre:** 2 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] Chart library seç (Recharts / Chart.js / Victory)
- [ ] Library kurulumu
- [ ] Theme configuration
- [ ] Responsive wrapper component'i
- [ ] Custom tooltip component'i

---

### Task 8.4: Line Chart (Improvement Trend)

**Tahmini Süre:** 4 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] ImprovementTrendChart component'i
- [ ] Line chart implementation
- [ ] X-axis: Evaluation number
- [ ] Y-axis: Meta score
- [ ] Trend line (moving average)
- [ ] Hover tooltip
- [ ] Data fetching (API integration)

---

### Task 8.5: Radar Chart (Metric Comparison)

**Tahmini Süre:** 4 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] MetricRadarChart component'i
- [ ] Radar chart implementation
- [ ] 8 axes (8 metrik)
- [ ] User scores vs Judge scores comparison
- [ ] Average gaps visualization
- [ ] Interactive labels

---

### Task 8.6: Per-Metric Stats Page

**Tahmini Süre:** 3 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] Per-metric stats page (`app/statistics/metrics/[metric]/page.tsx`)
- [ ] Metric header (icon + name)
- [ ] Detailed stats display
- [ ] Historical evaluations listesi
- [ ] Performance trend chart
- [ ] Back button

---

### ✅ Week 8 Checklist

- [ ] Stats overview page hazır
- [ ] Metric performance cards hazır
- [ ] Chart library kurulu
- [ ] Line chart hazır
- [ ] Radar chart hazır
- [ ] Per-metric stats page hazır

---

## 📅 Week 9: Polish & UX

**Tarih:** 24 - 30 Mart 2025
**Hedef:** UX iyileştirmeleri ve detaylar

---

### Task 9.1: Responsive Design

**Tahmini Süre:** 4 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] Mobile breakpoint kontrolü (320px+)
- [ ] Tablet breakpoint kontrolü (768px+)
- [ ] Desktop breakpoint kontrolü (1024px+)
- [ ] Component'leri responsive yap
- [ ] Touch-friendly交互 (min 44x44px)

---

### Task 9.2: Loading States

**Tahmini Süre:** 3 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] Global loading spinner
- [ ] Skeleton screens (shadcn/ui Skeleton)
- [ ] Progress indicators
- [ ] Optimistic UI updates
- [ ] Loading states for all async operations

---

### Task 9.3: Error Handling

**Tahmini Süre:** 3 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] Error boundary component'i
- [ ] Error alert component'i (shadcn/ui Alert)
- [ ] Retry buttons
- [ ] User-friendly error messages
- [ ] Fallback UI components
- [ ] Error logging (Sentry - optional)

---

### Task 9.4: Accessibility

**Tahmini Süre:** 4 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] ARIA labels ekle
- [ ] Keyboard navigation (Tab, Enter, Escape)
- [ ] Focus management
- [ ] Screen reader testing
- [ ] Color contrast kontrolü (WCAG AA)
- [ ] Semantic HTML

---

### Task 9.5: Dark Mode Support

**Tahmini Süre:** 3 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] Dark mode toggle component'i
- [ ] Theme provider (next-themes)
- [ ] Dark mode styles (Tailwind dark:)
- [ ] System preference detection
- [ ] Theme persistence (localStorage)

---

### ✅ Week 9 Checklist

- [ ] Responsive tasarım tamam
- [ ] Loading states hazır
- [ ] Error handling hazır
- [ ] Accessibility iyileştirmeleri
- [ ] Dark mode support

---

## 📅 Week 10: Testing & Deployment

**Tarih:** 31 Mart - 6 Nisan 2025
**Hedef:** Testler ve deployment

---

### Task 10.1: Unit Tests (Vitest)

**Tahmini Süre:** 4 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] Vitest kurulumu
- [ ] Test utility fonksiyonları
- [ ] Test custom hooks
- [ ] Test Zustand store'ları
- [ ] Test API client fonksiyonları
- [ ] Coverage report (target: 70%+)

---

### Task 10.2: Integration Tests

**Tahmini Süre:** 4 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] MSW (Mock Service Worker) kurulumu
- [ ] API response mock'ları
- [ ] Component integration tests
- [ ] Query cache tests
- [ ] State management tests

---

### Task 10.3: E2E Tests (Playwright)

**Tahmini Süre:** 6 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] Playwright kurulumu
- [ ] E2E test senaryoları:
  - [ ] Complete evaluation flow
  - [ ] Judge feedback polling
  - [ ] Statistics dashboard
  - [ ] Responsive testing
- [ ] Visual regression tests (optional)
- [ ] CI/CD entegrasyonu

---

### Task 10.4: Performance Optimization

**Tahmini Süre:** 3 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] Bundle analysis
- [ ] Code splitting (dynamic imports)
- [ ] Image optimization (Next.js Image)
- [ ] Font optimization (next/font)
- [ ] Lazy loading components
- [ ] Lighthouse score (target: 90+)

---

### Task 10.5: Vercel Deployment

**Tahmini Süre:** 2 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] Vercel proje oluştur
- [ ] Environment variables ayarla
- [ ] Deploy (vercel CLI)
- [ ] Custom domain (optional)
- [ ] Production build test
- [ ] Preview deployments

---

### Task 10.6: Documentation

**Tahmini Süre:** 2 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] FRONTEND.md güncelle
- [ ] README.md'ye frontend section ekle
- [ ] Component documentation (Storybook - optional)
- [ ] API integration docs
- [ ] Deployment instructions

---

### ✅ Week 10 Checklist

- [ ] Unit tests hazır (70%+ coverage)
- [ ] Integration tests hazır
- [ ] E2E tests hazır
- [ ] Performance optimized
- [ ] Deployed to Vercel
- [ ] Documentation güncel

---

## 🎯 Phase 2 Success Metrics

### Technical Metrics

- [ ] **Test Coverage:** 70%+ (frontend)
- [ ] **Lighthouse Score:** 90+ (Performance, Accessibility, Best Practices)
- [ ] **Bundle Size:** < 500KB (initial JS)
- [ ] **TTFB:** < 200ms (Vercel edge)
- [ ] **FID/INP:** < 100ms (interaction delay)

### Functional Metrics

- [ ] **Evaluation Flow:** End-to-end çalışıyor
- [ ] **Judge Polling:** Real-time feedback alıyor
- [ ] **Stats Dashboard:** Tüm grafikler görüntüleniyor
- [ ] **Responsive:** 320px - 4K çalışıyor
- [ ] **Type-Safe:** TypeScript hataları yok

### Quality Metrics

- [ ] **Accessibility:** WCAG 2.1 AA uyumlu
- [ ] **Dark Mode:** Tüm sayfalar destekliyor
- [ ] **Error Handling:** Tüm hatalar kullanıcı dostu
- [ ] **Loading States:** Tüm async işlemlerde
- [ ] **Documentation:** FRONTEND.md güncel

---

## 🎉 Phase 2 Completion

**Phase 2 tamamlandığında elimizde şunlar olacak:**

✅ **Modern Next.js Frontend** (14+ App Router)
✅ **UI Component Library** (shadcn/ui)
✅ **State Management** (TanStack Query + Zustand)
✅ **Evaluation Flow UI**
✅ **Judge Feedback Display** (Polling)
✅ **Statistics Dashboard** (Charts)
✅ **Responsive Design** (Mobile-first)
✅ **Type-Safe Code** (TypeScript)
✅ **Comprehensive Tests** (Unit + Integration + E2E)
✅ **Production Ready** (Vercel deployed)

**Sonraki adım:** Phase 3 - Advanced Features 🚀

---

**Başarılar!** 💪