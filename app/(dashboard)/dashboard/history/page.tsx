"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Download, Trash2, Loader2, Volume2 } from "lucide-react"
import { Separator } from "@/components/ui/separator"

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
    if (!confirm("Are you sure you want to delete this audio file?")) {
      return
    }

    setDeletingIds((prev) => new Set(prev).add(id))
    try {
      const response = await fetch(`/api/history?id=${id}`, {
        method: "DELETE",
      })

      if (response.ok) {
        setGenerations((prev) => prev.filter((g) => g.id !== id))
      } else {
        alert("Failed to delete audio file")
      }
    } catch (error) {
      console.error("Error deleting:", error)
      alert("Failed to delete audio file")
    } finally {
      setDeletingIds((prev) => {
        const next = new Set(prev)
        next.delete(id)
        return next
      })
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString()
  }

  // Group by batch_id for bulk generations
  const groupedGenerations = generations.reduce((acc, gen) => {
    const key = gen.batch_id || "single"
    if (!acc[key]) {
      acc[key] = []
    }
    acc[key].push(gen)
    return acc
  }, {} as Record<string, Generation[]>)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">History</h1>
        <p className="text-muted-foreground mt-2">
          View and manage your generated audio files
        </p>
      </div>

      {isLoading ? (
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin" />
          </CardContent>
        </Card>
      ) : generations.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Volume2 className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">No generated audio files yet</p>
            <p className="text-sm text-muted-foreground mt-2">
              Generate some audio to see it here
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {Object.entries(groupedGenerations).map(([batchId, batchGenerations]) => (
            <Card key={batchId}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>
                      {batchId === "single" ? "Single Generations" : `Batch: ${batchId.substring(0, 8)}`}
                    </CardTitle>
                    <CardDescription>
                      {batchGenerations.length} file{batchGenerations.length !== 1 ? "s" : ""}
                    </CardDescription>
                  </div>
                  {batchId !== "single" && (
                    <Badge variant="secondary">Bulk</Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {batchGenerations.map((gen) => (
                  <div key={gen.id}>
                    <div className="flex items-start gap-4 p-4 border rounded-lg">
                      <div className="flex-1 min-w-0 space-y-2">
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-medium truncate">{gen.filename}</p>
                          <Badge variant="outline" className="text-xs">
                            {gen.model_id}
                          </Badge>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Voice: {gen.voice_id}
                        </p>
                        <p className="text-sm text-muted-foreground line-clamp-2">
                          {gen.text}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {formatDate(gen.created_at)}
                        </p>
                      </div>
                      <div className="flex flex-col gap-2">
                        <audio controls className="h-8">
                          <source src={gen.blob_url} type="audio/mpeg" />
                        </audio>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => window.open(gen.blob_url, "_blank")}
                          >
                            <Download className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDelete(gen.id)}
                            disabled={deletingIds.has(gen.id)}
                          >
                            {deletingIds.has(gen.id) ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <Trash2 className="h-4 w-4" />
                            )}
                          </Button>
                        </div>
                      </div>
                    </div>
                    {gen.id !== batchGenerations[batchGenerations.length - 1].id && (
                      <Separator className="my-4" />
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
