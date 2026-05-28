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

export interface GenerateAudioParams {
  apiKey: string
  voiceId: string
  modelId: string
  text: string
  voiceSettings: VoiceSettings
  languageCode?: string
}

const ELEVENLABS_API_BASE = 'https://api.elevenlabs.io/v1'

export async function fetchModels(apiKey: string): Promise<ElevenLabsModel[]> {
  const response = await fetch(`${ELEVENLABS_API_BASE}/models`, {
    headers: {
      'xi-api-key': apiKey,
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch models: ${response.statusText}`)
  }

  return response.json()
}

export async function fetchVoices(apiKey: string): Promise<ElevenLabsVoice[]> {
  const response = await fetch(`${ELEVENLABS_API_BASE}/voices`, {
    headers: {
      'xi-api-key': apiKey,
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch voices: ${response.statusText}`)
  }

  const data = await response.json()
  return data.voices || []
}

export async function fetchVoiceById(apiKey: string, voiceId: string): Promise<ElevenLabsVoice | null> {
  try {
    const response = await fetch(`${ELEVENLABS_API_BASE}/voices/${voiceId}`, {
      headers: {
        'xi-api-key': apiKey,
      },
    })

    if (!response.ok) {
      return null
    }

    const data = await response.json()
    return {
      voice_id: data.voice_id || voiceId,
      name: data.name || 'Unknown Voice',
    }
  } catch (error) {
    return null
  }
}

export async function generateAudio({
  apiKey,
  voiceId,
  modelId,
  text,
  voiceSettings,
  languageCode,
}: GenerateAudioParams): Promise<ArrayBuffer> {
  const payload: any = {
    text,
    model_id: modelId,
    voice_settings: {
      stability: voiceSettings.stability,
      similarity_boost: voiceSettings.similarity_boost,
      style: voiceSettings.style,
      use_speaker_boost: voiceSettings.use_speaker_boost,
    },
  }

  if (voiceSettings.speed !== undefined) {
    payload.voice_settings.speed = voiceSettings.speed
  }

  if (languageCode) {
    payload.language_code = languageCode
  }

  const response = await fetch(`${ELEVENLABS_API_BASE}/text-to-speech/${voiceId}`, {
    method: 'POST',
    headers: {
      'xi-api-key': apiKey,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Failed to generate audio: ${error}`)
  }

  return response.arrayBuffer()
}
