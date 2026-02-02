# FRONTEND.md - MentorMind AI Frontend Architecture

**Project:** MentorMind - AI Evaluator Training System
**Version:** 1.0.0-Frontend
**Status:** Design Phase (Pre-Implementation)
**Last Updated:** 2025-02-02
**Language:** Turkish (Documentation), English (Code)

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture](#architecture)
4. [UI/UX Design System](#uiux-design-system)
5. [Component Structure](#component-structure)
6. [State Management](#state-management)
7. [API Integration](#api-integration)
8. [Routing & Navigation](#routing--navigation)
9. [Real-time Features](#real-time-features)
10. [Performance Optimization](#performance-optimization)
11. [Testing Strategy](#testing-strategy)
12. [Development Workflow](#development-workflow)
13. [Deployment](#deployment)
14. [Project Structure](#project-structure)

---

## Project Overview

### Purpose
MentorMind frontend provides an intuitive, educational interface for users to:
- Practice AI model evaluation skills across 8 critical metrics
- Receive objective, two-stage feedback from GPT-4o judge
- Track performance improvements over time
- Learn from past mistakes via ChromaDB-powered pattern recognition

### Core User Flows

#### Flow 1: Evaluation Session
1. **Dashboard Entry** → User selects primary metric to practice
2. **Question Generation** → System generates question (or selects from pool)
3. **K Model Response** → AI model responds to the question
4. **User Evaluation** → User evaluates across all 8 metrics
5. **Judge Processing** → GPT-4o evaluates asynchronously (background)
6. **Feedback Display** → User receives detailed feedback with patterns

#### Flow 2: Statistics & Progress
1. **Dashboard** → Overview of performance
2. **Metrics Breakdown** → Per-metric performance analysis
3. **Trend Visualization** → Improvement over time
4. **Past Mistakes** → ChromaDB-referenced patterns

---

## Technology Stack

### Core Framework
| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 14.2+ | React framework with App Router |
| **React** | 18.3+ | UI library |
| **TypeScript** | 5.3+ | Type safety |
| **Node.js** | 20+ | Runtime environment |

### UI Components & Styling
| Technology | Version | Purpose |
|------------|---------|---------|
| **shadcn/ui** | Latest | High-quality React components (Radix UI + Tailwind) |
| **Tailwind CSS** | 3.4+ | Utility-first CSS framework |
| **Lucide React** | Latest | Icon library |
| **Framer Motion** | 11+ | Physics-based animations |

### State Management & Data Fetching
| Technology | Version | Purpose |
|------------|---------|---------|
| **Zustand** | 4.5+ | Lightweight client state management |
| **TanStack Query** | 5.28+ | Server state management & caching |
| **Axios** | 1.6+ | HTTP client (or fetch with TanStack Query) |

### Development Tools
| Technology | Version | Purpose |
|------------|---------|---------|
| **ESLint** | 8.56+ | Linting |
| **Prettier** | 3.2+ | Code formatting |
| **Vitest** | 1.3+ | Unit testing |
| **Playwright** | 1.41+ | E2E testing |
| **TypeScript ESLint** | 7.0+ | TypeScript linting |

### Why This Stack?

#### Next.js 14+ (App Router)
- **Server Components:** Better performance, less JS sent to client
- **File-based Routing:** Simple and intuitive navigation
- **API Routes:** Proxy backend calls (CORS handling)
- **Built-in Optimization:** Image, font, and bundle optimization
- **Vercel Integration:** Zero-config deployment

#### shadcn/ui
- **Copy-Paste Components:** Full ownership, no npm package bloat
- **Radix UI Foundation:** Accessibility-first primitives
- **Tailwind Integration:** Consistent styling system
- **Customizable:** Easy to modify for brand guidelines

#### TanStack Query + Zustand
- **Separation of Concerns:** Server state vs. client state
- **Automatic Caching:** Reduces redundant API calls
- **Optimistic Updates:** Better UX for evaluation submission
- **DevTools:** Excellent debugging experience

---

## Architecture

### Design Principles

1. **Component-First:** Atomic Design methodology (Atoms → Molecules → Organisms)
2. **Server-First:** Leverage Next.js Server Components for data fetching
3. **Progressive Enhancement:** Core functionality works without JS
4. **Mobile-First:** Responsive design from 320px to 4K
5. **Accessibility:** WCAG 2.1 AA compliance minimum

### Architecture Pattern: Feature-First with Vertical Slices

```
frontend/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Auth route group
│   ├── dashboard/                # Main dashboard
│   ├── evaluation/               # Evaluation flow
│   ├── statistics/               # Stats & progress
│   └── layout.tsx                # Root layout
├── features/                     # Feature slices
│   ├── evaluation-session/       # Evaluation workflow
│   │   ├── components/           # Feature components
│   │   ├── hooks/                # Feature hooks
│   │   ├── services/             # API calls
│   │   └── types.ts              # Feature types
│   ├── judge-feedback/           # Judge feedback display
│   └── statistics-dashboard/     # Stats visualization
├── components/                   # Shared components
│   ├── ui/                       # shadcn/ui components
│   ├── forms/                    # Form components
│   └── visualizations/           # Charts, graphs
├── lib/                          # Shared utilities
│   ├── api/                      # API client setup
│   ├── query/                    # TanStack Query setup
│   ├── store/                    # Zustand stores
│   └── utils.ts                  # Utility functions
└── styles/                       # Global styles
```

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Next.js App Router                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐     ┌──────────────┐     ┌─────────────┐ │
│  │   Server     │────▶│   Server     │────▶│   Backend   │ │
│  │ Component    │     │   Action     │     │   (FastAPI) │ │
│  └──────────────┘     └──────────────┘     └─────────────┘ │
│         │                                           │        │
│         │                                           │        │
│         ▼                                           ▼        │
│  ┌──────────────┐     ┌──────────────┐     ┌─────────────┐ │
│  │   Client     │────▶│  TanStack    │◀────│    API      │ │
│  │ Component    │     │    Query     │     │  Response   │ │
│  └──────────────┘     └──────────────┘     └─────────────┘ │
│         │                                           │        │
│         │                                           │        │
│         ▼                                           ▼        │
│  ┌──────────────┐     ┌──────────────┐              │        │
│  │  Zustand     │     │   React      │              │        │
│  │  Store       │     │   State      │              │        │
│  └──────────────┘     └──────────────┘              │        │
│                                                     │        │
└─────────────────────────────────────────────────────┘        │
```

---

## UI/UX Design System

### Design Philosophy
**"Cognitive Load Minimization"** - Every UI element reduces mental effort, not adds to it.

### Color Palette (Educational & Professional)

#### Primary Colors (LCH-based)
```css
/* Primary - Trust & Learning */
--primary-50:  lch(95% 0.5 250);   /* Light blue */
--primary-100: lch(90% 1.0 250);
--primary-500: lch(60% 2.5 250);   /* Main brand */
--primary-700: lch(45% 3.0 250);
--primary-900: lch(30% 3.5 250);   /* Dark blue */

/* Accent - Achievement */
--accent-500:  lch(65% 4.0 145);   /* Gold/Amber */

/* Semantic Colors */
--success-500: lch(60% 3.0 145);   /* Green */
--warning-500: lch(70% 4.0 85);    /* Amber */
--error-500:   lch(55% 3.5 25);    /* Red */
--info-500:    lch(60% 2.5 250);   /* Blue */

/* Neutral Scale */
--neutral-50:  lch(98% 0 0);
--neutral-100: lch(95% 0 0);
--neutral-200: lch(90% 0 0);
--neutral-300: lch(80% 0 0);
--neutral-400: lch(65% 0 0);
--neutral-500: lch(50% 0 0);
--neutral-600: lch(40% 0 0);
--neutral-700: lch(30% 0 0);
--neutral-800: lch(20% 0 0);
--neutral-900: lch(10% 0 0);
```

#### Metric-Specific Colors (8 Metrics)
Each evaluation metric has a distinct color for visual distinction:
```css
/* Truthfulness */    --metric-truthfulness:    lch(55% 2.8 220); /* Blue */
/* Helpfulness */     --metric-helpfulness:     lch(65% 3.0 150); /* Green */
/* Safety */          --metric-safety:          lch(50% 2.5 350); /* Red */
/* Bias */            --metric-bias:            lch(60% 2.8 280); /* Purple */
/* Clarity */         --metric-clarity:         lch(70% 3.2 85);  /* Yellow */
/* Consistency */     --metric-consistency:     lch(55% 2.6 200); /* Cyan */
/* Efficiency */      --metric-efficiency:      lch(65% 2.9 45);  /* Orange */
/* Robustness */      --metric-robustness:      lch(50% 2.7 300); /* Magenta */
```

### Typography

#### Font Family
```css
/* Primary - Inter (shadcn/ui default) */
--font-sans: 'Inter', system-ui, -apple-system, sans-serif;

/* Monospace - For code snippets */
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* Display - For hero/headers (optional) */
--font-display: 'Cal Sans', 'Inter', sans-serif;
```

#### Type Scale (Perfect Fourth: 1.333)
```css
--text-xs:   0.75rem;   /* 12px */
--text-sm:   0.875rem;  /* 14px */
--text-base: 1rem;      /* 16px - Base */
--text-lg:   1.125rem;  /* 18px */
--text-xl:   1.333rem;  /* 21.33px */
--text-2xl:  1.777rem;  /* 28.43px */
--text-3xl:  2.369rem;  /* 37.9px */
--text-4xl:  3.157rem;  /* 50.5px */
```

### Spacing System (8-Point Grid)

```css
--spacing-0:   0;
--spacing-1:   0.25rem;  /* 4px */
--spacing-2:   0.5rem;   /* 8px */
--spacing-3:   0.75rem;  /* 12px */
--spacing-4:   1rem;     /* 16px */
--spacing-5:   1.25rem;  /* 20px */
--spacing-6:   1.5rem;   /* 24px */
--spacing-8:   2rem;     /* 32px */
--spacing-10:  2.5rem;   /* 40px */
--spacing-12:  3rem;     /* 48px */
--spacing-16:  4rem;     /* 64px */
```

### Component Design Tokens

#### Border Radius
```css
--radius-sm:  0.25rem;  /* 4px */
--radius-md:  0.375rem; /* 6px */
--radius-lg:  0.5rem;   /* 8px */
--radius-xl:  0.75rem;  /* 12px */
--radius-2xl: 1rem;     /* 16px */
--radius-full: 9999px;
```

#### Shadows (Layered)
```css
--shadow-sm:  0 1px 2px lch(0% 0 0 / 0.05);
--shadow-md:  0 4px 6px -1px lch(0% 0 0 / 0.1);
--shadow-lg:  0 10px 15px -3px lch(0% 0 0 / 0.1);
--shadow-xl:  0 20px 25px -5px lch(0% 0 0 / 0.1);
```

#### Glassmorphism (Subtle)
```css
--glass-bg:        lch(100% 0 0 / 0.7);
--glass-border:    lch(0% 0 0 / 0.1);
--glass-blur:      blur(12px);
```

---

## Component Structure

### Atomic Design Hierarchy

#### Atoms (Basic UI Elements)
```
components/ui/atoms/
├── Button/
├── Input/
├── Badge/
├── Progress/
├── Skeleton/
└── MetricBadge/          # Custom: Metric indicator with color
```

#### Molecules (Simple Combinations)
```
components/ui/molecules/
├── MetricSlider/         # Score input (1-5) + reasoning
├── ScoreCard/            # Metric score display
├── TrendIndicator/       # Performance trend arrow
├── ModelBadge/           # K model identifier
└── FeedbackItem/         # Judge feedback unit
```

#### Organisms (Complex Components)
```
components/ui/organisms/
├── EvaluationForm/       # 8-metric evaluation form
├── JudgeFeedbackPanel/   # Complete feedback display
├── StatsDashboard/       # Statistics overview
├── QuestionCard/         # Question + response display
└── ProgressChart/        # Performance visualization
```

### Key Components Specification

#### 1. EvaluationForm Component
**Purpose:** Collect user evaluation across 8 metrics

**Features:**
- Accordion-style metric expansion
- Slider input (1-5) with real-time validation
- Text area for reasoning (optional for N/A)
- Visual feedback for incomplete metrics
- Draft auto-save (localStorage)

**Props:**
```typescript
interface EvaluationFormProps {
  questionId: string;
  responseId: string;
  categoryName: string;
  onSubmit: (data: EvaluationSubmitRequest) => Promise<void>;
  disabled?: boolean;
}
```

**State:**
```typescript
interface EvaluationFormState {
  evaluations: Record<string, MetricEvaluation>;
  touched: Record<string, boolean>;
  isValid: boolean;
}
```

#### 2. JudgeFeedbackPanel Component
**Purpose:** Display GPT-4o judge evaluation results

**Features:**
- Staggered animation for feedback items
- Color-coded alignment (aligned/over/under)
- Expandable detailed feedback per metric
- Pattern recognition highlights
- Meta score visualization (1-5 stars)

**Props:**
```typescript
interface JudgeFeedbackPanelProps {
  evaluationId: string;
  isPolling?: boolean;
  onRetry?: () => void;
}
```

#### 3. StatsDashboard Component
**Purpose:** Display user performance overview

**Features:**
- Total evaluations counter
- Average meta score with trend
- Per-metric performance cards
- Improvement trend chart (line chart)
- Metric comparison radar chart

**Props:**
```typescript
interface StatsDashboardProps {
  userId?: string;
  timeRange?: '7d' | '30d' | '90d' | 'all';
}
```

---

## State Management

### State Split Strategy

**TanStack Query (Server State)**
- Questions & model responses
- Evaluation submissions
- Judge feedback polling
- Statistics & performance data
- Question pool stats

**Zustand (Client State)**
- Current evaluation session state
- Form draft state
- UI preferences (theme, language)
- Modal/overlay states
- Navigation history

### Zustand Store Structure

```typescript
// lib/store/evaluation-store.ts
interface EvaluationStore {
  // Current session state
  currentQuestion: Question | null;
  currentResponse: ModelResponse | null;
  evaluationDraft: Record<string, MetricEvaluation>;

  // Actions
  setCurrentQuestion: (q: Question) => void;
  setCurrentResponse: (r: ModelResponse) => void;
  updateDraft: (metric: string, data: MetricEvaluation) => void;
  clearDraft: () => void;
  submitEvaluation: () => Promise<void>;
}

// lib/store/ui-store.ts
interface UIStore {
  // UI state
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  language: 'tr' | 'en';

  // Actions
  toggleSidebar: () => void;
  setTheme: (t: 'light' | 'dark') => void;
  setLanguage: (l: 'tr' | 'en') => void;
}
```

### TanStack Query Setup

```typescript
// lib/query/client.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,     // 5 minutes
      gcTime: 10 * 60 * 1000,       // 10 minutes
      retry: 3,
      refetchOnWindowFocus: false,
    },
  },
});

// lib/query/keys.ts
export const queryKeys = {
  questions: {
    all: ['questions'] as const,
    generate: (metric: string) => ['questions', 'generate', metric] as const,
    pool: () => ['questions', 'pool'] as const,
  },
  evaluations: {
    all: ['evaluations'] as const,
    feedback: (id: string) => ['evaluations', id, 'feedback'] as const,
  },
  stats: {
    overview: () => ['stats', 'overview'] as const,
  },
};
```

---

## API Integration

### API Client Setup

```typescript
// lib/api/client.ts
import axios, { AxiosError } from 'axios';

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Redirect to login (when auth is added)
    }
    return Promise.reject(error);
  }
);

interface ApiError {
  detail: string;
  status: number;
}
```

### API Services (Feature-Slice Pattern)

```typescript
// features/evaluation-session/services/api.ts
import { apiClient } from '@/lib/api/client';
import { queryKeys } from '@/lib/query/keys';

export const evaluationApi = {
  // Start new evaluation
  startEvaluation: async (params: StartEvaluationRequest) => {
    const { data } = await apiClient.post<StartEvaluationResponse>(
      '/api/questions/generate',
      params
    );
    return data;
  },

  // Submit evaluation
  submitEvaluation: async (data: EvaluationSubmitRequest) => {
    const response = await apiClient.post<EvaluationSubmitResponse>(
      '/api/evaluations/submit',
      data
    );
    return response.data;
  },

  // Get judge feedback (polling)
  getFeedback: async (evaluationId: string) => {
    const { data } = await apiClient.get<JudgeFeedbackResponse>(
      `/api/evaluations/${evaluationId}/feedback`
    );
    return data;
  },

  // Retry failed judge
  retryJudge: async (evaluationId: string) => {
    const { data } = await apiClient.post<JudgeFeedbackResponse>(
      `/api/evaluations/${evaluationId}/retry`
    );
    return data;
  },
};
```

---

## Routing & Navigation

### Route Structure (App Router)

```
app/
├── (auth)/
│   └── login/
│       └── page.tsx                 # Login page (future)
├── dashboard/
│   ├── page.tsx                     # Main dashboard
│   └── layout.tsx                   # Dashboard layout
├── evaluation/
│   ├── [id]/
│   │   ├── page.tsx                 # Evaluation session
│   │   └── feedback/
│   │       └── page.tsx             # Judge feedback
│   └── page.tsx                     # Start new evaluation
├── statistics/
│   ├── page.tsx                     # Statistics overview
│   └── metrics/
│       └── [metric]/
│           └── page.tsx             # Per-metric stats
├── layout.tsx                       # Root layout
├── page.tsx                         # Landing page
└── globals.css                      # Global styles
```

### Navigation Patterns

#### Programmatic Navigation
```typescript
import { useRouter } from 'next/navigation';

// Start evaluation
router.push('/evaluation/new');

// After submission
router.push(`/evaluation/${id}/feedback`);

// Back to dashboard
router.push('/dashboard');
```

#### Link Navigation
```tsx
import Link from 'next/link';

<Link href="/statistics" className="nav-link">
  Statistics
</Link>
```

---

## Real-time Features

### Judge Feedback Polling Strategy

**Approach:** Optimistic UI + Polling

**Implementation:**
```typescript
// features/judge-feedback/hooks/use-judge-feedback.ts
import { useQuery } from '@tanstack/react-query';

export function useJudgeFeedback(evaluationId: string) {
  return useQuery({
    queryKey: queryKeys.evaluations.feedback(evaluationId),
    queryFn: () => evaluationApi.getFeedback(evaluationId),
    refetchInterval: (data) => {
      // Poll every 3 seconds if processing, stop if complete
      return data?.status === 'processing' ? 3000 : false;
    },
    retry: 3,
  });
}
```

**UI States:**
1. **Processing:** Show progress indicator + estimated time
2. **Success:** Display complete feedback
3. **Error:** Show retry button with error message

### Future Enhancement: Server-Sent Events (SSE)

When backend adds SSE support:
```typescript
// lib/sse/client.ts
export function connectJudgeFeedback(evaluationId: string) {
  const eventSource = new EventSource(
    `/api/evaluations/${evaluationId}/stream`
  );

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Update state
  };

  return eventSource;
}
```

---

## Performance Optimization

### Code Splitting Strategy

1. **Route-based Splitting:** Automatic with Next.js App Router
2. **Component Lazy Loading:**
```typescript
// Lazy load heavy components
const StatsDashboard = dynamic(
  () => import('@/components/ui/organisms/StatsDashboard'),
  { loading: () => <Skeleton /> }
);
```

### Image Optimization
```tsx
import Image from 'next/image';

<Image
  src="/images/metrics/truthfulness.png"
  alt="Truthfulness metric"
  width={400}
  height={300}
  priority={false}
  placeholder="blur"
/>
```

### Font Optimization
```typescript
// app/layout.tsx
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-sans',
});
```

### Bundle Analysis
```bash
# Analyze bundle size
npm run build
npm run analyze
```

---

## Testing Strategy

### Unit Tests (Vitest)

**What to Test:**
- Utility functions
- Custom hooks logic
- State management

**Example:**
```typescript
// lib/utils/__tests__/format-score.test.ts
import { describe, it, expect } from 'vitest';
import { formatScore } from '../format-score';

describe('formatScore', () => {
  it('should format score as integer', () => {
    expect(formatScore(4.5)).toBe('5');
  });

  it('should return N/A for null', () => {
    expect(formatScore(null)).toBe('N/A');
  });
});
```

### Integration Tests (Playwright)

**What to Test:**
- Complete evaluation flow
- Judge feedback polling
- Statistics dashboard

**Example:**
```typescript
// tests/e2e/evaluation-flow.spec.ts
import { test, expect } from '@playwright/test';

test('complete evaluation flow', async ({ page }) => {
  // Start evaluation
  await page.goto('/evaluation/new');
  await page.selectOption('primary-metric', 'Truthfulness');
  await page.click('button[type="submit"]');

  // Wait for question
  await expect(page.locator('[data-testid="question-card"]')).toBeVisible();

  // Submit evaluation
  await page.fill('[data-testid="metric-truthfulness-score"]', '4');
  await page.fill('[data-testid="metric-truthfulness-reasoning"]', 'Good response');
  // ... fill other metrics
  await page.click('button[type="submit"]');

  // Wait for feedback
  await expect(page.locator('[data-testid="judge-feedback"]')).toBeVisible({
    timeout: 30000,
  });
});
```

### Visual Regression Tests (Storybook - Optional)

**What to Test:**
- Component appearance
- Responsive layouts
- Dark/light mode

---

## Development Workflow

### Setup Instructions

```bash
# 1. Create frontend directory
cd /home/yigitalp/Projects/MentorMind
mkdir frontend
cd frontend

# 2. Initialize Next.js project
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir

# 3. Install dependencies
npm install zustand @tanstack/react-query axios
npm install framer-motion lucide-react
npm install -D vitest @playwright/test

# 4. Setup shadcn/ui
npx shadcn-ui@latest init

# 5. Add components
npx shadcn-ui@latest add button card input label
npx shadcn-ui@latest add slider textarea badge progress
npx shadcn-ui@latest add skeleton alert dialog

# 6. Setup environment
cp .env.example .env.local
```

### Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=MentorMind
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Development Server

```bash
# Run dev server
npm run dev

# Runs on http://localhost:3000
```

### Build & Production

```bash
# Build for production
npm run build

# Start production server
npm start

# Run type checking
npm run type-check

# Run linting
npm run lint

# Run tests
npm run test
```

---

## Deployment

### Vercel Deployment (Recommended)

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Deploy
vercel

# 3. Set environment variables in Vercel dashboard
# NEXT_PUBLIC_API_URL=https://api.mentormind.com
```

### Docker Deployment (Alternative)

```dockerfile
# Dockerfile
FROM node:20-alpine AS base

# Dependencies
FROM base AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Builder
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Runner
FROM base AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
```

### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/frontend-ci.yml
name: Frontend CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check
      - run: npm run test
      - run: npm run build
```

---

## Project Structure

```
frontend/
├── .github/                      # CI/CD
│   └── workflows/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Auth route group
│   │   └── login/
│   ├── dashboard/                # Dashboard pages
│   │   ├── page.tsx
│   │   └── layout.tsx
│   ├── evaluation/               # Evaluation flow
│   │   ├── [id]/
│   │   │   ├── page.tsx
│   │   │   └── feedback/
│   │   │       └── page.tsx
│   │   └── page.tsx
│   ├── statistics/               # Statistics pages
│   │   ├── page.tsx
│   │   └── metrics/
│   │       └── [metric]/
│   │           └── page.tsx
│   ├── api/                      # API routes (proxy)
│   │   └── health/
│   │       └── route.ts
│   ├── layout.tsx                # Root layout
│   ├── page.tsx                  # Landing page
│   └── globals.css               # Global styles
├── components/                   # Shared components
│   ├── ui/                       # shadcn/ui components
│   │   ├── atoms/
│   │   ├── molecules/
│   │   └── organisms/
│   ├── forms/                    # Form components
│   └── visualizations/           # Charts, graphs
├── features/                     # Feature slices
│   ├── evaluation-session/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── types.ts
│   ├── judge-feedback/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── types.ts
│   └── statistics-dashboard/
│       ├── components/
│       ├── hooks/
│       └── services/
├── lib/                          # Shared utilities
│   ├── api/                      # API client
│   │   ├── client.ts
│   │   └── errors.ts
│   ├── query/                    # TanStack Query
│   │   ├── client.ts
│   │   └── keys.ts
│   ├── store/                    # Zustand stores
│   │   ├── evaluation.ts
│   │   └── ui.ts
│   ├── utils.ts                  # Utility functions
│   └── constants.ts              # App constants
├── styles/                       # Additional styles
│   └── globals.css
├── public/                       # Static assets
│   ├── images/
│   ├── icons/
│   └── fonts/
├── tests/                        # Test files
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── .env.example                  # Environment template
├── .eslintrc.json                # ESLint config
├── .prettierrc                   # Prettier config
├── next.config.js                # Next.js config
├── package.json                  # Dependencies
├── tailwind.config.ts            # Tailwind config
├── tsconfig.json                 # TypeScript config
└── vitest.config.ts              # Vitest config
```

---

## Design Decisions & UI Specifications

### Design Narrative: "The Evaluation Terminal"

**Theme:** Technical & Hacker (Terminal-inspired, dark mode, data-dense)

**Setting:** A dark, data-dense terminal where users analyze AI outputs like code reviewers inspecting pull requests.

**Protagonist:** The user is a "Data Sensei in Training" - developing AI evaluation expertise through focused practice.

**Conflict:** Evaluating 8 metrics simultaneously creates cognitive load. The UI must reduce this friction through progressive disclosure.

**Resolution:** A guided, phased interface that reveals complexity progressively, not all at once.

### Visual Language

```css
/* Terminal-inspired Dark Theme */
:root {
  /* Backgrounds */
  --bg-primary: #0a0a0a;      /* Deep black */
  --bg-secondary: #111111;    /* Slightly lighter */
  --bg-tertiary: #1a1a1a;     /* Card backgrounds */

  /* Terminal Accents */
  --accent-terminal: #00ff41;  /* Terminal green */
  --accent-warning: #ffb000;   /* Amber */
  --accent-error: #ff4444;     /* Red */
  --accent-info: #00d9ff;      /* Cyan */

  /* Metric Colors (8 distinct for visual distinction) */
  --metric-truthfulness: #4dabf7;   /* Blue */
  --metric-helpfulness: #51cf66;   /* Green */
  --metric-safety: #ff6b6b;        /* Red */
  --metric-bias: #cc5de8;          /* Purple */
  --metric-clarity: #ffd43b;       /* Yellow */
  --metric-consistency: #22b8cf;   /* Cyan */
  --metric-efficiency: #ff922b;    /* Orange */
  --metric-robustness: #f06595;    /* Pink */

  /* Typography */
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
}

/* CRT Subtle Effect (Optional) */
.terminal::before {
  content: '';
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: repeating-linear-gradient(
    0deg, rgba(0,0,0,0.1), rgba(0,0,0,0.1) 1px, transparent 1px, transparent 2px
  );
  pointer-events: none;
  z-index: 9999;
}
```

### Layout Architecture

**Hybrid Layout:** Sidebar Navigation + Immersive Evaluation

```
┌─────────────────────────────────────────────────────────┐
│                    TerminalLayout                        │
├──────────┬──────────────────────────────────────────────┤
│          │                                               │
│  Side-   │         MainContentArea                       │
│  bar     │  ┌─────────────────────────────────────────┐ │
│  (Col-   │  │                                         │ │
│  lapsed) │  │   Dynamic View (Dashboard/Eval/Stats)   │ │
│          │  │                                         │ │
│ - Logo   │  └─────────────────────────────────────────┘ │
│ - Dash   │                                               │
│ - Eval   │  NOTE: During evaluation, sidebar            │
│ - Stats  │        collapses for full-screen immersion   │
│          │                                               │
└──────────┴──────────────────────────────────────────────┘
```

### Component Hierarchy

```
TerminalLayout (Root - Server Component)
├── SidebarNavigation (Client Component - Collapsible)
│   ├── Logo + App Name
│   ├── Nav Items (Dashboard, Evaluation, Statistics)
│   └── User Status (Meta score display)
│
├── MainContentArea
│   ├── DashboardView (Overview + Quick Start)
│   │   ├── WelcomeCard
│   │   ├── QuickStartButton (per metric)
│   │   └── RecentActivityList
│   │
│   ├── EvaluationView (Full-screen immersive - Client)
│   │   ├── QuestionCard (Question + Model Response)
│   │   │   ├── QuestionText
│   │   │   ├── ModelResponse (with syntax highlighting)
│   │   │   └── ModelBadge (K model identifier)
│   │   │
│   │   ├── EvaluationForm (Accordion - Client)
│   │   │   └── MetricSlider (Score 1-5 + Reasoning)
│   │   │       ├── RangeInput (1-5)
│   │   │       ├── TextArea (reasoning)
│   │   │       └── MetricBadge (color-coded)
│   │   │
│   │   └── SubmitBar (Sticky bottom - Client)
│   │       ├── DraftIndicator (auto-save status)
│   │       ├── ValidationMessage
│   │       └── SubmitButton
│   │
│   ├── FeedbackView (Judge Results - Client)
│   │   ├── MetaScoreDisplay (Large 1-5 score with animation)
│   │   ├── OverallFeedbackCard
│   │   ├── ExpandableMetricsTable (Progressive disclosure)
│   │   │   └── MetricAlignmentRow (user vs judge)
│   │   └── PatternHighlights (ChromaDB references)
│   │
│   └── StatisticsView (Server + Client)
│       ├── PerformanceOverview (Total evaluations, avg meta score)
│       ├── MetricCards (8 metrics with trends)
│       ├── TrendChart (Line chart - Recharts)
│       └── RadarChart (Metric comparison - Recharts)
```

### Interaction Patterns

#### 1. Evaluation Form (Accordion)
```
┌─────────────────────────────────────────────────┐
│  Truthfulness ▼                     [Score: 4]   │
│  ┌───────────────────────────────────────────┐ │
│  │  [=====●=====] 1 2 3 4 5                 │ │
│  │                                           │ │
│  │  Reasoning: _________________________     │ │
│  │            [Good response, accurate...]   │ │
│  └───────────────────────────────────────────┘ │
│  Helpfulness ▶                     [N/A]       │
│  Safety ▶                           [N/A]       │
│  ... (5 more collapsed)                        │
└─────────────────────────────────────────────────┘
```

#### 2. Judge Feedback (Progressive Disclosure)
```
Step 1: Meta Score
┌─────────────────────────────────────────────────┐
│              JUDGE EVALUATION                   │
│                                                 │
│           ★★★★★  4.2 / 5.0                    │
│        Excellent evaluation!                   │
│                                                 │
│           [View Detailed Feedback]             │
└─────────────────────────────────────────────────┘

Step 2: Detailed View (After click)
┌─────────────────────────────────────────────────┐
│  Overall Feedback                              │
│  ┌───────────────────────────────────────────┐ │
│  │ Excellent evaluation on Truthfulness!     │ │
│  │ Slight overestimation on Clarity...       │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  Metric Alignment [Expand All]                  │
│  ┌───────────────────────────────────────────┐ │
│  │ Truthfulness     You: 4  Judge: 4  ✓      │ │
│  │ Clarity          You: 5  Judge: 4  ⚠ +1   │ │
│  │ ...                                        │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  Past Patterns Referenced                       │
│  ┌───────────────────────────────────────────┐ │
│  │ • Overestimating minor errors (3rd time)  │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### Animation Specifications

**Framer Motion Spring Constants:**
```typescript
export const springs = {
  snappy: { stiffness: 400, damping: 17 },   // Buttons, micro-interactions
  fluid: { stiffness: 100, damping: 20 },    // Modals, accordions
  heavy: { stiffness: 50, damping: 10 },     // Background parallax
};
```

**Key Animations:**
1. **Page Transitions:** Fade out (200ms) → Slide in (300ms)
2. **Accordion Expand:** Spring-based, `height: auto`
3. **Feedback Reveal:** Staggered children, 40ms delay increment
4. **Metric Slider:** Real-time color change (red → yellow → green)
5. **Meta Score:** Count-up animation (0 → 4.2)

### Data Flow

```
USER ACTION                    COMPONENT              API/SERVER
─────────────────────────────────────────────────────────────────
Click "Start Evaluation"  →  DashboardView  →    POST /api/questions/generate
                               │                        ↓
                               │                  { question, response }
                               ↓
QuestionCard displays data ←───┘

Fill form (Accordion)    →  EvaluationForm → (Draft: localStorage)
                               │
Click "Submit"          →  SubmitBar     →    POST /api/evaluations/submit
                               │                        ↓
                               │                  { evaluation_id }
                               ↓
Navigate to feedback    →  Router.push(`/evaluation/${id}/feedback`)
                               │
                               ↓
Polling starts          →  useJudgeFeedback →  GET /api/evaluations/${id}/feedback
                               │       (every 3s)         ↓
                               │                  { status: "processing" }
                               ↓                        ↓
                         LoadingSpinner           Continue polling...
                               │                        ↓
                               │                  { status: "complete",
                               │                    feedback: {...} }
                               ↓
JudgeFeedbackPanel displays results
```

### State Management Split

**Server State (TanStack Query):**
```typescript
// Queries
const { data: question } = useQuery({
  queryKey: ['question', metric],
  queryFn: () => api.generateQuestion(metric)
});

const { data: feedback, status } = useQuery({
  queryKey: ['feedback', evaluationId],
  queryFn: () => api.getFeedback(evaluationId),
  refetchInterval: status === 'processing' ? 3000 : false
});
```

**Client State (Zustand):**
```typescript
// Evaluation Store
interface EvaluationStore {
  currentQuestion: Question | null;
  currentResponse: ModelResponse | null;
  evaluationDraft: Record<string, MetricEvaluation>;
  sidebarOpen: boolean;

  // Actions
  setCurrentQuestion: (q: Question) => void;
  updateDraft: (metric: string, data: MetricEvaluation) => void;
  toggleSidebar: () => void;
}
```

### File Structure (Implementation)

```
frontend/
├── app/
│   ├── layout.tsx                 # TerminalLayout wrapper
│   ├── page.tsx                   # Dashboard (redirect)
│   ├── globals.css                # Dark theme + CRT effects
│   ├── dashboard/
│   │   └── page.tsx               # Dashboard overview
│   ├── evaluation/
│   │   ├── page.tsx               # New evaluation start
│   │   └── [id]/
│   │       ├── page.tsx           # Evaluation session
│   │       └── feedback/
│   │           └── page.tsx       # Judge feedback results
│   └── statistics/
│       └── page.tsx               # Statistics dashboard
│
├── components/
│   ├── layout/
│   │   ├── SidebarNavigation.tsx  # Collapsible sidebar
│   │   └── TerminalLayout.tsx     # Root layout wrapper
│   ├── dashboard/
│   │   ├── WelcomeCard.tsx
│   │   └── QuickStartButton.tsx
│   ├── evaluation/
│   │   ├── QuestionCard.tsx
│   │   ├── EvaluationForm.tsx     # Accordion with 8 metrics
│   │   ├── MetricSlider.tsx       # Score input + reasoning
│   │   └── SubmitBar.tsx          # Sticky bottom bar
│   ├── feedback/
│   │   ├── MetaScoreDisplay.tsx   # Large score with animation
│   │   ├── OverallFeedbackCard.tsx
│   │   ├── ExpandableMetricsTable.tsx
│   │   └── PatternHighlights.tsx  # ChromaDB patterns
│   └── statistics/
│       ├── PerformanceOverview.tsx
│       ├── MetricCards.tsx
│       ├── TrendChart.tsx         # Recharts line
│       └── RadarChart.tsx         # Recharts radar
│
├── lib/
│   ├── api/
│   │   ├── client.ts              # Axios instance
│   │   └── evaluations.ts         # API functions
│   ├── query/
│   │   ├── client.ts              # QueryClient setup
│   │   └── keys.ts                # Query keys factory
│   ├── store/
│   │   ├── evaluation.ts          # Zustand store
│   │   └── ui.ts                  # UI preferences store
│   └── utils/
│       ├── format-score.ts        # Score formatting
│       └── metric-colors.ts       # Color utilities
│
├── styles/
│   └── themes.css                 # Terminal dark theme
│
└── hooks/
    ├── use-judge-feedback.ts      # Polling hook
    ├── use-evaluation-draft.ts    # Draft auto-save
    └── use-metric-colors.ts       # Color mapping
```

---

## Implementation Progress

### Phase 1: Foundation ✅ COMPLETED (2026-02-02)
- [x] Initialize Next.js project with TypeScript (Next.js 16.1.6)
- [x] Setup Tailwind CSS v4 + shadcn/ui (11 components added)
- [x] Configure TanStack Query + Zustand (stores created)
- [x] Setup API client with axios (evaluations API ready)
- [x] Create base layout with providers (dark theme default)
- [x] Setup routing structure (dashboard, evaluation, statistics routes)
- [x] Terminal dark theme colors + metric colors defined
- [x] Utility functions (metric-colors, format-score)
- [x] Zustand stores (evaluation, ui)
- [x] Query client + keys factory
- [x] Dashboard page with metric quick-start cards
- [x] Docker configuration (Dockerfile, docker-compose updated)
- [x] .env files (.env.local, .env.example)

**Current Files Created:**
```
frontend/
├── app/
│   ├── layout.tsx              # ✅ Root layout with providers
│   ├── page.tsx                # ✅ Redirect to dashboard
│   ├── globals.css             # ✅ Terminal dark theme
│   └── dashboard/
│       └── page.tsx           # ✅ Dashboard overview
├── components/
│   ├── providers.tsx           # ✅ QueryClient provider
│   └── ui/                     # ✅ shadcn/ui components (11)
├── lib/
│   ├── api/
│   │   ├── client.ts           # ✅ Axios client
│   │   └── evaluations.ts      # ✅ Evaluation API
│   ├── query/
│   │   ├── client.ts           # ✅ QueryClient setup
│   │   └── keys.ts             # ✅ Query keys
│   ├── store/
│   │   ├── evaluation.ts       # ✅ Evaluation store
│   │   └── ui.ts               # ✅ UI preferences store
│   └── utils/
│       ├── metric-colors.ts    # ✅ Color utilities
│       └── format-score.ts     # ✅ Score formatting
├── Dockerfile                  # ✅ Production Dockerfile
├── .dockerignore               # ✅ Docker ignore file
├── .env.local                  # ✅ Environment variables
└── .env.example                # ✅ Environment template
```

### Phase 2: Core Features (Week 2-3) ✅ COMPLETED (2026-02-02)
- [x] Implement evaluation flow
- [x] Create evaluation form component (Accordion with 8 metrics)
- [x] QuestionCard component (Question + Model Response display)
- [x] MetricSlider component (Score 1-5 + Reasoning)
- [x] Draft auto-save (localStorage integration)
- [x] Evaluation page (Metric selection + Evaluation)
- [x] Implement judge feedback polling (use-judge-feedback hook)
- [x] Build feedback display components (MetaScoreDisplay, AlignmentAnalysis)
- [x] Create [id]/feedback route with complete UI
- [x] Processing state with progress indicator
- [x] Complete/Failed state handling

**Phase 2 Files Created:**
```
components/evaluation/
├── MetricSlider.tsx       # ✅ Accordion metric input with slider
├── EvaluationForm.tsx     # ✅ Form with 8 metrics + submit bar
└── QuestionCard.tsx       # ✅ Display question + model response

app/evaluation/
├── page.tsx               # ✅ Metric selection + evaluation session
└── [id]/feedback/
    └── page.tsx           # ✅ Judge feedback display with polling

hooks/
└── use-judge-feedback.ts  # ✅ Polling hook for judge feedback
```

### Phase 3: Statistics & Dashboard (Week 4) - NEXT
- [ ] Implement statistics dashboard
- [ ] Create performance charts
- [ ] Add metric comparison views
- [ ] Implement trend visualization

### Phase 4: Polish & Testing (Week 5)
- [ ] Add animations with Framer Motion
- [ ] Implement error boundaries
- [ ] Write comprehensive tests
- [ ] Performance optimization
- [ ] Accessibility audit

### Phase 5: Deployment (Week 6)
- [ ] Setup Vercel deployment
- [ ] Configure environment variables
- [ ] Setup monitoring (Sentry, Vercel Analytics)
- [ ] Final testing in production

---

**End of FRONTEND.md**

This document provides a complete roadmap for building the MentorMind frontend. All technical decisions are justified based on project requirements, scalability needs, and best practices for 2025.
