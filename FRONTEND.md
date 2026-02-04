# MentorMind Frontend

Modern dashboard-style frontend for the MentorMind AI Evaluator Training System.

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Styling:** Tailwind CSS
- **State:** React hooks
- **Icons:** Lucide React
- **Charts:** Recharts

## Getting Started

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`

## Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Pages

| Route | Description |
|-------|-------------|
| `/` | Dashboard - Stats overview, performance charts |
| `/evaluate` | New evaluation - Metric selection, question display, evaluation form |
| `/feedback/[id]` | Judge feedback - Alignment analysis, improvement areas |
| `/history` | Evaluation history - Past evaluations summary |

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Dashboard
│   ├── evaluate/          # Evaluation flow
│   ├── feedback/[id]/     # Feedback detail
│   └── history/           # Evaluation history
├── components/
│   ├── ui/                # Base components (Card, Button, Badge, Spinner)
│   ├── layout/            # Sidebar, Header
│   ├── stats/             # MetaScoreGauge, Charts, StatsCard
│   ├── evaluation/        # MetricSelector, EvaluationForm, QuestionDisplay
│   └── feedback/          # AlignmentCard, FeedbackPanel
├── lib/
│   ├── api.ts             # API client functions
│   └── constants.ts       # Metrics, colors, labels
├── hooks/
│   └── usePolling.ts      # Polling hook for judge feedback
└── types/
    └── index.ts           # TypeScript interfaces
```

## Design System

- **Background:** Slate-50
- **Cards:** White with subtle shadows, rounded-xl
- **Primary:** Indigo-600
- **Success:** Emerald-500
- **Warning:** Amber-500
- **Error:** Rose-500
- **8 Metric Colors:** Blue, Emerald, Rose, Purple, Amber, Cyan, Orange, Indigo

## API Integration

Backend API endpoints used:

- `POST /api/questions/generate` - Generate question + K model response
- `POST /api/evaluations/submit` - Submit user evaluation
- `GET /api/evaluations/{id}/feedback` - Get judge feedback (polling)
- `GET /api/stats/overview` - Get user performance stats

## Build

```bash
npm run build
npm start
```
