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

export function filterFreeModels(models: OpenRouterModel[]): OpenRouterModel[] {
  return models.filter((model) => {
    const modelId = model.id || ''
    
    // Check if model ID ends with ":free"
    if (modelId.endsWith(':free')) {
      return true
    }

    // Check if both prices are 0
    const pricing = model.pricing || {}
    const promptPrice = pricing.prompt
    const completionPrice = pricing.completion

    if (promptPrice === 0 && completionPrice === 0) {
      return true
    }

    // Handle string prices
    if (
      typeof promptPrice === 'string' &&
      typeof completionPrice === 'string' &&
      parseFloat(promptPrice) === 0 &&
      parseFloat(completionPrice) === 0
    ) {
      return true
    }

    return false
  })
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
