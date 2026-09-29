export interface OpenRouterModel {
  id: string
  name: string
  description?: string
  pricing?: {
    prompt: number | string
    completion: number | string
  }
  context_length?: number
  architecture?: {
    modality: string
    tokenizer: string
    instruct_type?: string
  }
}

const OPENROUTER_API_BASE = 'https://openrouter.ai/api/v1'

export async function fetchModels(apiKey: string): Promise<OpenRouterModel[]> {
  const response = await fetch(`${OPENROUTER_API_BASE}/models`, {
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch models: ${response.statusText}`)
  }

  const data = await response.json()
  return data.data || []
}

/**
 * The single definition of "this model is free".
 *
 * A model counts as free if its id carries the `:free` suffix, or if both
 * prompt and completion prices are zero — OpenRouter reports those either as
 * numbers or as decimal strings, so both forms are handled here.
 */
export function isFreeModel(model: OpenRouterModel): boolean {
  if ((model.id || '').endsWith(':free')) return true

  const pricing: { prompt?: number | string; completion?: number | string } = model.pricing || {}
  const promptPrice = pricing.prompt
  const completionPrice = pricing.completion

  if (promptPrice === 0 && completionPrice === 0) return true

  return (
    typeof promptPrice === 'string' &&
    typeof completionPrice === 'string' &&
    parseFloat(promptPrice) === 0 &&
    parseFloat(completionPrice) === 0
  )
}

export function filterFreeModels(models: OpenRouterModel[]): OpenRouterModel[] {
  return models.filter(isFreeModel)
}

export function searchModelsFuzzy(
  models: OpenRouterModel[],
  query: string
): OpenRouterModel[] {
  if (!query || !query.trim()) {
    return models
  }

  const normalize = (value: string) => value.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim()
  const tokens = normalize(query).split(/\s+/).filter(Boolean)
  if (!tokens.length) return models

  // Token matching ignores punctuation and word order; edit distance allows typos.
  const distance = (a: string, b: string) => {
    let row = Array.from({ length: b.length + 1 }, (_, i) => i)
    for (let i = 1; i <= a.length; i++) {
      const next = [i]
      for (let j = 1; j <= b.length; j++) {
        next[j] = Math.min(next[j - 1] + 1, row[j] + 1, row[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1))
      }
      row = next
    }
    return row[b.length]
  }

  return models.map((model) => {
    const words = normalize(`${model.id} ${model.name || ''}`).split(/\s+/)
    const scores = tokens.map((token) => Math.min(...words.map((word) => {
      if (word === token) return 0
      if (word.startsWith(token)) return 1
      if (word.includes(token)) return 2
      const edits = distance(token, word)
      return token.length >= 3 && edits <= (token.length >= 6 ? 2 : 1) ? 3 + edits : Infinity
    })))
    return { model, score: scores.reduce((sum, score) => sum + score, 0) }
  }).filter(({ score }) => Number.isFinite(score))
    .sort((a, b) => a.score - b.score)
    .map(({ model }) => model)
}

export interface TranslateParams {
  apiKey: string
  text: string
  targetLanguage: string
  model?: string
}

export async function translate({
  apiKey,
  text,
  targetLanguage,
  model = 'openai/gpt-6-luna',
}: TranslateParams): Promise<string> {
  const prompt = `Translate the following text to ${targetLanguage}:\n\n${text}`

  const response = await fetch(`${OPENROUTER_API_BASE}/chat/completions`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model,
      messages: [
        {
          role: 'user',
          content: prompt,
        },
      ],
      max_tokens: 2048,
      temperature: 0.7,
    }),
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Failed to translate: ${error}`)
  }

  const data = await response.json()
  return data.choices[0]?.message?.content?.trim() || ''
}
