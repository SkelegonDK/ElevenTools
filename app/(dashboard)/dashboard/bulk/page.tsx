"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Progress } from "@/components/ui/progress"
import { CSVUpload } from "@/components/bulk-generator/csv-upload"
import { type CSVRow } from "@/lib/utils/csv"
import { Volume2, Download, Loader2, AlertCircle } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import {
  getModelCapabilities,
  STABILITY_PRESETS,
  type StabilityMode,
} from "@/lib/utils/model-capabilities"
import {
  type ElevenLabsModel,
  type ElevenLabsVoice,
  type OutputFormat,
  type TextNormalization,
} from "@/lib/elevenlabs/types"
import {
  DEFAULT_VOICE_SETTINGS,
  NORMALIZATION_OPTIONS,
  OUTPUT_FORMAT_OPTIONS,
  SEED_MAX,
  VOICE_SETTING_RANGES,
  parseSeed,
} from "@/lib/generation/request"
import { Panel } from "@/components/ui/panel"

interface GenerationResult {
  index: number
  filename: string
  url: string
  text: string
}

interface GenerationError {
  index: number
  error: string
}

function SliderRow({
  label,
  value,
  fmt = (v: number) => v.toFixed(1),
  ...rest
}: {
  label: string
  value: number
  fmt?: (v: number) => string
} & Omit<React.InputHTMLAttributes<HTMLInputElement>, "value">) {
  return (
    <div className="space-y-2">
      <div className="flex items-baseline justify-between">
        <Label>{label}</Label>
        <span className="font-mono text-xs font-bold tabular-nums text-primary">
          {fmt(value)}
        </span>
      </div>
      <input type="range" value={value} {...rest} />
    </div>
  )
}

export default function BulkGenerationPage() {
  const [models, setModels] = useState<ElevenLabsModel[]>([])
  const [voices, setVoices] = useState<ElevenLabsVoice[]>([])
  const [selectedModelId, setSelectedModelId] = useState<string>("")
  const [selectedVoiceId, setSelectedVoiceId] = useState<string>("")
  const [csvData, setCsvData] = useState<CSVRow[]>([])
  const [, setDetectedVariables] = useState<string[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [progress, setProgress] = useState(0)
  const [results, setResults] = useState<GenerationResult[]>([])
  const [rowErrors, setRowErrors] = useState<GenerationError[]>([])
  const [batchError, setBatchError] = useState<string | null>(null)
  // The server mints the batch id — it is the thing that owns the directory
  // name — and hands it back on the response.
  const [batchId, setBatchId] = useState<string | null>(null)

  const [isLoadingModels, setIsLoadingModels] = useState(true)
  const [isLoadingVoices, setIsLoadingVoices] = useState(true)
  const [modelsError, setModelsError] = useState<string | null>(null)
  const [voicesError, setVoicesError] = useState<string | null>(null)

  const [useManualVoiceId, setUseManualVoiceId] = useState(false)
  const [manualVoiceId, setManualVoiceId] = useState("")
  const [manualVoiceName, setManualVoiceName] = useState<string | null>(null)
  const [isValidatingVoiceId, setIsValidatingVoiceId] = useState(false)
  const [voiceIdError, setVoiceIdError] = useState<string | null>(null)

  const [stability, setStability] = useState(DEFAULT_VOICE_SETTINGS.stability)
  const [similarityBoost, setSimilarityBoost] = useState(DEFAULT_VOICE_SETTINGS.similarity_boost)
  const [style, setStyle] = useState(DEFAULT_VOICE_SETTINGS.style)
  const [useSpeakerBoost, setUseSpeakerBoost] = useState(DEFAULT_VOICE_SETTINGS.use_speaker_boost)
  const [speed, setSpeed] = useState<number | undefined>(undefined)
  const [outputFormat, setOutputFormat] = useState<OutputFormat>(
    OUTPUT_FORMAT_OPTIONS[0].value
  )
  const [seedInput, setSeedInput] = useState("")
  const [normalization, setNormalization] = useState<TextNormalization>("auto")

  const seed = parseSeed(seedInput)

  const modelCapabilities = selectedModelId ? getModelCapabilities(selectedModelId) : null
  const stabilityMode: StabilityMode | null = modelCapabilities?.stabilityPresets
    ? Object.entries(STABILITY_PRESETS).find(
        ([, v]) => Math.abs(v - stability) < 0.025
      )?.[0] as StabilityMode | undefined ?? null
    : null

  useEffect(() => {
    setIsLoadingModels(true)
    setIsLoadingVoices(true)
    setModelsError(null)
    setVoicesError(null)

    Promise.all([
      fetch("/api/elevenlabs/models")
        .then(async (r) => {
          if (!r.ok) {
            const error = await r.json().catch(() => ({ error: r.statusText }))
            throw new Error(error.error || "Failed to fetch models")
          }
          return r.json()
        })
        .then((data) => {
          if (data.models) setModels(data.models)
          else throw new Error("Invalid response format")
        })
        .catch((error) => setModelsError(error.message || "Failed to load models"))
        .finally(() => setIsLoadingModels(false)),
      fetch("/api/elevenlabs/voices")
        .then(async (r) => {
          if (!r.ok) {
            const error = await r.json().catch(() => ({ error: r.statusText }))
            throw new Error(error.error || "Failed to fetch voices")
          }
          return r.json()
        })
        .then((data) => {
          if (data.voices) setVoices(data.voices)
          else throw new Error("Invalid response format")
        })
        .catch((error) => setVoicesError(error.message || "Failed to load voices"))
        .finally(() => setIsLoadingVoices(false)),
    ])
  }, [])

  useEffect(() => {
    if (!selectedModelId) return
    const capabilities = getModelCapabilities(selectedModelId)
    if (!capabilities.speed) setSpeed(undefined)
    if (!capabilities.style) setStyle(DEFAULT_VOICE_SETTINGS.style)
    if (!capabilities.speakerBoost) setUseSpeakerBoost(DEFAULT_VOICE_SETTINGS.use_speaker_boost)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedModelId])

  const validateVoiceId = async (voiceId: string) => {
    if (!voiceId.trim()) {
      setManualVoiceName(null)
      setVoiceIdError(null)
      return
    }
    if (!/^[a-zA-Z0-9_-]+$/.test(voiceId.trim())) {
      setVoiceIdError("Invalid voice ID format")
      setManualVoiceName(null)
      return
    }
    setIsValidatingVoiceId(true)
    setVoiceIdError(null)
    try {
      const response = await fetch(`/api/elevenlabs/voices/${voiceId.trim()}`)
      const data = await response.json()
      if (response.ok && data.voice) {
        setManualVoiceName(data.voice.name)
        setVoiceIdError(null)
      } else {
        setVoiceIdError(data.error || "Voice not found")
        setManualVoiceName(null)
      }
    } catch {
      setVoiceIdError("Failed to validate voice ID")
      setManualVoiceName(null)
    } finally {
      setIsValidatingVoiceId(false)
    }
  }

  useEffect(() => {
    if (useManualVoiceId && manualVoiceId) {
      const timeoutId = setTimeout(() => validateVoiceId(manualVoiceId), 500)
      return () => clearTimeout(timeoutId)
    } else {
      setManualVoiceName(null)
      setVoiceIdError(null)
    }
  }, [manualVoiceId, useManualVoiceId])

  const getCurrentVoiceId = (): string => (useManualVoiceId ? manualVoiceId.trim() : selectedVoiceId)

  const handleDataLoaded = (data: CSVRow[], variables: string[]) => {
    setCsvData(data)
    setDetectedVariables(variables)
    setResults([])
    setRowErrors([])
    setBatchError(null)
  }

  const handleGenerate = async () => {
    const voiceId = getCurrentVoiceId()
    if (!csvData.length || !selectedModelId || !voiceId) return
    if (useManualVoiceId && voiceIdError) return
    if (!seed.ok) return

    setIsGenerating(true)
    setProgress(0)
    setResults([])
    setRowErrors([])
    setBatchError(null)

    try {
      const response = await fetch("/api/bulk/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          rows: csvData,
          voiceId,
          modelId: selectedModelId,
          voiceSettings: {
            stability,
            similarity_boost: similarityBoost,
            style,
            use_speaker_boost: useSpeakerBoost,
            speed,
          },
          outputFormat,
          ...(seed.value !== undefined ? { seed: seed.value } : {}),
          applyTextNormalization: normalization,
        }),
      })

      const data = await response.json()
      if (!response.ok) {
        setBatchError(data.error || `Request failed (${response.status})`)
        return
      }

      setResults(data.results || [])
      setRowErrors(data.errors || [])
      setBatchId(data.batchId ?? null)
      setProgress(100)
    } catch (error) {
      console.error("Error generating audio:", error)
      setBatchError(error instanceof Error ? error.message : "Failed to reach the server")
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="space-y-8">
      {/* PAGE HEADER */}
      <header className="border-b border-foreground/20 pb-6">
        <div className="label-section mb-3">[ 01 ] // BULK GENERATION</div>
        <div className="flex items-end justify-between gap-6">
          <h1 className="heading-display text-[clamp(2.5rem,6vw,5rem)] text-foreground">
            BULK<br />
            <span className="text-primary">SYNTHESIS</span>
          </h1>
          <div className="hidden md:block">
            <div className="border border-foreground/25 px-4 py-3 font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
              <div>BATCH ID</div>
              <div className="mt-1 font-bold text-foreground">{batchId ?? "—"}</div>
            </div>
          </div>
        </div>
        <p className="mt-4 max-w-2xl font-mono text-sm text-muted-foreground">
          Drop a CSV. Pick a voice. Hit transmit. Variables in {"{"}braces{"}"} are replaced per row before
          dispatch to ElevenLabs.
        </p>
      </header>

      <div className="grid gap-8 lg:grid-cols-5">
        {/* LEFT COLUMN — input + settings + transmit */}
        <div className="space-y-6 lg:col-span-3">
          <CSVUpload
            onDataLoaded={handleDataLoaded}
            audioTagsEnabled={!!modelCapabilities?.audioTags}
          />

          {/* VOICE SETTINGS */}
          <Panel
            code="02"
            title="Voice Parameters"
            hint={selectedModelId ? "ARMED" : "AWAITING MODEL"}
          >
            <div className="space-y-5">
              {/* Model select */}
              <div className="space-y-2">
                <Label>Model</Label>
                <Select
                  value={selectedModelId}
                  onValueChange={setSelectedModelId}
                  disabled={isLoadingModels}
                >
                  <SelectTrigger>
                    <SelectValue
                      placeholder={isLoadingModels ? "loading models…" : "select model"}
                    />
                  </SelectTrigger>
                  <SelectContent>
                    {models.map((model) => (
                      <SelectItem key={model.model_id} value={model.model_id}>
                        {model.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {modelsError && (
                  <div className="flex items-center gap-2 border border-destructive/40 bg-destructive/10 px-3 py-2 font-mono text-xs text-destructive">
                    <AlertCircle className="h-3.5 w-3.5" />
                    {modelsError}
                  </div>
                )}
              </div>

              {/* Voice select / manual */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>Voice</Label>
                  <label className="flex cursor-pointer items-center gap-2 font-mono text-[10px] uppercase tracking-[0.14em] text-muted-foreground">
                    <input
                      type="checkbox"
                      checked={useManualVoiceId}
                      onChange={(e) => {
                        setUseManualVoiceId(e.target.checked)
                        if (!e.target.checked) {
                          setManualVoiceId("")
                          setManualVoiceName(null)
                          setVoiceIdError(null)
                        }
                      }}
                    />
                    MANUAL ID
                  </label>
                </div>

                {useManualVoiceId ? (
                  <div className="space-y-2">
                    <Input
                      placeholder="21m00Tcm4TlvDq8ikWAM"
                      value={manualVoiceId}
                      onChange={(e) => setManualVoiceId(e.target.value)}
                      disabled={isValidatingVoiceId}
                      className={voiceIdError ? "border-destructive" : ""}
                    />
                    {isValidatingVoiceId && (
                      <div className="flex items-center gap-2 font-mono text-xs text-muted-foreground">
                        <Loader2 className="h-3 w-3 animate-spin" /> VALIDATING…
                      </div>
                    )}
                    {manualVoiceName && !voiceIdError && (
                      <div className="font-mono text-xs text-primary">
                        ▸ {manualVoiceName}
                      </div>
                    )}
                    {voiceIdError && (
                      <div className="flex items-center gap-2 border border-destructive/40 bg-destructive/10 px-3 py-2 font-mono text-xs text-destructive">
                        <AlertCircle className="h-3.5 w-3.5" /> {voiceIdError}
                      </div>
                    )}
                  </div>
                ) : (
                  <>
                    <Select
                      value={selectedVoiceId}
                      onValueChange={setSelectedVoiceId}
                      disabled={isLoadingVoices}
                    >
                      <SelectTrigger>
                        <SelectValue
                          placeholder={isLoadingVoices ? "loading voices…" : "select voice"}
                        />
                      </SelectTrigger>
                      <SelectContent>
                        {voices.map((voice) => (
                          <SelectItem key={voice.voice_id} value={voice.voice_id}>
                            {voice.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {voicesError && (
                      <div className="flex items-center gap-2 border border-destructive/40 bg-destructive/10 px-3 py-2 font-mono text-xs text-destructive">
                        <AlertCircle className="h-3.5 w-3.5" /> {voicesError}
                      </div>
                    )}
                  </>
                )}
              </div>

              {/* Output format */}
              <div className="space-y-2">
                <Label>Output Format</Label>
                <Select
                  value={outputFormat}
                  onValueChange={(v) => setOutputFormat(v as OutputFormat)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {OUTPUT_FORMAT_OPTIONS.map((opt) => (
                      <SelectItem key={opt.value} value={opt.value}>
                        {opt.label}
                        {opt.hint ? ` · ${opt.hint}` : ""}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {modelCapabilities?.deprecated && (
                <div className="flex items-center gap-2 border border-yellow-500/40 bg-yellow-500/10 px-3 py-2 font-mono text-xs text-yellow-600">
                  <AlertCircle className="h-3.5 w-3.5" />
                  DEPRECATED · use Flash v2.5 instead
                </div>
              )}

              {/* Divider */}
              <div className="flex items-center gap-2 pt-2">
                <span className="h-px flex-1 bg-foreground/15" />
                <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
                  ANALOG CONTROLS
                </span>
                <span className="h-px flex-1 bg-foreground/15" />
              </div>

              {/* v3 stability presets */}
              {modelCapabilities?.stabilityPresets && (
                <div className="space-y-2">
                  <div className="flex items-baseline justify-between">
                    <Label>Stability Mode (v3)</Label>
                    {stabilityMode && (
                      <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-primary">
                        {stabilityMode.toUpperCase()}
                      </span>
                    )}
                  </div>
                  <div className="flex gap-2">
                    {(Object.keys(STABILITY_PRESETS) as StabilityMode[]).map((mode) => {
                      const v = STABILITY_PRESETS[mode]
                      const active = stabilityMode === mode
                      return (
                        <button
                          key={mode}
                          type="button"
                          onClick={() => setStability(v)}
                          className={`flex-1 border px-3 py-2 font-mono text-[10px] font-bold uppercase tracking-[0.14em] transition-colors ${
                            active
                              ? "border-primary bg-primary text-primary-foreground"
                              : "border-foreground/30 bg-background text-foreground hover:border-primary"
                          }`}
                        >
                          {mode} · {v.toFixed(2)}
                        </button>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* Sliders */}
              <SliderRow
                label="Stability"
                value={stability}
                {...VOICE_SETTING_RANGES.stability}
                onChange={(e) => setStability(parseFloat(e.target.value))}
              />
              <SliderRow
                label="Similarity Boost"
                value={similarityBoost}
                {...VOICE_SETTING_RANGES.similarity_boost}
                onChange={(e) => setSimilarityBoost(parseFloat(e.target.value))}
              />
              {modelCapabilities?.style !== false && (
                <SliderRow
                  label="Style"
                  value={style}
                  {...VOICE_SETTING_RANGES.style}
                  onChange={(e) => setStyle(parseFloat(e.target.value))}
                />
              )}
              {modelCapabilities?.speakerBoost !== false && (
                <label className="flex cursor-pointer items-center gap-3">
                  <input
                    type="checkbox"
                    checked={useSpeakerBoost}
                    onChange={(e) => setUseSpeakerBoost(e.target.checked)}
                  />
                  <span className="font-mono text-[11px] font-bold uppercase tracking-[0.14em] text-foreground">
                    SPEAKER BOOST
                  </span>
                </label>
              )}
              {modelCapabilities?.speed && (
                <SliderRow
                  label="Speed"
                  value={speed ?? 1.0}
                  {...VOICE_SETTING_RANGES.speed}
                  fmt={(v) => `${v.toFixed(2)}×`}
                  onChange={(e) => {
                    const v = parseFloat(e.target.value)
                    setSpeed(v === 1.0 ? undefined : v)
                  }}
                />
              )}

              {/* Seed */}
              <div className="space-y-2">
                <div className="flex items-baseline justify-between">
                  <Label htmlFor="seed">Seed</Label>
                  <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-muted-foreground">
                    OPTIONAL · 0–{SEED_MAX}
                  </span>
                </div>
                <Input
                  id="seed"
                  inputMode="numeric"
                  pattern="[0-9]*"
                  placeholder="blank = random"
                  value={seedInput}
                  onChange={(e) => setSeedInput(e.target.value.replace(/[^0-9]/g, ""))}
                  className={!seed.ok ? "border-destructive" : ""}
                />
                {!seed.ok && (
                  <div className="flex items-center gap-2 border border-destructive/40 bg-destructive/10 px-3 py-2 font-mono text-xs text-destructive">
                    <AlertCircle className="h-3.5 w-3.5" /> {seed.error}
                  </div>
                )}
              </div>

              {/* Text normalization */}
              <div className="space-y-2">
                <Label>Text Normalization</Label>
                <div className="flex gap-2">
                  {NORMALIZATION_OPTIONS.map((mode) => {
                    const active = normalization === mode
                    return (
                      <button
                        key={mode}
                        type="button"
                        onClick={() => setNormalization(mode)}
                        className={`flex-1 border px-3 py-2 font-mono text-[10px] font-bold uppercase tracking-[0.14em] transition-colors ${
                          active
                            ? "border-primary bg-primary text-primary-foreground"
                            : "border-foreground/30 bg-background text-foreground hover:border-primary"
                        }`}
                      >
                        {mode}
                      </button>
                    )
                  })}
                </div>
              </div>
            </div>
          </Panel>

          {/* TRANSMIT */}
          <div className="border border-foreground/25 bg-card p-5">
            <div className="flex items-baseline justify-between">
              <div className="label-section">[ 03 ] // TRANSMIT</div>
              <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
                {csvData.length} ROW{csvData.length === 1 ? "" : "S"} QUEUED
              </span>
            </div>
            <Button
              onClick={handleGenerate}
              disabled={
                !csvData.length ||
                !selectedModelId ||
                !getCurrentVoiceId() ||
                isGenerating ||
                !seed.ok ||
                (useManualVoiceId && (!!voiceIdError || isValidatingVoiceId))
              }
              size="lg"
              className="mt-4 w-full"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="mr-2 h-3.5 w-3.5 animate-spin" />
                  TRANSMITTING…
                </>
              ) : (
                <>
                  <Volume2 className="mr-2 h-3.5 w-3.5" />
                  EXECUTE BATCH
                </>
              )}
            </Button>

            {(isGenerating || progress > 0) && (
              <div className="mt-4 space-y-2">
                <div className="flex items-baseline justify-between font-mono text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
                  <span>PROGRESS</span>
                  <span className="text-foreground tabular-nums">{progress}%</span>
                </div>
                <Progress value={progress} />
              </div>
            )}

            {batchError && (
              <div className="mt-4 flex items-start gap-2 border border-destructive/40 bg-destructive/10 px-3 py-2 font-mono text-xs text-destructive">
                <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                <span>{batchError}</span>
              </div>
            )}
          </div>
        </div>

        {/* RIGHT COLUMN — output / results */}
        <div className="lg:col-span-2">
          <Panel
            code="04"
            title="Dispatch Log"
            hint={
              rowErrors.length
                ? `${results.length} OK · ${rowErrors.length} FAILED`
                : results.length
                  ? `${results.length} FILES`
                  : "EMPTY"
            }
            className="sticky top-4"
          >
            {rowErrors.length > 0 && (
              <ul className="mb-4 space-y-2 border border-destructive/40 bg-destructive/10 p-3">
                {rowErrors.map((rowError) => (
                  <li
                    key={rowError.index}
                    className="flex items-start gap-2 font-mono text-[11px] text-destructive"
                  >
                    <span className="font-bold tabular-nums">
                      #{String(rowError.index + 1).padStart(3, "0")}
                    </span>
                    <span className="flex-1">{rowError.error}</span>
                  </li>
                ))}
              </ul>
            )}

            {results.length === 0 && rowErrors.length === 0 ? (
              <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
                <div className="font-display text-5xl text-foreground/15">▢</div>
                <p className="font-mono text-xs uppercase tracking-[0.18em] text-muted-foreground">
                  NO OUTPUT
                </p>
                <p className="max-w-[20ch] font-mono text-[11px] text-foreground/40">
                  Generated audio appears here after transmission.
                </p>
              </div>
            ) : (
              <ul className="divide-y divide-foreground/15">
                {results.map((result) => (
                  <li
                    key={result.index}
                    className="group flex flex-col gap-2 py-3 first:pt-0 last:pb-0"
                  >
                    <div className="flex items-baseline justify-between gap-3">
                      <span className="font-mono text-[10px] font-bold tabular-nums text-primary">
                        #{String(result.index + 1).padStart(3, "0")}
                      </span>
                      <span className="flex-1 truncate font-mono text-xs font-bold text-foreground">
                        {result.filename}
                      </span>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => window.open(result.url, "_blank")}
                      >
                        <Download className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                    <p className="line-clamp-2 font-mono text-[11px] text-muted-foreground">
                      {result.text}
                    </p>
                    <audio controls src={result.url} className="w-full" />
                  </li>
                ))}
              </ul>
            )}
          </Panel>

          {/* Voice tag preview when set */}
          {(selectedVoiceId || manualVoiceName) && (
            <div className="mt-4 border border-foreground/20 bg-card p-4">
              <div className="font-mono text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
                ACTIVE VOICE
              </div>
              <div className="mt-2 flex flex-wrap items-center gap-2">
                <Badge>
                  {manualVoiceName ??
                    voices.find((v) => v.voice_id === selectedVoiceId)?.name ??
                    "—"}
                </Badge>
                <Badge variant="secondary">
                  {(useManualVoiceId ? manualVoiceId : selectedVoiceId) || "—"}
                </Badge>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
