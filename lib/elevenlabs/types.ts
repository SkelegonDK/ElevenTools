/**
 * Type-only module — safe to import from client components without dragging
 * the SDK (and its node:* imports) into the browser bundle.
 */

export interface ElevenLabsModel {
  model_id: string
  name: string
}

export interface ElevenLabsVoice {
  voice_id: string
  name: string
}

export interface VoiceSettings {
  stability: number
  similarity_boost: number
  style: number
  use_speaker_boost: boolean
  speed?: number
}

export type OutputFormat =
  | 'mp3_22050_32'
  | 'mp3_44100_32'
  | 'mp3_44100_64'
  | 'mp3_44100_96'
  | 'mp3_44100_128'
  | 'mp3_44100_192'
  | 'pcm_16000'
  | 'pcm_22050'
  | 'pcm_24000'
  | 'pcm_44100'
  | 'pcm_48000'
  | 'ulaw_8000'

export const DEFAULT_OUTPUT_FORMAT: OutputFormat = 'mp3_44100_128'

export type TextNormalization = 'auto' | 'on' | 'off'

export interface DialogueInput {
  voiceId: string
  text: string
}

/**
 * Map an output_format string to the file extension we save it under.
 * Lives here (alongside the OutputFormat type) so callers don't need to
 * touch the SDK-bearing api module to get the extension.
 */
export function extensionForOutputFormat(format: OutputFormat): string {
  if (format.startsWith('mp3_')) return 'mp3'
  if (format.startsWith('pcm_')) return 'pcm'
  if (format.startsWith('ulaw_')) return 'ulaw'
  return 'mp3'
}
