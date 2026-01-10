"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Languages, Loader2, Search } from "lucide-react"

interface OpenRouterModel {
  id: string
  name: string
  pricing?: {
    prompt: number | string
    completion: number | string
  }
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

  useEffect(() => {
    fetchModels()
  }, [])

  useEffect(() => {
    filterModels()
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

        const pricing = model.pricing || {}
        const promptPrice = pricing.prompt
        const completionPrice = pricing.completion

        if (promptPrice === 0 && completionPrice === 0) return true
        if (
          typeof promptPrice === "string" &&
          typeof completionPrice === "string" &&
          parseFloat(promptPrice) === 0 &&
          parseFloat(completionPrice) === 0
        ) {
          return true
        }

        return false
      })
    }

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase().trim()
      filtered = filtered.filter((model) => {
        const modelId = (model.id || "").toLowerCase()
        const modelName = (model.name || "").toLowerCase()
        return modelId.includes(query) || modelName.includes(query)
      })
    }

    setFilteredModels(filtered)
  }

  const handleTranslate = async () => {
    if (!sourceText || !targetLanguage || !selectedModel) {
      return
    }

    setIsTranslating(true)
    try {
      const response = await fetch("/api/openrouter/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: sourceText,
          targetLanguage,
          model: selectedModel,
        }),
      })

      const data = await response.json()
      if (response.ok) {
        setTranslatedText(data.translatedText || "")
      } else {
        console.error("Translation error:", data.error)
      }
    } catch (error) {
      console.error("Error translating:", error)
    } finally {
      setIsTranslating(false)
    }
  }

  const isModelFree = (model: OpenRouterModel) => {
    const modelId = model.id || ""
    if (modelId.endsWith(":free")) return true

    const pricing = model.pricing || {}
    const promptPrice = pricing.prompt
    const completionPrice = pricing.completion

    return (
      promptPrice === 0 &&
      completionPrice === 0
    ) || (
      typeof promptPrice === "string" &&
      typeof completionPrice === "string" &&
      parseFloat(promptPrice) === 0 &&
      parseFloat(completionPrice) === 0
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Translation</h1>
        <p className="text-muted-foreground mt-2">
          Translate text before generating audio with OpenRouter models
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Source Text</CardTitle>
            <CardDescription>Enter the text you want to translate</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="source-text">Text</Label>
              <Textarea
                id="source-text"
                value={sourceText}
                onChange={(e) => setSourceText(e.target.value)}
                placeholder="Enter text to translate..."
                className="min-h-[200px] font-mono"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="target-language">Target Language</Label>
              <Input
                id="target-language"
                value={targetLanguage}
                onChange={(e) => setTargetLanguage(e.target.value)}
                placeholder="e.g., Spanish, French, German..."
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Model Selection</CardTitle>
            <CardDescription>Choose an OpenRouter model for translation</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="free-only"
                  checked={showFreeOnly}
                  onChange={(e) => setShowFreeOnly(e.target.checked)}
                />
                <Label htmlFor="free-only">Show only free models</Label>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="search-models">Search Models</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search-models"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search models..."
                  className="pl-9"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Select Model</Label>
              <Select value={selectedModel} onValueChange={setSelectedModel}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose a model" />
                </SelectTrigger>
                <SelectContent>
                  {filteredModels.map((model) => (
                    <SelectItem key={model.id} value={model.id}>
                      <div className="flex items-center gap-2">
                        <span>{model.name || model.id}</span>
                        {isModelFree(model) && (
                          <Badge variant="secondary" className="text-xs">Free</Badge>
                        )}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <Button
              onClick={handleTranslate}
              disabled={!sourceText || !targetLanguage || !selectedModel || isTranslating}
              className="w-full"
            >
              {isTranslating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Translating...
                </>
              ) : (
                <>
                  <Languages className="mr-2 h-4 w-4" />
                  Translate
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>

      {translatedText && (
        <Card>
          <CardHeader>
            <CardTitle>Translated Text</CardTitle>
            <CardDescription>Translation result</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="p-4 bg-muted rounded-lg font-mono text-sm whitespace-pre-wrap">
              {translatedText}
            </div>
            <Button
              variant="outline"
              className="mt-4"
              onClick={() => {
                navigator.clipboard.writeText(translatedText)
              }}
            >
              Copy to Clipboard
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
