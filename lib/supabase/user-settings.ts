import { supabaseAdmin } from './admin'
import { auth } from '@clerk/nextjs/server'

const DEFAULT_TRANSLATION_MODEL = 'minimax/minimax-m2:free'
const DEFAULT_ENHANCEMENT_MODEL = 'minimax/minimax-m2:free'

export interface UserSettings {
  default_translation_model: string
  default_enhancement_model: string
}

/**
 * Get user settings, creating default if they don't exist
 */
export async function getUserSettings(userId: string): Promise<UserSettings> {
  // Get user from Supabase by clerk_id
  const { data: user, error: userError } = await supabaseAdmin
    .from('users')
    .select('id')
    .eq('clerk_id', userId)
    .single()

  if (userError || !user) {
    throw new Error('User not found')
  }

  // Get or create settings
  let { data: settings } = await supabaseAdmin
    .from('user_settings')
    .select('default_translation_model, default_enhancement_model')
    .eq('user_id', user.id)
    .single()

  if (!settings) {
    // Create default settings
    const { data: newSettings, error: createError } = await supabaseAdmin
      .from('user_settings')
      .insert({
        user_id: user.id,
        default_translation_model: DEFAULT_TRANSLATION_MODEL,
        default_enhancement_model: DEFAULT_ENHANCEMENT_MODEL,
      })
      .select('default_translation_model, default_enhancement_model')
      .single()

    if (createError || !newSettings) {
      throw new Error('Failed to create user settings')
    }
    settings = newSettings
  }

  return {
    default_translation_model: settings.default_translation_model || DEFAULT_TRANSLATION_MODEL,
    default_enhancement_model: settings.default_enhancement_model || DEFAULT_ENHANCEMENT_MODEL,
  }
}

/**
 * Update user settings
 */
export async function updateUserSettings(
  userId: string,
  updates: Partial<UserSettings>
): Promise<UserSettings> {
  // Get user from Supabase by clerk_id
  const { data: user, error: userError } = await supabaseAdmin
    .from('users')
    .select('id')
    .eq('clerk_id', userId)
    .single()

  if (userError || !user) {
    throw new Error('User not found')
  }

  // Upsert settings
  const { data: settings, error } = await supabaseAdmin
    .from('user_settings')
    .upsert(
      {
        user_id: user.id,
        ...updates,
        updated_at: new Date().toISOString(),
      },
      {
        onConflict: 'user_id',
      }
    )
    .select('default_translation_model, default_enhancement_model')
    .single()

  if (error || !settings) {
    throw new Error(`Failed to update user settings: ${error?.message}`)
  }

  return {
    default_translation_model: settings.default_translation_model || DEFAULT_TRANSLATION_MODEL,
    default_enhancement_model: settings.default_enhancement_model || DEFAULT_ENHANCEMENT_MODEL,
  }
}

/**
 * Get default translation model for user
 */
export async function getDefaultTranslationModel(userId: string): Promise<string> {
  const settings = await getUserSettings(userId)
  return settings.default_translation_model
}

/**
 * Get default enhancement model for user
 */
export async function getDefaultEnhancementModel(userId: string): Promise<string> {
  const settings = await getUserSettings(userId)
  return settings.default_enhancement_model
}
