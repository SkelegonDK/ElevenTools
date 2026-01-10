---
name: ElevenTools v2 Migration
overview: Migrate ElevenTools from Streamlit to Next.js 15 with Clerk authentication, Supabase for user data, and Vercel Blob for audio storage. Focus on bulk generation with personalization and translation features that differentiate from native ElevenLabs offerings.
todos:
  - id: setup-nextjs
    content: Initialize Next.js 15 project with Bun, TypeScript, Tailwind, and App Router
    status: completed
  - id: setup-clerk
    content: Configure Clerk authentication with sign-in/sign-up pages and middleware
    status: completed
  - id: setup-supabase
    content: Set up Supabase project, create database schema, and configure client
    status: completed
  - id: setup-shadcn
    content: Initialize shadcn/ui with dark theme and install core components
    status: completed
    dependencies:
      - setup-nextjs
  - id: create-layout
    content: Build base layout with sidebar navigation and dark developer-focused theme
    status: completed
    dependencies:
      - setup-shadcn
      - setup-clerk
  - id: api-elevenlabs
    content: Create Edge API routes for ElevenLabs (voices, models, generate)
    status: completed
    dependencies:
      - setup-supabase
  - id: api-openrouter
    content: Create Edge API routes for OpenRouter (models, translate)
    status: completed
    dependencies:
      - setup-supabase
  - id: api-blob
    content: Integrate Vercel Blob for audio file storage
    status: completed
    dependencies:
      - api-elevenlabs
  - id: bulk-upload
    content: Build CSV upload component with variable detection and preview
    status: completed
    dependencies:
      - create-layout
  - id: bulk-processing
    content: Implement batch TTS generation with progress tracking
    status: completed
    dependencies:
      - api-elevenlabs
      - api-blob
      - bulk-upload
  - id: translation-page
    content: Create translation page with OpenRouter model selection
    status: completed
    dependencies:
      - api-openrouter
      - create-layout
  - id: settings-page
    content: Build settings page for API key management (encrypted storage)
    status: completed
    dependencies:
      - setup-supabase
      - create-layout
  - id: history-page
    content: Create generation history page with audio playback
    status: completed
    dependencies:
      - api-blob
      - create-layout
---

# ElevenTools v2: Next.js Migration Plan

## Overview

Rebuild ElevenTools as a developer-focused Next.js application for bulk text-to-speech generation with personalization and translation capabilities. The new architecture will use Edge Functions for low-latency API calls, Supabase for user data persistence, and Vercel Blob for audio file storage.

## Tech Stack

| Layer | Technology |

|-------|------------|

| Framework | Next.js 15 (App Router) |

| Package Manager | Bun |

| UI Components | shadcn/ui + Tailwind CSS |

| Authentication | Clerk (full auth with user accounts) |

| Database | Supabase (PostgreSQL) |

| File Storage | Vercel Blob |

| API Layer | Edge Functions (Vercel Edge Runtime) |

| Deployment | Vercel |

## Architecture

```mermaid
graph TB
    subgraph client [Client Layer]
        UI[Next.js App Router]
        Clerk[Clerk Auth]
    end
    
    subgraph edge [Edge Layer]
        ElevenLabsAPI["/api/elevenlabs"]
        OpenRouterAPI["/api/openrouter"]
        BulkProcessor["/api/bulk"]
    end
    
    subgraph storage [Storage Layer]
        Supabase[(Supabase DB)]
        VercelBlob[(Vercel Blob)]
    end
    
    subgraph external [External APIs]
        ElevenLabs[ElevenLabs TTS]
        OpenRouter[OpenRouter LLM]
    end
    
    UI --> Clerk
    UI --> ElevenLabsAPI
    UI --> OpenRouterAPI
    UI --> BulkProcessor
    
    ElevenLabsAPI --> ElevenLabs
    ElevenLabsAPI --> VercelBlob
    OpenRouterAPI --> OpenRouter
    BulkProcessor --> ElevenLabs
    BulkProcessor --> VercelBlob
    
    Clerk --> Supabase
    ElevenLabsAPI --> Supabase
```

## Core Features

### 1. Bulk Generation with Personalization

- CSV upload with variable columns (e.g., `{name}`, `{company}`, `{product}`)
- Template text with variable placeholders
- Batch processing with progress tracking
- Parallel generation for speed
- Download as ZIP or individual files

### 2. Translation Pipeline

- Pre-TTS translation via OpenRouter
- Model selection with fuzzy search and free-model filtering
- Language detection and target language selection
- Batch translation before bulk generation

### 3. User Dashboard

- Saved API keys (encrypted in Supabase)
- Generation history with audio playback
- Usage statistics
- Project/batch organization

### 4. Developer Experience

- Dark theme with monospace accents (Linear/Vercel aesthetic)
- Keyboard shortcuts for power users
- JSON/API response previews
- Export generation configs

## Database Schema (Supabase)

```sql
-- Users table (synced from Clerk)
users (
  id UUID PRIMARY KEY,
  clerk_id TEXT UNIQUE,
  email TEXT,
  created_at TIMESTAMP
)

-- Encrypted API keys per user
api_keys (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users,
  service TEXT, -- 'elevenlabs' | 'openrouter'
  encrypted_key TEXT,
  created_at TIMESTAMP
)

-- Generation history
generations (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users,
  batch_id UUID,
  text TEXT,
  voice_id TEXT,
  model_id TEXT,
  blob_url TEXT,
  created_at TIMESTAMP
)
```

## Project Structure

```
/
├── app/
│   ├── (auth)/
│   │   ├── sign-in/
│   │   └── sign-up/
│   ├── (dashboard)/
│   │   ├── bulk/
│   │   ├── translate/
│   │   ├── history/
│   │   └── settings/
│   ├── api/
│   │   ├── elevenlabs/
│   │   ├── openrouter/
│   │   ├── bulk/
│   │   └── webhooks/clerk/
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── ui/ (shadcn)
│   ├── bulk-generator/
│   ├── translation/
│   └── audio-player/
├── lib/
│   ├── supabase/
│   ├── elevenlabs/
│   ├── openrouter/
│   └── utils/
├── .env.local
├── package.json
└── tailwind.config.ts
```

## Implementation Phases

### Phase 1: Foundation (Days 1-2)

- Initialize Next.js 15 project with Bun
- Configure Clerk authentication
- Set up Supabase database and schema
- Install and configure shadcn/ui with dark theme
- Create base layout with navigation

### Phase 2: Core API Layer (Days 3-4)

- ElevenLabs Edge API routes (voices, models, generate)
- OpenRouter Edge API routes (models, translate)
- Supabase integration for API key storage
- Vercel Blob integration for audio storage

### Phase 3: Bulk Generation (Days 5-7)

- CSV upload and parsing component
- Variable detection and template preview
- Batch processing with progress UI
- Audio preview and download functionality
- ZIP export for bulk downloads

### Phase 4: Translation (Days 8-9)

- Translation page with model selection
- Batch translation before TTS
- Language detection integration
- Translation + TTS pipeline

### Phase 5: Polish (Days 10-11)

- Generation history page
- Settings page with API key management
- Dark theme refinement
- Keyboard shortcuts
- Error handling and loading states

## Key Files to Reference

From the current Streamlit app:

- [`scripts/Elevenlabs_functions.py`](scripts/Elevenlabs_functions.py) - ElevenLabs API integration
- [`scripts/openrouter_functions.py`](scripts/openrouter_functions.py) - OpenRouter API integration
- [`scripts/functions.py`](scripts/functions.py) - Variable detection, phonetic conversion
- [`pages/bulk_generation.py`](pages/bulk_generation.py) - Bulk processing logic
- [`pages/translation.py`](pages/translation.py) - Translation flow

## Branch Strategy

Work will be done on a new branch `eleventools-v2` to preserve the Streamlit app while building the Next.js version.

## Getting Started Commands

```bash
# Create and switch to new branch
git checkout -b eleventools-v2

# Initialize Next.js with Bun
bunx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir=false

# Install core dependencies
bun add @clerk/nextjs @supabase/supabase-js @vercel/blob
bun add lucide-react class-variance-authority clsx tailwind-merge

# Initialize shadcn/ui
bunx shadcn@latest init
```