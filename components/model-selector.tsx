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
    filterModels()
  }, [models, searchQuery, showFreeOnly])

  const fetchModels = async () => {
    try {
      setIsLoading(true)
      const response = await fetch("/api/openrouter/models")
      const data = await response.json()
      if (data.models) {
        setModels(data.models)
      }
    } catch (error) {
      console.error("Error fetching models:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const filterModels = () => {
    let filtered = models

    if (showFreeOnly) {
      filtered = filterFreeModels(filtered)
    }

    if (searchQuery.trim()) {
      filtered = searchModelsFuzzy(filtered, searchQuery.trim())
    }

    setFilteredModels(filtered)
  }

  const isModelFree = (model: OpenRouterModel) => {
    const modelId = model.id || ""
    if (modelId.endsWith(":free")) return true

    const pricing = model.pricing || {}
    const promptPrice = pricing.prompt
    const completionPrice = pricing.completion

    return (
      (promptPrice === 0 && completionPrice === 0) ||
      (typeof promptPrice === "string" &&
        typeof completionPrice === "string" &&
        parseFloat(promptPrice) === 0 &&
        parseFloat(completionPrice) === 0)
    )
  }

  const selectedModel = models.find((m) => m.id === value)

  return (
    <div className="space-y-4">
      <div>
        <Label className="text-base font-semibold">{title}</Label>
        {helpText && <p className="text-sm text-muted-foreground mt-1">{helpText}</p>}
      </div>

      {onShowFreeOnlyChange && (
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id={`free-only-${title}`}
            checked={showFreeOnly}
            onChange={(e) => onShowFreeOnlyChange(e.target.checked)}
            className="rounded"
          />
          <Label htmlFor={`free-only-${title}`} className="text-sm font-normal cursor-pointer">
            Show only free models
          </Label>
        </div>
      )}

      <div className="space-y-2">
        <Label htmlFor={`search-${title}`}>Search Models</Label>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            id={`search-${title}`}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search models..."
            className="pl-9"
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label>Select Model</Label>
        <Select value={value} onValueChange={onChange} disabled={isLoading}>
          <SelectTrigger>
            <SelectValue placeholder={isLoading ? "Loading models..." : "Choose a model"} />
          </SelectTrigger>
          <SelectContent>
            {filteredModels.map((model) => (
              <SelectItem key={model.id} value={model.id}>
                <div className="flex items-center gap-2">
                  <span>{model.name || model.id}</span>
                  {isModelFree(model) && (
                    <Badge variant="secondary" className="text-xs">
                      Free
                    </Badge>
                  )}
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {selectedModel && (
        <div className="p-3 bg-muted rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Selected: {selectedModel.id}</p>
              {selectedModel.pricing && (
                <p className="text-xs text-muted-foreground mt-1">
                  Prompt: ${selectedModel.pricing.prompt}, Completion: ${selectedModel.pricing.completion}
                </p>
              )}
            </div>
            {isModelFree(selectedModel) && (
              <Badge variant="default" className="bg-green-600">
                Free
              </Badge>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
