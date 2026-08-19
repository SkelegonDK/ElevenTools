"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Download, Trash2, Loader2 } from "lucide-react"

interface Generation {
  id: string
  text: string
  voice_id: string
  model_id: string
  blob_url: string
  filename: string
  created_at: string
  batch_id?: string | null
}

export default function HistoryPage() {
  const [generations, setGenerations] = useState<Generation[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [deletingIds, setDeletingIds] = useState<Set<string>>(new Set())

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      setIsLoading(true)
      const response = await fetch("/api/history")
      if (response.ok) {
        const data = await response.json()
        setGenerations(data.generations || [])
      }
    } catch (error) {
      console.error("Error loading history:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm("PURGE this audio file?")) return
    setDeletingIds((prev) => new Set(prev).add(id))
    try {
      const response = await fetch(`/api/history?id=${id}`, { method: "DELETE" })
      if (response.ok) {
        setGenerations((prev) => prev.filter((g) => g.id !== id))
      }
    } catch (error) {
      console.error("Error deleting:", error)
    } finally {
      setDeletingIds((prev) => {
        const next = new Set(prev)
        next.delete(id)
        return next
      })
    }
  }

  const formatTimestamp = (dateString: string) => {
    const d = new Date(dateString)
    return d.toISOString().replace("T", " ").slice(0, 19) + "Z"
  }

  const grouped = generations.reduce((acc, gen) => {
    const key = gen.batch_id || "single"
    if (!acc[key]) acc[key] = []
    acc[key].push(gen)
    return acc
  }, {} as Record<string, Generation[]>)

  return (
    <div className="space-y-8">
      <header className="border-b border-foreground/20 pb-6">
        <div className="label-section mb-3">[ 03 ] // HISTORY</div>
        <div className="flex items-end justify-between gap-6">
          <h1 className="heading-display text-[clamp(2.5rem,6vw,5rem)] text-foreground">
            ARCHIVE
          </h1>
          <div className="hidden md:block">
            <div className="border border-foreground/25 px-4 py-3 font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
              <div>RECORDS</div>
              <div className="mt-1 font-bold tabular-nums text-foreground">
                {String(generations.length).padStart(4, "0")}
              </div>
            </div>
          </div>
        </div>
        <p className="mt-4 max-w-2xl font-mono text-sm text-muted-foreground">
          Recall, audition, and purge prior generations. Stored locally — no remote copy.
        </p>
      </header>

      {isLoading ? (
        <div className="border border-foreground/20 bg-card p-16">
          <div className="flex items-center justify-center gap-3 font-mono text-xs uppercase tracking-[0.18em] text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin text-primary" />
            READING ARCHIVE
          </div>
        </div>
      ) : generations.length === 0 ? (
        <div className="border border-foreground/20 bg-card p-16">
          <div className="flex flex-col items-center justify-center gap-3 text-center">
            <div className="font-display text-6xl text-foreground/15">▢</div>
            <p className="font-mono text-xs uppercase tracking-[0.18em] text-muted-foreground">
              ARCHIVE EMPTY
            </p>
            <p className="max-w-xs font-mono text-[11px] text-foreground/40">
              Generated audio files appear here.
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-8">
          {Object.entries(grouped).map(([batchId, batchGenerations]) => (
            <section key={batchId} className="border border-foreground/25 bg-card">
              <div className="flex items-baseline justify-between border-b border-foreground/15 px-5 py-3">
                <div className="flex items-baseline gap-3">
                  <span className="font-mono text-[10px] font-bold tracking-[0.18em] text-muted-foreground">
                    [{batchId === "single" ? "SOLO" : "BULK"}]
                  </span>
                  <h2 className="font-mono text-xs font-bold uppercase tracking-[0.18em] text-foreground">
                    {batchId === "single" ? "Singles" : batchId.substring(0, 24)}
                  </h2>
                </div>
                <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
                  {batchGenerations.length} FILE{batchGenerations.length !== 1 ? "S" : ""}
                </span>
              </div>

              <ul className="divide-y divide-foreground/15">
                {batchGenerations.map((gen, idx) => (
                  <li key={gen.id} className="grid grid-cols-12 gap-4 px-5 py-4">
                    <div className="col-span-12 flex items-baseline gap-3 md:col-span-7">
                      <span className="font-mono text-[10px] font-bold tabular-nums text-primary">
                        {String(idx + 1).padStart(3, "0")}
                      </span>
                      <div className="min-w-0 flex-1 space-y-1.5">
                        <div className="flex flex-wrap items-baseline gap-2">
                          <span className="truncate font-mono text-xs font-bold text-foreground">
                            {gen.filename}
                          </span>
                          <Badge variant="outline">{gen.model_id}</Badge>
                        </div>
                        <p className="line-clamp-2 font-mono text-[11px] leading-snug text-muted-foreground">
                          {gen.text}
                        </p>
                        <div className="flex flex-wrap gap-x-4 gap-y-1 font-mono text-[10px] uppercase tracking-[0.14em] text-foreground/40">
                          <span>VOICE · <span className="text-foreground/60">{gen.voice_id}</span></span>
                          <span>{formatTimestamp(gen.created_at)}</span>
                        </div>
                      </div>
                    </div>

                    <div className="col-span-12 flex items-center justify-between gap-3 md:col-span-5 md:justify-end">
                      <audio controls src={gen.blob_url} className="w-full max-w-[280px]" />
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => window.open(gen.blob_url, "_blank")}
                          title="Download"
                        >
                          <Download className="h-3.5 w-3.5" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDelete(gen.id)}
                          disabled={deletingIds.has(gen.id)}
                          title="Purge"
                        >
                          {deletingIds.has(gen.id) ? (
                            <Loader2 className="h-3.5 w-3.5 animate-spin" />
                          ) : (
                            <Trash2 className="h-3.5 w-3.5" />
                          )}
                        </Button>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>
      )}
    </div>
  )
}
