"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Save, CheckCircle2, XCircle, Loader2 } from "lucide-react"
import { ModelSelector } from "@/components/model-selector"

interface ApiKeyStatus {
  service: string
  status: "valid" | "invalid" | "not_set" | "checking"
  message?: string
}

export default function SettingsPage() {
  const [elevenLabsKey, setElevenLabsKey] = useState("")
  const [openRouterKey, setOpenRouterKey] = useState("")
  const [elevenLabsStatus, setElevenLabsStatus] = useState<ApiKeyStatus>({
    service: "ElevenLabs",
    status: "not_set",
  })
  const [openRouterStatus, setOpenRouterStatus] = useState<ApiKeyStatus>({
    service: "OpenRouter",
    status: "not_set",
  })
  const [isSaving, setIsSaving] = useState(false)
  
  // Default model settings
  const [defaultTranslationModel, setDefaultTranslationModel] = useState("")
  const [defaultEnhancementModel, setDefaultEnhancementModel] = useState("")
  const [showFreeOnlyTranslation, setShowFreeOnlyTranslation] = useState(false)
  const [showFreeOnlyEnhancement, setShowFreeOnlyEnhancement] = useState(false)
  const [isLoadingSettings, setIsLoadingSettings] = useState(true)
  const [isSavingModels, setIsSavingModels] = useState(false)

  useEffect(() => {
    // Check existing API keys
    checkApiKeys()
    // Load default model settings
    loadDefaultModels()
  }, [])

  const loadDefaultModels = async () => {
    try {
      setIsLoadingSettings(true)
      const response = await fetch("/api/settings/defaults")
      if (response.ok) {
        const data = await response.json()
        setDefaultTranslationModel(data.default_translation_model || "")
        setDefaultEnhancementModel(data.default_enhancement_model || "")
      }
    } catch (error) {
      console.error("Error loading default models:", error)
    } finally {
      setIsLoadingSettings(false)
    }
  }

  const handleSaveModels = async () => {
    setIsSavingModels(true)
    try {
      const response = await fetch("/api/settings/defaults", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          default_translation_model: defaultTranslationModel,
          default_enhancement_model: defaultEnhancementModel,
        }),
      })

      if (response.ok) {
        // Show success feedback
        alert("Default models saved successfully!")
      } else {
        const data = await response.json()
        alert(`Failed to save: ${data.error}`)
      }
    } catch (error) {
      console.error("Error saving default models:", error)
      alert("Failed to save default models")
    } finally {
      setIsSavingModels(false)
    }
  }

  const checkApiKeys = async () => {
    // Check ElevenLabs
    setElevenLabsStatus({ service: "ElevenLabs", status: "checking" })
    try {
      const response = await fetch("/api/elevenlabs/models")
      if (response.ok) {
        setElevenLabsStatus({ service: "ElevenLabs", status: "valid" })
      } else {
        setElevenLabsStatus({
          service: "ElevenLabs",
          status: "invalid",
          message: "API key not configured or invalid",
        })
      }
    } catch {
      setElevenLabsStatus({
        service: "ElevenLabs",
        status: "not_set",
      })
    }

    // Check OpenRouter
    setOpenRouterStatus({ service: "OpenRouter", status: "checking" })
    try {
      const response = await fetch("/api/openrouter/models")
      if (response.ok) {
        setOpenRouterStatus({ service: "OpenRouter", status: "valid" })
      } else {
        setOpenRouterStatus({
          service: "OpenRouter",
          status: "invalid",
          message: "API key not configured or invalid",
        })
      }
    } catch {
      setOpenRouterStatus({
        service: "OpenRouter",
        status: "not_set",
      })
    }
  }

  const handleSave = async () => {
    setIsSaving(true)
    try {
      // Save API keys
      const responses = await Promise.all([
        elevenLabsKey
          ? fetch("/api/settings/api-keys", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                service: "elevenlabs",
                apiKey: elevenLabsKey,
              }),
            })
          : Promise.resolve(null),
        openRouterKey
          ? fetch("/api/settings/api-keys", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                service: "openrouter",
                apiKey: openRouterKey,
              }),
            })
          : Promise.resolve(null),
      ])

      // Recheck status
      await checkApiKeys()

      // Clear input fields
      setElevenLabsKey("")
      setOpenRouterKey("")
    } catch (error) {
      console.error("Error saving API keys:", error)
    } finally {
      setIsSaving(false)
    }
  }

  const getStatusBadge = (status: ApiKeyStatus) => {
    switch (status.status) {
      case "valid":
        return (
          <Badge variant="default" className="bg-green-600">
            <CheckCircle2 className="mr-1 h-3 w-3" />
            Valid
          </Badge>
        )
      case "invalid":
        return (
          <Badge variant="destructive">
            <XCircle className="mr-1 h-3 w-3" />
            Invalid
          </Badge>
        )
      case "checking":
        return (
          <Badge variant="secondary">
            <Loader2 className="mr-1 h-3 w-3 animate-spin" />
            Checking...
          </Badge>
        )
      default:
        return (
          <Badge variant="secondary">Not Set</Badge>
        )
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-2">
          Configure your API keys and preferences
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>API Key Management</CardTitle>
          <CardDescription>
            Store your API keys securely. Keys are encrypted and stored per user.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="elevenlabs-key">ElevenLabs API Key</Label>
                {getStatusBadge(elevenLabsStatus)}
              </div>
              <Input
                id="elevenlabs-key"
                type="password"
                value={elevenLabsKey}
                onChange={(e) => setElevenLabsKey(e.target.value)}
                placeholder="Enter your ElevenLabs API key"
              />
              {elevenLabsStatus.message && (
                <p className="text-sm text-muted-foreground">{elevenLabsStatus.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="openrouter-key">OpenRouter API Key</Label>
                {getStatusBadge(openRouterStatus)}
              </div>
              <Input
                id="openrouter-key"
                type="password"
                value={openRouterKey}
                onChange={(e) => setOpenRouterKey(e.target.value)}
                placeholder="Enter your OpenRouter API key"
              />
              {openRouterStatus.message && (
                <p className="text-sm text-muted-foreground">{openRouterStatus.message}</p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-4">
            <Button onClick={handleSave} disabled={isSaving}>
              {isSaving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Save API Keys
                </>
              )}
            </Button>
            <Button variant="outline" onClick={checkApiKeys}>
              Refresh Status
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Default Model Configuration</CardTitle>
          <CardDescription>
            Configure default models for translation and script enhancement. These defaults will be used when no model is explicitly selected.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {isLoadingSettings ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin" />
            </div>
          ) : (
            <>
              <ModelSelector
                title="Default Translation Model"
                helpText="This model will be used for translations when no model is selected on the Translation page."
                value={defaultTranslationModel}
                onChange={setDefaultTranslationModel}
                showFreeOnly={showFreeOnlyTranslation}
                onShowFreeOnlyChange={setShowFreeOnlyTranslation}
              />

              <Separator />

              <ModelSelector
                title="Default Script Enhancement Model"
                helpText="This model will be used for script enhancement when no model is specified."
                value={defaultEnhancementModel}
                onChange={setDefaultEnhancementModel}
                showFreeOnly={showFreeOnlyEnhancement}
                onShowFreeOnlyChange={setShowFreeOnlyEnhancement}
              />

              <div className="flex items-center gap-4">
                <Button onClick={handleSaveModels} disabled={isSavingModels || !defaultTranslationModel || !defaultEnhancementModel}>
                  {isSavingModels ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="mr-2 h-4 w-4" />
                      Save Default Models
                    </>
                  )}
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
