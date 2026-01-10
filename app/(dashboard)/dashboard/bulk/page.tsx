"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Progress } from "@/components/ui/progress"
import { CSVUpload } from "@/components/bulk-generator/csv-upload"
import { type CSVRow } from "@/lib/utils/csv"
import { replaceVariables } from "@/lib/utils/csv"
import { Volume2, Download, Loader2 } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface ElevenLabsModel {
  model_id: string
  name: string
}

interface ElevenLabsVoice {
  voice_id: string
  name: string
}

interface GenerationResult {
  index: number
  filename: string
  url: string
  text: string
}

export default function BulkGenerationPage() {
  const [models, setModels] = useState<ElevenLabsModel[]>([])
  const [voices, setVoices] = useState<ElevenLabsVoice[]>([])
  const [selectedModelId, setSelectedModelId] = useState<string>("")
  const [selectedVoiceId, setSelectedVoiceId] = useState<string>("")
  const [csvData, setCsvData] = useState<CSVRow[]>([])
  const [detectedVariables, setDetectedVariables] = useState<string[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [progress, setProgress] = useState(0)
  const [results, setResults] = useState<GenerationResult[]>([])
  const [batchId] = useState(() => `batch-${Date.now()}`)

  // Voice settings
  const [stability, setStability] = useState(0.5)
  const [similarityBoost, setSimilarityBoost] = useState(0.5)
  const [style, setStyle] = useState(0.0)
  const [useSpeakerBoost, setUseSpeakerBoost] = useState(false)
  const [speed, setSpeed] = useState<number | undefined>(undefined)

  useEffect(() => {
    // Fetch models and voices
    Promise.all([
      fetch("/api/elevenlabs/models").then((r) => r.json()),
      fetch("/api/elevenlabs/voices").then((r) => r.json()),
    ]).then(([modelsData, voicesData]) => {
      if (modelsData.models) setModels(modelsData.models)
      if (voicesData.voices) setVoices(voicesData.voices)
    })
  }, [])

  const handleDataLoaded = (data: CSVRow[], variables: string[]) => {
    setCsvData(data)
    setDetectedVariables(variables)
    setResults([])
  }

  const handleGenerate = async () => {
    if (!csvData.length || !selectedModelId || !selectedVoiceId) {
      return
    }

    setIsGenerating(true)
    setProgress(0)
    setResults([])

    try {
      const response = await fetch("/api/bulk/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          rows: csvData,
          voiceId: selectedVoiceId,
          modelId: selectedModelId,
          voiceSettings: {
            stability,
            similarity_boost: similarityBoost,
            style,
            use_speaker_boost: useSpeakerBoost,
            speed,
          },
          batchId,
        }),
      })

      const data = await response.json()

      if (response.ok) {
        setResults(data.results || [])
        setProgress(100)
      } else {
        console.error("Generation error:", data.error)
      }
    } catch (error) {
      console.error("Error generating audio:", error)
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Bulk Generation</h1>
        <p className="text-muted-foreground mt-2">
          Generate multiple audio files from CSV with variable personalization
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="space-y-6">
          <CSVUpload onDataLoaded={handleDataLoaded} />

          <Card>
            <CardHeader>
              <CardTitle>Voice Settings</CardTitle>
              <CardDescription>Configure voice parameters for generation</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Model</Label>
                <Select value={selectedModelId} onValueChange={setSelectedModelId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a model" />
                  </SelectTrigger>
                  <SelectContent>
                    {models.map((model) => (
                      <SelectItem key={model.model_id} value={model.model_id}>
                        {model.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Voice</Label>
                <Select value={selectedVoiceId} onValueChange={setSelectedVoiceId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a voice" />
                  </SelectTrigger>
                  <SelectContent>
                    {voices.map((voice) => (
                      <SelectItem key={voice.voice_id} value={voice.voice_id}>
                        {voice.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Stability: {stability.toFixed(1)}</Label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={stability}
                  onChange={(e) => setStability(parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>

              <div className="space-y-2">
                <Label>Similarity Boost: {similarityBoost.toFixed(1)}</Label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={similarityBoost}
                  onChange={(e) => setSimilarityBoost(parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>

              <div className="space-y-2">
                <Label>Style: {style.toFixed(1)}</Label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={style}
                  onChange={(e) => setStyle(parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="speaker-boost"
                  checked={useSpeakerBoost}
                  onChange={(e) => setUseSpeakerBoost(e.target.checked)}
                />
                <Label htmlFor="speaker-boost">Use Speaker Boost</Label>
              </div>
            </CardContent>
          </Card>

          <Button
            onClick={handleGenerate}
            disabled={!csvData.length || !selectedModelId || !selectedVoiceId || isGenerating}
            className="w-full"
            size="lg"
          >
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Volume2 className="mr-2 h-4 w-4" />
                Generate Audio
              </>
            )}
          </Button>

          {isGenerating && (
            <div className="space-y-2">
              <Label>Progress</Label>
              <Progress value={progress} />
            </div>
          )}
        </div>

        <div className="space-y-6">
          {results.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Generated Audio ({results.length} files)</CardTitle>
                <CardDescription>Download individual files or all as ZIP</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {results.map((result) => (
                    <div
                      key={result.index}
                      className="flex items-center justify-between p-3 border rounded-lg"
                    >
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{result.filename}</p>
                        <p className="text-xs text-muted-foreground truncate">{result.text}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <audio controls className="h-8">
                          <source src={result.url} type="audio/mpeg" />
                        </audio>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => window.open(result.url, "_blank")}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
