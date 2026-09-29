import { describe, expect, it } from 'vitest'
import { searchModelsFuzzy } from '@/lib/openrouter/api'

const models = [
  { id: 'openai/gpt-6-luna', name: 'OpenAI: GPT-6 Luna' },
  { id: 'vendor/lunar', name: 'Lunar' },
  { id: 'vendor/other', name: 'Other' },
]

describe('model fuzzy search', () => {
  it('matches punctuation and reordered tokens', () => {
    expect(searchModelsFuzzy(models, 'LUNA gpt 6')).toEqual([models[0]])
  })
  it('tolerates a typo', () => {
    expect(searchModelsFuzzy(models, 'gpt lunz')).toEqual([models[0]])
  })
  it('ranks exact words before prefixes', () => {
    expect(searchModelsFuzzy(models, 'luna')).toEqual([models[0], models[1]])
  })
  it('handles empty and unmatched searches', () => {
    expect(searchModelsFuzzy(models, '  ')).toEqual(models)
    expect(searchModelsFuzzy(models, 'zzzzzzzz')).toEqual([])
  })
})
