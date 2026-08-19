/**
 * Model capabilities detection for ElevenLabs models.
 *
 * v3 went GA in Feb 2026 with audio tags + Text-to-Dialogue.
 * Turbo v2 / Turbo v2.5 are deprecated — superseded by Flash v2.5
 * (same latency, half the credit cost). They are still recognised here
 * (via the pattern fall-back) for backwards compatibility if the API
 * returns them.
 */

// Allow-list of model IDs that explicitly support speed control
const SPEED_SUPPORTED_MODELS = new Set([
  'eleven_multilingual_v2',
  'eleven_flash_v2_5',
  'eleven_flash_v2',
  'eleven_v3',
  'eleven_multilingual_v3',
  'eleven_multilingual_sts_v2',
])

// Allow-list of model IDs that support Audio Tags (v3 family)
const AUDIO_TAGS_SUPPORTED_MODELS = new Set(['eleven_v3', 'eleven_multilingual_v3'])

// Pattern-based detection for models that might support speed (covers
// deprecated Turbo variants and unknown future model IDs).
const SPEED_SUPPORT_PATTERNS = ['multilingual', 'turbo_v2', 'flash_v2', '_v3']

const AUDIO_TAGS_SUPPORT_PATTERNS = ['_v3']

export function supportsSpeed(modelId: string): boolean {
  if (!modelId) return false
  if (SPEED_SUPPORTED_MODELS.has(modelId)) return true
  const lower = modelId.toLowerCase()
  return SPEED_SUPPORT_PATTERNS.some((p) => lower.includes(p))
}

export function supportsAudioTags(modelId: string): boolean {
  if (!modelId) return false
  if (AUDIO_TAGS_SUPPORTED_MODELS.has(modelId)) return true
  const lower = modelId.toLowerCase()
  return AUDIO_TAGS_SUPPORT_PATTERNS.some((p) => lower.includes(p))
}

const NO_SPEAKER_BOOST_MODELS = new Set(['eleven_monolingual_v1', 'eleven_multilingual_v1'])
const NO_STYLE_MODELS = new Set(['eleven_monolingual_v1', 'eleven_multilingual_v1'])

export function supportsSpeakerBoost(modelId: string): boolean {
  if (!modelId) return true
  return !NO_SPEAKER_BOOST_MODELS.has(modelId)
}

export function supportsStyle(modelId: string): boolean {
  if (!modelId) return true
  return !NO_STYLE_MODELS.has(modelId)
}

/**
 * v3 introduces three recommended stability presets:
 *   Creative ~0.3 — most expressive, may hallucinate
 *   Natural  ~0.5 — balanced (default)
 *   Robust   ~0.8 — consistent, ignores audio tags more
 */
export type StabilityMode = 'creative' | 'natural' | 'robust'

export const STABILITY_PRESETS: Record<StabilityMode, number> = {
  creative: 0.3,
  natural: 0.5,
  robust: 0.8,
}

export function supportsStabilityPresets(modelId: string): boolean {
  return supportsAudioTags(modelId)
}

/**
 * Text-to-Dialogue (multi-speaker) is currently v3-only.
 */
export function supportsDialogue(modelId: string): boolean {
  return supportsAudioTags(modelId)
}

/**
 * Deprecated models still surface in the /models API. We don't hide them,
 * but we flag them so the UI can show a deprecation hint.
 */
const DEPRECATED_MODELS = new Set(['eleven_turbo_v2', 'eleven_turbo_v2_5'])

export function isDeprecated(modelId: string): boolean {
  return DEPRECATED_MODELS.has(modelId)
}

export function getModelCapabilities(modelId: string): {
  speed: boolean
  audioTags: boolean
  speakerBoost: boolean
  style: boolean
  stabilityPresets: boolean
  dialogue: boolean
  deprecated: boolean
} {
  return {
    speed: supportsSpeed(modelId),
    audioTags: supportsAudioTags(modelId),
    speakerBoost: supportsSpeakerBoost(modelId),
    style: supportsStyle(modelId),
    stabilityPresets: supportsStabilityPresets(modelId),
    dialogue: supportsDialogue(modelId),
    deprecated: isDeprecated(modelId),
  }
}
