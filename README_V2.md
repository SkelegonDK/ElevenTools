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

Create a `.env.local` file in the root directory with the following variables:

**Authentication (Clerk):**
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` - Clerk publishable key
- `CLERK_SECRET_KEY` - Clerk secret key
- `WEBHOOK_SECRET` - Clerk webhook secret (for user sync)

**Database (Supabase):**
- `NEXT_PUBLIC_SUPABASE_URL` - Supabase project URL
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` - Supabase publishable key
- `SUPABASE_SECRET_KEY` - Supabase secret key (service role key)

**Service API Keys (configured by deployment operator):**
- `ELEVENLABS_API_KEY` - ElevenLabs API key (shared by all users)
- `OPENROUTER_API_KEY` - OpenRouter API key (shared by all users)

**Rate Limiting (Upstash Redis):**
- `UPSTASH_REDIS_REST_URL` - Upstash Redis REST API URL
- `UPSTASH_REDIS_REST_TOKEN` - Upstash Redis REST API token

> **Note:** This is an open-source service. API keys are configured server-side via `.env.local` (local development) or environment variables (production). Users do not manage their own API keys - they are shared by all users of the deployed instance.
>
> **Rate Limiting Setup:** Create a free Upstash Redis database at https://upstash.com and add the REST URL and token to your environment variables. Rate limiting is disabled if these variables are not set (for development only).

### Database Setup

1. Create a new Supabase project
2. Run the SQL schema from `supabase/schema.sql` in the Supabase SQL editor
3. Note: RLS policies are defined in the schema but are not actively used. The application enforces authorization at the application level using explicit user_id filtering in all database queries.

### Rate Limiting Setup

1. Create a free Upstash Redis database at https://upstash.com
2. Copy the REST URL and token from the Upstash dashboard
3. Add `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` to your `.env.local` file
4. Rate limits are configured per endpoint:
   - Bulk generation: 5 requests/minute
   - Translation: 20 requests/minute
   - Models/Voices: 30 requests/minute
   - History: 30 requests/minute
   - Settings: 10 requests/minute

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
- User preferences and default model configuration
- Per-user settings (default translation model, default enhancement model)

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

### Architecture

ElevenTools is designed as an **open-source service** where:
- **Deployment operator** configures API keys via environment variables
- **All users** share the same API keys (server-side)
- **Users** don't manage API keys - they simply use the service
- **Fork → Deploy → Configure → Use** model

### Local Development

1. Copy `.env.local.example` to `.env.local` (or create it manually)
2. Fill in all required environment variables
3. Run `bun dev` to start the development server

### Production Deployment (Vercel)

1. Connect your repository to Vercel
2. Configure all environment variables in Vercel dashboard:
   - Clerk authentication keys
   - Supabase connection details
   - **ELEVENLABS_API_KEY** (required)
   - **OPENROUTER_API_KEY** (required)
3. Deploy

The app uses Edge Runtime for optimal performance.

> **Important:** Ensure `ELEVENLABS_API_KEY` and `OPENROUTER_API_KEY` are set in your deployment environment. These keys are shared by all users of your deployed instance.

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
