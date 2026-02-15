# MentorMind - Project Roadmap

**Proje:** MentorMind - AI Evaluator Training System  
**Phase 1:** MVP Backend (4 hafta) — 27 Ocak 2025  
**Phase 2:** Frontend UI (6 hafta) — 24 Şubat 2025  
**Phase 3:** Coach Chat + Evidence Backend (6 hafta) — 7 Nisan 2025  

---

## 📋 İçindekiler

### Phase 1: MVP Backend
- [Phase 1 Overview](#-phase-1-overview)
- [Week 1: Database & Infrastructure](#-week-1-database--infrastructure)
- [Week 2: Question Generation & K Models](#-week-2-question-generation--k-models)
- [Week 3: User Evaluation & Judge Stage 1](#-week-3-user-evaluation--judge-stage-1)
- [Week 4: Judge Stage 2 & End-to-End Testing](#-week-4-judge-stage-2--end-to-end-testing)
- [Phase 1 Success Metrics](#-success-metrics)

### Phase 2: Frontend UI
- [Phase 2 Overview](#-phase-2-overview)
- [Week 5: Foundation & Setup](#-week-5-foundation--setup)
- [Week 6: Evaluation Flow UI](#-week-6-evaluation-flow-ui)
- [Week 7: Judge Feedback Display](#-week-7-judge-feedback-display)
- [Week 8: Statistics Dashboard](#-week-8-statistics-dashboard)
- [Week 9: Polish & UX](#-week-9-polish--ux)
- [Week 10: Testing & Deployment](#-week-10-testing--deployment)
- [Phase 2 Success Metrics](#-phase-2-success-metrics)

### Phase 3: Coach Chat + Evidence (Backend)
- [Phase 3 Overview](#-phase-3-overview)
- [Week 11: Database Schema & Infrastructure](#-week-11-database-schema--infrastructure)
- [Week 12: Evidence Generation & Verification](#-week-12-evidence-generation--verification)
- [Week 13: Snapshot Service & Judge Integration](#-week-13-snapshot-service--judge-integration)
- [Week 14: Coach Chat Service](#-week-14-coach-chat-service)
- [Week 15: Chat Endpoints & Integration](#-week-15-chat-endpoints--integration)
- [Week 16: End-to-End Testing & Polish](#-week-16-end-to-end-testing--polish)
- [Phase 3 Success Metrics](#-phase-3-success-metrics)

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
- [x] Tüm database tabloları oluşturuldu
- [x] Docker container'lar çalışıyor
- [x] Claude ile soru üretilebiliyor
- [x] 4 K model soru cevaplayabiliyor
- [x] Kullanıcı değerlendirmesi kaydedilebiliyor
- [x] Judge 2-stage workflow çalışıyor
- [x] ChromaDB hafıza aktif
- [x] CLI üzerinden end-to-end test başarılı
- [x] Documentation güncel

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
- [x] Integration tests geçiyor

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
- [x] Manuel test senaryoları çalıştır (CLI kullanarak):
  1. [x] **İlk değerlendirme (Truthfulness):**
     - Soru üret
     - Model cevaplasın
     - Değerlendirme yap (8 metrik)
     - Judge feedback al
     - Meta score kontrol et
  2. [x] **Havuzdan seç (Safety):**
     - Havuzdan soru seç
     - Değerlendirme yap
     - Feedback al
  3. [x] **Tekrar eden hata:**
     - Aynı metrikte (Truthfulness) 3 farklı değerlendirme yap
     - Her birinde biraz yumuşak/sert değerlendir
     - 3. değerlendirmede judge'ın "past patterns" referans ettiğini kontrol et
  4. [x] **İstatistikler:**
     - Stats endpoint çağır
     - Metrics performance kontrol et
     - Improvement trend kontrol et
- [x] Logları incele (mentormind.log, errors.log, llm_calls.jsonl)
- [x] Bug'ları tespit et ve fix'le

---

### Task 4.16: Performance Testing

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [x] Judge duration ölç (Stage 1 + Stage 2)
- [x] Database query performance kontrol et
- [x] ChromaDB query latency ölç
- [x] Bottleneck'leri belirle
- [x] Optimization notları al (Phase 2 için)

---

### Task 4.17: Documentation Update

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [x] README.md güncelle:
  - [x] Installation instructions doğru mu?
  - [x] API endpoints listesi ekle
  - [x] Example usage ekle (CLI)
- [x] API documentation kontrol et (FastAPI auto-gen)
- [x] Code comments ekle (missing parts)

---

### Task 4.18: Bug Fixes & Cleanup

**Tahmini Süre:** 3 saat

**Yapılacaklar:**
- [x] Tespit edilen bug'ları fix'le
- [x] Dead code sil
- [x] Unused imports temizle
- [x] Code formatting (black)
- [x] Linting (flake8)
- [x] Type hints ekle (mypy)

---

### Task 4.19: Final Verification

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [x] Tüm tests çalıştır: `pytest`
- [x] Coverage kontrol et (target: 80%+)
- [x] Docker build test: `docker-compose build`
- [x] Docker run test: `docker-compose up -d`
- [x] Health check: All services healthy
- [x] End-to-end workflow: Baştan sona çalışıyor mu?

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
- [x] Statistics API çalışıyor
- [x] CLI testing interface hazır
- [x] End-to-end tests geçiyor (16 tests + 7 new = 23 tests passed)
- [x] Manual test senaryoları başarılı
- [x] Documentation güncel
- [x] Code clean ve formatlanmış

---

## 🎯 Success Metrics

### Technical Metrics

- [x] **Test Coverage:** 80%+ (backend)
- [x] **API Response Time:** < 200ms (non-LLM endpoints)
- [x] **Judge Duration:** 10-30 seconds (2-stage)
- [x] **Database Queries:** Optimized (indexes kullanılıyor)
- [x] **Docker Build:** < 5 dakika
- [x] **Container Startup:** < 30 saniye (all services)

### Functional Metrics

- [x] **Question Generation:** 100% success rate
- [x] **K Model Answers:** 4/4 model çalışıyor
- [x] **User Evaluation:** Validation %100 doğru
- [x] **Judge Evaluation:** 2-stage workflow %100 başarılı
- [x] **ChromaDB Memory:** Past mistakes doğru retrieve ediliyor
- [x] **End-to-End:** Full workflow hiçbir hata vermeden çalışıyor

### Quality Metrics

- [x] **Code Quality:** Linting errors yok (flake8)
- [x] **Code Format:** Black formatlanmış
- [x] **Type Hints:** Critical functions'larda mevcut
- [x] **Documentation:** README + API docs güncel
- [x] **Logging:** Comprehensive (3 log types)
- [x] **Error Handling:** Try/except blokları mevcut

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
- [x] Next.js proje kurulumu tamamlandı
- [x] Tüm sayfalar render ediliyor
- [x] Evaluation flow çalışıyor
- [x] Judge feedback polling çalışıyor
- [x] Statistics dashboard görüntüleniyor
- [x] Responsive tasarım (mobile-friendly)
- [x] Type-safe kod (TypeScript)
- [x] Test suite hazır

---

## 📅 Week 5: Foundation & Setup

**Tarih:** 24 Şubat - 2 Mart 2025
**Hedef:** Next.js proje kurulumu ve temel yapı

---

### Task 5.1: Project Initialization

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `frontend/` klasörünü oluştur
- [x] Next.js 14+ initialize et (`npx create-next-app@latest`)
- [x] TypeScript seç
- [x] Tailwind CSS seç
- [x] App Router seç
- [x] `frontend/` klasör yapısını oluştur
- [x] `.gitignore` güncelle (frontend-specific)

---

### Task 5.2: shadcn/ui Setup

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] shadcn/ui initialize et (`npx shadcn-ui@latest init`)
- [x] Component library kurulumu
- [x] Temel component'leri ekle:
  - [x] button
  - [x] card
  - [x] input
  - [x] label
  - [x] slider
  - [x] textarea
  - [x] badge
  - [x] progress
  - [x] skeleton
  - [x] alert
  - [x] dialog
- [x] `components/ui/` klasör yapısını oluştur

---

### Task 5.3: TanStack Query + Zustand Setup

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `@tanstack/react-query` kur
- [x] `zustand` kur
- [x] `axios` kur
- [x] Query client setup (`lib/query/client.ts`)
- [x] Query keys tanımla (`lib/query/keys.ts`)
- [x] Zustand store'ları oluştur:
  - [x] evaluation store
  - [x] UI store
- [x] Provider setup (`app/providers.tsx`)

---

### Task 5.4: API Client Setup

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] API client oluştur (`lib/api/client.ts`)
- [x] Axios instance konfigürasyonu
- [x] Error handling middleware
- [x] Request/response interceptor'lar
- [x] Environment variables setup
- [x] API base URL konfigürasyonu

---

### Task 5.5: Routing Structure

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] App Router yapısını oluştur:
  - [x] `app/(auth)/` - Auth route group (future)
  - [x] `app/dashboard/` - Dashboard
  - [x] `app/evaluation/` - Evaluation flow
  - [x] `app/statistics/` - Statistics
- [x] Layout component'leri oluştur
- [x] Navigation component'i oluştur
- [x] Route guards ekle (future auth)

---

### Task 5.6: Design System Setup

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Tailwind config güncelle (design tokens)
- [x] Color palette ekle (LCH-based)
- [x] Type scale ekle (Perfect Fourth)
- [x] Spacing system ekle (8-point grid)
- [x] Border radius tokens ekle
- [x] Shadow system ekle
- [x] `globals.css` güncelle
- [x] Custom utility classes ekle

---

### ✅ Week 5 Checklist

- [x] Next.js proje hazır
- [x] shadcn/ui component'leri yüklü
- [x] TanStack Query + Zustand kurulu
- [x] API client hazır
- [x] Routing yapısı kuruldu
- [x] Design system tanımlandı

---

## 📅 Week 6: Evaluation Flow

**Tarih:** 3 - 9 Mart 2025
**Hedef:** Değerlendirme akışı UI

---

### Task 6.1: Dashboard Page

**Tahmini Süre:** 4 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Dashboard page component'i oluştur (`app/dashboard/page.tsx`)
- [x] Metric selector card (8 metrik kartları)
- [x] "Start Evaluation" butonu
- [x] Quick stats display (toplam değerlendirme, ortalama meta score)
- [x] Recent evaluations listesi
- [x] Responsive layout

---

### Task 6.2: Start Evaluation Page

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Evaluation start page (`app/evaluation/page.tsx`)
- [x] Primary metric selection
- [x] Use pool toggle (havuzdan seç / yeni üret)
- [x] Start button with loading state
- [x] Error handling
- [x] API integration (`POST /api/questions/generate`)

---

### Task 6.3: Question Card Component

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] QuestionCard organism component'i
- [x] Question display (formatted text)
- [x] Category badge
- [x] Model response display
- [x] Model name badge
- [x] Reference answer (collapsible)
- [x] Loading skeleton

---

### Task 6.4: Evaluation Form Component

**Tahmini Süre:** 6 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] EvaluationForm organism component'i
- [x] 8 metric card (accordion-style):
  - [x] Metric name + icon
  - [x] Score slider (1-5)
  - [x] N/A checkbox
  - [x] Reasoning textarea
- [x] Form validation (tüm metrikler doldurulmalı)
- [x] Draft auto-save (localStorage)
- [x] Submit button with loading state
- [x] Progress indicator (doldurulan metrikler)

---

### Task 6.5: Evaluation Page Integration

**Tahmini Süre:** 4 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Evaluation page component'i (`app/evaluation/[id]/page.tsx`)
- [x] QuestionCard + EvaluationForm entegrasyonu
- [x] State management (Zustand)
- [x] API integration (`POST /api/evaluations/submit`)
- [x] Success state → redirect to feedback
- [x] Error handling
- [x] Loading states

---

### ✅ Week 6 Checklist

- [x] Dashboard page hazır
- [x] Start evaluation page hazır
- [x] Question card component hazır
- [x] Evaluation form component hazır
- [x] Evaluation page entegrasyonu tamam
- [x] API endpoint'leri entegre

---

## 📅 Week 7: Judge Feedback Display

**Tarih:** 10 - 16 Mart 2025
**Hedef:** Judge feedback polling ve display

---

### Task 7.1: Feedback Polling Hook

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `useJudgeFeedback` hook oluştur
- [x] TanStack Query ile polling implement et
- [x] 3 saniyede bir poll et
- [x] Status check (processing vs completed)
- [x] Error handling
- [x] Retry mechanism

---

### Task 7.2: Processing State Component

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Processing state component'i
- [x] Loading animation (Framer Motion)
- [x] Estimated time display
- [x] Progress steps (Stage 1 → Stage 2)
- [x] Status messages

---

### Task 7.3: Judge Feedback Panel

**Tahmini Süre:** 6 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] JudgeFeedbackPanel organism component'i
- [x] Meta score display (1-5 stars)
- [x] Overall feedback section
- [x] Alignment analysis (8 metrik için):
  - [x] User score vs Judge score
  - [x] Gap indicator
  - [x] Verdict badge (aligned/over/under)
  - [x] Feedback text
- [x] Improvement areas list
- [x] Positive feedback list
- [x] Past patterns section (ChromaDB)

---

### Task 7.4: Feedback Page Integration

**Tahmini Süre:** 4 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Feedback page component'i (`app/evaluation/[id]/feedback/page.tsx`)
- [x] Processing state → Feedback state transition
- [x] JudgeFeedbackPanel entegrasyonu
- [x] Retry button (failed judge için)
- [x] Back to dashboard navigation
- [x] Error handling

---

### Task 7.5: Animations (Framer Motion)

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Feedback item stagger animation
- [x] Score comparison animation
- [x] Progress bar animation
- [x] Page transition animations
- [x] Micro-interactions (hover, tap)

---

### ✅ Week 7 Checklist

- [x] Feedback polling hook hazır
- [x] Processing state component hazır
- [x] Judge feedback panel hazır
- [x] Feedback page entegrasyonu tamam
- [x] Animalar implement edildi

---

## 📅 Week 8: Statistics Dashboard

**Tarih:** 17 - 23 Mart 2025
**Hedef:** İstatistik dashboard ve grafikler

---

### Task 8.1: Stats Overview Page

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Stats overview page (`app/statistics/page.tsx`)
- [x] Total evaluations counter
- [x] Average meta score display
- [x] Trend indicator (improving/declining)
- [x] Quick stats cards
- [x] Responsive layout

---

### Task 8.2: Metric Performance Cards

**Tahmini Süre:** 4 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] MetricPerformanceCard component'i
- [x] 8 metrik için card'lar
- [x] Average gap display
- [x] Evaluation count
- [x] Trend indicator (arrow + color)
- [x] Metric-specific color theming

---

### Task 8.3: Chart Library Setup

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Chart library seç (Recharts / Chart.js / Victory)
- [x] Library kurulumu
- [x] Theme configuration
- [x] Responsive wrapper component'i
- [x] Custom tooltip component'i

---

### Task 8.4: Scores Over Time Chart

**Tahmini Süre:** 5 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] ScoresOverTimeChart molecule component'i
- [x] Line chart (judge meta scores over time)
- [x] Time range selection (week, month, all)
- [x] Loading & empty states
- [x] API integration (`GET /api/stats/overview`)

---

### Task 8.5: Metric Radar Chart

**Tahmini Süre:** 4 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] MetricRadarChart molecule component'i
- [x] Radar chart (user vs judge scores per metric)
- [x] Comparison layer
- [x] Interactive legend
- [x] Tooltip details

---

### ✅ Week 8 Checklist

- [x] Stats overview page hazır
- [x] Metric performance card'lar hazır
- [x] Chart library kurulu
- [x] Meta score line chart hazır
- [x] Radar comparison chart hazır

---

## 📅 Week 9: Polish & UX

**Tarih:** 24 - 30 Mart 2025
**Hedef:** UI/UX iyileştirmeleri ve cila

---

### Task 9.1: Global Navigation & Footer

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Sidebar navigation
- [x] Header with breadcrumbs
- [x] Theme toggle (dark/light mode)
- [x] User quick-actions
- [x] Responsive navigation drawer

---

### Task 9.2: Dark Mode Implementation

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `next-themes` integration
- [x] Dark mode color tokens
- [x] Conditional chart colors
- [x] Dark mode switch UI

---

### Task 9.3: Error States & Toast Notifications

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Global error boundary
- [x] toast component implementation (shadcn)
- [x] API failure notifications
- [x] Success confirmation toasts

---

### Task 9.4: Skeleton Screens & Loading UX

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Skeleton component'ler:
  - [x] Dashboard skeleton
  - [x] Evaluation skeleton
  - [x] Chart skeletons
- [x] Smooth loading transitions

---

### Task 9.5: Responsive Polish

**Tahmini Süre:** 4 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Mobile-specific navigation
- [x] Adaptive chart sizes
- [x] Form input adjustments for touch
- [x] Cross-browser testing

---

### ✅ Week 9 Checklist

- [x] Navigation & Layout mühürlendi
- [x] Dark mode aktif
- [x] Error/Success toast'lar hazır
- [x] Skeleton screens eklendi
- [x] Mobile responsive doğruluğu sağlandı

---

## 📅 Week 10: Testing & Deployment

**Tarih:** 31 Mart - 6 Nisan 2025
**Hedef:** Testler ve yayın hazırlığı

---

### Task 10.1: Frontend Unit Tests (Vitest)

**Tahmini Süre:** 4 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Vitest + React Testing Library setup
- [x] Metric helper unit tests
- [x] Component tests (UI atoms)
- [x] Mock service worker (MSW) setup

---

### Task 10.2: Component Integration Tests

**Tahmini Süre:** 5 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] EvaluationForm integration test
- [x] Dashboard workflow test
- [x] Feedback polling test (MSW)

---

### Task 10.3: E2E Tests (Playwright)

**Tahmini Süre:** 6 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Playwright setup
- [x] Full evaluation workflow E2E test
- [x] Stats page navigation E2E test
- [x] Multi-device responsive testing

---

### Task 10.4: Production Build & Optimization

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Bundle size analysis
- [x] Image optimizations (next/image)
- [x] Dynamic imports for heavy charts
- [x] Production build validation

---

### Task 10.5: Documentation & Handover

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Frontend README update
- [x] Style guide documentation
- [x] API client usage guide

---

### ✅ Week 10 Checklist

- [x] Unit tests passed
- [x] Integration tests passed
- [x] E2E Playwright tests passed
- [x] Production build optimized
- [x] Handover docs hazır

---

## 🎯 Phase 2 Success Metrics

### Technical Metrics

- [x] **Core Web Vitals:** LCP < 2.5s, CLS < 0.1
- [x] **Bundle Size:** < 200kb (first load)
- [x] **Type Safety:** 0 `any` usage
- [x] **Test Coverage:** 70%+ frontend

### UX Metrics

- [x] **Evaluation Completion Rate:** > 90%
- [x] **Time to Feedback:** < 15s (polling average)
- [x] **Mobile Usability:** 100% feature parity

---

## 🎉 Phase 2 Completion

**Phase 2 tamamlandığında elimizde şunlar olacak:**

✅ **Modern Next.js Arayüzü**  
✅ **Responsive & Dark Mode Desteği**  
✅ **İnteraktif Grafik Paneli** (Stats)  
✅ **Dinamik Değerlendirme Formu**  
✅ **Canlı Feedback Takibi**  
✅ **Full-stack Entegrasyon**  

**Sonraki adım:** Phase 3 - Coach Chat & Evidence Backend 🚀

---

## 📅 Phase 3: Coach Chat + Evidence (6 Weeks)

**Tarih:** 7 Nisan - 18 Mayıs 2025  
**Hedef:** Evidence-based evaluation ve interaktif Coach Chat backend

---

## 🎯 Phase 3 Overview

### Scope

**Dahil:**
- Evidence (kanıt) toplama altyapısı (Stage 1)
- 5-Aşamalı Self-Healing Evidence Verification algoritması
- Evaluation Snapshot sistemi (immutability)
- Coach Chat Service (SSE streaming, GPT-4o-mini)
- Idempotency & SSE Reconnect yönetimi
- Chat History (Rolling Window) yönetimi
- Snapshot CRUD API

**Hariç:**
- Frontend UI (Phase 4'te yapılacak)
- Multi-user Chat (MVP single-user)
- Advanced Chat Analytics

### Definition of Done

Phase 3 tamamlanmış sayılır eğer:
- [x] Judge (GPT-4o) kanıt toplayabiliyor
- [x] Kanıtlar %90+ başarıyla doğrulanabiliyor (Self-healing)
- [x] Değerlendirmeler Snapshot olarak mühürlenebiliyor
- [x] Coach Chat SSE ile kelime kelime akabiliyor
- [x] 15 mesaj limiti ve turn yönetimi çalışıyor
- [x] Reconnect durumunda cevap kaldığı yerden devam ediyor
- [x] Tüm Phase 3 unit/integration testleri geçiyor

---

## 📅 Week 11: Database Schema & Infrastructure

**Tarih:** 7 Nisan - 13 Nisan 2025  
**Hedef:** Phase 3 için gerekli DB tabloları ve temel yardımcılar

---

### Task 11.1: Metric Slug Constants & Helpers

**Tahmini Süre:** 1.5 saat

**Durum:** ✅ **TAMAMLANDI** (8 Şubat 2026)

**Referans:** AD-6

**Yapılacaklar:**
- [x] `backend/constants/metrics.py` oluştur:
  - [x] 8 metrik için slug eşlemeleri (Truthfulness -> truthfulness)
  - [x] Display Name <-> Slug dönüştürücü yardımcılar
- [x] Unit test yaz (21 test passed)

---

### Task 11.2: SQL Schema - evaluation_snapshots

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (8 Şubat 2026)

**Referans:** AD-3, AD-11

**Yapılacaklar:**
- [x] `backend/schemas/08_evaluation_snapshots.sql` oluştur (24 sütun)
- [x] Snapshot ID formatı: `snap_YYYYMMDD_HHMMSS_randomhex`
- [x] JSONB skorlar ve kanıtlar için alanlar ekle
- [x] Soft delete (deleted_at) desteği ekle
- [x] Index'leri tanımla (created_at DESC, status, deleted_at)

---

### Task 11.3: SQL Schema - chat_messages

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (8 Şubat 2026)

**Referans:** AD-4

**Yapılacaklar:**
- [x] `backend/schemas/09_chat_messages.sql` oluştur
- [x] Shared Turn ID (`client_message_id`) sütunu ekle
- [x] Idempotency index: `UNIQUE (snapshot_id, client_message_id, role)`
- [x] JSONB `selected_metrics` alanı ekle

---

### Task 11.4: SQLAlchemy Models — Phase 3

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (8 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/models/evaluation_snapshot.py` oluştur (23 alan)
- [x] `backend/models/chat_message.py` oluştur (9 alan)
- [x] `snapshot_status` ENUM entegrasyonu
- [x] Property metodları ekle (`is_chat_available`, `is_user_message` vb.)

---

### Task 11.5: Pydantic Schemas — Phase 3

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (8 Şubat 2026)

**Yapılacaklar:**
- [x] Evidence schemas (`EvidenceItem`, `MetricEvidence`)
- [x] Snapshot schemas (`SnapshotResponse`, `SnapshotListItem`)
- [x] Chat schemas (`ChatRequest`, `ChatMessageResponse`)
- [x] Custom validator'lar (UUIDv4, metric slug validation)

---

### Task 11.6: Settings Update — Coach & Evidence

**Tahmini Süre:** 1 saat

**Durum:** ✅ **TAMAMLANDI** (8 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/config/settings.py` güncelle:
  - [x] `coach_model` (gpt-4o-mini)
  - [x] `max_chat_turns` (15)
  - [x] `chat_history_window` (6)
  - [x] `evidence_anchor_len` (25)
  - [x] `evidence_search_window` (2000)

---

### Task 11.7: Schema Validation & Test Coverage

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (8 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/tests/test_phase3_schemas.py` oluştur
- [x] Pydantic validation testleri (32 test passed)
- [x] `end > start` gibi iş mantığı kontrolleri

---

### ✅ Week 11 Checklist

- [x] Metrik slug sistemi hazır
- [x] Snapshot ve Chat tabloları SQL şemaları hazır
- [x] SQLAlchemy modelleri mühürlendi
- [x] Pydantic şemaları ve validatorlar hazır
- [x] Proje ayarları (turn limit, window size) güncellendi
- [x] %90+ schema test coverage sağlandı

---

## 📅 Week 12: Evidence Implementation

**Tarih:** 14 Nisan - 20 Nisan 2025  
**Hedef:** Kanıt toplama, doğrulama ve self-healing algoritması

---

### Task 12.1: Stage 1 Prompt Update — Evidence Output

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (8 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/prompts/judge_prompts.py` güncelle:
  - [x] Evidence Collection bölümü ekle
  - [x] 5 zorunlu alan: `quote`, `start`, `end`, `why`, `better`
  - [x] JSON örneğini kanıtlı formatla güncelle
- [x] Token sayımı ve optimizasyon (~2111 tokens)

---

### Task 12.2: Evidence JSON Parser

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (8 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/services/evidence_service.py` oluştur:
  - [x] `parse_evidence_from_stage1()` fonksiyonu
  - [x] Display name -> Slug dönüşümü
  - [x] Yapısal validasyon (5 alan kontrolü)
- [x] Graceful degradation (hata logla, devam et)

---

### Task 12.3: Self-Healing Verification Algorithm

**Tahmini Süre:** 6 saat

**Durum:** ✅ **TAMAMLANDI** (9 Şubat 2026)

**Referans:** AD-2

**Yapılacaklar:**
- [x] `verify_evidence_item()` fonksiyonu:
  - [x] **Aşama 1 (Exact):** İndeksler birebir tutuyor mu?
  - [x] **Aşama 2 (Substring):** Metin kaymış mı? (Full search)
  - [x] **Aşama 3 (Anchor):** `anchor_len` karakter ile yerini bul ve indeksleri tamir et
  - [x] **Aşama 4 (Whitespace):** Boşlukları ignore ederek bul
  - [x] **Aşama 5 (Fallback):** Bulunamazsa `verified: false`, `highlight_available: false`
- [x] Unit test yaz (40 test passed)

---

### Task 12.4: Evidence Service — Orchestration

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (9 Şubat 2026)

**Yapılacaklar:**
- [x] `process_evidence(model_answer, raw_evidence) -> dict` fonksiyonu:
  - [x] Tüm metriklerdeki kanıtları döngüye al
  - [x] `verify_all_evidence` çağır
  - [x] İstatistik logla (verified/total)
- [x] `judge_service.py` entegrasyonu

---

### Task 12.5: Evidence Unit Tests

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (9 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/tests/test_evidence_verification.py`
- [x] `backend/tests/test_evidence_service.py`
- [x] Kenar durumları test et (boş cevap, çok uzun cevap, uydurma alıntı)

---

### Task 12.6: Judge Service Integration — Evidence

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (9 Şubat 2026)

**Yapılacaklar:**
- [x] `full_judge_evaluation()` akışını güncelle:
  - [x] Stage 1'den kanıtları ayıkla
  - [x] Evidence Service ile doğrula
  - [x] Veritabanına mühürle (Snapshot öncesi son durak)
- [x] Regression testleri (40 judge testi passed)

---

### ✅ Week 12 Checklist

- [x] Judge artık her metrik için kanıt topluyor
- [x] 5-Aşamalı doğrulama algoritması çalışıyor
- [x] İndeks kaymaları (tokenization mismatch) otomatik tamir ediliyor
- [x] Kanıt işleme hataları ana akışı bozmuyor (graceful)
- [x] Tüm evidence servis testleri yeşil

---

## 📅 Week 13: Snapshot Service & Judge Integration

**Tarih:** 21 Nisan - 27 Nisan 2025  
**Hedef:** Değerlendirmelerin Snapshot olarak kaydedilmesi ve API entegrasyonu

---

### Task 13.1: Snapshot Service — Create

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (11 Şubat 2026)

**Referans:** AD-7 (Atomic Write), AD-11 (Otomatik Kayıt)

**Yapılacaklar:**
- [x] `backend/services/snapshot_service.py` oluştur:
  - [x] `create_evaluation_snapshot(db, stage1_result, stage2_result, user_eval, question, model_response) -> EvaluationSnapshot` fonksiyonu:
    - [x] Snapshot ID oluştur (`snap_YYYYMMDD_HHMMSS_randomhex`)
    - [x] Slug dönüşümü uygula (user_scores, judge_scores, evidence → slug key'ler)
    - [x] Evidence işle: `process_evidence(model_answer, raw_evidence)` çağır
    - [x] Tüm alanları birleştir (Stage 1 + Stage 2 + question + response)
    - [x] `judge_scores_json` ← Stage 1 `independent_scores` direkt kullanılır
    - [x] Tek transaction'da DB've yaz (atomik)
    - [x] Return: oluşturulan snapshot objesi
  - [x] ID generator helper: `generate_snapshot_id() -> str`
- [x] Hata durumunda rollback (yarım snapshot oluşmaz)
- [x] Başarılı oluşturma log'u: `INFO "Snapshot created: {id}"`
- [x] Unit test yaz (19 test passed)

---

### Task 13.2: Snapshot Service — CRUD (Soft Delete)

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/services/snapshot_service.py` içine ekle:
  - [x] `get_snapshot(db, snapshot_id) -> EvaluationSnapshot` (deleted_at filtreli)
  - [x] `list_snapshots(db, status, limit, offset) -> list` (deleted_at filtreli)
  - [x] `soft_delete_snapshot(db, snapshot_id) -> bool` (`deleted_at = now`, `status = archived`)
- [x] Unit test yaz (6 test passed)

---

### Task 13.3: Judge Task Update — Automatic Snapshot

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/tasks/judge_task.py` güncelle:
  - [x] Judge evaluation bittikten hemen sonra `create_evaluation_snapshot()` çağır
  - [x] Snapshot hatası judge akışını kırmamalı (try/except, WARNING log)
- [x] `judge_evaluation_id`'yi `stage2_result` içine enjekte et (Snapshot FK için)
- [x] Unit test yaz (TestJudgeTaskSnapshotIntegration)

---

### Task 13.4: Graceful Degradation — Evidence Parse Failure

**Tahmini Süre:** 1.5 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Referans:** AD-8

**Yapılacaklar:**
- [x] `snapshot_service.py` içinde kanıt işleme bloğunu `try/except` ile koru
- [x] Evidence parse hatası → snapshot `evidence_json = null` ile oluşturulur (Skorlar kurtarılır)
- [x] Unit test yaz (TestEvidenceGracefulDegradation - 6 test passed)

---

### Task 13.5: Snapshot Router & Endpoints

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/routers/snapshots.py` oluştur:
  - [x] `GET /api/snapshots/` (List with pagination & status filter)
  - [x] `GET /api/snapshots/{snapshot_id}` (Get detail)
  - [x] `DELETE /api/snapshots/{snapshot_id}` (Soft delete)
- [x] `main.py` entegrasyonu (prefix: `/api/snapshots`)
- [x] Unit test yaz (TestSnapshotsRouter - 13 test passed)

---

### Task 13.6: End-to-End Testing & Polish

**Tahmini Süre:** 4 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/tests/test_snapshot_integration.py` oluştur
- [x] Live API testi: Full Workflow (Soru -> Değerlendirme -> Snapshot)
- [x] Concurrency testi: Aynı anda snapshot oluşturma
- [x] Status transition testi: active -> completed -> archived -> deleted
- [x] Cleanup: `conftest.py`'deki test database TRUNCATE mantığını mühürle

---

### ✅ Week 13 Checklist

- [x] Snapshot Service oluşturuldu
- [x] Judge bittiğinde otomatik snapshot alınıyor (AD-11)
- [x] Metrikler slug formatında mühürleniyor (AD-6)
- [x] Snapshot CRUD endpoint'leri hazır
- [x] Soft delete (arşivleme) mekanizması çalışıyor
- [x] %100 snapshot service test coverage sağlandı

---

## 📅 Week 14: Coach Chat Service

**Tarih:** 28 Nisan - 4 Mayıs 2025  
**Hedef:** Interaktif mentorluk için Coach Chat logic ve SSE altyapısı

---

### Task 14.1: Coach Prompt Design

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Referans:** AD-5 (GPT-4o-mini), AD-10 (Strict Evidence)

**Yapılacaklar:**
- [x] `backend/prompts/coach_prompts.py` oluştur:
  - [x] `COACH_SYSTEM_PROMPT`: İngilizce sistem promptu (Rol: Mentor)
  - [x] `COACH_USER_PROMPT_TEMPLATE`: Türkçe çıktı kuralları ve context yapısı
  - [x] `COACH_INIT_GREETING_TEMPLATE`: İlk selamlama şablonu
- [x] **AD-10 Uygulaması:** Sadece judge kanıtlarını kullanma kuralı eklendi
- [x] Unit test yaz (TestCoachPrompts - 168 test passed)

---

### Task 14.2: Chat Service — Logic & Streaming

**Tahmini Süre:** 5 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Referans:** AD-4 (SSE), AD-5 (OpenRouter)

**Yapılacaklar:**
- [x] `backend/services/coach_service.py` oluştur:
  - [x] `CoachService` sınıfı (OpenAI client with OpenRouter base URL)
  - [x] `stream_coach_response()` asenkron generator fonksiyonu
  - [x] Mesajları DB'ye kaydetme logic'i (`save_user_message`, `save_assistant_message`)
- [x] OpenRouter entegrasyonu (gpt-4o-mini)
- [x] SSE formatında stream desteği
- [x] Unit test yaz (TestCoachService - 25 test passed)

---

### Task 14.3: Chat Router — SSE & Logic Polish

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/routers/coach.py` ve `main.py` prefix uyumu sağlandı
- [x] `StreamingResponse` ile `X-Accel-Buffering: no` desteği eklendi
- [x] Early validation: Stream başlamadan snapshot kontrolü (404/429)
- [x] Router unit testleri (TestCoachRouter - 21 test passed)

---

### Task 14.4: Chat Service — Init Greeting (Streaming)

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Referans:** AD-4 (Init Greeting)

**Yapılacaklar:**
- [x] `handle_init_greeting(db, snapshot_id, client_message_id, selected_metrics) -> AsyncGenerator` fonksiyonu:
  - [x] `client_message_id = "init_{snapshot_id}"` sabit kimlik
  - [x] Idempotent: Zaten init greeting varsa DB'deki cevabı dön (LLM'e gitmez)
  - [x] Yoksa:
    - [x] Init greeting template'i render et (seçilen metriklerdeki gap + evidence özeti)
    - [x] LLM'e gönder, streaming cevap al
    - [x] DB've yaz (`role: assistant`, `is_complete` akışı)
  - [x] `chat_turn_count` **artmaz** (bonus mesaj)
- [x] **Shared Turn ID İstisnası:**
  - [x] Init greeting'de sadece `role: assistant` mesajı var, eşleşen `role: user` yok
  - [x] `UNIQUE (snapshot_id, client_message_id, role)` buna izin verir
- [x] `selected_metrics` ilk init mesajıyla birlikte DB'ye kaydedilir (immutable)
- [x] Unit test yaz (ilk init, tekrar init, metrics immutability)

---

### Task 14.5: Chat Service — Turn Limit (Atomic SQL)

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Referans:** AD-9 (Turn Limit)

**Yapılacaklar:**
- [x] `check_and_increment_turn(db, snapshot_id: str) -> bool` fonksiyonu:
  - [x] Atomik SQL sorgusu:
    ```sql
    UPDATE evaluation_snapshots
    SET chat_turn_count = chat_turn_count + 1
    WHERE id = :id AND chat_turn_count < max_chat_turns
    ```
  - [x] `rows_affected == 0` → limit dolmuş, `False` dön
  - [x] `rows_affected == 1` → başarılı, `True` dön
  - [x] Race condition koruması (concurrent requests)
- [x] Limit aşıldığında HTTP 429 response:
  ```json
  {"error": "turn_limit_reached", "message": "Bu değerlendirme üzerine yeterince konuştuk..."}
  ```
- [x] `get_remaining_turns(db, snapshot_id) -> int` helper
- [x] Unit test yaz (normal artırım, limit dolmuş, concurrent test)

---

### Task 14.6: Chat Service — Idempotency & Reconnect

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Referans:** AD-4 (SSE Reconnect & Idempotency)

**Yapılacaklar:**
- [x] **Idempotency (client_message_id):**
  - [x] `check_duplicate_message(db, snapshot_id, client_message_id) -> ChatMessage | None` fonksiyonu:
    - [x] `(snapshot_id, client_message_id, "user")` DB'de var mı kontrol et
    - [x] Varsa mevcut assistant cevabını dön (LLM'e gitmez, sayaç artmaz)
- [x] **Reconnect (last_event_id):**
  - [x] `handle_reconnect(db, snapshot_id, client_message_id) -> tuple[str, bool]` fonksiyonu:
    - [x] `(snapshot_id, client_message_id, "assistant")` kaydını bul
    - [x] `is_complete: true` → DB'deki tam cevabı dön
    - [x] `is_complete: false` → **Update-In-Place:**
      - [x] `content = ""` sıfırla
      - [x] `is_complete = false` kalsın
      - [x] LLM üretimini baştan başlat, aynı satırın üzerine yaz
    - [x] Kayıt yok → Yeni assistant satırı INSERT et
- [x] **Turn Counter Sıralaması:**
  ```
  1. Dedup kontrol (client_message_id)
  2. Turn limit kontrol + artırım (atomik)
  3. User mesajı yaz (is_complete: true)
  4. Assistant mesajı yaz (is_complete: false, content: "")
  5. LLM streaming → content güncelle
  6. is_complete: true güncelle
  ```
- [x] Unit test yaz (duplicate mesaj, reconnect yarım cevap, reconnect tam cevap)

---

### 📌 Week 14 — Kritik Teknik Notlar

**1. SSE (Server-Sent Events) Streaming Altyapısı (AD-4):**
- FastAPI `StreamingResponse` ile `text/event-stream` content type kullanılır.
- Event formatı:
  ```
  event: token
  data: {"content": "kelime"}

  event: done
  data: {"msg_id": "msg_..."}
  ```
- OpenRouter API'den gelen streaming chunk'lar doğrudan client'a iletilir.
- Streaming tamamlandığında DB'deki assistant mesajı `is_complete: true` yapılır.

**2. Rolling Window — Son 6 Mesaj Context Yönetimi (AD-4):**
- LLM'e gönderilen context: **Snapshot (evidence)** + **Son 6 mesaj** (3 user + 3 assistant).
- Eski mesajlar DB'de saklanır ama LLM'e gönderilmez → token tasarrufu ~%60.
- `is_complete: false` olan yarım mesajlar window'a dahil edilmez.
- Window size configurable: `settings.CHAT_HISTORY_WINDOW = 6`

**3. Update-In-Place — Yarım Kalan Cevapları Güncelleme (AD-4):**
- SSE bağlantısı koptuğunda assistant cevabı yarım kalabilir (`is_complete: false`).
- Reconnect geldiğinde:
  ```
  (snapshot_id, client_message_id, "assistant") kaydı bulunur
  ├─ is_complete: true  → DB'deki tam cevap dönülür (LLM çağrılmaz)
  ├─ is_complete: false → content sıfırlanır, LLM baştan üretir (UPDATE, DELETE değil)
  └─ Kayıt yok          → Yeni assistant satırı INSERT edilir
  ```
- **Neden UPDATE?** (1) UNIQUE constraint ihlal edilmez, (2) `msg_id` değişmez (frontend state bozulmaz), (3) Tek UPDATE, DELETE+INSERT'e göre daha az indeks maliyeti.

---

### ✅ Week 14 Checklist

- [x] Coach prompt hazır (system + user + init)
- [x] SSE streaming çalışıyor (kelime kelime)
- [x] Token windowing çalışıyor (son 6 mesaj)
- [x] Init greeting çalışıyor (idempotent)
- [x] Turn limit enforce ediliyor (atomik SQL)
- [x] Idempotency ve reconnect çalışıyor
- [x] Update-In-Place stratejisi çalışıyor
- [x] Tüm chat service unit testleri geçiyor (28 test)
- [x] Task 14.3: Coach Router & Endpoints (21 test passed)
- [x] Task 14.4: Coach Integration Tests (3 test passed)
- [x] Task 14.5: Git commit & documentation update

---

## 📅 Week 15: Chat Endpoints & Integration

**Tarih:** 5 Mayıs - 11 Mayıs 2025  
**Hedef:** Chat router, entegrasyon testleri, error handling

---

### Task 15.1: Chat Router — POST /api/snapshots/{id}/chat

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/routers/snapshots.py` içine chat endpoint'i ekle:
  - [x] `POST /api/snapshots/{snapshot_id}/chat`:
    - [x] Request body: `ChatMessageRequest` (message, client_message_id, selected_metrics, is_init)
    - [x] Response: `StreamingResponse` (SSE, `text/event-stream`)
    - [x] **Akış sırası:**
      1. Snapshot var mı kontrol et (404)
      2. Snapshot status == 'active' mi kontrol et (409 eğer archived)
      3. `is_init: true` ise → `handle_init_greeting()` çağır
      4. Dedup kontrol (`check_duplicate_message`)
      5. Turn limit kontrol (`check_and_increment_turn`) → 429
      6. User mesajı DB'ye yaz
      7. Assistant mesajı DB'ye yaz (boş)
      8. SSE streaming başlat (`stream_coach_response`)
    - [x] `selected_metrics` validasyonu:
      - [x] Slug formatında mı? (ALL_METRIC_SLUGS'ta var mı?)
      - [x] Max 3 metrik
      - [x] İlk mesajda zorunlu, sonrasında ignore
- [x] SSE response headers:
  - [x] `Content-Type: text/event-stream`
  - [x] `Cache-Control: no-cache`
  - [x] `Connection: keep-alive`
- [x] Error response'lar:
  - [x] 404: Snapshot bulunamadı
  - [x] 409: Snapshot archived
  - [x] 429: Turn limit dolmuş
  - [x] 422: Validation hatası (eksik client_message_id, geçersiz metrik)

---

### Task 15.2: Chat Router — GET Messages

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/routers/snapshots.py` içine messages endpoint'i ekle:
  - [x] `GET /api/snapshots/{snapshot_id}/messages`:
    - [x] Query params: `limit` (default: 50), `offset` (default: 0)
    - [x] Response: `ChatHistoryResponse` (messages list + total + snapshot_id)
    - [x] `ORDER BY created_at ASC` (kronolojik sıra)
    - [x] Sadece `is_complete: true` mesajları dön (yarım cevaplar hariç)
    - [x] 404 eğer snapshot bulunamazsa
  - [x] Sayfa reload'da frontend bu endpoint'i çağırır
- [x] Pagination (limit/offset)
- [x] Unit test yaz (boş geçmiş, dolu geçmiş, pagination)

---

### Task 15.3: Chat Service Unit Tests

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/tests/test_chat_service.py` oluştur:
  - [x] **Streaming testleri:**
    - [x] SSE event formatı doğru (event: token, data: ...)
    - [x] Streaming tamamlandığında is_complete güncelleniyor
    - [x] DB'deki content streaming sonucu ile aynı
  - [x] **Windowing testleri:**
    - [x] Boş geçmiş → boş list
    - [x] 3 mesaj → 3 mesaj dönüyor
    - [x] 10 mesaj → son 6 mesaj dönüyor
    - [x] Yarım mesajlar (is_complete: false) dahil edilmiyor
  - [x] **Init greeting testleri:**
    - [x] İlk init → LLM çağrılır, mesaj oluşturulur
    - [x] Tekrar init → DB'deki mevcut greeting dönüyor (idempotent)
    - [x] Init turn_count artırmıyor
    - [x] selected_metrics DB'ye kaydediliyor
  - [x] **Turn limit testleri:**
    - [x] Normal artırım çalışıyor
    - [x] Limit dolduğunda False dönüyor
    - [x] Remaining turns doğru hesaplanıyor
  - [x] **Idempotency testleri:**
    - [x] Aynı client_message_id → aynı cevap, LLM çağrılmıyor
    - [x] Farklı client_message_id → yeni cevap

---

### Task 15.4: Chat Integration Tests

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/tests/test_chat_integration.py` oluştur:
  - [x] **Full flow testi:**
    1. Snapshot oluştur (mock veya fixture)
    2. Init greeting gönder → cevap al
    3. Chat mesajı gönder → SSE cevap al
    4. 2. mesaj gönder → geçmiş mesajlar context'te
    5. Messages endpoint → tüm mesajlar dönüyor
  - [x] **Turn limit flow:**
    1. 15 mesaj gönder → tümü başarılı
    2. 16. mesaj → 429 response
    3. Messages endpoint → 30+ mesaj (15 user + 15 assistant + init)
  - [x] **Reconnect flow:**
    1. Mesaj gönder, yarım kal (mock)
    2. Aynı client_message_id ile retry
    3. Update-in-place çalışıyor
  - [x] **Duplicate flow:**
    1. Mesaj gönder → cevap al
    2. Aynı client_message_id ile tekrar → aynı cevap, LLM çağrılmıyor

---

### Task 15.5: LLM Call Logging — Coach Chat

**Tahmini Süre:** 1.5 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Coach chat LLM çağrılarını `data/logs/llm_calls.jsonl`'e kaydet:
  - [x] `provider`: "openrouter"
  - [x] `model`: "openai/gpt-4o-mini"
  - [x] `purpose`: "coach_chat" veya "coach_init_greeting"
  - [x] `prompt_tokens`: input token sayısı
  - [x] `completion_tokens`: output token sayısı
  - [x] `total_tokens`: toplam
  - [x] `duration_seconds`: istek süresi
  - [x] `success`: true/false
  - [x] `error`: hata mesajı (varsa)
  - [x] `snapshot_id`: ilgili snapshot ID
- [x] Mevcut LLM logging altyapısını kullan (logging_config.py)
- [x] Token count'u streaming sonrası hesapla

---

### Task 15.6: Error Handling & Edge Cases

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] **LLM API hataları:**
  - [x] Timeout handling (configurable timeout)
  - [x] Rate limit handling (429 from OpenRouter → retry veya user'a bilgi)
  - [x] Connection error handling
  - [x] Invalid response handling
- [x] **Edge case'ler:**
  - [x] Snapshot evidence_json null → Coach "Evidence bulunamadı" der
  - [x] Seçilen metrik için evidence yok → Coach bunu belirtir
  - [x] Çok uzun kullanıcı mesajı → truncate veya reject
  - [x] Boş mesaj (is_init: false) → 422 validation error
  - [x] Geçersiz snapshot_id → 404
  - [x] Concurrent mesajlar (aynı snapshot, farklı client_message_id) → sırayla işlenir
- [x] Error log'ları (ERROR seviyesi)
- [x] Test senaryoları yaz

---

### 📌 Week 15 — Kritik Teknik Notlar

**1. Coach-Initiated Opening — Otomatik Selamlama (AD-4):**
- `POST /api/snapshots/{id}/chat` endpoint'ine `is_init: true` flag'i gönderilir.
- Coach, seçilen metriklerdeki gap ve evidence verilerini analiz ederek açılış mesajı üretir.
- `client_message_id: "init_{snapshot_id}"` sabit kimlikle kaydedilir → idempotent (tekrar çağrılırsa aynı greeting döner).
- `chat_turn_count` **artmaz** (bonus mesaj, kullanıcının 15 hakkından düşmez).
- **Shared Turn ID İstisnası:** Init greeting'de sadece `role: assistant` mesajı var, eşleşen `role: user` yok.

**2. Snapshot CRUD Endpoint'leri:**
```
GET  /api/snapshots/                     → Tüm snapshot listesi (pagination, status filtre)
GET  /api/snapshots/{snapshot_id}        → Snapshot detayı (evidence dahil)
GET  /api/snapshots/{snapshot_id}/messages → Chat geçmişi (kronolojik sıra)
POST /api/snapshots/{snapshot_id}/chat   → Coach Chat (SSE streaming)
DELETE /api/snapshots/{snapshot_id}      → Soft delete (archived)
```
- Resource = snapshot, URL = `/api/snapshots/` (REST convention — `/api/evaluations/` değil).
- Tüm GET endpoint'lerinde `WHERE deleted_at IS NULL` filtresi zorunlu.

**3. Endpoint Akış Sırası (POST /chat):**
```
1. Snapshot var mı? (404)
2. Status == 'active'? (409 eğer archived)
3. is_init: true? → Init greeting akışı
4. Dedup kontrol (client_message_id) → Varsa mevcut cevap dön
5. Turn limit (atomik SQL) → 429 eğer dolmuş
6. User mesajı yaz → Assistant mesajı yaz → SSE streaming başlat
```

---

### ✅ Week 15 Checklist

- [x] POST /api/snapshots/{id}/chat çalışıyor (SSE)
- [x] GET /api/snapshots/{id}/messages çalışıyor
- [x] Init greeting (otomatik selamlama) çalışıyor
- [x] Snapshot CRUD endpoint'leri çalışıyor
- [x] Chat service unit testleri geçiyor
- [x] Chat integration testleri geçiyor
- [x] LLM call logging çalışıyor
- [x] Error handling ve edge case'ler çözüldü

---

## 📅 Week 16: End-to-End Testing & Polish

**Tarih:** 12 Mayıs - 18 Mayıs 2025  
**Hedef:** Full flow E2E testleri, manual test, documentation, cleanup

---

### Task 16.1: E2E Test — Evidence Flow

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/tests/test_e2e_phase3.py` oluştur:
  - [x] **Scenario 1: Evidence Generation + Snapshot:**
    1. POST /api/evaluations/start (soru üret)
    2. POST /api/evaluations/submit (değerlendirme gönder)
    3. GET /api/evaluations/{id}/feedback (judge feedback bekle)
    4. GET /api/snapshots/ (snapshot listesinde yeni kayıt var)
    5. GET /api/snapshots/{id} (evidence_json dolu)
    6. Assert: evidence doğrulanmış (`verified: true`)
    7. Assert: `highlight_available` alanları doğru
  - [x] **Scenario 2: Evidence Graceful Degradation:**
    1. Stage 1'den evidence parse hatası (mock)
    2. Snapshot yine oluşturulur (`evidence_json: null`)
    3. Chat yine çalışır (evidence referansı olmadan)

---

### Task 16.2: E2E Test — Chat Flow

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/tests/test_e2e_phase3.py` içine chat testleri ekle:
  - [x] **Scenario 3: Full Chat Flow:**
    1. Snapshot oluştur (Scenario 1'den devam veya fixture)
    2. POST /api/snapshots/{id}/chat (is_init: true) → Init greeting
    3. POST /api/snapshots/{id}/chat (message: "Neden Truthfulness'ta 3 verdin?") → SSE cevap
    4. POST /api/snapshots/{id}/chat (message: "Peki nasıl düzeltebilirim?") → SSE cevap
    5. GET /api/snapshots/{id}/messages → Tüm mesajlar (init + 2 user + 2 assistant)
    6. Assert: chat_turn_count == 2 (init sayılmıyor)
  - [x] **Scenario 4: Turn Limit:**
    1. 15 mesaj gönder
    2. 16. mesaj → 429 response
    3. GET /api/snapshots/{id} → chat_turn_count == 15
    4. Messages endpoint → 30+ mesaj dönüyor

---

### Task 16.3: E2E Test — Reconnect & Idempotency

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/tests/test_e2e_phase3.py` içine reconnect testleri ekle:
  - [x] **Scenario 5: Duplicate Message:**
    1. Mesaj gönder (client_message_id: "abc")
    2. Aynı mesajı tekrar gönder (client_message_id: "abc")
    3. Assert: Aynı cevap dönüyor, turn_count artmıyor
  - [x] **Scenario 6: Reconnect (yarım cevap):**
    1. Mesaj gönder, streaming yarıda kes (mock)
    2. Assert: DB'de `is_complete: false` kayıt var
    3. Aynı client_message_id ile retry
    4. Assert: Cevap baştan üretildi, `is_complete: true`
  - [x] **Scenario 7: Init Greeting Idempotency:**
    1. Init greeting gönder → cevap al
    2. Tekrar init greeting gönder → aynı cevap (DB'den)
    3. Assert: LLM sadece 1 kere çağrıldı

---

### Task 16.4: Manual Testing Session

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] CLI üzerinden full flow testi:
  1. [x] Soru üret (POST /evaluations/start)
  2. [x] Değerlendirme yap (POST /evaluations/submit)
  3. [x] Judge feedback bekle (GET /evaluations/{id}/feedback)
  4. [x] Snapshot kontrol et (GET /snapshots/)
  5. [x] Evidence kontrol et (GET /snapshots/{id})
  6. [x] Init greeting (POST /snapshots/{id}/chat, is_init: true)
  7. [x] Coach sohbeti (3-4 mesaj)
  8. [x] Messages kontrol et (GET /snapshots/{id}/messages)
- [x] Log'ları incele:
  - [x] `mentormind.log` — akış logları
  - [x] `errors.log` — hata yok mu?
  - [x] `llm_calls.jsonl` — coach_chat kayıtları
- [x] Bug'ları tespit et ve fix'le
- [x] Latency ölç (chat SSE ilk token süresi)

---

### Task 16.5: Documentation Update

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `CLAUDE.md` güncelle:
  - [x] Phase 3 status ekle (Week 11-16 checklist)
  - [x] Yeni tabloları database schema bölümüne ekle
  - [x] Yeni endpoint'leri API endpoints bölümüne ekle
  - [x] Coach Chat service açıklaması ekle
  - [x] Evidence service açıklaması ekle
  - [x] Project Structure güncelle (yeni dosyalar)
- [x] `README.md` güncelle:
  - [x] Coach Chat özelliği ekle
  - [x] Yeni API endpoint'leri listele
- [x] Inline code comments kontrol et

---

### Task 16.6: Bug Fixes & Final Verification

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Tespit edilen bug'ları fix'le
- [x] Dead code sil
- [x] Unused imports temizle
- [x] Code formatting (black)
- [x] Linting (flake8)
- [x] Type hints ekle (yeni fonksiyonlarda)
- [x] Tüm testleri çalıştır: `pytest`
- [x] Coverage kontrol et
- [x] Docker build test: `docker-compose build`
- [x] Docker run test: `docker-compose up -d`
- [x] Health check: All services healthy

---

### ✅ Week 16 Checklist

- [x] E2E Evidence flow testi geçiyor
- [x] E2E Chat flow testi geçiyor
- [x] E2E Reconnect & idempotency testi geçiyor
- [x] Manual test senaryoları başarılı
- [x] Documentation güncel (CLAUDE.md, README.md)
- [x] Code clean ve formatlanmış
- [x] Tüm testler geçiyor

---

## 🎯 Phase 3 Success Metrics

### Technical Metrics

- [x] **Test Coverage:** 80%+ (Phase 3 yeni kodlar)
- [x] **API Response Time:** < 200ms (non-LLM endpoints: snapshots, messages)
- [x] **Chat SSE First Token:** < 2 saniye (ilk kelime süresi)
- [x] **Evidence Verification:** > 90% doğrulama oranı (Aşama 1-3)
- [x] **Snapshot Creation:** < 500ms (atomik yazım)
- [x] **Docker Build:** < 5 dakika (mevcut süre korunuyor)

### Functional Metrics

- [x] **Evidence Generation:** Stage 1 evidence üretiyor (8 metrik)
- [x] **Self-Healing:** 5 aşamalı doğrulama çalışıyor
- [x] **Highlight Available:** Aşama 1-3 `true`, Aşama 4-5 `false`
- [x] **Snapshot CRUD:** Oluşturma, listeleme, detay, soft delete çalışıyor
- [x] **Coach Chat:** SSE streaming çalışıyor (GPT-4o-mini)
- [x] **Init Greeting:** Otomatik açılış mesajı idempotent
- [x] **Turn Limit:** 15 mesaj limiti atomik enforce ediliyor
- [x] **Idempotency:** Duplicate mesajlar engelleniyor
- [x] **Reconnect:** Yarım kalan cevaplar Update-In-Place ile çözülüyor
- [x] **Token Windowing:** Son 6 mesaj LLM'e gönderiliyor

### Quality Metrics

- [x] **Code Quality:** Linting errors yok (flake8)
- [x] **Code Format:** Black formatlanmış
- [x] **Type Hints:** Tüm yeni fonksiyonlarda mevcut
- [x] **Documentation:** CLAUDE.md + README.md güncel
- [x] **Logging:** Coach chat LLM çağrıları `llm_calls.jsonl`'de
- [x] **Error Handling:** Graceful degradation, proper HTTP status codes
- [x] **Architectural Decisions:** 13 AD tümüyle uygulanmış

---

## 🎉 Phase 3 Completion

**Phase 3 tamamlandığında elimizde şunlar olacak:**

✅ **Evidence Generation** (Stage 1 entegrasyonu)  
✅ **5-Stage Self-Healing Verification** (Exact → Substring → Anchor → Whitespace → Fallback)  
✅ **Evaluation Snapshots** (denormalize, atomik yazım)  
✅ **Snapshot CRUD API** (list, detail, soft delete)  
✅ **Coach Chat Service** (SSE streaming, GPT-4o-mini)  
✅ **Init Greeting** (otomatik açılış, idempotent)  
✅ **Turn Limit** (15 mesaj, atomik SQL)  
✅ **Idempotency & Reconnect** (Shared Turn ID, Update-In-Place)  
✅ **Token Windowing** (son 6 mesaj)  
✅ **Metric Slug System** (explicit mapping)  
✅ **Soft Delete Infrastructure** (retention policy hazır)  
✅ **Comprehensive Tests** (Unit + Integration + E2E)  

**Sonraki adım:** Phase 4 - Frontend: Evidence Highlight + Coach Chat UI 🚀

---

# Phase 4: Frontend Implementation (6 Weeks)

**Başlangıç:** 14 Şubat 2026  
**Bitiş:** 27 Mart 2026  
**Hedef:** Evidence highlight, metric cards, coach chat UI, SSE streaming

---

## Week 17: UI Foundation & Evaluation Screen (Feb 14 - Feb 20)

### Task 17.1: Project Setup & Tech Stack Decision

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (Daha önce tamamlanmış — Next.js 16 + React 19 + Tailwind CSS 4)

**Yapılacaklar:**
- [x] Frontend teknoloji seçimi → Next.js 16.1.6 + React 19.2.3 + TypeScript 5
- [x] `frontend/` dizini oluştur
- [x] `package.json` + dependencies:
  - [x] React 19 (Next.js 16 ile)
  - [x] TypeScript 5
  - [x] Next.js (build tool — Vite yerine)
  - [x] TailwindCSS 4 (styling)
  - [x] SWR (data fetching — React Query yerine)
  - [x] lucide-react (icons)
  - [x] recharts (charts)
- [x] ESLint setup (eslint-config-next)
- [x] `tsconfig.json` (strict mode)
- [x] `.env.local` (NEXT_PUBLIC_API_URL)

---

### Task 17.2: API Client & Type Definitions

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `lib/api.ts` - Fetch-based API client (base URL, error handling)
- [x] `types/index.ts` TypeScript type definitions:
  - [x] MetricSlug type (Phase 3 slug system)
  - [x] EvidenceItem, MetricEvidence, EvidenceByMetric
  - [x] SnapshotResponse, SnapshotListItem, SnapshotListResponse
  - [x] ChatMessage, ChatHistoryResponse, ChatRequest
- [x] Evaluation API functions (daha önce mevcut):
  - [x] `generateQuestion()`, `submitEvaluation()`, `getFeedback()`
- [x] Snapshot API functions (yeni eklendi):
  - [x] `listSnapshots(limit, offset, status)`
  - [x] `getSnapshot(snapshotId)`
  - [x] `deleteSnapshot(snapshotId)`
- [x] Chat API functions (yeni eklendi):
  - [x] `getChatHistory(snapshotId)`
  - [x] `initChatGreeting(snapshotId, selectedMetrics)` - SSE Response
  - [x] `sendChatMessage(snapshotId, message, clientMessageId, selectedMetrics)` - SSE Response

---

### Task 17.3: Metric Constants & Helpers

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `lib/constants.ts` - Slug-based metric constants:
  - [x] `METRIC_SLUGS` array
  - [x] `SLUG_TO_DISPLAY` mapping (slug → display name)
  - [x] `DISPLAY_TO_SLUG` mapping (display name → slug)
  - [x] `SLUG_COLORS` ve `SLUG_COLORS_LIGHT` (slug-based renk paleti)
  - [x] `GAP_COLORS` (0=green, 1=amber, 2+=red)
- [x] `types/index.ts` - `MetricSlug` type tanımı
- [x] Helper functions:
  - [x] `slugToDisplay(slug): string`
  - [x] `displayToSlug(name): MetricSlug`
  - [x] `isValidSlug(slug): boolean`
  - [x] `getGapColor(gap): string`

---

### Task 17.4: Evaluation Result Screen — Layout

**Tahmini Süre:** 4 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `app/snapshots/[id]/page.tsx` oluşturuldu (Snapshot Result Screen)
- [x] Layout: Meta Score + Overall Feedback + 8 Metric Card Grid (2x4) + Actions
- [x] Components:
  - [x] MetaScoreGauge (mevcut bileşen kullanıldı)
  - [x] OverallFeedback (inline section)
  - [x] SnapshotMetricCard grid (8 kart)
  - [x] ActionButtons (Sohbet Başlat + Yeni Değerlendirme)
  - [x] Improvement Areas + Good Metrics summary cards
  - [x] Collapsible Question & Model Answer section
- [x] `getSnapshot()` ile data fetch + loading/error states

---

### Task 17.5: Metric Card Component

**Tahmini Süre:** 5 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `components/snapshot/SnapshotMetricCard.tsx` oluşturuldu
- [x] Gap color coding (0=green, 1=amber, 2+=red) + gap icon
- [x] User/Judge score gösterimi (N/A desteği)
- [x] "Kanıt Gör" button (evidence count badge)
- [x] Slug-based color system (SLUG_COLORS_LIGHT)
- [x] `components/snapshot/index.ts` export

---

### Task 17.6: Evidence Modal — Basic Structure

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `components/evidence/EvidenceModal.tsx` oluşturuldu
- [x] 3 view modu: Birlikte (split), Sadece Metin, Sadece Liste
- [x] Metric header: Gap badge + User/Judge scores
- [x] Modal backdrop (click dışarı → close)
- [x] Escape key handling
- [x] Overflow scroll (uzun model cevapları)
- [x] Active index sync: evidence tıkla → highlight'a scroll

---

## Week 18: Evidence Highlight Implementation (Feb 21 - Feb 27)

### Task 18.1: Evidence Highlighter Component

**Tahmini Süre:** 6 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `components/evidence/EvidenceHighlighter.tsx` oluşturuldu
- [x] useMemo ile segment hesaplama (performans)
- [x] Algorithm: start'a göre sırala → overlap skip → `<mark>` tag
- [x] 5-stage verification desteği:
  - [x] `verified && highlight_available` → amber highlight + click handler
  - [x] `verified && !highlight_available` → sadece quote göster
  - [x] `!verified` → skip (EvidenceList'te uyarı gösterilir)
- [x] Active index desteği (tıklanan evidence ring ile vurgulanır)
- [x] Tooltip: title attribute ile `why` gösterimi

---

### Task 18.2: Evidence List Component

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `components/evidence/EvidenceList.tsx` oluşturuldu
- [x] Quote + Why + Better layout
- [x] VerificationBadge component:
  - [x] ✅ Doğrulandı (verified + highlight_available)
  - [x] ⚠️ Pozisyon tespit edilemedi (verified + !highlight_available)
  - [x] ❌ Kanıt doğrulanamadı (!verified)
- [x] Active index → border highlight
- [x] Empty state: "Bu metrik için kanıt bulunamadı"
- [x] Click → highlight sync

---

### Task 18.3: Evidence Modal Integration

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `EvidenceModal.tsx` içinde `<EvidenceHighlighter />` + `<EvidenceList />` entegrasyonu
- [x] `activeIndex` state: highlight ↔ list sync
- [x] 3 view modu (Birlikte, Metin, Liste)
- [x] Graceful degradation: empty evidence → fallback mesaj

---

### Task 18.4: Metric Card Evidence Button Integration

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `SnapshotMetricCard.tsx` "Kanıt Gör" button → parent callback
- [x] Snapshot Result Page'de local state ile modal yönetimi (Zustand gerekmedi)
- [x] `<EvidenceModal />` snapshot sayfasında render
- [x] Modal açılınca: snapshot'tan metric evidence + model answer çekilir

---

### Task 18.5: Evidence UI Testing

**Tahmini Süre:** 3 saat

**Durum:** ⏳ Bekliyor (Manuel test aşamasında)

**Yapılacaklar:**
- [ ] Evidence highlighter unit test
- [ ] Evidence modal integration test
- [ ] Manual browser testing

---

## Week 19: Coach Chat UI (Feb 28 - Mar 6)

### Task 19.1: Chat UI Layout & Components

**Tahmini Süre:** 5 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `app/snapshots/[id]/chat/page.tsx` oluşturuldu (CoachChatPage)
- [x] Full-height layout: Header + Message List + Input
- [x] Components:
  - [x] Chat header (geri butonu + seçili metrik badge'leri + rapor linki)
  - [x] Scrollable message list (auto-scroll bottom)
  - [x] `<MessageBubble />` - User (mavi, sağ) / Assistant (beyaz, sol)
  - [x] `<ChatInput />` - Textarea + send button + turn counter
  - [x] Turn counter: "Kalan mesaj: X/15"

---

### Task 19.2: Metric Selection Modal

**Tahmini Süre:** 4 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `components/chat/MetricSelectionModal.tsx` oluşturuldu
- [x] 8 metrik checkbox listesi (max 3 seçim)
- [x] Gap gösterimi (color coded badge)
- [x] "Kanıt" label (evidence olan metriklerde)
- [x] N/A metrikleri disabled
- [x] Seçim sayacı + "Sohbeti Başlat" butonu
- [x] Backdrop click close + validation

---

### Task 19.3: SSE Message Streaming

**Tahmini Süre:** 6 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `hooks/useChatStream.ts` custom hook oluşturuldu
- [x] ReadableStream ile SSE parse (fetch + reader)
- [x] `data: {content}` parse + accumulate
- [x] `data: [DONE]` → onComplete callback
- [x] Error handling (HTTP errors, stream errors, abort)
- [x] `sendInit()` — init greeting SSE
- [x] `sendMessage()` — normal chat SSE
- [x] State: `isStreaming`, `streamedContent`, `error`

---

### Task 19.4: Chat Message Components

**Tahmini Süre:** 4 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `components/chat/MessageBubble.tsx` oluşturuldu
- [x] User: Sağda, indigo-600 bubble (rounded-br-md)
- [x] Assistant: Solda, white bubble + border (rounded-bl-md)
- [x] Avatar icons (User / Bot)
- [x] Typing indicator: animated bounce dots
- [x] Streaming cursor: animated pulse bar
- [x] Timestamp gösterimi (tr-TR format)
- [x] Auto-scroll (messagesEndRef + scrollIntoView)

---

### Task 19.5: Chat Input & Turn Limit Handling

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `components/chat/ChatInput.tsx` oluşturuldu
- [x] Auto-resize textarea (Enter→send, Shift+Enter→newline)
- [x] Char limit: 500 (counter göster)
- [x] Turn counter: "Kalan mesaj: X/15"
- [x] Read-only mode (AD-9):
  - [x] Limit dolunca Lock icon + "Yeterince konuştuk" mesajı
  - [x] Input disable
  - [x] "Yeni bir soru çözmeye ne dersin?" yönlendirme

---

### Task 19.6: Init Greeting & Idempotency

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Chat page mount → metric selection modal → init greeting SSE
- [x] Init greeting: `POST /chat/init` (selected_metrics)
- [x] Existing chat restore: `getChatHistory()` ile mevcut mesajları yükle
- [x] Client message ID: `crypto.randomUUID()`, init için `init_{snapshotId}`
- [x] Optimistic UI: user mesajı hemen göster, sonra SSE stream

---

## Week 20: Integration & Testing (Mar 7 - Mar 13)

### Task 20.1: Navigation & Routing

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Next.js App Router ile routing (React Router gerekmedi):
  ```
  /                        → Dashboard
  /evaluate                → Evaluation workflow
  /feedback/[id]           → Judge feedback
  /snapshots               → Snapshot list (YENİ)
  /snapshots/[id]          → Snapshot detail + evidence (YENİ)
  /snapshots/[id]/chat     → Coach chat (YENİ)
  /history                 → Stats history
  ```
- [x] Sidebar güncellendi: "Snapshots" linki eklendi (BookOpen icon)
- [x] FeedbackPanel → "Snapshot Detaylarını Gör" butonu
- [x] WaitingForJudge → "Snapshots" butonu
- [x] Snapshot 404 handling + error states

---

### Task 20.2: Snapshot History List

**Tahmini Süre:** 4 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] `app/snapshots/page.tsx` oluşturuldu (SnapshotsPage)
- [x] `listSnapshots()` ile pagination (20 per page)
- [x] Önceki/Sonraki butonlu sayfalama
- [x] Snapshot card: primary_metric badge + yıldız + kategori + tarih
- [x] Card actions: [Detay] + [Sohbet]
- [x] Empty state: BookOpen icon + "Henüz Snapshot Yok" + CTA
- [x] 3-column responsive grid (1/2/3 cols)

---

### Task 20.3: Frontend E2E Tests

**Tahmini Süre:** 6 saat

**Durum:** ⏳ Bekliyor

**Yapılacaklar:**
- [ ] Playwright veya Cypress setup
- [ ] Test senaryoları:
  - [ ] **E2E 1: Full Evaluation Flow**
    1. Home → Start evaluation
    2. Submit evaluations (8 metrics)
    3. Wait for judge feedback (polling)
    4. Navigate to result screen
    5. Assert: 8 metric cards visible
    6. Click "Kanıt Gör" → modal açılıyor
  - [ ] **E2E 2: Evidence Highlight**
    1. Result screen → Click evidence button
    2. Modal açılıyor
    3. Highlight'lar görünüyor (yellow background)
    4. Hover → tooltip göster
    5. Evidence list item click → scroll to highlight
  - [ ] **E2E 3: Coach Chat Flow**
    1. Result screen → Click "Sohbet Başlat"
    2. Metric selection modal → select 2 metrics
    3. Init greeting görünüyor
    4. User mesajı gönder → SSE streaming
    5. Assistant cevabı render oluyor
    6. 2 mesaj daha gönder
    7. Turn counter: 3/15
  - [ ] **E2E 4: Turn Limit**
    1. 15 mesaj gönder
    2. Input disable oluyor
    3. "Yeterince konuştuk" mesajı
    4. [Yeni Değerlendirme] butonu

---

### Task 20.4: Error Handling & Loading States

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] API error handling:
  - [x] 404 → "Snapshot bulunamadı" / "Değerlendirme bulunamadı"
  - [x] 429 → "Mesaj limitine ulaşıldı" (useChatStream)
  - [x] Generic error → error state + retry button
- [x] Loading states:
  - [x] LoadingState component (mevcut) tüm sayfalarda
  - [x] Streaming indicator (typing dots + cursor bar)
- [x] ApiError class (lib/api.ts — mevcut)

---

### Task 20.5: Responsive Design & Mobile

**Tahmini Süre:** 4 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Metric cards grid: `grid-cols-2 md:grid-cols-4`
- [x] Snapshot list: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`
- [x] Evidence modal: `max-w-5xl` centered, `lg:grid-cols-2` split view
- [x] Chat: full-height layout `h-[calc(100vh-6rem)]`
- [x] Overall feedback grid: `grid-cols-1 lg:grid-cols-3`

---

### Task 20.6: Performance Optimization

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (13 Şubat 2026)

**Yapılacaklar:**
- [x] Next.js automatic code splitting (page-based)
- [x] `useMemo()` — EvidenceHighlighter segment calculation
- [x] `useCallback()` — Chat scroll, SSE stream handlers
- [x] `useRef()` — textarea auto-resize, messagesEndRef
- [x] Build test: `next build` — 0 error, tüm sayfalar derlendi

---

### Task 20.7: Documentation & Cleanup

**Tahmini Süre:** 3 saat

**Durum:** ⏳ Bekliyor

**Yapılacaklar:**
- [ ] `FRONTEND.md` oluştur:
  - Tech stack
  - Folder structure
  - Component hierarchy
  - API integration
  - Deployment guide
- [ ] Inline code comments (complex logic)
- [ ] Component prop documentation (TSDoc)
- [ ] `.env.example` update:
  ```
  VITE_API_BASE_URL=http://localhost:8000/api
  ```
- [ ] Dead code removal
- [ ] ESLint clean (0 errors)
- [ ] Prettier format

---

## Week 21: Docker & Deployment (Mar 14 - Mar 20)

### Task 21.1: Frontend Docker Setup

**Tahmini Süre:** 3 saat

**Durum:** ⏳ Bekliyor

**Yapılacaklar:**
- [ ] `frontend/Dockerfile` oluştur:
  ```dockerfile
  FROM node:20-alpine as build
  WORKDIR /app
  COPY package*.json ./
  RUN npm ci
  COPY . .
  RUN npm run build
  
  FROM nginx:alpine
  COPY --from=build /app/dist /usr/share/nginx/html
  COPY nginx.conf /etc/nginx/nginx.conf
  EXPOSE 80
  CMD ["nginx", "-g", "daemon off;"]
  ```
- [ ] `frontend/nginx.conf` oluştur:
  - SPA routing (try_files)
  - CORS headers (API proxy optional)
  - Gzip compression
- [ ] `docker-compose.yml` update:
  ```yaml
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000/api
    depends_on:
      - backend
  ```

---

### Task 21.2: Production Build & Testing

**Tahmini Süre:** 2 saat

**Durum:** ⏳ Bekliyor

**Yapılacaklar:**
- [ ] Production build test:
  ```bash
  npm run build
  npm run preview
  ```
- [ ] Bundle size analiz:
  - `vite-plugin-bundle-analyzer`
  - Target: < 500KB gzipped
- [ ] Docker build test:
  ```bash
  docker-compose build frontend
  docker-compose up frontend
  ```
- [ ] Health check: http://localhost:3000
- [ ] API connectivity test (backend integration)

---

### Task 21.3: CI/CD Pipeline (Optional)

**Tahmini Süre:** 3 saat

**Durum:** ⏳ Bekliyor

**Yapılacaklar:**
- [ ] GitHub Actions workflow: `.github/workflows/frontend-ci.yml`
- [ ] Steps:
  1. Checkout code
  2. Setup Node.js 20
  3. Install dependencies
  4. Run ESLint
  5. Run TypeScript check
  6. Run unit tests (Vitest)
  7. Build production bundle
  8. Upload artifacts
- [ ] Badge'ler ekle (README.md):
  - Build status
  - Test coverage
  - Bundle size

---

### Task 21.4: Manual Integration Testing

**Tahmini Süre:** 4 saat

**Durum:** ⏳ Bekliyor

**Yapılacaklar:**
- [ ] Full stack test (backend + frontend):
  1. Docker compose up
  2. Seed data (POST /evaluations/start)
  3. Frontend'den evaluation submit
  4. Judge feedback bekle
  5. Evidence modal kontrol
  6. Chat başlat
  7. 5 mesaj sohbet et
  8. History sayfası kontrol
- [ ] Bug triage:
  - Log'ları incele (browser console + backend logs)
  - Network tab (API calls)
  - Performance profiling
- [ ] Fix critical bugs
- [ ] Regression testing

---

### Task 21.5: Final Documentation Update

**Tahmini Süre:** 2 saat

**Durum:** ⏳ Bekliyor

**Yapılacaklar:**
- [ ] `README.md` update:
  - Frontend setup instructions
  - Docker compose startup
  - Environment variables
  - Deployment guide
- [ ] `CLAUDE.md` update:
  - Phase 4 completion status
  - Frontend architecture
  - Component hierarchy diagram
  - API integration notes
- [ ] `ROADMAP.md` update:
  - Phase 4 tasks [x] işaretle
  - Phase 5 placeholder (future features)
- [ ] Screenshots:
  - Evaluation result screen
  - Evidence modal
  - Coach chat screen
  - Snapshot history

---

## ✅ Phase 4 Success Metrics

### Technical Metrics

- [ ] **Lighthouse Score:** Performance > 90, Accessibility > 90
- [ ] **Bundle Size:** < 500KB gzipped
- [ ] **API Response Time:** Snapshot fetch < 200ms
- [ ] **SSE First Token:** < 2 saniye (chat streaming)
- [ ] **Test Coverage:** 70%+ (frontend components)

### Functional Metrics

- [x] **Evidence Highlight:** 5-stage verification sonuçları doğru render
- [x] **Metric Cards:** 8 metrik, gap color coding, evidence button
- [x] **Evidence Modal:** Highlight + tooltip + evidence list (3 view modu)
- [x] **Coach Chat:** SSE streaming, init greeting, turn limit
- [x] **Idempotency:** client_message_id ile backend tarafında sağlanıyor
- [x] **Reconnect:** Mevcut chat history restore (getChatHistory)
- [x] **Responsive:** Mobile, tablet, desktop Tailwind breakpoints

### Quality Metrics

- [x] **TypeScript:** 0 type errors (`next build` başarılı)
- [ ] **ESLint:** 0 errors, < 10 warnings
- [ ] **Prettier:** Tüm dosyalar formatlanmış
- [ ] **Accessibility:** WCAG 2.1 AA (keyboard nav, screen reader)
- [ ] **Browser Support:** Chrome, Firefox, Safari, Edge

---

## 🎯 Phase 4 Completion

**Phase 4 tamamlandığında elimizde şunlar olacak:**

✅ **8 Metric Card UI** (gap gösterimi, evidence preview)  
✅ **Evidence Modal** (highlight + tooltip + evidence list)  
✅ **Evidence Highlighter** (5-stage verification support)  
✅ **Metric Selection Modal** (1-3 metrik seçimi)  
✅ **Coach Chat UI** (SSE streaming, message history)  
✅ **Init Greeting** (otomatik açılış, idempotent)  
✅ **Turn Limit UI** (read-only mode, yönlendirme)  
✅ **Snapshot History** (list + pagination)  
✅ **Responsive Design** (mobile, tablet, desktop)  
✅ **E2E Tests** (Playwright/Cypress)  
✅ **Docker Setup** (frontend container + nginx)  

**Sonraki adım:** Phase 5 - Advanced Features (Analytics, Admin Panel, etc.) 🚀

---

**Başarılar!** 💪
