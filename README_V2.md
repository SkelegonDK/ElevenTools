# ElevenTools v2 - Next.js Migration

This is the Next.js 15 version of ElevenTools, rebuilt with modern web technologies for better performance and developer experience.

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Package Manager**: Bun
- **UI Components**: shadcn/ui + Tailwind CSS + [Vercel AI SDK](https://ai-sdk.dev)
- **Authentication**: Clerk
- **Database**: Supabase (PostgreSQL)
- **File Storage**: Supabase Storage
- **Runtime**: Edge Functions (Vercel Edge Runtime)

## Setup

### Prerequisites

1. Node.js 18+ (or Bun)
2. Supabase account
3. Clerk account

### Installation

```bash
# Install dependencies
bun install

# Copy environment variables
cp .env.local.example .env.local

# Edit .env.local with your credentials
```

### Environment Variables

See `.env.local.example` for required environment variables:

- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` - Clerk publishable key
- `CLERK_SECRET_KEY` - Clerk secret key
- `NEXT_PUBLIC_SUPABASE_URL` - Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Supabase anon key
- `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key
- `WEBHOOK_SECRET` - Clerk webhook secret (for user sync)

### Database Setup

1. Create a new Supabase project
2. Run the SQL schema from `supabase/schema.sql` in the Supabase SQL editor
3. Configure Row Level Security (RLS) policies as defined in the schema

### Clerk Setup

1. Create a Clerk application
2. Configure sign-in/sign-up methods
3. Set up webhook endpoint: `/api/webhooks/clerk`
4. Add webhook secret to `.env.local`

### Development

```bash
# Start development server
bun dev

# Build for production
bun build

# Start production server
bun start
```

## Features

### Bulk Generation
- CSV upload with variable detection
- Batch TTS generation with progress tracking
- Variable personalization (e.g., `{name}`, `{company}`)
- Audio preview and download

### Translation
- Pre-TTS translation via OpenRouter
- Model selection with fuzzy search
- Free model filtering
- Language detection

### Settings
- Secure API key storage (encrypted in Supabase)
- Per-user configuration
- API key validation

### History
- Generation history with audio playback
- Batch organization
- Download functionality

## Project Structure

```
/
├── app/
│   ├── (auth)/          # Authentication pages
│   ├── (dashboard)/     # Dashboard pages
│   └── api/             # API routes (Edge Functions)
├── components/          # React components
│   ├── ui/              # shadcn/ui components
│   └── bulk-generator/   # Bulk generation components
├── lib/                 # Utility libraries
│   ├── elevenlabs/      # ElevenLabs API client
│   ├── openrouter/      # OpenRouter API client
│   └── supabase/        # Supabase client
└── supabase/            # Database schema
```

## Deployment

### Vercel (Recommended)

1. Connect your repository to Vercel
2. Configure environment variables in Vercel dashboard
3. Deploy

The app uses Edge Runtime for optimal performance.

## Roadmap

### Planned Features

#### Script Enhancement (Phase 3)
- **AI-powered script enhancement** using [Vercel AI SDK](https://ai-sdk.dev)
- Support for ElevenLabs v3 Audio Tags enhancement
- Traditional script enhancement for non-v3 models
- Integration with default enhancement model from user settings
- Real-time enhancement preview with streaming responses

**Implementation Notes:**
- Will use AI SDK's `streamText` for real-time streaming
- Leverage AI SDK's unified provider API for OpenRouter integration
- Use AI SDK's built-in error handling and retry logic
- Consider using [AI Elements](https://ai-sdk.dev/elements/overview) pre-built React components for enhanced UI

#### AI SDK Integration
- Migrate translation API to use AI SDK's `streamText` for streaming responses
- Integrate AI SDK's React hooks (`useChat`, `useCompletion`) for better UX
- Leverage AI SDK's provider abstraction for easier model switching
- Use AI SDK's built-in streaming and error handling capabilities

## Migration Notes

This version replaces the Streamlit app with a modern Next.js application. Key differences:

- **Authentication**: Full user accounts with Clerk (vs session-based)
- **Storage**: Supabase Storage (vs local filesystem)
- **Database**: Supabase (vs session state)
- **API**: Edge Functions (vs Python backend)
- **AI Integration**: Vercel AI SDK for LLM interactions

The original Streamlit app has been removed. All functionality has been migrated to React/Next.js.
