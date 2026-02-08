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

**Sonraki adım:** Phase 3 - Coach Chat + Evidence (Backend) 🚀

---

## 📅 Phase 3: Coach Chat + Evidence — Backend (6 Weeks)

**Tarih:** 7 Nisan - 18 Mayıs 2025  
**Hedef:** Evidence (Kanıt) üretimi, 5 aşamalı doğrulama, Snapshot sistemi ve Coach Chat (SSE) backend altyapısı  
**Referans Döküman:** [NEW_FEATURES.md](NEW_FEATURES.md) (13 Architectural Decision)

---

## 🎯 Phase 3 Overview

### Scope

**Dahil:**
- Evidence üretimi (Stage 1 entegrasyonu)
- 5 aşamalı Self-Healing Evidence doğrulama algoritması
- `evaluation_snapshots` tablosu (denormalize snapshot)
- `chat_messages` tablosu (sohbet geçmişi)
- Snapshot CRUD servisi ve endpoint'leri
- Coach Chat servisi (SSE streaming, GPT-4o-mini)
- Idempotency, Reconnect, Turn Limit altyapısı
- Metric slug mapping sistemi
- Soft delete altyapısı

**Hariç:**
- Frontend UI (Evidence highlight, Chat UI — ayrı phase)
- Multi-user authentication
- Production deployment
- Advanced analytics dashboard

### Definition of Done

Phase 3 tamamlanmış sayılır eğer:
- [ ] `evaluation_snapshots` ve `chat_messages` tabloları oluşturuldu
- [ ] Stage 1 prompt'u evidence çıktısı üretiyor
- [ ] 5 aşamalı self-healing doğrulama çalışıyor
- [ ] Judge task sonrası otomatik snapshot oluşturuluyor
- [ ] Snapshot CRUD endpoint'leri çalışıyor
- [ ] Coach Chat SSE streaming çalışıyor
- [ ] Init greeting çalışıyor
- [ ] Turn limit (15 user mesaj) enforce ediliyor
- [ ] Idempotency ve reconnect çalışıyor
- [ ] Token windowing (son 6 mesaj) uygulanıyor
- [ ] E2E testler geçiyor
- [ ] Documentation güncel

---

## 📅 Week 11: Database Schema & Infrastructure

**Tarih:** 7 Nisan - 13 Nisan 2025  
**Hedef:** Yeni tablolar, modeller, şemalar ve konfigürasyon

---

### Task 11.1: Metric Slug Constants & Helpers

**Tahmini Süre:** 1 saat

**Durum:** ✅ **TAMAMLANDI** (8 Şubat 2026)

**Referans:** AD-6 (Slug-Based Metric Keys)

**Yapılanlar:**
- [x] `backend/constants/` klasörü oluştur
- [x] `backend/constants/__init__.py` oluştur
- [x] `backend/constants/metrics.py` oluştur:
  - [x] `METRIC_SLUG_MAP` dictionary (8 metrik: "Truthfulness" → "truthfulness", ...)
  - [x] `SLUG_DISPLAY_MAP` reverse dictionary (otomatik oluştur)
  - [x] `display_name_to_slug(name: str) -> str` helper fonksiyonu
  - [x] `slug_to_display_name(slug: str) -> str` helper fonksiyonu
  - [x] `ALL_METRIC_SLUGS: list[str]` constant
  - [x] `ALL_METRIC_NAMES: list[str]` constant
- [x] Bilinmeyen metrik adı/slug için `ValueError` raise et
- [x] Unit test yaz (test_metrics.py) - **21 test passed, 100% coverage**

**Notlar:**
- Otomatik `lower()` kullanılmaz, explicit dictionary ile mapping yapılır
- Mevcut tablolara dokunulmaz, sadece yeni snapshot tablosu slug kullanır
- İleride "Safety & Policy" gibi karmaşık isimler gelirse kod kırılmaz

---

### Task 11.2: SQL Schema - evaluation_snapshots

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (8 Şubat 2026)

**Referans:** AD-3 (New Snapshot Table), AD-13 (Retention Policy)

**Yapılanlar:**
- [x] `backend/schemas/00_enums.sql` güncellendi:
  - [x] `snapshot_status` ENUM eklendi (active, completed, archived)
- [x] `backend/schemas/08_evaluation_snapshots.sql` oluşturuldu:
  - [x] `id` TEXT PRIMARY KEY (Format: `snap_YYYYMMDD_HHMMSS_randomhex`)
  - [x] `created_at` TIMESTAMP DEFAULT NOW()
  - [x] `question_id` TEXT (referans, FK değil)
  - [x] `question` TEXT NOT NULL (snapshot)
  - [x] `model_answer` TEXT NOT NULL (snapshot)
  - [x] `model_name` TEXT NOT NULL
  - [x] `judge_model` TEXT NOT NULL DEFAULT 'gpt-4o'
  - [x] `primary_metric` TEXT NOT NULL (slug format: truthfulness, helpfulness, etc.)
  - [x] `bonus_metrics` JSONB
  - [x] `category` TEXT
  - [x] `user_scores_json` JSONB NOT NULL (nested structure)
  - [x] `judge_scores_json` JSONB NOT NULL (nested structure)
  - [x] `evidence_json` JSONB
  - [x] `judge_meta_score` INTEGER CHECK (1-5)
  - [x] `weighted_gap` REAL
  - [x] `overall_feedback` TEXT
  - [x] `user_evaluation_id` TEXT (referans)
  - [x] `judge_evaluation_id` TEXT (referans)
  - [x] `chat_turn_count` INTEGER DEFAULT 0
  - [x] `max_chat_turns` INTEGER DEFAULT 15
  - [x] `status snapshot_status` DEFAULT 'active'
  - [x] `deleted_at` TIMESTAMP (nullable, soft delete altyapısı)
- [x] Index'ler oluşturuldu:
  - [x] `idx_snapshots_status` (status)
  - [x] `idx_snapshots_primary_metric` (primary_metric)
  - [x] `idx_snapshots_created_at` (created_at DESC)
  - [x] `idx_snapshots_deleted_at` (deleted_at) — soft delete sorguları için
  - [x] `idx_snapshots_active_metric` (partial index, active snapshots için)
- [x] SQL dosyası Docker container'da çalıştırıldı
- [x] Test insert başarılı (nested JSONB doğrulandı)

---

### Task 11.3: SQL Schema - chat_messages

**Tahmini Süre:** 1.5 saat

**Durum:** ✅ **TAMAMLANDI** (8 Şubat 2026)

**Referans:** AD-3 (New Snapshot Table), AD-4 (SSE + DB Chat)

**Yapılacaklar:**
- [x] `backend/schemas/09_chat_messages.sql` oluştur:
  - [x] `id` TEXT PRIMARY KEY (Format: `msg_YYYYMMDD_HHMMSS_randomhex`)
  - [x] `client_message_id` TEXT NOT NULL (Shared Turn ID)
  - [x] `is_complete` BOOLEAN NOT NULL DEFAULT TRUE
  - [x] `snapshot_id` TEXT NOT NULL REFERENCES evaluation_snapshots(id)
  - [x] `role` TEXT NOT NULL CHECK (role IN ('user', 'assistant'))
  - [x] `content` TEXT NOT NULL DEFAULT ''
  - [x] `selected_metrics` JSONB
  - [x] `token_count` INTEGER DEFAULT 0
  - [x] `created_at` TIMESTAMP DEFAULT NOW()
- [x] Constraint'ler:
  - [x] `UNIQUE (snapshot_id, client_message_id, role)` — idempotency garantisi
- [x] Index'ler:
  - [x] `idx_chat_snapshot_created` (snapshot_id, created_at) — sohbet geçmişi sorguları
  - [x] `idx_chat_client_message` (snapshot_id, client_message_id) — dedup lookup
- [x] SQL dosyasını Docker container'da çalıştır

---

### Task 11.4: SQLAlchemy Models

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (8 Şubat 2026)

**Referans:** AD-3

**Yapılacaklar:**
- [x] `backend/models/evaluation_snapshot.py` oluştur:
  - [x] `EvaluationSnapshot` SQLAlchemy model
  - [x] Tüm kolonlar (Task 11.2'deki şemaya uygun)
  - [x] `__tablename__ = "evaluation_snapshots"`
  - [x] `snapshot_status` ENUM referenced correctly (create_type=False)
  - [x] `is_chat_available` property (status == 'active' ve chat_turn_count < max_chat_turns)
  - [x] No relationships (following existing pattern to avoid circular imports)
- [x] `backend/models/chat_message.py` oluştur:
  - [x] `ChatMessage` SQLAlchemy model
  - [x] Tüm kolonlar (Task 11.3'deki şemaya uygun)
  - [x] `__tablename__ = "chat_messages"`
  - [x] `is_user_message` ve `is_assistant_message` property'leri
  - [x] No relationships (following existing pattern)
- [x] `backend/models/__init__.py` güncelle:
  - [x] `EvaluationSnapshot` export ekle
  - [x] `ChatMessage` export ekle
- [x] Modellerin database ile senkronize olduğunu test et:
  - [x] 23 columns for EvaluationSnapshot
  - [x] 9 columns for ChatMessage
  - [x] All properties working correctly

---

### Task 11.5: Pydantic Schemas

**Tahmini Süre:** 2.5 saat

**Durum:** ✅ **TAMAMLANDI** (8 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/models/schemas.py` güncelle:
  - [x] **Evidence Schemas:**
    - [x] `EvidenceItem` (start, end, quote, why, better, verified, highlight_available)
    - [x] `MetricEvidence` (user_score, judge_score, metric_gap, user_reason, judge_reason, evidence: list[EvidenceItem])
    - [x] `EvidenceByMetric` (evidence_by_metric: dict[str, list[EvidenceItem]])
  - [x] **Snapshot Schemas:**
    - [x] `SnapshotBase` (question, model_answer, model_name, judge_model, primary_metric, bonus_metrics, category)
    - [x] `SnapshotResponse` (tüm snapshot alanları + is_chat_available)
    - [x] `SnapshotListItem` (id, created_at, primary_metric, category, judge_meta_score, status, chat_turn_count)
    - [x] `SnapshotListResponse` (items, total, page, per_page)
  - [x] **Chat Schemas:**
    - [x] `ChatMessageBase` (role, content)
    - [x] `ChatMessageCreate` (snapshot_id, client_message_id, selected_metrics)
    - [x] `ChatMessageResponse` (id, role, content, created_at, is_complete, selected_metrics, token_count)
    - [x] `ChatRequest` (message, client_message_id, selected_metrics, is_init)
    - [x] `ChatHistoryResponse` (messages, total, snapshot_id, is_chat_available, turns_remaining)
  - [x] **Validation kuralları:**
    - [x] `validate_metric_slugs` → max 3 item, valid slug check
    - [x] `validate_client_message_id` → non-empty string
    - [x] `validate_chat_role` → user or assistant only
  - [x] **Constants:**
    - [x] `VALID_SNAPSHOT_STATUSES = ["active", "completed", "archived"]`
    - [x] `VALID_CHAT_ROLES = ["user", "assistant"]`
  - [x] `from_attributes = True` on all response schemas
  - [x] Import `ALL_METRIC_SLUGS` and `is_valid_slug` from `backend.constants.metrics`

---

### Task 11.6: Settings Update

**Tahmini Süre:** 1 saat

**Durum:** ✅ **TAMAMLANDI** (8 Şubat 2026)

**Referans:** AD-5 (Coach Model), AD-9 (Turn Limit)

**Yapılacaklar:**
- [x] `backend/config/settings.py` güncelle:
  - [x] `coach_model: str = "openai/gpt-4o-mini"` (OpenRouter üzerinden)
  - [x] `max_chat_turns: int = 15` (kullanıcı mesaj limiti)
  - [x] `chat_history_window: int = 6` (LLM'e gönderilen son mesaj sayısı)
  - [x] `evidence_anchor_len: int = 25` (anchor karakter uzunluğu)
  - [x] `evidence_search_window: int = 2000` (anchor search tolerans penceresi)
  - [x] `validate_positive_int()` validator eklendi
- [x] `.env.example` güncelle (yeni config'ler)
- [x] Config'lerin environment variable'dan override edilebilirliğini test et

---

### Task 11.7: Schema Validation & Test Coverage

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (8 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/models/schemas.py` - EvidenceItem validation:
  - [x] `@model_validator(mode='after')` ile `end > start` kontrolü
  - [x] Geçersiz range'leri engelle (end <= start)
- [x] `backend/models/schemas.py` - UUID v4 validation:
  - [x] `validate_client_message_id()` fonksiyonunu UUID v4 strict validation ile güncelle
  - [x] Sadece geçerli UUID v4 formatı kabul et
  - [x] XSS payload'larını reddet (`<script>`, SQL injection, vs.)
  - [x] Diğer UUID versiyonlarını reddet (v1, v3, v5)
- [x] `backend/tests/test_phase3_schemas.py` oluştur:
  - [x] `TestEvidenceItem` - 8 test (position validation, edge cases)
  - [x] `TestChatMessageCreate` - 13 test (UUID v4, XSS protection)
  - [x] `TestChatRequest` - 8 test (UUID v4, metric limits)
  - [x] `TestSnapshotResponse` - 1 test (ORM config)
  - [x] `TestMetricEvidence` - 2 test (evidence structure)
- [x] Tüm testler geçti (32/32)
- [x] Coverage: `backend/models/schemas.py` = 94%

---

### 📌 Week 11 — Kritik Teknik Notlar

**1. evaluation_snapshots Tablosu (AD-3):**
- Mevcut 4 tabloya (questions, model_responses, user_evaluations, judge_evaluations) dokunulmaz.
- Snapshot, tüm aktörlerin (kullanıcı, judge, model) verisini **denormalize** ederek tek satırda tutar.
- Soft delete altyapısı (`deleted_at`, `status: archived`) baştan yerleştirilir (AD-13).

**2. chat_messages Tablosu (AD-3, AD-4):**
- **Shared Turn ID modeli:** Aynı konuşma turundaki user ve assistant mesajları aynı `client_message_id`'yi paylaşır.
- **Deduplication Constraint:** `UNIQUE(snapshot_id, client_message_id, role)` — DB seviyesinde mükerrerlik engeli. Bu constraint olmadan idempotency garantisi verilemez.
- `is_complete` alanı SSE reconnect stratejisinin temelini oluşturur (yarım kalan cevapları tespit).

**3. Tablo İlişkisi:**
```
evaluation_snapshots (1) ──→ (N) chat_messages
                              │
                              ├─ role: "user"      (client_message_id: "abc")
                              └─ role: "assistant"  (client_message_id: "abc")
```

---

### ✅ Week 11 Checklist

- [x] Metric slug mapping çalışıyor
- [x] `evaluation_snapshots` tablosu oluşturuldu
- [x] `chat_messages` tablosu oluşturuldu
- [x] `UNIQUE(snapshot_id, client_message_id, role)` constraint aktif
- [x] SQLAlchemy modelleri hazır
- [x] Pydantic şemaları hazır
- [x] Yeni config değerleri ayarlandı
- [x] Schema validation güçlendirmeleri (EvidenceItem, UUID v4)
- [x] Phase 3 test coverage (32 tests, 94% coverage)

---

## 📅 Week 12: Evidence Generation & Verification

**Tarih:** 14 Nisan - 20 Nisan 2025  
**Hedef:** Stage 1 evidence çıktısı, 5 aşamalı self-healing doğrulama

---

### Task 12.1: Stage 1 Prompt Update — Evidence Output

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (8 Şubat 2026)

**Referans:** AD-1 (Evidence Generation in Stage 1)

**Yapılanlar:**
- [x] `backend/prompts/judge_prompts.py` güncellendi:
  - [x] Stage 1 system prompt'una "Evidence Collection" bölümü eklendi
  - [x] Evidence formatı tanımlandı (5 zorunlu alan): `quote`, `start`, `end`, `why`, `better`
  - [x] `start`/`end` karakter pozisyonları (0-based, Python slice style) açıklandı
  - [x] Verbatim (birebir) alıntı kuralı vurgulandı
  - [x] Score null olan metrikler için `[]` (boş array) kuralı eklendi
  - [x] Few-shot örneği güncellendi (evidence içeren)
- [x] Stage 1 output JSON örneği güncellendi (scores + evidence)
- [x] Stage 1 user prompt template güncellendi (evidence example)
- [x] Prompt token sayısı kontrol edildi: ~2111 tokens (< 4000 hedefi)
- [x] `backend/services/judge_service.py` `_validate_judge_response()` güncellendi:
  - [x] Evidence alanı validasyonu eklendi
  - [x] 5 zorunlu alan kontrolü
  - [x] `start < end` validasyonu
  - [x] Graceful error handling (boş array'a düşürme)
- [x] `backend/tests/test_evidence_validation.py` oluşturuldu (17 test, tümü geçti)

**Test Sonuçları:**
- 17/17 tests passed
- Evidence validation logic çalışıyor
- Prompt içerdiği doğrulandı

**Notlar:**
- Mevcut Stage 1 akışı bozulmadı — evidence "ek çıktı" olarak eklendi
- Metric key formatı: Display Name (örn. "Truthfulness") — slug dönüşümü Task 12.2'de

---

### Task 12.2: Evidence JSON Parser

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (8 Şubat 2026)

**Referans:** AD-6 (Slug-Based Metric Keys)

**Yapılanlar:**
- [x] `backend/services/evidence_service.py` oluşturuldu:
  - [x] `parse_evidence_from_stage1(stage1_response: dict) -> dict` fonksiyonu:
    - [x] Stage 1 JSON çıktısından evidence bölümünü ayıkla
    - [x] Display name key'lerini slug key'lere dönüştür (örn. "Truthfulness" → "truthfulness")
    - [x] Her metrik için evidence listesini validate et
    - [x] `quote`, `start`, `end`, `why`, `better` alanlarını kontrol et
  - [x] `_validate_evidence_list(evidence_list: list, metric_name: str) -> list` fonksiyonu:
    - [x] Liste tipi validasyonu
    - [x] `start < end` kontrolü ve correction (0, 0)
    - [x] Invalid item'leri filtrele
  - [x] `_is_valid_evidence_item(item: dict) -> bool` fonksiyonu:
    - [x] 5 zorunlu alan kontrolü (quote, start, end, why, better)
    - [x] Tip kontrolü (quote/why/better: str, start/end: int)
    - [x] Boş quote kontrolü
  - [x] `convert_to_evidence_by_metric(stage1_response: dict) -> dict[str, list[EvidenceItem]]` fonksiyonu:
    - [x] Pydantic `EvidenceItem` model'lerine dönüşüm
    - [x] `verified=False`, `highlight_available=True` explicit set
- [x] `backend/services/judge_service.py` entegrasyonu:
  - [x] `parse_judge_response()` method'unda evidence parser çağrısı
  - [x] Graceful degradation (hata durumunda devam et)
- [x] `backend/services/__init__.py` export'ları eklendi
- [x] Unit test yaz (`backend/tests/test_evidence_service.py`):
  - [x] 25 test oluşturuldu
  - [x] Tüm testler geçti
- [x] `backend/tests/test_judge_service.py` güncellendi:
  - [x] `test_parse_direct_json` display name preservation ile güncellendi
- [x] **Display name preservation fix (9 Şubat 2026):**
  - [x] `parse_evidence_from_stage1()` artık display names koruyor
  - [x] `convert_to_evidence_by_metric()` slug conversion yapıyor (Phase 3 için)
  - [x] Backward compatibility sağlandı (mevcut testler korundu)
  - [x] Invalid metric filtreleme eklendi

**Test Sonuçları:**
- 25/25 evidence service tests passed
- 38/38 judge service tests passed (including live API)
- Display name preservation works correctly

**Notlar:**
- Display names `parse_evidence_from_stage1()` sonunda korunur (backward compatibility)
- Slug conversion sadece `convert_to_evidence_by_metric()`'de yapılır (Phase 3 Coach Chat)
- Invalid metric'ler skip ediliyor, log yazılıyor

---

### Task 12.3: Self-Healing Verification Algorithm

**Tahmini Süre:** 4 saat

**Durum:** ✅ **TAMAMLANDI** (9 Şubat 2026)

**Referans:** AD-2 (5-Stage Self-Healing Verification)

**Yapılacaklar:**
- [x] `backend/services/evidence_service.py` içine doğrulama fonksiyonları ekle:
  - [x] **Aşama 1 — Exact Slice:**
    - [x] `_verify_exact_slice(model_answer: str, quote: str, start: int, end: int) -> bool`
    - [x] `model_answer[start:end] == quote` kontrolü
  - [x] **Aşama 2 — Substring Search:**
    - [x] `_verify_substring_search(model_answer: str, quote: str) -> tuple[bool, int, int]`
    - [x] `model_answer.find(quote)` ile tam alıntı araması
    - [x] Bulunursa yeni `start`/`end` dön
  - [x] **Aşama 3 — Anchor-Based Search:**
    - [x] `_verify_anchor_based(model_answer: str, quote: str, anchor_len: int, search_window: int) -> tuple[bool, int, int]`
    - [x] `head_anchor = quote[:anchor_len]`, `tail_anchor = quote[-anchor_len:]`
    - [x] Head bulunursa, `head_idx + len(quote) + search_window` penceresi içinde tail ara
    - [x] Her iki anchor bulunursa `start=head_idx`, `end=tail_idx+len(tail_anchor)` dön
  - [x] **Aşama 4 — Whitespace-Insensitive Match (Safe Mode):**
    - [x] `_verify_whitespace_safe(model_answer: str, quote: str) -> bool`
    - [x] `normalize()` fonksiyonu: fazla boşluk/newline temizle
    - [x] Normalize edilmiş metinde ara
    - [x] Bulunursa `verified: true` ama `start`/`end` **güncellenmez**
    - [x] `highlight_available: false` set edilir
  - [x] **Aşama 5 — Fallback:**
    - [x] Hiçbir aşamada bulunamazsa → `verified: false`, `highlight_available: false`
- [x] **Orchestrator fonksiyonu:**
  - [x] `verify_evidence_item(model_answer: str, evidence_item: dict) -> dict`
  - [x] 5 aşamayı sırayla çalıştır, ilk başarıda dur
  - [x] `verified`, `highlight_available`, güncel `start`/`end` dön
- [x] `verify_all_evidence(model_answer: str, evidence_list: list) -> list` fonksiyonu eklendi

**Notlar:**
- `verify_evidence_item` ve `verify_all_evidence` fonksiyonları `evidence_service.py`'e eklendi
- Her aşama başarılı olursa ilgili `verified`, `highlight_available` ve pozisyonlar dönülür
- Aşama 4 (whitespace safe mode) için `highlight_available: false` set ediliyor

---

### Task 12.4: Evidence Service — Orchestration

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI** (9 Şubat 2026)

**Referans:** AD-2, AD-8 (Graceful Degradation)

**Yapılacaklar:**
- [x] `process_evidence(model_answer: str, raw_evidence: dict) -> dict` fonksiyonu:
  - [x] Her metrik için evidence listesini dolaş
  - [x] Her evidence item'a `verify_evidence()` uygula
  - [x] `verified` ve `highlight_available` alanlarını set et
  - [x] Başarılı/başarısız doğrulama istatistiklerini logla
- [x] Graceful degradation (AD-8):
  - [x] Parse hatası → `evidence_json = null`, pipeline devam eder
  - [x] WARNING log: `"Evidence parse failed for eval {id}, continuing without evidence"`
  - [x] Tek bir evidence item hatası diğerlerini etkilemez
- [x] `highlight_available` hesaplama mantığı:
  - [x] Aşama 1-3'te `true` (indeksler doğru/düzeltildi)
  - [x] Aşama 4'te `false` (indeksler güncellenmedi, safe mode)
  - [x] Aşama 5'te `false` (doğrulanamadı)
- [x] judge_service.py entegrasyonu (process_evidence kullanımı)
- [x] Unit testler (18 test)

---

### Task 12.5: Evidence Unit Tests

**Tahmini Süre:** 3 saat

**Durum:** ✅ **TAMAMLANDI** (9 Şubat 2026)

**Yapılacaklar:**
- [x] `backend/tests/test_evidence_service.py` oluştur:
  - [x] **Aşama 1 testleri:**
    - [x] Exact match başarılı
    - [x] Exact match başarısız (yanlış indeks)
  - [x] **Aşama 2 testleri:**
    - [x] Substring bulundu, indeksler düzeltildi
    - [x] Substring bulunamadı
  - [x] **Aşama 3 testleri:**
    - [x] Anchor bulundu (head + tail), indeksler düzeltildi
    - [x] Sadece head bulundu, tail bulunamadı
    - [x] Search window dışında tail (false positive koruması)
  - [x] **Aşama 4 testleri:**
    - [x] Whitespace farkı ile bulundu, `highlight_available: false`
    - [x] Normalize sonrası da bulunamadı
  - [x] **Aşama 5 testleri:**
    - [x] Hiçbir aşamada bulunamadı, `verified: false`
  - [x] **Orchestration testleri:**
    - [x] Tam akış (happy path)
    - [x] Graceful degradation (hatalı JSON)
    - [x] Boş evidence listesi
    - [x] Null score metrikler için boş evidence
  - [x] **Edge case'ler:**
    - [x] Çok kısa quote (< 25 karakter, anchor mümkün değil)
    - [x] Çok uzun model_answer (performance)
    - [x] Unicode karakterler
    - [x] Boş model_answer

---

### Task 12.6: Judge Service Integration — Evidence

**Tahmini Süre:** 2 saat

**Durum:** ✅ **TAMAMLANDI (9 Şubat 2026)**

**Referans:** AD-1 (Evidence Integration Test Coverage)

**Yapılacaklar:**
- [x] `backend/services/judge_service.py` güncelle:
  - [x] `stage1_independent_evaluation()` return değerine `evidence` ekle
  - [x] Stage 1 response parse'ını güncelle (scores + evidence)
  - [x] `parse_stage1_response()` fonksiyonuna evidence extraction ekle
  - [x] Evidence yoksa boş dict dön (graceful)
- [x] `_validate_stage1_response()` güncelle:
  - [x] Evidence alanının varlığını kontrol et (opsiyonel)
- [x] Evidence parse hatası Stage 1'i kırmaz (AD-8)
- [x] Test güncelle (mevcut testlere evidence assertion ekle)

---

### 📌 Week 12 — Kritik Teknik Notlar

**1. Stage 1 Prompt Güncellemesi (AD-1):**
- Mevcut Stage 1 akışı (skor + rationale) korunur, evidence **ek çıktı** olarak eklenir.
- Judge'a "model_answer'dan verbatim alıntı yap, start/end karakter indeksleri ver" talimatı verilir.
- Evidence yoksa (score: null) boş array `[]` kabul edilir — pipeline kırılmaz.

**2. 5 Aşamalı Self-Healing Doğrulama (AD-2):**
```
Aşama 1: Exact Slice    → model_answer[start:end] == quote?
Aşama 2: Substring       → model_answer.find(quote) >= 0?
Aşama 3: Anchor Search   → head(25ch) + tail(25ch) + search_window(+2000ch)
Aşama 4: Whitespace Safe → normalize() sonrası ara, indeks GÜNCELLENMEZ
Aşama 5: Fallback        → verified: false
```
- Aşamalar **en güvenilirden en düşüğe** sıralıdır. Çoğu case Aşama 1-2'de çözülür.
- Anchor search'te `search_window` ile false positive koruması sağlanır.

**3. `highlight_available` Flag Mantığı:**

| Doğrulama Aşaması | `verified` | `highlight_available` | UI Davranışı |
|---|---|---|---|
| Aşama 1-3 (indeks doğru/düzeltildi) | `true` | `true` | Highlight aktif, metin boyanır |
| Aşama 4 (whitespace safe mode) | `true` | `false` | Quote gösterilir, highlight kapalı, info label |
| Aşama 5 (fallback) | `false` | `false` | "Kanıt doğrulanamadı" uyarısı |

---

### ✅ Week 12 Checklist

- [x] Stage 1 prompt evidence çıktısı üretiyor (Task 12.1)
- [x] Evidence JSON parse çalışıyor (Task 12.2)
- [x] 5 aşamalı self-healing doğrulama çalışıyor (Task 12.3)
- [x] `highlight_available` doğru hesaplanıyor (3 durum)
- [x] Graceful degradation çalışıyor (AD-8)
- [x] Evidence unit testleri geçiyor (Task 12.5)
- [x] Live API testleri geçiyor
- [x] Display name -> Slug conversion fix (arka uyumluluk)
        - [x] Judge Service Integration test coverage (Task 12.6)

---

## 📅 Week 13: Snapshot Service & Judge Integration

**Tarih:** 21 Nisan - 27 Nisan 2025  
**Hedef:** Snapshot oluşturma, CRUD endpoint'leri, Judge task entegrasyonu

---

### Task 13.1: Snapshot Service — Create

**Tahmini Süre:** 3 saat

**Durum:** ⏳ **PLANLANDI**

**Referans:** AD-7 (Atomic Write), AD-11 (Otomatik Kayıt)

**Yapılacaklar:**
- [ ] `backend/services/snapshot_service.py` oluştur:
  - [ ] `create_evaluation_snapshot(db, stage1_result, stage2_result, user_eval, question, model_response) -> EvaluationSnapshot` fonksiyonu:
    - [ ] Snapshot ID oluştur (`snap_YYYYMMDD_HHMMSS_randomhex`)
    - [ ] Slug dönüşümü uygula (user_scores, judge_scores, evidence → slug key'ler)
    - [ ] Evidence işle: `process_evidence(model_answer, raw_evidence)` çağır
    - [ ] Tüm alanları birleştir (Stage 1 + Stage 2 + question + response)
    - [ ] `judge_scores_json` ← Stage 1 `independent_scores` direkt kullanılır
    - [ ] Tek transaction'da DB'ye yaz (atomik)
    - [ ] Return: oluşturulan snapshot objesi
  - [ ] ID generator helper: `generate_snapshot_id() -> str`
- [ ] Hata durumunda rollback (yarım snapshot oluşmaz)
- [ ] Başarılı oluşturma log'u: `INFO "Snapshot created: {id}"`
- [ ] Unit test yaz

---

### Task 13.2: Snapshot Service — CRUD

**Tahmini Süre:** 2 saat

**Durum:** ⏳ **PLANLANDI**

**Referans:** AD-13 (Retention Policy)

**Yapılacaklar:**
- [ ] `backend/services/snapshot_service.py` içine CRUD fonksiyonları ekle:
  - [ ] `get_snapshot(db, snapshot_id: str) -> EvaluationSnapshot`:
    - [ ] `WHERE deleted_at IS NULL` filtresi
    - [ ] Bulunamazsa `None` dön
  - [ ] `list_snapshots(db, status: str = None, limit: int = 20, offset: int = 0) -> list`:
    - [ ] `WHERE deleted_at IS NULL` filtresi
    - [ ] Opsiyonel status filtresi
    - [ ] `ORDER BY created_at DESC`
    - [ ] Pagination (limit/offset)
  - [ ] `soft_delete_snapshot(db, snapshot_id: str) -> bool`:
    - [ ] `deleted_at = datetime.utcnow()` set et
    - [ ] `status = 'archived'` set et
    - [ ] Return: başarılı/başarısız
  - [ ] `get_snapshot_count(db, status: str = None) -> int`:
    - [ ] Total count (pagination için)
- [ ] Unit test yaz (CRUD testleri)

---

### Task 13.3: Judge Task Update — Otomatik Snapshot

**Tahmini Süre:** 2.5 saat

**Durum:** ⏳ **PLANLANDI**

**Referans:** AD-7 (Atomic Write), AD-8 (Graceful Degradation), AD-11 (Otomatik Kayıt)

**Yapılacaklar:**
- [ ] `backend/tasks/judge_task.py` güncelle:
  - [ ] `run_judge_evaluation()` fonksiyonuna snapshot oluşturma adımı ekle:
    ```python
    # Mevcut akış
    stage1_result = judge_service.stage1_independent_evaluation(...)
    stage2_result = judge_service.stage2_mentoring_comparison(...)
    
    # YENİ: Atomik snapshot yazımı
    snapshot = snapshot_service.create_evaluation_snapshot(
        db, stage1_result, stage2_result, user_eval, question, model_response
    )
    ```
  - [ ] Stage 1 veya Stage 2 başarısızsa snapshot oluşturma (hata handling)
  - [ ] Snapshot oluşturma hatası judge akışını kırmamalı (try/except, WARNING log)
- [ ] Evidence graceful degradation entegrasyonu:
  - [ ] Evidence parse hatası → snapshot `evidence_json = null` ile oluşturulur
  - [ ] Skorlar ve feedback yine kaydedilir
- [ ] Import'ları güncelle (snapshot_service)
- [ ] Test güncelle (mevcut judge task testlerine snapshot assertion ekle)

---

### Task 13.4: Graceful Degradation — Evidence Parse Failure

**Tahmini Süre:** 1.5 saat

**Durum:** ⏳ **PLANLANDI**

**Referans:** AD-8

**Yapılacaklar:**
- [ ] Evidence parse hata senaryolarını handle et:
  - [ ] Stage 1 evidence alanı eksik → `evidence_json = null`
  - [ ] Stage 1 evidence JSON formatı bozuk → `evidence_json = null`
  - [ ] Tek bir evidence item geçersiz → o item atlanır, diğerleri korunur
  - [ ] Tüm evidence item'lar geçersiz → `evidence_json = {}` (boş dict)
- [ ] Her hata durumunda WARNING seviyesinde log yaz
- [ ] Chat ve rapor ekranı evidence olmadan da çalışır:
  - [ ] `evidence_json IS NULL` kontrolü ekle (snapshot service)
  - [ ] Coach chat evidence yoksa "evidence bulunamadı" mesajı üretir
- [ ] Test senaryoları yaz (hatalı JSON, eksik alan, boş evidence)

---

### Task 13.5: Snapshot Router & Endpoints

**Tahmini Süre:** 2.5 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] `backend/routers/snapshots.py` oluştur:
  - [ ] `APIRouter(prefix="/api/snapshots", tags=["snapshots"])` oluştur
  - [ ] `GET /api/snapshots/` — Snapshot listesi:
    - [ ] Query params: `status` (optional), `limit` (default: 20), `offset` (default: 0)
    - [ ] Response: `SnapshotListPaginated`
    - [ ] `WHERE deleted_at IS NULL` filtresi
  - [ ] `GET /api/snapshots/{snapshot_id}` — Snapshot detayı:
    - [ ] Response: `SnapshotResponse` (tam veri + evidence)
    - [ ] 404 eğer bulunamazsa veya deleted ise
  - [ ] `DELETE /api/snapshots/{snapshot_id}` — Soft delete:
    - [ ] `deleted_at` set et, `status = 'archived'`
    - [ ] 204 No Content response
- [ ] `backend/main.py` güncelle:
  - [ ] Snapshot router'ı dahil et
- [ ] Logger setup
- [ ] Unit test yaz (endpoint testleri)

---

### Task 13.6: Snapshot Tests

**Tahmini Süre:** 3 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] `backend/tests/test_snapshot_service.py` oluştur:
  - [ ] **Create testleri:**
    - [ ] Başarılı snapshot oluşturma (tüm alanlar doğru)
    - [ ] Slug dönüşümü doğru çalışıyor
    - [ ] Evidence ile snapshot
    - [ ] Evidence olmadan snapshot (null)
    - [ ] Atomik yazım (ya hepsi ya hiçbiri)
  - [ ] **CRUD testleri:**
    - [ ] Get snapshot (var/yok)
    - [ ] List snapshots (pagination, status filtresi)
    - [ ] Soft delete (deleted_at set, status archived)
    - [ ] Deleted snapshot get'te görünmez
    - [ ] Deleted snapshot list'te görünmez
- [ ] `backend/tests/test_snapshots_router.py` oluştur:
  - [ ] GET /api/snapshots/ — 200, pagination
  - [ ] GET /api/snapshots/{id} — 200, 404
  - [ ] DELETE /api/snapshots/{id} — 204, 404
  - [ ] Deleted snapshot'a GET → 404

---

### ✅ Week 13 Checklist

- [ ] Snapshot service create çalışıyor (atomik yazım)
- [ ] Snapshot CRUD (get, list, soft delete) çalışıyor
- [ ] Judge task sonrası otomatik snapshot oluşturuluyor
- [ ] Evidence graceful degradation çalışıyor
- [ ] Snapshot endpoint'leri çalışıyor
- [ ] Tüm testler geçiyor

---

## 📅 Week 14: Coach Chat Service

**Tarih:** 28 Nisan - 4 Mayıs 2025  
**Hedef:** Coach Chat servisinin tüm bileşenleri (SSE, windowing, init, limit, reconnect)

---

### Task 14.1: Coach Prompt Design

**Tahmini Süre:** 3 saat

**Durum:** ⏳ **PLANLANDI**

**Referans:** AD-10 (Strict Evidence Usage)

**Yapılacaklar:**
- [ ] `backend/prompts/coach_prompts.py` oluştur:
  - [ ] **System Prompt:**
    - [ ] Coach rolü tanımı (AI Evaluator Mentor)
    - [ ] Sadece seçilen metrikler hakkında konuşma kuralı
    - [ ] **Strict Evidence Usage kuralı (AD-10):**
      > "You must ONLY reference evidence items provided in the context. Do NOT quote from the model answer directly. If no evidence exists for a topic, say so honestly."
    - [ ] Seçilmeyen metrikler hakkında konuşmayı reddetme talimatı
    - [ ] Gap'i açıklama, evidence'a referans verme, iyileştirme önerme akışı
    - [ ] Türkçe konuşma, teknik terimler İngilizce kalabilir kuralı
  - [ ] **User Message Template:**
    - [ ] Snapshot context'i (question, model_answer, selected metrics + scores + evidence)
    - [ ] Chat history (son 6 mesaj)
    - [ ] Kullanıcının mesajı
  - [ ] **Init Greeting Template:**
    - [ ] Seçilen metriklerdeki gap ve evidence özetleme talimatı
    - [ ] Samimi ama profesyonel açılış tonu
    - [ ] Kullanıcıyı soru sormaya teşvik eden kapanış
- [ ] Prompt token sayısı tahmini (maliyet kontrolü)
- [ ] Few-shot örneği ekle (opsiyonel)

---

### Task 14.2: Chat Service — SSE Streaming

**Tahmini Süre:** 4 saat

**Durum:** ⏳ **PLANLANDI**

**Referans:** AD-4 (SSE), AD-5 (Coach Model)

**Yapılacaklar:**
- [ ] `backend/services/chat_service.py` oluştur:
  - [ ] `stream_coach_response(db, snapshot_id, message, client_message_id, selected_metrics, is_init) -> AsyncGenerator` fonksiyonu:
    - [ ] Snapshot context'i DB'den çek
    - [ ] Chat history'yi DB'den çek (son 6 mesaj — AD-4 windowing)
    - [ ] Coach prompt'u render et
    - [ ] OpenRouter API'ye streaming request gönder (GPT-4o-mini)
    - [ ] `yield` ile SSE event'leri dön:
      - [ ] `event: token`, `data: {"content": "kelime"}`
      - [ ] `event: done`, `data: {"msg_id": "msg_..."}`
    - [ ] Streaming bitince DB'deki assistant mesajını güncelle (`is_complete: true`, final content)
  - [ ] `_build_chat_context(snapshot, selected_metrics, chat_history) -> list[dict]` helper:
    - [ ] System prompt + snapshot context + son 6 mesaj + user mesajı
    - [ ] Seçilmeyen metrikleri filtrele
- [ ] OpenRouter streaming entegrasyonu (SSE from provider)
- [ ] LLM call logging (provider: openrouter, model: gpt-4o-mini, purpose: coach_chat)
- [ ] Error handling (timeout, API error)

---

### Task 14.3: Chat Service — Token Windowing

**Tahmini Süre:** 2 saat

**Durum:** ⏳ **PLANLANDI**

**Referans:** AD-4 (Token Windowing)

**Yapılacaklar:**
- [ ] `get_chat_history_window(db, snapshot_id: str, window_size: int = 6) -> list[dict]` fonksiyonu:
  - [ ] `chat_messages` tablosundan son `window_size` mesajı çek
  - [ ] `ORDER BY created_at DESC LIMIT {window_size}` sonra reverse
  - [ ] `is_complete: true` olan mesajları dahil et (yarım mesajlar hariç)
  - [ ] Return: `[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]`
- [ ] Window size configurable (`settings.CHAT_HISTORY_WINDOW`)
- [ ] Boş geçmiş handling (ilk mesaj)
- [ ] Unit test yaz (0 mesaj, 3 mesaj, 10 mesaj, yarım mesajlar)

---

### Task 14.4: Chat Service — Init Greeting

**Tahmini Süre:** 2 saat

**Durum:** ⏳ **PLANLANDI**

**Referans:** AD-4 (Init Greeting)

**Yapılacaklar:**
- [ ] `handle_init_greeting(db, snapshot_id, client_message_id, selected_metrics) -> AsyncGenerator` fonksiyonu:
  - [ ] `client_message_id = "init_{snapshot_id}"` sabit kimlik
  - [ ] Idempotent: Zaten init greeting varsa DB'deki cevabı dön (LLM'e gitmez)
  - [ ] Yoksa:
    - [ ] Init greeting template'i render et (seçilen metriklerdeki gap + evidence özeti)
    - [ ] LLM'e gönder, streaming cevap al
    - [ ] DB'ye yaz (`role: assistant`, `is_complete` akışı)
  - [ ] `chat_turn_count` **artmaz** (bonus mesaj)
- [ ] **Shared Turn ID İstisnası:**
  - [ ] Init greeting'de sadece `role: assistant` mesajı var, eşleşen `role: user` yok
  - [ ] `UNIQUE (snapshot_id, client_message_id, role)` buna izin verir
- [ ] `selected_metrics` ilk init mesajıyla birlikte DB'ye kaydedilir (immutable)
- [ ] Unit test yaz (ilk init, tekrar init, metrics immutability)

---

### Task 14.5: Chat Service — Turn Limit (Atomic SQL)

**Tahmini Süre:** 2 saat

**Durum:** ⏳ **PLANLANDI**

**Referans:** AD-9 (Turn Limit)

**Yapılacaklar:**
- [ ] `check_and_increment_turn(db, snapshot_id: str) -> bool` fonksiyonu:
  - [ ] Atomik SQL sorgusu:
    ```sql
    UPDATE evaluation_snapshots
    SET chat_turn_count = chat_turn_count + 1
    WHERE id = :id AND chat_turn_count < max_chat_turns
    ```
  - [ ] `rows_affected == 0` → limit dolmuş, `False` dön
  - [ ] `rows_affected == 1` → başarılı, `True` dön
  - [ ] Race condition koruması (concurrent requests)
- [ ] Limit aşıldığında HTTP 429 response:
  ```json
  {"error": "turn_limit_reached", "message": "Bu değerlendirme üzerine yeterince konuştuk..."}
  ```
- [ ] `get_remaining_turns(db, snapshot_id) -> int` helper
- [ ] Unit test yaz (normal artırım, limit dolmuş, concurrent test)

---

### Task 14.6: Chat Service — Idempotency & Reconnect

**Tahmini Süre:** 3 saat

**Durum:** ⏳ **PLANLANDI**

**Referans:** AD-4 (SSE Reconnect & Idempotency)

**Yapılacaklar:**
- [ ] **Idempotency (client_message_id):**
  - [ ] `check_duplicate_message(db, snapshot_id, client_message_id) -> ChatMessage | None` fonksiyonu:
    - [ ] `(snapshot_id, client_message_id, "user")` DB'de var mı kontrol et
    - [ ] Varsa mevcut assistant cevabını dön (LLM'e gitmez, sayaç artmaz)
- [ ] **Reconnect (last_event_id):**
  - [ ] `handle_reconnect(db, snapshot_id, client_message_id) -> tuple[str, bool]` fonksiyonu:
    - [ ] `(snapshot_id, client_message_id, "assistant")` kaydını bul
    - [ ] `is_complete: true` → DB'deki tam cevabı dön
    - [ ] `is_complete: false` → **Update-In-Place:**
      - [ ] `content = ""` sıfırla
      - [ ] `is_complete = false` kalsın
      - [ ] LLM üretimini baştan başlat, aynı satırın üzerine yaz
    - [ ] Kayıt yok → Yeni assistant satırı INSERT et
- [ ] **Turn Counter Sıralaması:**
  ```
  1. Dedup kontrol (client_message_id)
  2. Turn limit kontrol + artırım (atomik)
  3. User mesajı yaz (is_complete: true)
  4. Assistant mesajı yaz (is_complete: false, content: "")
  5. LLM streaming → content güncelle
  6. is_complete: true güncelle
  ```
- [ ] Unit test yaz (duplicate mesaj, reconnect yarım cevap, reconnect tam cevap)

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

- [ ] Coach prompt hazır (system + user + init)
- [ ] SSE streaming çalışıyor (kelime kelime)
- [ ] Token windowing çalışıyor (son 6 mesaj)
- [ ] Init greeting çalışıyor (idempotent)
- [ ] Turn limit enforce ediliyor (atomik SQL)
- [ ] Idempotency ve reconnect çalışıyor
- [ ] Update-In-Place stratejisi çalışıyor
- [ ] Tüm chat service unit testleri geçiyor

---

## 📅 Week 15: Chat Endpoints & Integration

**Tarih:** 5 Mayıs - 11 Mayıs 2025  
**Hedef:** Chat router, entegrasyon testleri, error handling

---

### Task 15.1: Chat Router — POST /api/snapshots/{id}/chat

**Tahmini Süre:** 3 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] `backend/routers/snapshots.py` içine chat endpoint'i ekle:
  - [ ] `POST /api/snapshots/{snapshot_id}/chat`:
    - [ ] Request body: `ChatMessageRequest` (message, client_message_id, selected_metrics, is_init)
    - [ ] Response: `StreamingResponse` (SSE, `text/event-stream`)
    - [ ] **Akış sırası:**
      1. Snapshot var mı kontrol et (404)
      2. Snapshot status == 'active' mi kontrol et (409 eğer archived)
      3. `is_init: true` ise → `handle_init_greeting()` çağır
      4. Dedup kontrol (`check_duplicate_message`)
      5. Turn limit kontrol (`check_and_increment_turn`) → 429
      6. User mesajı DB'ye yaz
      7. Assistant mesajı DB'ye yaz (boş)
      8. SSE streaming başlat (`stream_coach_response`)
    - [ ] `selected_metrics` validasyonu:
      - [ ] Slug formatında mı? (ALL_METRIC_SLUGS'ta var mı?)
      - [ ] Max 3 metrik
      - [ ] İlk mesajda zorunlu, sonrasında ignore
- [ ] SSE response headers:
  - [ ] `Content-Type: text/event-stream`
  - [ ] `Cache-Control: no-cache`
  - [ ] `Connection: keep-alive`
- [ ] Error response'lar:
  - [ ] 404: Snapshot bulunamadı
  - [ ] 409: Snapshot archived
  - [ ] 429: Turn limit dolmuş
  - [ ] 422: Validation hatası (eksik client_message_id, geçersiz metrik)

---

### Task 15.2: Chat Router — GET Messages

**Tahmini Süre:** 2 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] `backend/routers/snapshots.py` içine messages endpoint'i ekle:
  - [ ] `GET /api/snapshots/{snapshot_id}/messages`:
    - [ ] Query params: `limit` (default: 50), `offset` (default: 0)
    - [ ] Response: `ChatHistoryResponse` (messages list + total + snapshot_id)
    - [ ] `ORDER BY created_at ASC` (kronolojik sıra)
    - [ ] Sadece `is_complete: true` mesajları dön (yarım cevaplar hariç)
    - [ ] 404 eğer snapshot bulunamazsa
  - [ ] Sayfa reload'da frontend bu endpoint'i çağırır
- [ ] Pagination (limit/offset)
- [ ] Unit test yaz (boş geçmiş, dolu geçmiş, pagination)

---

### Task 15.3: Chat Service Unit Tests

**Tahmini Süre:** 3 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] `backend/tests/test_chat_service.py` oluştur:
  - [ ] **Streaming testleri:**
    - [ ] SSE event formatı doğru (event: token, data: ...)
    - [ ] Streaming tamamlandığında is_complete güncelleniyor
    - [ ] DB'deki content streaming sonucu ile aynı
  - [ ] **Windowing testleri:**
    - [ ] Boş geçmiş → boş list
    - [ ] 3 mesaj → 3 mesaj dönüyor
    - [ ] 10 mesaj → son 6 mesaj dönüyor
    - [ ] Yarım mesajlar (is_complete: false) dahil edilmiyor
  - [ ] **Init greeting testleri:**
    - [ ] İlk init → LLM çağrılır, mesaj oluşturulur
    - [ ] Tekrar init → DB'deki mevcut greeting dönüyor (idempotent)
    - [ ] Init turn_count artırmıyor
    - [ ] selected_metrics DB'ye kaydediliyor
  - [ ] **Turn limit testleri:**
    - [ ] Normal artırım çalışıyor
    - [ ] Limit dolduğunda False dönüyor
    - [ ] Remaining turns doğru hesaplanıyor
  - [ ] **Idempotency testleri:**
    - [ ] Aynı client_message_id → aynı cevap, LLM çağrılmıyor
    - [ ] Farklı client_message_id → yeni cevap

---

### Task 15.4: Chat Integration Tests

**Tahmini Süre:** 3 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] `backend/tests/test_chat_integration.py` oluştur:
  - [ ] **Full flow testi:**
    1. Snapshot oluştur (mock veya fixture)
    2. Init greeting gönder → cevap al
    3. Chat mesajı gönder → SSE cevap al
    4. 2. mesaj gönder → geçmiş mesajlar context'te
    5. Messages endpoint → tüm mesajlar dönüyor
  - [ ] **Turn limit flow:**
    1. 15 mesaj gönder → tümü başarılı
    2. 16. mesaj → 429 response
    3. Messages endpoint → 30+ mesaj (15 user + 15 assistant + init)
  - [ ] **Reconnect flow:**
    1. Mesaj gönder, yarım kal (mock)
    2. Aynı client_message_id ile retry
    3. Update-in-place çalışıyor
  - [ ] **Duplicate flow:**
    1. Mesaj gönder → cevap al
    2. Aynı client_message_id ile tekrar → aynı cevap, LLM çağrılmıyor

---

### Task 15.5: LLM Call Logging — Coach Chat

**Tahmini Süre:** 1.5 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] Coach chat LLM çağrılarını `data/logs/llm_calls.jsonl`'e kaydet:
  - [ ] `provider`: "openrouter"
  - [ ] `model`: "openai/gpt-4o-mini"
  - [ ] `purpose`: "coach_chat" veya "coach_init_greeting"
  - [ ] `prompt_tokens`: input token sayısı
  - [ ] `completion_tokens`: output token sayısı
  - [ ] `total_tokens`: toplam
  - [ ] `duration_seconds`: istek süresi
  - [ ] `success`: true/false
  - [ ] `error`: hata mesajı (varsa)
  - [ ] `snapshot_id`: ilgili snapshot ID
- [ ] Mevcut LLM logging altyapısını kullan (logging_config.py)
- [ ] Token count'u streaming sonrası hesapla

---

### Task 15.6: Error Handling & Edge Cases

**Tahmini Süre:** 2 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] **LLM API hataları:**
  - [ ] Timeout handling (configurable timeout)
  - [ ] Rate limit handling (429 from OpenRouter → retry veya user'a bilgi)
  - [ ] Connection error handling
  - [ ] Invalid response handling
- [ ] **Edge case'ler:**
  - [ ] Snapshot evidence_json null → Coach "Evidence bulunamadı" der
  - [ ] Seçilen metrik için evidence yok → Coach bunu belirtir
  - [ ] Çok uzun kullanıcı mesajı → truncate veya reject
  - [ ] Boş mesaj (is_init: false) → 422 validation error
  - [ ] Geçersiz snapshot_id → 404
  - [ ] Concurrent mesajlar (aynı snapshot, farklı client_message_id) → sırayla işlenir
- [ ] Error log'ları (ERROR seviyesi)
- [ ] Test senaryoları yaz

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

- [ ] POST /api/snapshots/{id}/chat çalışıyor (SSE)
- [ ] GET /api/snapshots/{id}/messages çalışıyor
- [ ] Init greeting (otomatik selamlama) çalışıyor
- [ ] Snapshot CRUD endpoint'leri çalışıyor
- [ ] Chat service unit testleri geçiyor
- [ ] Chat integration testleri geçiyor
- [ ] LLM call logging çalışıyor
- [ ] Error handling ve edge case'ler çözüldü

---

## 📅 Week 16: End-to-End Testing & Polish

**Tarih:** 12 Mayıs - 18 Mayıs 2025  
**Hedef:** Full flow E2E testleri, manual test, documentation, cleanup

---

### Task 16.1: E2E Test — Evidence Flow

**Tahmini Süre:** 3 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] `backend/tests/test_e2e_phase3.py` oluştur:
  - [ ] **Scenario 1: Evidence Generation + Snapshot:**
    1. POST /api/evaluations/start (soru üret)
    2. POST /api/evaluations/submit (değerlendirme gönder)
    3. GET /api/evaluations/{id}/feedback (judge feedback bekle)
    4. GET /api/snapshots/ (snapshot listesinde yeni kayıt var)
    5. GET /api/snapshots/{id} (evidence_json dolu)
    6. Assert: evidence doğrulanmış (`verified: true`)
    7. Assert: `highlight_available` alanları doğru
  - [ ] **Scenario 2: Evidence Graceful Degradation:**
    1. Stage 1'den evidence parse hatası (mock)
    2. Snapshot yine oluşturulur (`evidence_json: null`)
    3. Chat yine çalışır (evidence referansı olmadan)

---

### Task 16.2: E2E Test — Chat Flow

**Tahmini Süre:** 3 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] `backend/tests/test_e2e_phase3.py` içine chat testleri ekle:
  - [ ] **Scenario 3: Full Chat Flow:**
    1. Snapshot oluştur (Scenario 1'den devam veya fixture)
    2. POST /api/snapshots/{id}/chat (is_init: true) → Init greeting
    3. POST /api/snapshots/{id}/chat (message: "Neden Truthfulness'ta 3 verdin?") → SSE cevap
    4. POST /api/snapshots/{id}/chat (message: "Peki nasıl düzeltebilirim?") → SSE cevap
    5. GET /api/snapshots/{id}/messages → Tüm mesajlar (init + 2 user + 2 assistant)
    6. Assert: chat_turn_count == 2 (init sayılmıyor)
  - [ ] **Scenario 4: Turn Limit:**
    1. 15 mesaj gönder
    2. 16. mesaj → 429 response
    3. GET /api/snapshots/{id} → chat_turn_count == 15
    4. Messages endpoint → 30+ mesaj dönüyor

---

### Task 16.3: E2E Test — Reconnect & Idempotency

**Tahmini Süre:** 2 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] `backend/tests/test_e2e_phase3.py` içine reconnect testleri ekle:
  - [ ] **Scenario 5: Duplicate Message:**
    1. Mesaj gönder (client_message_id: "abc")
    2. Aynı mesajı tekrar gönder (client_message_id: "abc")
    3. Assert: Aynı cevap dönüyor, turn_count artmıyor
  - [ ] **Scenario 6: Reconnect (yarım cevap):**
    1. Mesaj gönder, streaming yarıda kes (mock)
    2. Assert: DB'de `is_complete: false` kayıt var
    3. Aynı client_message_id ile retry
    4. Assert: Cevap baştan üretildi, `is_complete: true`
  - [ ] **Scenario 7: Init Greeting Idempotency:**
    1. Init greeting gönder → cevap al
    2. Tekrar init greeting gönder → aynı cevap (DB'den)
    3. Assert: LLM sadece 1 kere çağrıldı

---

### Task 16.4: Manual Testing Session

**Tahmini Süre:** 3 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] CLI üzerinden full flow testi:
  1. [ ] Soru üret (POST /evaluations/start)
  2. [ ] Değerlendirme yap (POST /evaluations/submit)
  3. [ ] Judge feedback bekle (GET /evaluations/{id}/feedback)
  4. [ ] Snapshot kontrol et (GET /snapshots/)
  5. [ ] Evidence kontrol et (GET /snapshots/{id})
  6. [ ] Init greeting (POST /snapshots/{id}/chat, is_init: true)
  7. [ ] Coach sohbeti (3-4 mesaj)
  8. [ ] Messages kontrol et (GET /snapshots/{id}/messages)
- [ ] Log'ları incele:
  - [ ] `mentormind.log` — akış logları
  - [ ] `errors.log` — hata yok mu?
  - [ ] `llm_calls.jsonl` — coach_chat kayıtları
- [ ] Bug'ları tespit et ve fix'le
- [ ] Latency ölç (chat SSE ilk token süresi)

---

### Task 16.5: Documentation Update

**Tahmini Süre:** 2 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] `CLAUDE.md` güncelle:
  - [ ] Phase 3 status ekle (Week 11-16 checklist)
  - [ ] Yeni tabloları database schema bölümüne ekle
  - [ ] Yeni endpoint'leri API endpoints bölümüne ekle
  - [ ] Coach Chat service açıklaması ekle
  - [ ] Evidence service açıklaması ekle
  - [ ] Project Structure güncelle (yeni dosyalar)
- [ ] `README.md` güncelle:
  - [ ] Coach Chat özelliği ekle
  - [ ] Yeni API endpoint'leri listele
- [ ] Inline code comments kontrol et

---

### Task 16.6: Bug Fixes & Final Verification

**Tahmini Süre:** 3 saat

**Durum:** ⏳ **PLANLANDI**

**Yapılacaklar:**
- [ ] Tespit edilen bug'ları fix'le
- [ ] Dead code sil
- [ ] Unused imports temizle
- [ ] Code formatting (black)
- [ ] Linting (flake8)
- [ ] Type hints ekle (yeni fonksiyonlarda)
- [ ] Tüm testleri çalıştır: `pytest`
- [ ] Coverage kontrol et
- [ ] Docker build test: `docker-compose build`
- [ ] Docker run test: `docker-compose up -d`
- [ ] Health check: All services healthy

---

### ✅ Week 16 Checklist

- [ ] E2E Evidence flow testi geçiyor
- [ ] E2E Chat flow testi geçiyor
- [ ] E2E Reconnect & idempotency testi geçiyor
- [ ] Manual test senaryoları başarılı
- [ ] Documentation güncel (CLAUDE.md, README.md)
- [ ] Code clean ve formatlanmış
- [ ] Tüm testler geçiyor

---

## 🎯 Phase 3 Success Metrics

### Technical Metrics

- [ ] **Test Coverage:** 80%+ (Phase 3 yeni kodlar)
- [ ] **API Response Time:** < 200ms (non-LLM endpoints: snapshots, messages)
- [ ] **Chat SSE First Token:** < 2 saniye (ilk kelime süresi)
- [ ] **Evidence Verification:** > 90% doğrulama oranı (Aşama 1-3)
- [ ] **Snapshot Creation:** < 500ms (atomik yazım)
- [ ] **Docker Build:** < 5 dakika (mevcut süre korunuyor)

### Functional Metrics

- [ ] **Evidence Generation:** Stage 1 evidence üretiyor (8 metrik)
- [ ] **Self-Healing:** 5 aşamalı doğrulama çalışıyor
- [ ] **Highlight Available:** Aşama 1-3 `true`, Aşama 4-5 `false`
- [ ] **Snapshot CRUD:** Oluşturma, listeleme, detay, soft delete çalışıyor
- [ ] **Coach Chat:** SSE streaming çalışıyor (GPT-4o-mini)
- [ ] **Init Greeting:** Otomatik açılış mesajı idempotent
- [ ] **Turn Limit:** 15 mesaj limiti atomik enforce ediliyor
- [ ] **Idempotency:** Duplicate mesajlar engelleniyor
- [ ] **Reconnect:** Yarım kalan cevaplar Update-In-Place ile çözülüyor
- [ ] **Token Windowing:** Son 6 mesaj LLM'e gönderiliyor

### Quality Metrics

- [ ] **Code Quality:** Linting errors yok (flake8)
- [ ] **Code Format:** Black formatlanmış
- [ ] **Type Hints:** Tüm yeni fonksiyonlarda mevcut
- [ ] **Documentation:** CLAUDE.md + README.md güncel
- [ ] **Logging:** Coach chat LLM çağrıları `llm_calls.jsonl`'de
- [ ] **Error Handling:** Graceful degradation, proper HTTP status codes
- [ ] **Architectural Decisions:** 13 AD tümüyle uygulanmış

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

**Başarılar!** 💪