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

/**
 * Get all capabilities for a given model
 */
export function getModelCapabilities(modelId: string): {
  speed: boolean
  audioTags: boolean
} {
  return {
    speed: supportsSpeed(modelId),
    audioTags: supportsAudioTags(modelId),
  }
}
