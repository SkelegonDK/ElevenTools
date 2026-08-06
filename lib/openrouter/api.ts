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

  const normalizedQuery = query.toLowerCase().trim()
  
  return models.filter((model) => {
    const modelId = (model.id || '').toLowerCase()
    const modelName = (model.name || '').toLowerCase()
    
    return (
      modelId.includes(normalizedQuery) ||
      modelName.includes(normalizedQuery)
    )
  })
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
  model = 'openrouter/auto',
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
