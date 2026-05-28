"use client"

import { useState, useEffect } from "react"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Search } from "lucide-react"
import { OpenRouterModel, filterFreeModels, searchModelsFuzzy } from "@/lib/openrouter/api"

interface ModelSelectorProps {
  title: string
  helpText?: string
  value: string
  onChange: (modelId: string) => void
  showFreeOnly?: boolean
  onShowFreeOnlyChange?: (show: boolean) => void
}

export function ModelSelector({
  title,
  helpText,
  value,
  onChange,
  showFreeOnly = false,
  onShowFreeOnlyChange,
}: ModelSelectorProps) {
  const [models, setModels] = useState<OpenRouterModel[]>([])
  const [filteredModels, setFilteredModels] = useState<OpenRouterModel[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchModels()
  }, [])

  useEffect(() => {
    let filtered = models
    if (showFreeOnly) filtered = filterFreeModels(filtered)
    if (searchQuery.trim()) filtered = searchModelsFuzzy(filtered, searchQuery.trim())
    setFilteredModels(filtered)
  }, [models, searchQuery, showFreeOnly])

  const fetchModels = async () => {
    try {
      setIsLoading(true)
      const response = await fetch("/api/openrouter/models")
      const data = await response.json()
      if (data.models) setModels(data.models)
    } catch (error) {
      console.error("Error fetching models:", error)
    } finally {
      setIsLoading(false)
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

  const selectedModel = models.find((m) => m.id === value)

  return (
    <div className="space-y-4">
      <div>
        <div className="font-mono text-sm font-bold uppercase tracking-[0.14em] text-foreground">
          {title}
        </div>
        {helpText && (
          <p className="mt-1 font-mono text-xs text-muted-foreground">{helpText}</p>
        )}
      </div>

      {onShowFreeOnlyChange && (
        <label className="flex cursor-pointer items-center gap-3">
          <input
            type="checkbox"
            checked={showFreeOnly}
            onChange={(e) => onShowFreeOnlyChange(e.target.checked)}
          />
          <span className="font-mono text-[11px] font-bold uppercase tracking-[0.14em] text-foreground">
            FREE TIER ONLY
          </span>
        </label>
      )}

      <div className="space-y-2">
        <Label htmlFor={`search-${title}`}>Search</Label>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-foreground/40" />
          <Input
            id={`search-${title}`}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="filter models…"
            className="pl-9"
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label>Select Model</Label>
        <Select value={value} onValueChange={onChange} disabled={isLoading}>
          <SelectTrigger>
            <SelectValue placeholder={isLoading ? "loading models…" : "choose model"} />
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

      {selectedModel && (
        <div className="border-l-2 border-primary bg-background p-3">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <div>
              <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
                ACTIVE
              </p>
              <p className="mt-1 font-mono text-xs font-bold text-foreground">{selectedModel.id}</p>
              {selectedModel.pricing && (
                <p className="mt-1 font-mono text-[10px] text-muted-foreground">
                  PROMPT ${selectedModel.pricing.prompt} · COMPLETION ${selectedModel.pricing.completion}
                </p>
              )}
            </div>
            {isModelFree(selectedModel) && <Badge>FREE</Badge>}
          </div>
        </div>
      )}
    </div>
  )
}
