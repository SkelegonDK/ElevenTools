import { defineConfig, devices } from '@playwright/test'

const PORT = 3100

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  retries: 0,
  workers: 1,
  reporter: 'list',
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    trace: 'off',
    headless: true,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: `pnpm dev --port ${PORT}`,
    url: `http://127.0.0.1:${PORT}`,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    env: {
      // The bulk page itself doesn't make any TTS calls; voices/models are
      // intercepted via page.route(). A placeholder API key keeps the API
      // routes from short-circuiting if they ever do load before the route
      // handlers are installed.
      ELEVENLABS_API_KEY: 'pw-stub-key',
    },
  },
})
