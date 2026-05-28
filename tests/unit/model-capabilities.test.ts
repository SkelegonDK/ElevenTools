import { describe, expect, it } from 'vitest'
import {
  STABILITY_PRESETS,
  getModelCapabilities,
  isDeprecated,
  supportsAudioTags,
  supportsDialogue,
  supportsSpeakerBoost,
  supportsSpeed,
  supportsStabilityPresets,
  supportsStyle,
} from '@/lib/utils/model-capabilities'

describe('model capabilities', () => {
  it('flash v2.5 supports speed but not audio tags', () => {
    expect(supportsSpeed('eleven_flash_v2_5')).toBe(true)
    expect(supportsAudioTags('eleven_flash_v2_5')).toBe(false)
    expect(supportsDialogue('eleven_flash_v2_5')).toBe(false)
  })

  it('v3 supports audio tags, dialogue, and stability presets', () => {
    expect(supportsAudioTags('eleven_v3')).toBe(true)
    expect(supportsDialogue('eleven_v3')).toBe(true)
    expect(supportsStabilityPresets('eleven_v3')).toBe(true)
    expect(supportsSpeed('eleven_v3')).toBe(true)
  })

  it('multilingual v1 does not support style or speaker boost', () => {
    expect(supportsStyle('eleven_multilingual_v1')).toBe(false)
    expect(supportsSpeakerBoost('eleven_multilingual_v1')).toBe(false)
  })

  it('deprecated Turbo models are flagged but still capability-detected', () => {
    expect(isDeprecated('eleven_turbo_v2_5')).toBe(true)
    expect(isDeprecated('eleven_turbo_v2')).toBe(true)
    expect(isDeprecated('eleven_flash_v2_5')).toBe(false)
    // Pattern fallback still detects speed support for legacy turbo models.
    expect(supportsSpeed('eleven_turbo_v2_5')).toBe(true)
  })

  it('unknown model falls back via patterns', () => {
    expect(supportsSpeed('eleven_multilingual_future_x')).toBe(true)
    expect(supportsAudioTags('eleven_multilingual_v3')).toBe(true)
    expect(supportsSpeed('totally_unknown_model')).toBe(false)
    expect(supportsAudioTags('totally_unknown_model')).toBe(false)
  })

  it('empty model id returns falsy', () => {
    expect(supportsSpeed('')).toBe(false)
    expect(supportsAudioTags('')).toBe(false)
  })

  it('stability presets are 0.3 / 0.5 / 0.8', () => {
    expect(STABILITY_PRESETS.creative).toBeCloseTo(0.3, 5)
    expect(STABILITY_PRESETS.natural).toBeCloseTo(0.5, 5)
    expect(STABILITY_PRESETS.robust).toBeCloseTo(0.8, 5)
  })

  it('getModelCapabilities returns the consolidated bag', () => {
    const v3 = getModelCapabilities('eleven_v3')
    expect(v3).toMatchObject({
      speed: true,
      audioTags: true,
      speakerBoost: true,
      style: true,
      stabilityPresets: true,
      dialogue: true,
      deprecated: false,
    })

    const legacy = getModelCapabilities('eleven_monolingual_v1')
    expect(legacy.style).toBe(false)
    expect(legacy.speakerBoost).toBe(false)
    expect(legacy.audioTags).toBe(false)
  })
})
