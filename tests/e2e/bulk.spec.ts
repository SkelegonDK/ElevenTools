import { expect, test } from '@playwright/test'

test('bulk page renders cleanly with stubbed models + voices', async ({ page }) => {
  const consoleErrors: string[] = []
  page.on('console', (msg) => {
    if (msg.type() === 'error') consoleErrors.push(msg.text())
  })
  page.on('pageerror', (err) => consoleErrors.push(err.message))

  await page.route('**/api/elevenlabs/models', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        models: [
          { model_id: 'eleven_v3', name: 'Eleven v3' },
          { model_id: 'eleven_flash_v2_5', name: 'Eleven Flash v2.5' },
        ],
      }),
    })
  })

  await page.route('**/api/elevenlabs/voices', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        voices: [
          { voice_id: 'voice-a', name: 'Voice A' },
          { voice_id: 'voice-b', name: 'Voice B' },
        ],
      }),
    })
  })

  await page.goto('/dashboard/bulk')

  await expect(page.getByRole('heading', { name: /BULK/i })).toBeVisible()
  await expect(page.getByText(/Voice Parameters/i)).toBeVisible()
  await expect(page.getByText(/Output Format/i)).toBeVisible()
  await expect(page.getByText(/Text Normalization/i)).toBeVisible()

  // Filter out benign next.js / favicon noise.
  const meaningful = consoleErrors.filter(
    (e) => !/favicon/i.test(e) && !/Failed to load resource.*404/i.test(e)
  )
  expect(meaningful, meaningful.join('\n')).toHaveLength(0)
})
