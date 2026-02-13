"""
Coach AI Prompts for MentorMind Coach Chat Service

This module contains hardcoded coach prompt templates for GPT-4o-mini
conversational mentoring about user evaluations.

Coach Chat Workflow:
1. Init Greeting: First message when conversation starts (idempotent)
2. Chat Turn: User asks questions, Coach responds based on context

Language:
- System prompts: English (consistent with judge_prompts.py pattern)
- LLM output: Turkish (user preference from survey)

Key Constraints:
- Selected Metrics Only: Coach may ONLY discuss metrics user selected (1-3 metrics)
- AD-10 Strict Evidence Usage: Must ONLY reference evidence from Stage 1
- No Off-Topic Discussions: Politely redirect questions about non-selected metrics
- Turkish Responses: All responses in Turkish, technical terms can remain English

Usage:
    from backend.prompts.coach_prompts import COACH_PROMPTS, render_coach_user_prompt, render_coach_init_greeting

    # Init greeting
    init_greeting = render_coach_init_greeting(
        question="What is 2+2?",
        model_answer="The answer is 5.",
        user_scores={"truthfulness": {"score": 4, ...}},
        judge_scores={"truthfulness": {"score": 3, ...}},
        evidence_json={"truthfulness": [{"quote": "...", ...}]},
        selected_metrics=["truthfulness", "clarity"]
    )

    # Chat turn
    user_prompt = render_coach_user_prompt(
        question="What is 2+2?",
        model_answer="The answer is 5.",
        user_scores={"truthfulness": {"score": 4, ...}},
        judge_scores={"truthfulness": {"score": 3, ...}},
        evidence_json={"truthfulness": [{"quote": "...", ...}]},
        chat_history=[...],  # Last 6 messages
        user_message="Why is my Truthfulness score too high?",
        selected_metrics=["truthfulness", "clarity"]
    )
"""

from typing import Any

from backend.constants.metrics import slug_to_display_name

# =====================================================
# System Prompt
# =====================================================

COACH_SYSTEM_PROMPT = """
You are an expert AI Evaluator Mentor for MentorMind training platform. Your role is to help users improve their LLM evaluation skills through interactive conversation about their completed evaluations.

## Selected Metrics Constraint

CRITICAL: You may ONLY discuss metrics that the user has explicitly selected.
- User selects 1-3 metrics to focus discussion
- Do NOT provide feedback on non-selected metrics, even if scores exist
- Selected metrics are LOCKED after first message (init greeting)
- If user asks about unselected metric: politely redirect to selected ones

Example response to off-topic question:
"Bu değerlendirme için seçtiğiniz metrikler: {selected_metrics_display}. Bu metrikler hakkında konuşabilirim. Diğer metrikler hakkında sorularınız varsa, lütfen yeni bir sohbet başlatın."

This constraint prevents scope drift and keeps conversation focused on user's learning goals.

## Strict Evidence Usage (AD-10)

You MUST ONLY reference evidence items provided in context:
- Evidence items were collected by Judge (GPT-4o) during Stage 1 evaluation
- Each evidence contains: quote (exact text), start/end positions, why, better alternative
- DO NOT generate your own quotes from model_answer
- DO NOT directly quote from model_answer text

### Evidence Reference Format

When explaining a gap, use this pattern:
"Judge bu konuda şunu tespit etti: '{evidence.quote}'

Neden: {evidence.why}

Daha iyi olurdu: {evidence.better}"

### No Evidence Available

If no evidence exists for topic:
"Bu metrik için judge tarafından toplanan kanıt bulunmuyor. Skor farkı muhtemelen küçük detaylardan kaynaklanıyor."

## Conversation Flow

Follow this structure for each response:

1. **Acknowledge and Validate:** Start with positive acknowledgment of user's question
   - "Harika bir soru!" / "Bu önemli bir nokta."
   - Validate their curiosity about evaluation skills

2. **Explain Gaps:** If user selected metric has score gap, explain what it means
   - What does gap of 1 indicate? (minor disagreement)
   - What does gap of 2+ indicate? (significant disagreement)
   - Use Turkish display names for metrics

3. **Reference Evidence:** Use specific evidence items to illustrate your points
   - Only use evidence from selected metrics
   - Follow evidence reference format above
   - 1-2 evidence items maximum per response (quality over quantity)

4. **Suggest Improvements:** Provide actionable, specific guidance
   - "Bir sonraki değerlendirmenizde şuna dikkat edin: ..."
   - Be specific about what to look for
   - Connect to evaluation skill development

5. **Encourage Questions:** Always end by inviting follow-up questions
   - "Başka ne sormak istersiniz?" / "Bu konuda derinleşelim mi?"

## Tone and Style

- **Friendly and Educational:** You are a mentor, not a critic
- **Constructive:** Focus on improvement, not criticism
- **Specific:** Use evidence and examples, not vague advice
- **Encouraging:** Acknowledge what user did well, even when discussing gaps
- **Concise:** 3-5 sentences per response (get to the point)

## Output Language

ALL responses MUST be in Turkish. User is learning evaluation skills in Turkish.

Exception: Technical terms that don't have common Turkish translations:
- API, endpoint, JSON, prompt, LLM, model, score, metric
- These can remain in English for clarity

## Few-Shot Example

User asks: "Truthfulness metriğinde neden 1 puan fark var?"

Coach responds:
"Harika soru! Judge, Truthfulness metriğinde modelin cevabında küçük bir doğruluk sorunu tespit etti.

Judge bu konuda şunu tespit etti: 'Jennifer Doudna 2024 Nobel Kimya ödülünü kazandı'

Neden: Bu ifade yanlış. 2024 Nobel Kimya ödülü David Baker'a verildi.

Daha iyi olurdu: 2024 Nobel Kimya ödülü David Baker'a verildi.

Bu tür küçük doğruluk hatalarını yakalamak için referans cevabı dikkatlice incelemeniz gerekiyor. Model iddialarını referansla karşılaştırmak değerlendirmenizi daha doğru yapar.

Bir sonraki değerlendirmenizde, isim ve tarih gibi doğruluk açısından kritik detaylara öncelik verin. Başka ne sormak istersiniz?"

## Score Gap Reference

For context when explaining gaps:
- **Gap = 0:** Perfect alignment (mükemmel uyum)
- **Gap = 1:** Minor disagreement (küçük fark - detay seviyesi)
- **Gap = 2:** Moderate disagreement (orta fark - önemli farklılık)
- **Gap = 3+:** Major disagreement (büyük fark - temel farklılık)

## Metric Display Names (Turkish)

Use these Turkish names when referring to metrics:
- truthfulness → Truthfulness (Doğruluk)
- helpfulness → Helpfulness (Yararlılık)
- safety → Safety (Güvenlik)
- bias → Bias (Önyargı)
- clarity → Clarity (Açıklık)
- consistency → Consistency (Tutarlılık)
- efficiency → Efficiency (Verimlilik)
- robustness → Robustness (Dayanıklılık)

## Response Format

Your response should be:
1. In Turkish
2. 3-5 sentences (concise)
3. Friendly and educational tone
4. End with a question to encourage follow-up
5. Only discuss selected metrics
6. Reference evidence using the format above

Remember: You are helping users become better evaluators. Every interaction should build their skills and confidence.
"""

# =====================================================
# User Prompt Template (Chat Turn)
# =====================================================

COACH_USER_PROMPT_TEMPLATE = """
Kullanıcının sorusuna aşağıdaki bağlama dayanarak Türkçe yanıt ver.

## Seçilen Metrikler (SADECE BU METRİKLER HAKKINDA KONUŞ)
{selected_metrics_display}

KRİTİK: Sadece yukarıdaki metrikler hakkında konuş. Diğer metrikler için yönlendirme yap.

## Değerlendirme Bağlamı

### Soru
{question}

### Model Cevabı
{model_answer}

### Kullanıcı Puanları
{user_scores_display}

### Judge Puanları
{judge_scores_display}

### Kanıtlar (Judge tarafından Stage 1'de toplanan)
{evidence_display}

## Sohbet Geçmişi (Son {history_window} Mesaj)
{chat_history}

## Kullanıcının Güncel Sorusu
{user_message}

Lütfen kullanıcının sorusunu yanıtla ve SADECE seçili metrikler ({selected_metrics_display}) hakkında konuş.
"""

# =====================================================
# Init Greeting Template (First Message)
# =====================================================

COACH_INIT_GREETING_TEMPLATE = """
Bu değerlendirmeyi birlikte inceleyelim. Seçtiğiniz metrikler için hızlı bir analiz:

{gaps_summary}

## Kanıtlanan Sorunlar
{evidence_summary}

Bu değerlendirme hakkında {selected_metrics_display} metrik(ler)inde ne sormak istersiniz? İlk sorunuzla başlayalım.
"""

# =====================================================
# Helper Functions
# =====================================================


def format_evidence_display(
    evidence_json: dict[str, Any] | None,
    selected_metrics: list[str]
) -> str:
    """
    Format evidence for display in Turkish context.

    Only includes evidence for selected metrics.
    Uses Turkish display names for metric labels.

    Args:
        evidence_json: Evidence dictionary keyed by metric slugs
        selected_metrics: List of metric slugs user selected

    Returns:
        Formatted evidence string in Turkish
    """
    if not evidence_json:
        return "Kanıt yok."

    lines = []
    for metric_slug in selected_metrics:
        if metric_slug not in evidence_json:
            continue

        try:
            display_name = slug_to_display_name(metric_slug)
            evidence_list = evidence_json[metric_slug]

            if not evidence_list:
                lines.append(f"**{display_name}:** Kanıt yok.")
                continue

            lines.append(f"**{display_name}:**")
            for i, item in enumerate(evidence_list[:3], 1):  # Max 3 items
                quote = item.get("quote", "")[:80]  # Truncate long quotes
                why = item.get("why", "")
                better = item.get("better", "")

                evidence_line = f"  {i}. \"{quote}\""
                if why:
                    evidence_line += f"\n     Neden: {why}"
                if better:
                    evidence_line += f"\n     Daha iyi: {better}"
                lines.append(evidence_line)

        except Exception:
            # Skip if metric name conversion fails
            continue

    return "\n".join(lines) if lines else "Seçili metrikler için kanıt yok."


def format_gaps_summary(
    user_scores: dict[str, dict[str, Any]],
    judge_scores: dict[str, dict[str, Any]],
    selected_metrics: list[str]
) -> str:
    """
    Create Turkish summary of score gaps for selected metrics.

    Args:
        user_scores: User scores by metric slug
        judge_scores: Judge scores by metric slug
        selected_metrics: List of metric slugs user selected

    Returns:
        Formatted gaps summary in Turkish
    """
    lines = []

    for metric_slug in selected_metrics:
        if metric_slug not in user_scores or metric_slug not in judge_scores:
            continue

        try:
            display_name = slug_to_display_name(metric_slug)
            user_score = user_scores[metric_slug].get("score")
            judge_score = judge_scores[metric_slug].get("score")

            if user_score is None or judge_score is None:
                gap_str = "karşılaştırılamaz"
            else:
                gap = abs(user_score - judge_score)
                if gap == 0:
                    gap_str = "mükemmel uyum"
                elif gap == 1:
                    gap_str = "küçük fark (1 puan)"
                elif gap == 2:
                    gap_str = "orta fark (2 puan)"
                else:
                    gap_str = f"büyük fark ({gap} puan)"

            lines.append(f"- **{display_name}:** Kullanıcı {user_score}, Judge {judge_score} → {gap_str}")

        except Exception:
            # Skip if metric name conversion fails
            continue

    return "\n".join(lines) if lines else "Skor farkı yok."


def format_scores_display(
    scores: dict[str, dict[str, Any]],
    selected_metrics: list[str]
) -> str:
    """
    Format scores for display (Turkish display names).

    Args:
        scores: Scores dict by metric slug
        selected_metrics: List of metric slugs to display

    Returns:
        Formatted scores string
    """
    if not scores:
        return "Puan yok."

    lines = []
    for metric_slug in selected_metrics:
        if metric_slug not in scores:
            continue

        try:
            display_name = slug_to_display_name(metric_slug)
            score_data = scores[metric_slug]
            score = score_data.get("score")

            # Get reasoning or rationale
            reasoning = score_data.get("reasoning") or score_data.get("rationale", "")
            reasoning_short = reasoning[:60] + "..." if len(reasoning) > 60 else reasoning

            if score is not None:
                lines.append(f"- **{display_name}:** {score}/5 - {reasoning_short}")
            else:
                lines.append(f"- **{display_name}:** N/A")

        except Exception:
            continue

    return "\n".join(lines) if lines else "Puan bilgisi yok."


def format_chat_history(
    chat_history: list[dict[str, Any]]
) -> str:
    """
    Format chat history for context display.

    Args:
        chat_history: List of message dicts with 'role' and 'content'

    Returns:
        Formatted chat history string
    """
    if not chat_history:
        return "Sohbet geçmişi yok (ilk mesaj)."

    lines = []
    for msg in chat_history:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")[:200]  # Truncate long messages

        if role == "user":
            lines.append(f"**Kullanıcı:** {content}")
        elif role == "assistant":
            lines.append(f"**Coach:** {content}")

    return "\n\n".join(lines) if lines else "Sohbet geçmişi yok."


def render_coach_user_prompt(
    question: str,
    model_answer: str,
    user_scores: dict[str, dict[str, Any]],
    judge_scores: dict[str, dict[str, Any]],
    evidence_json: dict[str, Any] | None,
    chat_history: list[dict[str, Any]],
    user_message: str,
    selected_metrics: list[str],
    history_window: int = 6
) -> str:
    """
    Render coach user prompt with full context for chat turn.

    Args:
        question: Question text
        model_answer: Model's response text
        user_scores: User scores by metric slug (from snapshot.user_scores_json)
        judge_scores: Judge scores by metric slug (from snapshot.judge_scores_json)
        evidence_json: Evidence by metric slug (from snapshot.evidence_json)
        chat_history: Last N messages (role, content)
        user_message: Current user message to respond to
        selected_metrics: List of metric slugs user selected
        history_window: Number of messages to include in context

    Returns:
        Rendered prompt string ready for Coach AI
    """
    # Convert metric slugs to Turkish display names
    selected_display = [
        slug_to_display_name(slug) for slug in selected_metrics
    ]
    selected_metrics_display = ", ".join(selected_display)

    # Format scores for selected metrics only
    user_scores_display = format_scores_display(user_scores, selected_metrics)
    judge_scores_display = format_scores_display(judge_scores, selected_metrics)

    # Format evidence for selected metrics only
    evidence_display = format_evidence_display(evidence_json, selected_metrics)

    # Format chat history (last N messages)
    recent_history = chat_history[-history_window:] if chat_history else []
    chat_history_display = format_chat_history(recent_history)

    return COACH_USER_PROMPT_TEMPLATE.format(
        selected_metrics_display=selected_metrics_display,
        question=question,
        model_answer=model_answer,
        user_scores_display=user_scores_display,
        judge_scores_display=judge_scores_display,
        evidence_display=evidence_display,
        chat_history=chat_history_display,
        history_window=history_window,
        user_message=user_message,
    )


def render_coach_init_greeting(
    question: str,
    model_answer: str,
    user_scores: dict[str, dict[str, Any]],
    judge_scores: dict[str, dict[str, Any]],
    evidence_json: dict[str, Any] | None,
    selected_metrics: list[str],
) -> str:
    """
    Render coach init greeting message (first message in conversation).

    This greeting is idempotent - same greeting for same snapshot.

    Args:
        question: Question text
        model_answer: Model's response text
        user_scores: User scores by metric slug
        judge_scores: Judge scores by metric slug
        evidence_json: Evidence by metric slug
        selected_metrics: List of metric slugs user selected

    Returns:
        Rendered greeting string in Turkish
    """
    # Convert metric slugs to Turkish display names
    selected_display = [
        slug_to_display_name(slug) for slug in selected_metrics
    ]
    selected_metrics_display = ", ".join(selected_display)

    # Create gaps summary for selected metrics
    gaps_summary = format_gaps_summary(user_scores, judge_scores, selected_metrics)

    # Create evidence summary
    evidence_display = format_evidence_display(evidence_json, selected_metrics)

    # Build evidence summary (shorter version)
    if evidence_display and evidence_display != "Kanıt yok.":
        evidence_summary = f"Judge bu konularda kanıtlar tespit etti:\n\n{evidence_display}"
    else:
        evidence_summary = "Bu değerlendirme için judge tarafından toplanan spesifik kanıt yok."

    return COACH_INIT_GREETING_TEMPLATE.format(
        gaps_summary=gaps_summary,
        evidence_summary=evidence_summary,
        selected_metrics_display=selected_metrics_display,
    )


# =====================================================
# Export Dictionary
# =====================================================

COACH_PROMPTS = {
    "system_prompt": COACH_SYSTEM_PROMPT,
    "user_prompt_template": COACH_USER_PROMPT_TEMPLATE,
    "init_greeting_template": COACH_INIT_GREETING_TEMPLATE,
    "render_user_prompt": render_coach_user_prompt,
    "render_init_greeting": render_coach_init_greeting,
}

# Export constants
COACH_MAX_HISTORY_WINDOW = 6  # AD-4: Default chat history window
COACH_MAX_SELECTED_METRICS = 3  # Maximum metrics user can select
