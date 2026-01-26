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

**Yapılacaklar:**
- [ ] GitHub repository oluştur
- [ ] Ana klasör yapısını oluştur:
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
- [ ] `.gitignore` dosyası ekle
- [ ] Initial commit yap

---

### Task 1.2: Environment Configuration

**Tahmini Süre:** 1 saat

**Yapılacaklar:**
- [ ] `.env.example` oluştur (tüm environment variables ile)
- [ ] `.env` dosyası oluştur
- [ ] API key'leri ekle:
  - [ ] ANTHROPIC_API_KEY
  - [ ] OPENAI_API_KEY
  - [ ] GOOGLE_API_KEY
- [ ] Database credentials ayarla
- [ ] `.env` dosyasının `.gitignore`'da olduğunu doğrula

---

### Task 1.3: Docker Setup

**Tahmini Süre:** 3 saat

**Yapılacaklar:**
- [ ] `Dockerfile` oluştur
- [ ] `docker-compose.yml` oluştur (3 service: backend, postgres, chromadb)
- [ ] `.dockerignore` oluştur
- [ ] `docker-compose build` ile build al
- [ ] `docker-compose up -d` ile container'ları başlat
- [ ] `docker-compose ps` ile durumları kontrol et
- [ ] `curl http://localhost:8000` ile backend'e erişimi test et

---

### Task 1.4: Python Backend Foundation

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `backend/requirements.txt` oluştur
- [ ] Backend klasör yapısını oluştur:
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
- [ ] `backend/config/settings.py` oluştur (environment loader)
- [ ] `backend/main.py` oluştur (minimal FastAPI app)
- [ ] FastAPI app'in çalıştığını test et

---

### Task 1.5: Database Models - SQLAlchemy Setup

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `backend/models/database.py` oluştur:
  - [ ] SQLAlchemy Base
  - [ ] Database engine
  - [ ] SessionLocal
  - [ ] get_db() dependency
- [ ] `backend/config/database.py` oluştur (DB connection config)
- [ ] Database connection'ı test et

---

### Task 1.6: SQL Schema - question_prompts

**Tahmini Süre:** 1 saat

**Yapılacaklar:**
- [ ] `backend/schemas/01_question_prompts.sql` oluştur
- [ ] Tablo tanımını yaz (id, primary_metric, bonus_metrics, question_type, user_prompt, golden_examples, difficulty, category_hint, timestamps)
- [ ] UNIQUE constraint ekle (primary_metric, question_type)
- [ ] Indexes ekle (primary_metric, difficulty)

---

### Task 1.7: SQL Schema - questions

**Tahmini Süre:** 1 saat

**Yapılacaklar:**
- [ ] `backend/schemas/02_questions.sql` oluştur
- [ ] Tablo tanımını yaz (id, question, category, reference_answer, expected_behavior, rubric_breakdown, denormalized fields, usage tracking)
- [ ] Foreign key ekle (question_prompt_id)
- [ ] Indexes ekle (primary_metric, category, times_used, difficulty)

---

### Task 1.8: SQL Schema - model_responses

**Tahmini Süre:** 1 saat

**Yapılacaklar:**
- [ ] `backend/schemas/03_model_responses.sql` oluştur
- [ ] Tablo tanımını yaz (id, question_id, model_name, response_text, evaluated, evaluation_id)
- [ ] Foreign key ekle (question_id)
- [ ] UNIQUE constraint ekle (question_id, model_name)
- [ ] Indexes ekle (question_id, model_name, evaluated)

---

### Task 1.9: SQL Schema - user_evaluations

**Tahmini Süre:** 1 saat

**Yapılacaklar:**
- [ ] `backend/schemas/04_user_evaluations.sql` oluştur
- [ ] Tablo tanımını yaz (id, response_id, evaluations JSON, judged, judge_evaluation_id)
- [ ] Foreign key ekle (response_id)
- [ ] Indexes ekle (response_id, judged, created_at)

---

### Task 1.10: SQL Schema - judge_evaluations

**Tahmini Süre:** 1 saat

**Yapılacaklar:**
- [ ] `backend/schemas/05_judge_evaluations.sql` oluştur
- [ ] Tablo tanımını yaz (id, user_evaluation_id, independent_scores, alignment_analysis, judge_meta_score, overall_feedback, improvement_areas, positive_feedback, vector_context, primary_metric, gaps)
- [ ] Foreign key ekle (user_evaluation_id)
- [ ] CHECK constraint ekle (judge_meta_score BETWEEN 1 AND 5)
- [ ] Indexes ekle (user_evaluation_id, meta_score, primary_metric, created_at)

---

### Task 1.11: SQLAlchemy Models

**Tahmini Süre:** 3 saat

**Yapılacaklar:**
- [ ] `backend/models/question_prompt.py` oluştur (QuestionPrompt model)
- [ ] `backend/models/question.py` oluştur (Question model)
- [ ] `backend/models/model_response.py` oluştur (ModelResponse model)
- [ ] `backend/models/user_evaluation.py` oluştur (UserEvaluation model)
- [ ] `backend/models/judge_evaluation.py` oluştur (JudgeEvaluation model)
- [ ] `backend/models/__init__.py` oluştur (tüm modelleri export et)

---

### Task 1.12: Pydantic Schemas

**Tahmini Süre:** 3 saat

**Yapılacaklar:**
- [ ] `backend/models/schemas.py` oluştur
- [ ] QuestionPrompt schemas (Base, Create, Response)
- [ ] Question schemas (Base, Create, Response)
- [ ] ModelResponse schemas (Base, Create, Response)
- [ ] UserEvaluation schemas (Base, Create, Response)
- [ ] JudgeEvaluation schemas (Base, Create, Response)
- [ ] Validation logic ekle

---

### Task 1.13: Database Initialization Script

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `backend/scripts/init_db.py` oluştur
- [ ] Tüm SQL schema dosyalarını okuma logic'i ekle
- [ ] Sırayla execute et (01 → 05)
- [ ] Error handling ekle
- [ ] Script'i test et: `docker-compose exec backend python scripts/init_db.py`
- [ ] Tabloları kontrol et: `docker-compose exec postgres psql -U mentormind -d mentormind -c "\dt"`

---

### Task 1.14: Logging Infrastructure

**Tahmini Süre:** 3 saat

**Yapılacaklar:**
- [ ] `backend/config/logging_config.py` oluştur:
  - [ ] Log formatters (default, detailed)
  - [ ] Handlers (console, file, error_file)
  - [ ] Loggers (mentormind, root)
  - [ ] RotatingFileHandler (10MB, 5 backups)
- [ ] `backend/services/llm_logger.py` oluştur:
  - [ ] LLMCallLogger class
  - [ ] log_call() method (provider, model, purpose, tokens, duration, success)
  - [ ] JSONL format
- [ ] `backend/middleware/logging_middleware.py` oluştur:
  - [ ] RequestLoggingMiddleware class
  - [ ] Request/Response logging
  - [ ] Duration tracking
- [ ] `backend/main.py`'a logging ekle
- [ ] Test: `curl http://localhost:8000` ve logları kontrol et

---

### Task 1.15: Health Check Endpoints

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `backend/routers/health.py` oluştur
- [ ] `GET /api/health` endpoint (basic health)
- [ ] `GET /api/health/detailed` endpoint:
  - [ ] Database connection check
  - [ ] ChromaDB connection check
  - [ ] Status response (healthy/degraded)
- [ ] `backend/main.py`'a router'ı ekle
- [ ] Test: `curl http://localhost:8000/api/health`
- [ ] Test: `curl http://localhost:8000/api/health/detailed`

---

### Task 1.16: Testing Infrastructure

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `backend/tests/conftest.py` oluştur:
  - [ ] Test database setup (SQLite)
  - [ ] db fixture
  - [ ] client fixture (TestClient)
- [ ] `backend/pytest.ini` oluştur
- [ ] `backend/tests/test_health.py` oluştur (örnek test)
- [ ] Tests çalıştır: `docker-compose exec backend pytest`
- [ ] Coverage report kontrol et

---

### Task 1.17: Seed Data Script (Skeleton)

**Tahmini Süre:** 1 saat

**Yapılacaklar:**
- [ ] `backend/scripts/seed_data.py` oluştur
- [ ] seed_question_prompts() fonksiyonu (boş, Week 2'de doldurulacak)
- [ ] main() fonksiyonu
- [ ] Error handling
- [ ] Script çalıştırılabilir durumda bırak (empty seed)

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

- [ ] Docker container'lar çalışıyor (backend, postgres, chromadb)
- [ ] Database tabloları oluşturuldu (5 tablo)
- [ ] SQLAlchemy models hazır
- [ ] Pydantic schemas hazır
- [ ] Logging sistemi çalışıyor (3 log dosyası: mentormind.log, errors.log, llm_calls.jsonl)
- [ ] Health check endpoints çalışıyor
- [ ] Test infrastructure kurulu
- [ ] Scripts hazır (init_db.py, seed_data.py, analyze_llm_costs.py)

---

## 📅 Week 2: Question Generation & K Models

**Tarih:** 3 - 9 Şubat 2025  
**Hedef:** Soru üretimi ve K model entegrasyonu

---

### Task 2.1: Question Prompts Data Preparation

**Tahmini Süre:** 4 saat

**Yapılacaklar:**

**Truthfulness prompts:**
- [ ] hallucination_test prompt yaz (user_prompt, golden_examples)
- [ ] factual_accuracy prompt yaz
- [ ] edge_case prompt yaz

**Clarity prompts:**
- [ ] explain_like_5 prompt yaz
- [ ] technical_jargon prompt yaz
- [ ] step_by_step prompt yaz

**Safety prompts:**
- [ ] harmful_content prompt yaz
- [ ] medical_advice prompt yaz
- [ ] illegal_activity prompt yaz

**Bias prompts:**
- [ ] stereotype_check prompt yaz
- [ ] implicit_bias prompt yaz
- [ ] fairness_test prompt yaz

**Helpfulness prompts:**
- [ ] practical_guidance prompt yaz
- [ ] example_provision prompt yaz
- [ ] actionable_advice prompt yaz

**Consistency prompts:**
- [ ] multi_part_question prompt yaz
- [ ] repeated_query prompt yaz
- [ ] contradiction_check prompt yaz

**Efficiency prompts:**
- [ ] concise_explanation prompt yaz
- [ ] time_complexity prompt yaz
- [ ] resource_optimization prompt yaz

**Robustness prompts:**
- [ ] edge_case prompt yaz
- [ ] adversarial_input prompt yaz
- [ ] stress_test prompt yaz

---

### Task 2.2: Seed Data Implementation

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `backend/scripts/seed_data.py`'daki seed_question_prompts() fonksiyonunu tamamla
- [ ] 24 prompt'u dictionary formatında ekle
- [ ] bonus_metrics'i belirle (her primary metric için 2 bonus)
- [ ] difficulty ve category_hint ekle
- [ ] Script'i çalıştır: `docker-compose exec backend python scripts/seed_data.py`
- [ ] Database'i kontrol et: `SELECT COUNT(*) FROM question_prompts;` (24 olmalı)

---

### Task 2.3: Claude Service - Setup

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `backend/services/claude_service.py` oluştur
- [ ] Anthropic client initialize et
- [ ] API key'i environment'tan al
- [ ] Basic error handling ekle
- [ ] Logger setup

---

### Task 2.4: Claude Service - Category Selection

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `select_category(category_hint: str) -> str` fonksiyonu yaz:
  - [ ] "any" → random category seç
  - [ ] "prefer_medical" → %80 Medical, %20 random
  - [ ] "prefer_coding" → %80 Coding, %20 random
  - [ ] "prefer_math" → %80 Math, %20 random
- [ ] CATEGORIES constant tanımla: ["Math", "Coding", "Medical", "General"]
- [ ] Test fonksiyonu

---

### Task 2.5: Claude Service - Prompt Template

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `render_question_prompt(prompt_data, category) -> str` fonksiyonu yaz
- [ ] Template render et (user_prompt'ta {category}, {golden_examples} replace)
- [ ] Golden examples formatla (eğer varsa)
- [ ] Return full prompt

---

### Task 2.6: Claude Service - Question Generation

**Tahmini Süre:** 3 saat

**Yapılacaklar:**
- [ ] `generate_question(primary_metric: str, use_pool: bool) -> Question` fonksiyonu yaz:
  - [ ] use_pool=True ise havuzdan seç (times_used en az olan)
  - [ ] use_pool=False ise yeni üret
- [ ] Yeni üretim logic'i:
  - [ ] question_prompts'tan random seç (WHERE primary_metric=?)
  - [ ] Category belirle
  - [ ] Prompt render et
  - [ ] Claude API'ya gönder (claude-sonnet-4-20250514)
  - [ ] Response parse et (JSON)
  - [ ] Question object oluştur (ID: q_YYYYMMDD_HHMMSS_randomhex)
  - [ ] Database'e kaydet
- [ ] LLM call logging ekle
- [ ] Error handling (timeout, invalid JSON, API error)

---

### Task 2.7: Claude Service - Response Parsing

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `parse_claude_response(response) -> dict` fonksiyonu yaz
- [ ] Expected fields validate et:
  - [ ] question (str)
  - [ ] reference_answer (str)
  - [ ] expected_behavior (str)
  - [ ] rubric_breakdown (dict: 1-5 → descriptions)
- [ ] Validation errors handle et
- [ ] Return parsed data

---

### Task 2.8: Claude Service - Tests

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `backend/tests/test_claude_service.py` oluştur
- [ ] test_select_category() (all category_hint variations)
- [ ] test_render_question_prompt()
- [ ] test_parse_claude_response()
- [ ] test_generate_question() (mock API)
- [ ] Tests çalıştır

---

### Task 2.9: K Model Service - Setup

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `backend/services/model_service.py` oluştur
- [ ] K_MODELS constant tanımla:
  ```python
  K_MODELS = [
      "gpt-3.5-turbo",
      "gpt-4o-mini",
      "claude-3-5-haiku-20241022",
      "gemini-2.0-flash-exp"
  ]
  ```
- [ ] API clients initialize et (OpenAI, Anthropic, Google)
- [ ] Logger setup

---

### Task 2.10: K Model Service - Model Selection

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `select_model(question_id: str) -> str` fonksiyonu yaz:
  - [ ] Bu soruyu hangi modeller cevapladı? (query model_responses)
  - [ ] Cevaplamamış modeller listele
  - [ ] Eğer tümü cevaplamış → random seç
  - [ ] Eğer bazıları cevaplamamış → onlardan random seç
- [ ] Test fonksiyonu

---

### Task 2.11: K Model Service - OpenAI Integration

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `call_openai(model_name: str, question: str) -> str` fonksiyonu yaz
- [ ] OpenAI client ile API call
- [ ] Messages format: `[{"role": "user", "content": question}]`
- [ ] Response parse et (message.content)
- [ ] LLM call logging ekle
- [ ] Error handling
- [ ] Test (mock API)

---

### Task 2.12: K Model Service - Anthropic Integration

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `call_anthropic(model_name: str, question: str) -> str` fonksiyonu yaz
- [ ] Anthropic client ile API call
- [ ] Messages format
- [ ] Response parse et
- [ ] LLM call logging ekle
- [ ] Error handling
- [ ] Test (mock API)

---

### Task 2.13: K Model Service - Google Gemini Integration

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `call_google(model_name: str, question: str) -> str` fonksiyonu yaz
- [ ] Google Generative AI client ile API call
- [ ] Prompt format
- [ ] Response parse et
- [ ] LLM call logging ekle
- [ ] Error handling
- [ ] Test (mock API)

---

### Task 2.14: K Model Service - Unified Interface

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `answer_question(question_id: str, model_name: str) -> ModelResponse` fonksiyonu yaz:
  - [ ] Question'ı database'den getir
  - [ ] Model'e göre doğru provider'ı seç (if/elif)
  - [ ] API call yap
  - [ ] ModelResponse object oluştur (ID: resp_YYYYMMDD_HHMMSS_randomhex)
  - [ ] Database'e kaydet
  - [ ] Return response
- [ ] Error handling

---

### Task 2.15: K Model Service - Tests

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `backend/tests/test_model_service.py` oluştur
- [ ] test_select_model()
- [ ] test_call_openai() (mock)
- [ ] test_call_anthropic() (mock)
- [ ] test_call_google() (mock)
- [ ] test_answer_question() (mock)
- [ ] Tests çalıştır

---

### Task 2.16: Questions Router - Setup

**Tahmini Süre:** 1 saat

**Yapılacaklar:**
- [ ] `backend/routers/questions.py` oluştur
- [ ] APIRouter oluştur
- [ ] Logger setup

---

### Task 2.17: Questions Router - Generate Endpoint

**Tahmini Süre:** 3 saat

**Yapılacaklar:**
- [ ] `POST /api/questions/generate` endpoint yaz:
  - [ ] Request schema: `{primary_metric: str, use_pool: bool}`
  - [ ] Claude service'i çağır (generate_question)
  - [ ] Model seç (select_model)
  - [ ] Model service'i çağır (answer_question)
  - [ ] Response format: `{question_id, response_id, question, model_response, model_name, category}`
  - [ ] Error handling
- [ ] Pydantic request/response schemas
- [ ] Test endpoint (integration test)

---

### Task 2.18: Questions Router - Pool Stats Endpoint

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `GET /api/questions/pool/stats` endpoint yaz:
  - [ ] Total questions count
  - [ ] By metric breakdown
  - [ ] By category breakdown
  - [ ] By difficulty breakdown
  - [ ] Average times_used
- [ ] Response schema
- [ ] Test endpoint

---

### Task 2.19: Router Integration

**Tahmini Süre:** 1 saat

**Yapılacaklar:**
- [ ] `backend/main.py`'a questions router'ı ekle
- [ ] Prefix: `/api/questions`
- [ ] Tags: `["questions"]`
- [ ] Test: `curl -X POST http://localhost:8000/api/questions/generate -d '{"primary_metric": "Truthfulness", "use_pool": false}'`

---

### Task 2.20: End-to-End Test (Week 2)

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] Manuel test senaryosu çalıştır:
  1. [ ] Seed data yükle
  2. [ ] Yeni soru üret (Truthfulness)
  3. [ ] Havuzdan soru seç (Safety)
  4. [ ] Pool stats kontrol et
  5. [ ] Database'de question ve model_response kayıtlarını kontrol et
- [ ] Logları incele (mentormind.log, llm_calls.jsonl)
- [ ] Bug'ları tespit et ve fix'le

---

### ✅ Week 2 Checklist

- [ ] 24 question_prompt seeded
- [ ] Claude service soru üretebiliyor
- [ ] 4 K model soru cevaplayabiliyor
- [ ] Question pool sistemi çalışıyor
- [ ] API endpoints çalışıyor (generate, pool stats)
- [ ] LLM call logging aktif
- [ ] Integration tests geçiyor

---

## 📅 Week 3: User Evaluation & Judge Stage 1

**Tarih:** 10 - 16 Şubat 2025  
**Hedef:** User evaluation API ve judge'ın independent evaluation'ı

---

### Task 3.1: Evaluation Router - Setup

**Tahmini Süre:** 1 saat

**Yapılacaklar:**
- [ ] `backend/routers/evaluations.py` oluştur
- [ ] APIRouter oluştur
- [ ] Logger setup

---

### Task 3.2: Evaluation Schemas

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `backend/models/schemas.py`'ye ekle:
  - [ ] MetricEvaluation schema (score: 1-5 or null, reasoning: str)
  - [ ] EvaluationSubmitRequest schema (response_id, evaluations: Dict[str, MetricEvaluation])
  - [ ] EvaluationSubmitResponse schema (evaluation_id, status, judge_status)
- [ ] Validation logic:
  - [ ] 8 metrik olmalı
  - [ ] Score 1-5 veya null
  - [ ] Reasoning required if score given

---

### Task 3.3: Evaluation Submit Endpoint

**Tahmini Süre:** 3 saat

**Yapılacaklar:**
- [ ] `POST /api/evaluations/submit` endpoint yaz:
  - [ ] Request validate et
  - [ ] UserEvaluation object oluştur (ID: eval_YYYYMMDD_HHMMSS_randomhex)
  - [ ] evaluations JSON'u serialize et
  - [ ] Database'e kaydet
  - [ ] Async judge task başlat (arka planda)
  - [ ] Immediate response dön: `{evaluation_id, status: "submitted", judge_status: "processing"}`
- [ ] Error handling

---

### Task 3.4: Evaluation Update Endpoint

**Tahmini Süre:** 1 saat

**Yapılacaklar:**
- [ ] model_responses tablosunda evaluated flag'i update et
- [ ] evaluation_id'yi set et
- [ ] Endpoint çağrısında bu update'i yap

---

### Task 3.5: Judge Prompts - Hardcoded

**Tahmini Süre:** 3 saat

**Yapılacaklar:**
- [ ] `backend/prompts/judge_prompts.py` oluştur
- [ ] JUDGE_PROMPTS dictionary:
  - [ ] "independent" key:
    - [ ] system_prompt
    - [ ] user_prompt_template (placeholders: {question}, {model_name}, {model_response}, {reference_answer}, {expected_behavior}, {rubric_breakdown})
  - [ ] "mentoring" key:
    - [ ] system_prompt
    - [ ] user_prompt_template
- [ ] Prompt'ları yaz (detaylı, net instruction'lar)

---

### Task 3.6: Judge Service - Setup

**Tahmini Süre:** 1 saat

**Yapılacaklar:**
- [ ] `backend/services/judge_service.py` oluştur
- [ ] OpenAI client initialize et (GPT-4o için)
- [ ] Logger setup
- [ ] Import judge_prompts

---

### Task 3.7: Judge Service - Data Fetching

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `fetch_evaluation_data(user_eval_id: str) -> dict` fonksiyonu yaz:
  - [ ] user_evaluation getir
  - [ ] model_response getir (response_id üzerinden)
  - [ ] question getir (question_id üzerinden)
  - [ ] Return: `{user_eval, model_response, question, user_scores: dict}`
- [ ] Test fonksiyonu

---

### Task 3.8: Judge Service - Stage 1 Implementation

**Tahmini Süre:** 4 saat

**Yapılacaklar:**
- [ ] `stage1_independent_evaluation(user_eval_id: str) -> dict` fonksiyonu yaz:
  - [ ] Evaluation data fetch et
  - [ ] Prompt render et (judge_prompts["independent"])
  - [ ] Placeholders replace et
  - [ ] GPT-4o'ya gönder
  - [ ] Response parse et (JSON)
  - [ ] Validate: 8 metrik, her biri {score, rationale}
  - [ ] Return independent_scores dict
- [ ] LLM call logging ekle
- [ ] Error handling (timeout, invalid JSON)

---

### Task 3.9: Judge Service - Response Parsing

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `parse_judge_response(response: str) -> dict` fonksiyonu yaz
- [ ] JSON parse et
- [ ] Validate structure
- [ ] Handle errors (malformed JSON)
- [ ] Return parsed dict

---

### Task 3.10: Async Task Infrastructure - Setup

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `backend/tasks/__init__.py` oluştur
- [ ] `backend/tasks/judge_task.py` oluştur
- [ ] Background task decorator kullan (FastAPI BackgroundTasks)
- [ ] Logger setup

---

### Task 3.11: Async Task - Judge Task

**Tahmini Süre:** 3 saat

**Yapılacaklar:**
- [ ] `run_judge_evaluation(user_eval_id: str)` async fonksiyonu yaz:
  - [ ] Try/except wrapper
  - [ ] Stage 1 çağır
  - [ ] (Stage 2 Week 4'te eklenecek)
  - [ ] user_evaluations.judged = TRUE set et
  - [ ] Errors handle et ve logla
- [ ] Task'ı evaluation submit endpoint'ten çağır (BackgroundTasks)

---

### Task 3.12: Judge Feedback Endpoint - Basic

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `GET /api/evaluations/{evaluation_id}/feedback` endpoint yaz:
  - [ ] user_evaluation getir
  - [ ] judged flag kontrol et
  - [ ] Eğer FALSE → return `{status: "processing"}`
  - [ ] Eğer TRUE → judge_evaluation getir ve return
- [ ] Response schema
- [ ] Test endpoint

---

### Task 3.13: Judge Service - Tests

**Tahmini Süre:** 3 saat

**Yapılacaklar:**
- [ ] `backend/tests/test_judge_service.py` oluştur
- [ ] test_fetch_evaluation_data()
- [ ] test_parse_judge_response()
- [ ] test_stage1_independent_evaluation() (mock GPT-4o)
- [ ] Tests çalıştır

---

### Task 3.14: Integration Test (Week 3)

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] Manuel test senaryosu:
  1. [ ] Soru üret ve K model cevapla
  2. [ ] User evaluation submit et (8 metrik)
  3. [ ] Judge task'ın arka planda çalıştığını loglardan kontrol et
  4. [ ] 10-30 saniye bekle
  5. [ ] Feedback endpoint'ten judge sonucunu al
  6. [ ] judge_evaluations tablosunu kontrol et
- [ ] Bug'ları tespit et ve fix'le

---

### ✅ Week 3 Checklist

- [ ] User evaluation API çalışıyor
- [ ] Evaluation validation doğru
- [ ] Judge prompts hazır (hardcoded)
- [ ] Judge Stage 1 (independent) çalışıyor
- [ ] Async task infrastructure kurulu
- [ ] Judge feedback endpoint çalışıyor
- [ ] LLM logging GPT-4o call'larını kaydediyor
- [ ] Integration tests geçiyor

---

## 📅 Week 4: Judge Stage 2 & End-to-End Testing

**Tarih:** 17 - 23 Şubat 2025  
**Hedef:** ChromaDB entegrasyonu, judge Stage 2, end-to-end test

---

### Task 4.1: ChromaDB Service - Setup

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `backend/services/chromadb_service.py` oluştur
- [ ] ChromaDB client initialize et
- [ ] Collection oluştur ("evaluation_memory")
- [ ] Embedding function setup (OpenAI text-embedding-3-small)
- [ ] Logger setup

---

### Task 4.2: ChromaDB Service - Add to Memory

**Tahmini Süre:** 3 saat

**Yapılacaklar:**
- [ ] `add_to_memory(user_eval_id: str, judge_eval_id: str) -> None` fonksiyonu yaz:
  - [ ] Evaluation data fetch et
  - [ ] Judge evaluation fetch et
  - [ ] Document text oluştur (summary format)
  - [ ] Metadata oluştur:
    - evaluation_id
    - judge_id
    - category
    - primary_metric
    - judge_meta_score
    - alignment_gap
    - mistake_pattern
    - timestamp
  - [ ] ChromaDB'ye add et
- [ ] Error handling
- [ ] Test fonksiyonu

---

### Task 4.3: ChromaDB Service - Query Past Mistakes

**Tahmini Süre:** 3 saat

**Yapılacaklar:**
- [ ] `query_past_mistakes(primary_metric: str, category: str, n: int = 5) -> dict` fonksiyonu yaz:
  - [ ] Query text oluştur: "User evaluating {primary_metric} in {category} category"
  - [ ] ChromaDB query (where filter: primary_metric & category)
  - [ ] n_results=5
  - [ ] Return: `{ids, documents, metadatas, distances}`
- [ ] Empty result handling
- [ ] Error handling
- [ ] Test fonksiyonu

---

### Task 4.4: Judge Service - Comparison Table Generator

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `generate_comparison_table(user_scores: dict, judge_scores: dict) -> str` fonksiyonu yaz:
  - [ ] Markdown table oluştur
  - [ ] Columns: Metric, User Score, Judge Score, Gap, Verdict
  - [ ] Her 8 metrik için satır
  - [ ] Gap hesapla (user - judge)
  - [ ] Verdict belirle (over_estimated, under_estimated, aligned, not_applicable)
  - [ ] Return markdown string
- [ ] Test fonksiyonu

---

### Task 4.5: Judge Service - Weighted Gap Calculation

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `calculate_weighted_gap(user_scores: dict, judge_scores: dict, primary_metric: str, bonus_metrics: list) -> float` fonksiyonu yaz:
  - [ ] Primary gap hesapla (abs)
  - [ ] Bonus gaps hesapla (avg)
  - [ ] Other gaps hesapla (avg)
  - [ ] Weighted gap: primary*0.7 + bonus*0.2 + other*0.1
  - [ ] Return weighted_gap
- [ ] Test fonksiyonu

---

### Task 4.6: Judge Service - Meta Score Mapping

**Tahmini Süre:** 1 saat

**Yapılacaklar:**
- [ ] `weighted_gap_to_meta_score(weighted_gap: float) -> int` fonksiyonu yaz:
  - [ ] <= 0.5 → 5
  - [ ] <= 1.0 → 4
  - [ ] <= 1.5 → 3
  - [ ] <= 2.0 → 2
  - [ ] else → 1
- [ ] Test fonksiyonu

---

### Task 4.7: Judge Service - Stage 2 Implementation

**Tahmini Süre:** 4 saat

**Yapılacaklar:**
- [ ] `stage2_mentoring_comparison(user_eval_id: str, stage1_scores: dict, vector_context: dict) -> dict` fonksiyonu yaz:
  - [ ] Evaluation data fetch et
  - [ ] Question data getir (primary_metric, bonus_metrics)
  - [ ] Comparison table oluştur
  - [ ] User scores serialize et
  - [ ] Past mistakes formatla (vector_context'ten)
  - [ ] Prompt render et (judge_prompts["mentoring"])
  - [ ] Placeholders replace et
  - [ ] GPT-4o'ya gönder
  - [ ] Response parse et
  - [ ] Weighted gap hesapla
  - [ ] Meta score hesapla
  - [ ] Return: alignment_analysis, judge_meta_score, overall_feedback, improvement_areas, positive_feedback, primary_metric_gap, weighted_gap
- [ ] LLM call logging
- [ ] Error handling

---

### Task 4.8: Judge Service - Full Flow Integration

**Tahmini Süre:** 3 saat

**Yapılacaklar:**
- [ ] `full_judge_evaluation(user_eval_id: str) -> str` fonksiyonu yaz:
  - [ ] Stage 1: independent evaluation
  - [ ] ChromaDB: query past mistakes
  - [ ] Stage 2: mentoring comparison
  - [ ] Judge ID oluştur (judge_YYYYMMDD_HHMMSS_randomhex)
  - [ ] judge_evaluations'a kaydet
  - [ ] ChromaDB: add to memory
  - [ ] user_evaluations.judged = TRUE, judge_evaluation_id = judge_id
  - [ ] Return judge_id
- [ ] Error handling (rollback on failure)

---

### Task 4.9: Async Task - Full Judge

**Tahmini Süre:** 1 saat

**Yapılacaklar:**
- [ ] `backend/tasks/judge_task.py`'daki run_judge_evaluation() fonksiyonunu güncelle:
  - [ ] full_judge_evaluation() çağır
  - [ ] Success/failure logla
- [ ] Test async task

---

### Task 4.10: Judge Feedback Endpoint - Complete

**Tahmini Süre:** 2 saat

**Yapılacaklar:**
- [ ] `GET /api/evaluations/{evaluation_id}/feedback` endpoint'i güncelle:
  - [ ] Complete response format:
    - evaluation_id
    - judge_meta_score
    - overall_feedback
    - alignment_analysis (full dict)
    - improvement_areas
    - positive_feedback
    - past_patterns_referenced (ChromaDB'den)
  - [ ] Response schema güncelle
- [ ] Test endpoint

---

### Task 4.11: Statistics Router - Setup

**Tahmini Süre:** 1 saat

**Yapılacaklar:**
- [ ] `backend/routers/stats.py` oluştur
- [ ] APIRouter oluştur
- [ ] Logger setup

---

### Task 4.12: Statistics - Overview Endpoint

**Tahmini Süre:** 3 saat

**Yapılacaklar:**
- [ ] `GET /api/stats/overview` endpoint yaz:
  - [ ] Total evaluations (COUNT user_evaluations)
  - [ ] Average meta score (AVG judge_meta_score)
  - [ ] Metrics performance:
    - Her metrik için: avg primary_metric_gap, count
    - Trend hesapla (son 10 vs önceki 10)
  - [ ] Improvement trend (overall)
  - [ ] Response format
- [ ] Database queries optimize et (indexes kullan)
- [ ] Test endpoint

---

### Task 4.13: CLI Testing Interface

**Tahmini Süre:** 3 saat

**Yapılacaklar:**
- [ ] `backend/cli.py` oluştur:
  - [ ] `start_evaluation(primary_metric, use_pool)` → API call
  - [ ] `submit_evaluation(response_id, evaluations)` → API call
  - [ ] `get_feedback(evaluation_id)` → API call
  - [ ] `get_stats()` → API call
  - [ ] Pretty print results
- [ ] Interactive CLI (input prompts)
- [ ] Test CLI

---

### Task 4.14: End-to-End Test Suite

**Tahmini Süre:** 4 saat

**Yapılacaklar:**
- [ ] `backend/tests/test_e2e.py` oluştur
- [ ] Test Scenario 1: Yeni soru üretme → değerlendirme → judge → feedback
- [ ] Test Scenario 2: Havuzdan soru seçme → değerlendirme → judge → feedback
- [ ] Test Scenario 3: Tekrar eden hata (ChromaDB hafıza)
- [ ] Test Scenario 4: İstatistikler
- [ ] Assert conditions:
  - [ ] Database records created
  - [ ] Judge meta score calculated
  - [ ] ChromaDB document added
  - [ ] Feedback returned
- [ ] Tests çalıştır

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

### ✅ Week 4 Checklist

- [ ] ChromaDB entegrasyonu çalışıyor
- [ ] Judge Stage 2 (mentoring) çalışıyor
- [ ] Full judge workflow (Stage 1 + ChromaDB + Stage 2) çalışıyor
- [ ] Past mistakes judge'a hatırlatılıyor
- [ ] Statistics API çalışıyor
- [ ] CLI testing interface hazır
- [ ] End-to-end tests geçiyor
- [ ] Manual test senaryoları başarılı
- [ ] Documentation güncel
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

**Başarılar!** 💪