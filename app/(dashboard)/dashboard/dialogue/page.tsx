"use client"

import { useEffect, useMemo, useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { AudioTagPicker } from "@/components/bulk-generator/audio-tag-picker"
import {
  AlertCircle,
  Download,
  Loader2,
  Minus,
  Plus,
  Volume2,
} from "lucide-react"
import {
  type ElevenLabsModel,
  type ElevenLabsVoice,
  type OutputFormat,
} from "@/lib/elevenlabs/types"
import { supportsDialogue } from "@/lib/utils/model-capabilities"
import {
  DEFAULT_STABILITY,
  DIALOGUE_LIMITS,
  OUTPUT_FORMAT_OPTIONS,
  SEED_MAX,
  VOICE_SETTING_RANGES,
  parseSeed,
} from "@/lib/generation/request"
import { Panel } from "@/components/ui/panel"

const { maxUniqueVoices: MAX_UNIQUE_VOICES, maxTotalChars: MAX_TOTAL_CHARS } = DIALOGUE_LIMITS

interface Line {
  voiceId: string
  text: string
}

export default function DialoguePage() {
  const [models, setModels] = useState<ElevenLabsModel[]>([])
  const [voices, setVoices] = useState<ElevenLabsVoice[]>([])
  const [selectedModelId, setSelectedModelId] = useState<string>("eleven_v3")
  const [lines, setLines] = useState<Line[]>([
    { voiceId: "", text: "" },
    { voiceId: "", text: "" },
  ])
  const [stability, setStability] = useState(DEFAULT_STABILITY)
  const [seedInput, setSeedInput] = useState("")
  const [outputFormat, setOutputFormat] = useState<OutputFormat>(OUTPUT_FORMAT_OPTIONS[0].value)
  const seed = parseSeed(seedInput)

  const [isGenerating, setIsGenerating] = useState(false)
  const [result, setResult] = useState<{ url: string; filename: string } | null>(null)
  const [error, setError] = useState<string | null>(null)

  const [modelsError, setModelsError] = useState<string | null>(null)
  const [voicesError, setVoicesError] = useState<string | null>(null)

  const textareaRefs = useRef<Array<HTMLTextAreaElement | null>>([])

  useEffect(() => {
    fetch("/api/elevenlabs/models")
      .then((r) => r.json().then((d) => (r.ok ? d : Promise.reject(d.error))))
      .then((data) => setModels(data.models ?? []))
      .catch((e) => setModelsError(typeof e === "string" ? e : "Failed to load models"))

    fetch("/api/elevenlabs/voices")
      .then((r) => r.json().then((d) => (r.ok ? d : Promise.reject(d.error))))
      .then((data) => setVoices(data.voices ?? []))
      .catch((e) => setVoicesError(typeof e === "string" ? e : "Failed to load voices"))
  }, [])

  const totalChars = useMemo(() => lines.reduce((s, l) => s + l.text.length, 0), [lines])
  const uniqueVoices = useMemo(
    () => new Set(lines.map((l) => l.voiceId).filter(Boolean)).size,
    [lines]
  )
  const modelSupportsDialogue = supportsDialogue(selectedModelId)
  const charsOver = totalChars > MAX_TOTAL_CHARS
  const voicesOver = uniqueVoices > MAX_UNIQUE_VOICES
  const canSubmit =
    !isGenerating &&
    !!selectedModelId &&
    modelSupportsDialogue &&
    !charsOver &&
    !voicesOver &&
    seed.ok &&
    lines.every((l) => l.voiceId && l.text.trim().length > 0)

  const insertTagAt = (idx: number) => (tag: string) => {
    const el = textareaRefs.current[idx]
    const current = lines[idx]?.text ?? ""
    if (!el) {
      updateLine(idx, { text: current + tag })
      return
    }
    const start = el.selectionStart ?? current.length
    const end = el.selectionEnd ?? current.length
    const next = current.slice(0, start) + tag + current.slice(end)
    updateLine(idx, { text: next })
    queueMicrotask(() => {
      const ref = textareaRefs.current[idx]
      if (!ref) return
      const pos = start + tag.length
      ref.focus()
      ref.setSelectionRange(pos, pos)
    })
  }

  const updateLine = (idx: number, patch: Partial<Line>) => {
    setLines((prev) => prev.map((l, i) => (i === idx ? { ...l, ...patch } : l)))
  }

  const addLine = () => {
    if (lines.length >= DIALOGUE_LIMITS.maxLines) return
    setLines((prev) => [...prev, { voiceId: prev[prev.length - 1]?.voiceId ?? "", text: "" }])
  }

  const removeLine = (idx: number) => {
    if (lines.length <= 1) return
    setLines((prev) => prev.filter((_, i) => i !== idx))
  }

  const handleTransmit = async () => {
    setError(null)
    setResult(null)
    setIsGenerating(true)
    try {
      const response = await fetch("/api/elevenlabs/dialogue", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          modelId: selectedModelId,
          inputs: lines.map((l) => ({ voiceId: l.voiceId, text: l.text })),
          stability,
          outputFormat,
          ...(seed.ok && seed.value !== undefined ? { seed: seed.value } : {}),
        }),
      })
      const data = await response.json()
      if (!response.ok) {
        setError(data.error || `Failed (${response.status})`)
      } else {
        setResult({ url: data.url, filename: data.filename })
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Network error")
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="space-y-8">
      <header className="border-b border-foreground/20 pb-6">
        <div className="label-section mb-3">[ 05 ] // DIALOGUE</div>
        <div className="flex items-end justify-between gap-6">
          <h1 className="heading-display text-[clamp(2.5rem,6vw,5rem)] text-foreground">
            MULTI<br />
            <span className="text-primary">SPEAKER</span>
          </h1>
          <div className="hidden md:block">
            <div className="border border-foreground/25 px-4 py-3 font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
              <div>LIMITS</div>
              <div className="mt-1 font-bold text-foreground">
                ≤ {MAX_UNIQUE_VOICES} VOICES · ≤ {MAX_TOTAL_CHARS} CHARS
              </div>
            </div>
          </div>
        </div>
        <p className="mt-4 max-w-2xl font-mono text-sm text-muted-foreground">
          Compose multi-speaker dialogue. v3 model only. Drop in audio tags like{" "}
          <span className="text-primary">[whispers]</span> and{" "}
          <span className="text-primary">[laughs]</span> for delivery hints.
        </p>
      </header>

      <div className="grid gap-8 lg:grid-cols-5">
        <div className="space-y-6 lg:col-span-3">
          {/* MODEL + GLOBAL SETTINGS */}
          <Panel
            code="01"
            title="Cast & Settings"
            hint={modelSupportsDialogue ? "READY" : "v3 REQUIRED"}
          >
            <div className="space-y-5">
              <div className="space-y-2">
                <Label>Model</Label>
                <Select value={selectedModelId} onValueChange={setSelectedModelId}>
                  <SelectTrigger>
                    <SelectValue placeholder="select model" />
                  </SelectTrigger>
                  <SelectContent>
                    {models
                      .filter((m) => supportsDialogue(m.model_id))
                      .map((m) => (
                        <SelectItem key={m.model_id} value={m.model_id}>
                          {m.name}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
                {!modelSupportsDialogue && (
                  <div className="flex items-center gap-2 border border-yellow-500/40 bg-yellow-500/10 px-3 py-2 font-mono text-xs text-yellow-600">
                    <AlertCircle className="h-3.5 w-3.5" />
                    Selected model does not support multi-speaker dialogue.
                  </div>
                )}
                {modelsError && (
                  <div className="flex items-center gap-2 border border-destructive/40 bg-destructive/10 px-3 py-2 font-mono text-xs text-destructive">
                    <AlertCircle className="h-3.5 w-3.5" /> {modelsError}
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <div className="flex items-baseline justify-between">
                  <Label>Stability</Label>
                  <span className="font-mono text-xs font-bold tabular-nums text-primary">
                    {stability.toFixed(2)}
                  </span>
                </div>
                <input
                  type="range"
                  value={stability}
                  {...VOICE_SETTING_RANGES.stability}
                  onChange={(e) => setStability(parseFloat(e.target.value))}
                />
              </div>

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
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <div className="flex items-baseline justify-between">
                  <Label htmlFor="seed-d">Seed</Label>
                  <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-muted-foreground">
                    OPTIONAL · 0–{SEED_MAX}
                  </span>
                </div>
                <Input
                  id="seed-d"
                  inputMode="numeric"
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
            </div>
          </Panel>

          {/* LINES */}
          <Panel
            code="02"
            title="Dialogue Lines"
            hint={`${lines.length} LINE${lines.length === 1 ? "" : "S"} · ${uniqueVoices}/${MAX_UNIQUE_VOICES} VOICES · ${totalChars}/${MAX_TOTAL_CHARS} CHARS`}
          >
            <div className="space-y-5">
              {voicesError && (
                <div className="flex items-center gap-2 border border-destructive/40 bg-destructive/10 px-3 py-2 font-mono text-xs text-destructive">
                  <AlertCircle className="h-3.5 w-3.5" /> {voicesError}
                </div>
              )}

              <ul className="space-y-4">
                {lines.map((line, idx) => (
                  <li
                    key={idx}
                    className="space-y-2 border border-foreground/15 bg-background p-4"
                  >
                    <div className="flex items-baseline justify-between">
                      <span className="font-mono text-[10px] font-bold tabular-nums text-primary">
                        #{String(idx + 1).padStart(2, "0")}
                      </span>
                      <button
                        type="button"
                        onClick={() => removeLine(idx)}
                        disabled={lines.length <= 1}
                        className="border border-foreground/30 p-1 text-foreground transition-colors hover:border-destructive hover:text-destructive disabled:opacity-40"
                        aria-label="Remove line"
                      >
                        <Minus className="h-3 w-3" />
                      </button>
                    </div>
                    <Select
                      value={line.voiceId}
                      onValueChange={(v) => updateLine(idx, { voiceId: v })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="select voice" />
                      </SelectTrigger>
                      <SelectContent>
                        {voices.map((voice) => (
                          <SelectItem key={voice.voice_id} value={voice.voice_id}>
                            {voice.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Textarea
                      ref={(el) => {
                        textareaRefs.current[idx] = el
                      }}
                      value={line.text}
                      onChange={(e) => updateLine(idx, { text: e.target.value })}
                      placeholder="[whispers] Did you hear that?"
                      className="min-h-[80px]"
                    />
                    <AudioTagPicker onInsert={insertTagAt(idx)} />
                  </li>
                ))}
              </ul>

              <Button
                type="button"
                variant="outline"
                onClick={addLine}
                disabled={lines.length >= 20}
                className="w-full"
              >
                <Plus className="mr-2 h-3.5 w-3.5" />
                ADD LINE
              </Button>

              {(charsOver || voicesOver) && (
                <div className="flex items-center gap-2 border border-destructive/40 bg-destructive/10 px-3 py-2 font-mono text-xs text-destructive">
                  <AlertCircle className="h-3.5 w-3.5" />
                  {charsOver ? `Over ${MAX_TOTAL_CHARS} char limit. ` : ""}
                  {voicesOver ? `Over ${MAX_UNIQUE_VOICES} unique voices.` : ""}
                </div>
              )}
            </div>
          </Panel>

          {/* TRANSMIT */}
          <div className="border border-foreground/25 bg-card p-5">
            <div className="flex items-baseline justify-between">
              <div className="label-section">[ 03 ] // TRANSMIT</div>
              <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
                {canSubmit ? "ARMED" : "AWAITING INPUTS"}
              </span>
            </div>
            <Button
              onClick={handleTransmit}
              disabled={!canSubmit}
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
                  GENERATE DIALOGUE
                </>
              )}
            </Button>
            {error && (
              <div className="mt-4 flex items-center gap-2 border border-destructive/40 bg-destructive/10 px-3 py-2 font-mono text-xs text-destructive">
                <AlertCircle className="h-3.5 w-3.5" /> {error}
              </div>
            )}
          </div>
        </div>

        {/* OUTPUT */}
        <div className="lg:col-span-2">
          <Panel
            code="04"
            title="Output"
            hint={result ? "READY" : "EMPTY"}
          >
            {!result ? (
              <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
                <div className="font-display text-5xl text-foreground/15">▢</div>
                <p className="font-mono text-xs uppercase tracking-[0.18em] text-muted-foreground">
                  NO OUTPUT
                </p>
                <p className="max-w-[20ch] font-mono text-[11px] text-foreground/40">
                  Combined dialogue audio appears here after transmission.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex items-baseline justify-between gap-3">
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
                <audio controls src={result.url} className="w-full" />
              </div>
            )}
          </Panel>
        </div>
      </div>
    </div>
  )
}
