"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Languages, Loader2, Search, Copy, Check } from "lucide-react"

interface OpenRouterModel {
  id: string
  name: string
  pricing?: {
    prompt: number | string
    completion: number | string
  }
}

function Panel({
  code,
  title,
  hint,
  children,
}: {
  code: string
  title: string
  hint?: string
  children: React.ReactNode
}) {
  return (
    <section className="relative border border-foreground/25 bg-card">
      <div className="flex items-baseline justify-between border-b border-foreground/15 px-5 py-3">
        <div className="flex items-baseline gap-3">
          <span className="font-mono text-[10px] font-bold tracking-[0.18em] text-muted-foreground">
            [{code}]
          </span>
          <h2 className="font-mono text-xs font-bold uppercase tracking-[0.18em] text-foreground">
            {title}
          </h2>
        </div>
        {hint && (
          <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
            {hint}
          </span>
        )}
      </div>
      <div className="p-5">{children}</div>
    </section>
  )
}

export default function TranslationPage() {
  const [models, setModels] = useState<OpenRouterModel[]>([])
  const [filteredModels, setFilteredModels] = useState<OpenRouterModel[]>([])
  const [selectedModel, setSelectedModel] = useState<string>("")
  const [searchQuery, setSearchQuery] = useState("")
  const [showFreeOnly, setShowFreeOnly] = useState(false)
  const [sourceText, setSourceText] = useState("")
  const [targetLanguage, setTargetLanguage] = useState("")
  const [translatedText, setTranslatedText] = useState("")
  const [isTranslating, setIsTranslating] = useState(false)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    fetchModels()
  }, [])

  useEffect(() => {
    filterModels()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [models, searchQuery, showFreeOnly])

  const fetchModels = async () => {
    try {
      const response = await fetch("/api/openrouter/models")
      const data = await response.json()
      if (data.models) {
        setModels(data.models)
        setFilteredModels(data.models)
      }
    } catch (error) {
      console.error("Error fetching models:", error)
    }
  }

  const filterModels = () => {
    let filtered = models
    if (showFreeOnly) {
      filtered = filtered.filter((model) => {
        const modelId = model.id || ""
        if (modelId.endsWith(":free")) return true
        const pricing: { prompt?: number | string; completion?: number | string } = model.pricing || {}
        const p = pricing.prompt
        const c = pricing.completion
        if (p === 0 && c === 0) return true
        if (typeof p === "string" && typeof c === "string" && parseFloat(p) === 0 && parseFloat(c) === 0) {
          return true
        }
        return false
      })
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim()
      filtered = filtered.filter((m) => (m.id || "").toLowerCase().includes(q) || (m.name || "").toLowerCase().includes(q))
    }
    setFilteredModels(filtered)
  }

  const handleTranslate = async () => {
    if (!sourceText || !targetLanguage || !selectedModel) return
    setIsTranslating(true)
    try {
      const response = await fetch("/api/openrouter/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: sourceText, targetLanguage, model: selectedModel }),
      })
      const data = await response.json()
      if (response.ok) setTranslatedText(data.translatedText || "")
    } catch (error) {
      console.error("Error translating:", error)
    } finally {
      setIsTranslating(false)
    }
  }

  const isModelFree = (model: OpenRouterModel) => {
    const modelId = model.id || ""
    if (modelId.endsWith(":free")) return true
    const pricing: { prompt?: number | string; completion?: number | string } = model.pricing || {}
    const p = pricing.prompt
    const c = pricing.completion
    return (p === 0 && c === 0) || (typeof p === "string" && typeof c === "string" && parseFloat(p) === 0 && parseFloat(c) === 0)
  }

  const copy = () => {
    navigator.clipboard.writeText(translatedText)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <div className="space-y-8">
      {/* HEADER */}
      <header className="border-b border-foreground/20 pb-6">
        <div className="label-section mb-3">[ 02 ] // TRANSLATION</div>
        <div className="flex items-end justify-between gap-6">
          <h1 className="heading-display text-[clamp(2.5rem,6vw,5rem)] text-foreground">
            TRANS<span className="text-primary">·</span>LATE
          </h1>
          <div className="hidden md:block">
            <div className="border border-foreground/25 px-4 py-3 font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
              <div>ENGINE</div>
              <div className="mt-1 font-bold text-foreground">OPENROUTER</div>
            </div>
          </div>
        </div>
        <p className="mt-4 max-w-2xl font-mono text-sm text-muted-foreground">
          Route text through any OpenRouter model before voice synthesis. Bring your own model — free
          tiers labelled.
        </p>
      </header>

      <div className="grid gap-8 lg:grid-cols-2">
        <Panel code="01" title="Source" hint={`${sourceText.length} CHAR`}>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="source-text">Text</Label>
              <Textarea
                id="source-text"
                value={sourceText}
                onChange={(e) => setSourceText(e.target.value)}
                placeholder="paste source text…"
                className="min-h-[260px]"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="target-language">Target Language</Label>
              <Input
                id="target-language"
                value={targetLanguage}
                onChange={(e) => setTargetLanguage(e.target.value)}
                placeholder="spanish · french · japanese …"
              />
            </div>
          </div>
        </Panel>

        <Panel code="02" title="Model" hint={`${filteredModels.length} AVAILABLE`}>
          <div className="space-y-4">
            <label className="flex cursor-pointer items-center gap-3">
              <input
                type="checkbox"
                checked={showFreeOnly}
                onChange={(e) => setShowFreeOnly(e.target.checked)}
              />
              <span className="font-mono text-[11px] font-bold uppercase tracking-[0.14em] text-foreground">
                FREE TIER ONLY
              </span>
            </label>

            <div className="space-y-2">
              <Label htmlFor="search-models">Search</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-foreground/40" />
                <Input
                  id="search-models"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="filter models…"
                  className="pl-9"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Select Model</Label>
              <Select value={selectedModel} onValueChange={setSelectedModel}>
                <SelectTrigger>
                  <SelectValue placeholder="choose model" />
                </SelectTrigger>
                <SelectContent>
                  {filteredModels.map((model) => (
                    <SelectItem key={model.id} value={model.id}>
                      <div className="flex w-full items-center gap-2">
                        <span className="flex-1">{model.name || model.id}</span>
                        {isModelFree(model) && (
                          <span className="border border-primary px-1 font-mono text-[9px] font-bold uppercase tracking-[0.14em] text-primary">
                            FREE
                          </span>
                        )}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="pt-2">
              <Button
                onClick={handleTranslate}
                disabled={!sourceText || !targetLanguage || !selectedModel || isTranslating}
                size="lg"
                className="w-full"
              >
                {isTranslating ? (
                  <>
                    <Loader2 className="mr-2 h-3.5 w-3.5 animate-spin" />
                    PROCESSING…
                  </>
                ) : (
                  <>
                    <Languages className="mr-2 h-3.5 w-3.5" />
                    EXECUTE TRANSLATION
                  </>
                )}
              </Button>
            </div>
          </div>
        </Panel>
      </div>

      {/* OUTPUT */}
      <section className="relative border border-foreground/30 bg-card">
        <div className="flex items-baseline justify-between border-b border-foreground/15 px-5 py-3">
          <div className="flex items-baseline gap-3">
            <span className="font-mono text-[10px] font-bold tracking-[0.18em] text-muted-foreground">
              [ 03 ]
            </span>
            <h2 className="font-mono text-xs font-bold uppercase tracking-[0.18em] text-foreground">
              Output
            </h2>
            {translatedText && (
              <Badge variant="secondary">{targetLanguage.toUpperCase() || "—"}</Badge>
            )}
          </div>
          {translatedText && (
            <button
              onClick={copy}
              className="flex items-center gap-2 border border-foreground/40 px-3 py-1 font-mono text-[10px] font-bold uppercase tracking-[0.14em] transition-colors hover:border-primary hover:text-primary"
            >
              {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
              {copied ? "COPIED" : "COPY"}
            </button>
          )}
        </div>
        <div className="p-5">
          {translatedText ? (
            <pre className="whitespace-pre-wrap font-mono text-sm leading-relaxed text-foreground">
              {translatedText}
            </pre>
          ) : (
            <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
              <div className="font-display text-5xl text-foreground/15">▢</div>
              <p className="font-mono text-xs uppercase tracking-[0.18em] text-muted-foreground">
                AWAITING TRANSMISSION
              </p>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
