import { supabaseAdmin } from './admin'
import { auth } from '@clerk/nextjs/server'

export async function getApiKey(userId: string, service: 'elevenlabs' | 'openrouter'): Promise<string | null> {
  // Get user from Supabase by clerk_id
  const { data: user, error: userError } = await supabaseAdmin
    .from('users')
    .select('id')
    .eq('clerk_id', userId)
    .single()

  if (userError || !user) {
    return null
  }

  // Get API key for user
  const { data: apiKey, error } = await supabaseAdmin
    .from('api_keys')
    .select('encrypted_key')
    .eq('user_id', user.id)
    .eq('service', service)
    .single()

  if (error || !apiKey) {
    return null
  }

  // TODO: Decrypt the key (for now, assuming it's stored as plaintext - should use encryption in production)
  return apiKey.encrypted_key
}

export async function saveApiKey(
  userId: string,
  service: 'elevenlabs' | 'openrouter',
  apiKey: string
): Promise<void> {
  // Get or create user
  let { data: user } = await supabaseAdmin
    .from('users')
    .select('id')
    .eq('clerk_id', userId)
    .single()

  if (!user) {
    // Create user if doesn't exist
    const { data: newUser, error: createError } = await supabaseAdmin
      .from('users')
      .insert({
        clerk_id: userId,
      })
      .select('id')
      .single()

    if (createError || !newUser) {
      throw new Error('Failed to create user')
    }
    user = newUser
  }

  // TODO: Encrypt the key before storing (for now storing as plaintext - should use encryption in production)
  const encryptedKey = apiKey

  // Upsert API key
  const { error } = await supabaseAdmin
    .from('api_keys')
    .upsert(
      {
        user_id: user.id,
        service,
        encrypted_key: encryptedKey,
        updated_at: new Date().toISOString(),
      },
      {
        onConflict: 'user_id,service',
      }
    )

  if (error) {
    throw new Error(`Failed to save API key: ${error.message}`)
  }
}
