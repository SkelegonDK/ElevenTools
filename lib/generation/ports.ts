import 'server-only'
import { randomUUID } from 'node:crypto'
import { generateAudio, generateDialogue } from '@/lib/elevenlabs/api'
import { insertGeneration } from '@/lib/db'
import { getAudioStore } from '@/lib/storage'
import type { GenerationPorts } from './batch'

/**
 * The production adapter at the generation seam: the ElevenLabs SDK, the audio
 * store, and SQLite. The in-memory adapter used by the unit tests satisfies the
 * same interface — two adapters, one seam.
 */
export function createGenerationPorts(apiKey: string): GenerationPorts {
  const store = getAudioStore()

  return {
    generateAudio: (call) => generateAudio({ apiKey, ...call }),
    generateDialogue: (call) => generateDialogue({ apiKey, ...call }),
    newBatchId: (prefix) => store.newBatchId(prefix),
    newGenerationId: () => randomUUID(),
    save: (batchId, name, ext, bytes) => store.put(batchId, name, ext, bytes),
    persist: (row) => insertGeneration(row),
  }
}

export function readApiKey(): string | null {
  return process.env.ELEVENLABS_API_KEY?.trim() || null
}
