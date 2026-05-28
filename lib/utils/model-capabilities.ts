/**
 * Model capabilities detection for ElevenLabs models
 */

// Allow-list of model IDs that explicitly support speed control
const SPEED_SUPPORTED_MODELS = new Set([
  'eleven_multilingual_v2',
  'eleven_turbo_v2_5',
  'eleven_flash_v2_5',
  'eleven_v3',
  'eleven_multilingual_sts_v2',
])

// Allow-list of model IDs that support Audio Tags (v3 models)
const AUDIO_TAGS_SUPPORTED_MODELS = new Set([
  'eleven_v3',
  'eleven_multilingual_v3',
])

// Pattern-based detection for models that might support speed
const SPEED_SUPPORT_PATTERNS = [
  'multilingual', // Multilingual models typically support speed
  'turbo_v2', // Turbo v2+ models support speed
  'flash_v2', // Flash v2+ models support speed
]

// Pattern-based detection for models that might support Audio Tags
const AUDIO_TAGS_SUPPORT_PATTERNS = [
  '_v3', // v3 models support Audio Tags
]

/**
 * Check if a model supports speed control
 */
export function supportsSpeed(modelId: string): boolean {
  if (!modelId) {
    return false
  }

  // Check allow-list first (most reliable)
  if (SPEED_SUPPORTED_MODELS.has(modelId)) {
    return true
  }

  // Fall back to pattern matching for unknown models
  const modelIdLower = modelId.toLowerCase()
  return SPEED_SUPPORT_PATTERNS.some((pattern) => modelIdLower.includes(pattern))
}

/**
 * Check if a model supports Audio Tags (v3 feature)
 */
export function supportsAudioTags(modelId: string): boolean {
  if (!modelId) {
    return false
  }

  // Check allow-list first (most reliable)
  if (AUDIO_TAGS_SUPPORTED_MODELS.has(modelId)) {
    return true
  }

  // Fall back to pattern matching for unknown models
  const modelIdLower = modelId.toLowerCase()
  return AUDIO_TAGS_SUPPORT_PATTERNS.some((pattern) => modelIdLower.includes(pattern))
}

// Models that don't support speaker boost (older models)
const NO_SPEAKER_BOOST_MODELS = new Set([
  'eleven_monolingual_v1',
  'eleven_multilingual_v1',
])

// Models that don't support style parameter (older models)
const NO_STYLE_MODELS = new Set([
  'eleven_monolingual_v1',
  'eleven_multilingual_v1',
])

/**
 * Check if a model supports speaker boost
 */
export function supportsSpeakerBoost(modelId: string): boolean {
  if (!modelId) {
    return true // Default to true for unknown models
  }

  // Check deny-list
  if (NO_SPEAKER_BOOST_MODELS.has(modelId)) {
    return false
  }

  // Most models support speaker boost
  return true
}

/**
 * Check if a model supports style parameter
 */
export function supportsStyle(modelId: string): boolean {
  if (!modelId) {
    return true // Default to true for unknown models
  }

  // Check deny-list
  if (NO_STYLE_MODELS.has(modelId)) {
    return false
  }

  // Most models support style
  return true
}

/**
 * Get all capabilities for a given model
 */
export function getModelCapabilities(modelId: string): {
  speed: boolean
  audioTags: boolean
  speakerBoost: boolean
  style: boolean
} {
  return {
    speed: supportsSpeed(modelId),
    audioTags: supportsAudioTags(modelId),
    speakerBoost: supportsSpeakerBoost(modelId),
    style: supportsStyle(modelId),
  }
}
