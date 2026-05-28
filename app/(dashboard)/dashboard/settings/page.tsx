"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Save, Loader2, Check } from "lucide-react"
import { ModelSelector } from "@/components/model-selector"

export default function SettingsPage() {
  const [defaultTranslationModel, setDefaultTranslationModel] = useState("")
  const [defaultEnhancementModel, setDefaultEnhancementModel] = useState("")
  const [showFreeOnlyTranslation, setShowFreeOnlyTranslation] = useState(false)
  const [showFreeOnlyEnhancement, setShowFreeOnlyEnhancement] = useState(false)
  const [isLoadingSettings, setIsLoadingSettings] = useState(true)
  const [isSavingModels, setIsSavingModels] = useState(false)
  const [savedFlash, setSavedFlash] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
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
    } catch (e) {
      console.error("Error loading default models:", e)
    } finally {
      setIsLoadingSettings(false)
    }
  }

  const handleSaveModels = async () => {
    setIsSavingModels(true)
    setError(null)
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
        setSavedFlash(true)
        setTimeout(() => setSavedFlash(false), 1800)
      } else {
        const data = await response.json()
        setError(`Failed to save: ${data.error}`)
      }
    } catch (e) {
      console.error(e)
      setError("Failed to save default models")
    } finally {
      setIsSavingModels(false)
    }
  }

  return (
    <div className="space-y-8">
      <header className="border-b border-foreground/20 pb-6">
        <div className="label-section mb-3">[ 04 ] // SETTINGS</div>
        <div className="flex items-end justify-between gap-6">
          <h1 className="heading-display text-[clamp(2.5rem,6vw,5rem)] text-foreground">
            OPERATOR<br />
            <span className="text-primary">PREFS</span>
          </h1>
          <div className="hidden md:block">
            <div className="border border-foreground/25 px-4 py-3 font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
              <div>STORAGE</div>
              <div className="mt-1 font-bold text-foreground">SQLITE · KEY/VAL</div>
            </div>
          </div>
        </div>
        <p className="mt-4 max-w-2xl font-mono text-sm text-muted-foreground">
          Wire defaults for translation and script enhancement. Used when no model is explicitly selected
          downstream.
        </p>
      </header>

      <section className="relative border border-foreground/25 bg-card">
        <div className="flex items-baseline justify-between border-b border-foreground/15 px-5 py-3">
          <div className="flex items-baseline gap-3">
            <span className="font-mono text-[10px] font-bold tracking-[0.18em] text-muted-foreground">
              [ 01 ]
            </span>
            <h2 className="font-mono text-xs font-bold uppercase tracking-[0.18em] text-foreground">
              Default Models
            </h2>
          </div>
          <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
            {isLoadingSettings ? "READING…" : "READY"}
          </span>
        </div>

        <div className="p-6">
          {isLoadingSettings ? (
            <div className="flex items-center justify-center gap-3 py-12 font-mono text-xs uppercase tracking-[0.18em] text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin text-primary" />
              LOADING CONFIG
            </div>
          ) : (
            <div className="space-y-10">
              <ModelSelector
                title="// Translation Model"
                helpText="Used on the Translation page when no model is selected."
                value={defaultTranslationModel}
                onChange={setDefaultTranslationModel}
                showFreeOnly={showFreeOnlyTranslation}
                onShowFreeOnlyChange={setShowFreeOnlyTranslation}
              />

              <div className="flex items-center gap-3">
                <span className="h-px flex-1 bg-foreground/15" />
                <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-foreground/40">
                  ━━━━━━━━━━
                </span>
                <span className="h-px flex-1 bg-foreground/15" />
              </div>

              <ModelSelector
                title="// Script Enhancement Model"
                helpText="Used for script enhancement when no model is specified."
                value={defaultEnhancementModel}
                onChange={setDefaultEnhancementModel}
                showFreeOnly={showFreeOnlyEnhancement}
                onShowFreeOnlyChange={setShowFreeOnlyEnhancement}
              />

              <div className="flex flex-wrap items-center gap-3 border-t border-foreground/15 pt-6">
                <Button
                  onClick={handleSaveModels}
                  disabled={isSavingModels || !defaultTranslationModel || !defaultEnhancementModel}
                  size="lg"
                >
                  {isSavingModels ? (
                    <>
                      <Loader2 className="mr-2 h-3.5 w-3.5 animate-spin" /> WRITING…
                    </>
                  ) : (
                    <>
                      <Save className="mr-2 h-3.5 w-3.5" /> COMMIT
                    </>
                  )}
                </Button>
                {savedFlash && (
                  <span className="flex items-center gap-2 border border-primary bg-primary/10 px-3 py-2 font-mono text-[11px] font-bold uppercase tracking-[0.14em] text-primary">
                    <Check className="h-3.5 w-3.5" /> WRITTEN
                  </span>
                )}
                {error && (
                  <span className="border border-destructive/40 bg-destructive/10 px-3 py-2 font-mono text-[11px] uppercase tracking-[0.14em] text-destructive">
                    {error}
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      </section>

      <aside className="border border-foreground/20 bg-card">
        <div className="grid grid-cols-12">
          <div className="col-span-1 hazard-band" aria-hidden="true" />
          <div className="col-span-11 px-6 py-4 font-mono text-xs text-muted-foreground">
            <span className="font-bold uppercase tracking-[0.16em] text-foreground">// NOTE.</span>{" "}
            Settings persist locally in <span className="text-foreground">data/eleventools.db</span>.
            No remote sync.
          </div>
        </div>
      </aside>
    </div>
  )
}
