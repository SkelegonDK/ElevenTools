/* eslint-disable react/no-unescaped-entities */
"use client"

import { useState, useCallback, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { parseCSV, detectVariables, type CSVRow } from "@/lib/utils/csv"
import { FileText, X, Info, Download } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { AudioTagPicker } from "@/components/bulk-generator/audio-tag-picker"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

interface CSVUploadProps {
  onDataLoaded: (data: CSVRow[], variables: string[]) => void
  audioTagsEnabled?: boolean
}

export function CSVUpload({ onDataLoaded, audioTagsEnabled = false }: CSVUploadProps) {
  const [file, setFile] = useState<File | null>(null)
  const [csvText, setCsvText] = useState("")
  const [preview, setPreview] = useState<CSVRow[]>([])
  const [detectedVariables, setDetectedVariables] = useState<string[]>([])
  const textareaRef = useRef<HTMLTextAreaElement | null>(null)

  const processCSV = useCallback(
    (text: string) => {
      try {
        const rows = parseCSV(text)
        setPreview(rows.slice(0, 5))

        const allVariables = new Set<string>()
        rows.forEach((row) => {
          Object.values(row).forEach((value) => {
            detectVariables(value).forEach((v) => allVariables.add(v))
          })
        })

        const variablesArray = Array.from(allVariables)
        setDetectedVariables(variablesArray)
        onDataLoaded(rows, variablesArray)
      } catch (error) {
        console.error("Error parsing CSV:", error)
        setPreview([])
        setDetectedVariables([])
        onDataLoaded([], [])
      }
    },
    [onDataLoaded]
  )

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selectedFile = e.target.files?.[0]
      if (selectedFile) {
        setFile(selectedFile)
        const reader = new FileReader()
        reader.onload = (event) => {
          const text = event.target?.result as string
          setCsvText(text)
          processCSV(text)
        }
        reader.readAsText(selectedFile)
      }
    },
    [processCSV]
  )

  const handleTextChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      const text = e.target.value
      setCsvText(text)
      if (text.trim()) {
        processCSV(text)
      } else {
        setPreview([])
        setDetectedVariables([])
        onDataLoaded([], [])
      }
    },
    [onDataLoaded, processCSV]
  )

  const clearFile = useCallback(() => {
    setFile(null)
    setCsvText("")
    setPreview([])
    setDetectedVariables([])
    onDataLoaded([], [])
  }, [onDataLoaded])

  const insertAtCursor = useCallback(
    (snippet: string) => {
      const el = textareaRef.current
      if (!el) {
        const next = (csvText || "") + snippet
        setCsvText(next)
        if (next.trim()) processCSV(next)
        return
      }
      const start = el.selectionStart ?? csvText.length
      const end = el.selectionEnd ?? csvText.length
      const next = csvText.slice(0, start) + snippet + csvText.slice(end)
      setCsvText(next)
      if (next.trim()) processCSV(next)
      // Restore caret right after inserted text
      queueMicrotask(() => {
        if (!textareaRef.current) return
        const pos = start + snippet.length
        textareaRef.current.focus()
        textareaRef.current.setSelectionRange(pos, pos)
      })
    },
    [csvText, processCSV]
  )

  return (
    <section className="relative border border-foreground/25 bg-card">
      {/* Header */}
      <div className="flex items-baseline justify-between border-b border-foreground/15 px-5 py-3">
        <div className="flex items-baseline gap-3">
          <span className="font-mono text-[10px] font-bold tracking-[0.18em] text-muted-foreground">
            [01]
          </span>
          <h2 className="font-mono text-xs font-bold uppercase tracking-[0.18em] text-foreground">
            CSV Input
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <a
            href="/bulk_template.csv"
            download="bulk_template.csv"
            className="flex items-center gap-2 border border-foreground/40 px-2 py-1 font-mono text-[10px] font-bold uppercase tracking-[0.14em] text-foreground transition-colors hover:border-primary hover:text-primary"
            aria-label="Download CSV template"
          >
            <Download className="h-3 w-3" />
            TEMPLATE
          </a>
          <Dialog>
            <DialogTrigger asChild>
              <button
                className="flex items-center gap-2 border border-foreground/40 px-2 py-1 font-mono text-[10px] font-bold uppercase tracking-[0.14em] text-foreground transition-colors hover:border-primary hover:text-primary"
                aria-label="Interpolation guide"
              >
                <Info className="h-3 w-3" />
                GUIDE
              </button>
            </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>// Interpolation Guide</DialogTitle>
              <DialogDescription>
                Variable substitution in CSV-driven bulk generation
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-6 py-4">
              <div className="space-y-2">
                <div className="label-section">▸ MECHANISM</div>
                <p className="font-mono text-xs leading-relaxed text-muted-foreground">
                  Wrap a column name in <code className="text-primary">{`{braces}`}</code> inside any text
                  or filename cell. Per row, each <code className="text-primary">{`{column}`}</code> is
                  replaced with the value from that column in the same row.
                </p>
              </div>

              <div className="space-y-2">
                <div className="label-section">▸ EXAMPLE INPUT</div>
                <pre className="border border-foreground/20 bg-background p-3 font-mono text-[11px] text-foreground overflow-x-auto">
{`text,name,filename
Hello {name},Alice,greeting_{name}.mp3
Welcome {name} to {company},Bob,welcome_{name}.mp3
Hi {firstName} {lastName},John,hi_{firstName}.mp3`}
                </pre>
              </div>

              <div className="space-y-2">
                <div className="label-section">▸ RESULT</div>
                <div className="space-y-2">
                  {[
                    { row: 1, text: "Hello Alice", file: "greeting_Alice.mp3" },
                    { row: 2, text: "Welcome Bob to Acme Corp", file: "welcome_Bob.mp3" },
                    { row: 3, text: "Hi John Doe", file: "hi_John.mp3" },
                  ].map((r) => (
                    <div
                      key={r.row}
                      className="grid grid-cols-12 gap-3 border border-foreground/15 bg-background p-3 font-mono text-xs"
                    >
                      <span className="col-span-1 text-primary">#{r.row}</span>
                      <span className="col-span-7 text-foreground">{r.text}</span>
                      <span className="col-span-4 truncate text-muted-foreground">{r.file}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <div className="label-section">▸ RULES</div>
                <ul className="space-y-1 font-mono text-xs text-muted-foreground">
                  <li className="flex gap-2"><span className="text-primary">·</span> Names are case-sensitive.</li>
                  <li className="flex gap-2"><span className="text-primary">·</span> Multiple variables per cell are supported.</li>
                  <li className="flex gap-2"><span className="text-primary">·</span> Variables work in both text and filename columns.</li>
                  <li className="flex gap-2"><span className="text-primary">·</span> Unknown variables pass through unchanged.</li>
                </ul>
              </div>

              <div className="border-l-2 border-primary bg-primary/5 px-3 py-2 font-mono text-xs text-foreground">
                <span className="font-bold text-primary">// TIP.</span>{" "}
                Detected variables are listed in the panel below after upload.
              </div>
            </div>
          </DialogContent>
        </Dialog>
        </div>
      </div>

      {/* Body */}
      <div className="space-y-5 p-5">
        <div className="space-y-2">
          <Label htmlFor="csv-file">Upload CSV</Label>
          <div className="flex items-center gap-2">
            <Input
              id="csv-file"
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="flex-1"
            />
            {file && (
              <Button variant="outline" size="icon" onClick={clearFile} title="Clear">
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
          {file && (
            <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-primary">
              ▸ {file.name}
            </p>
          )}
        </div>

        <div className="flex items-center gap-3">
          <span className="h-px flex-1 bg-foreground/15" />
          <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
            OR PASTE
          </span>
          <span className="h-px flex-1 bg-foreground/15" />
        </div>

        <div className="space-y-2">
          <Label htmlFor="csv-text">Paste CSV</Label>
          <Textarea
            id="csv-text"
            ref={textareaRef}
            value={csvText}
            onChange={handleTextChange}
            placeholder={`text,filename,name,user\nHello {name},audio_{name}.mp3\nWelcome {user},welcome_{user}.mp3`}
            className="min-h-[140px]"
          />
        </div>

        {audioTagsEnabled && (
          <div className="border-t border-foreground/15 pt-4">
            <AudioTagPicker onInsert={insertAtCursor} />
          </div>
        )}

        {preview.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-baseline justify-between">
              <Label>Preview</Label>
              <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
                <FileText className="mr-1 inline h-3 w-3" />
                {preview.length} ROWS
              </span>
            </div>
            <div className="overflow-x-auto border border-foreground/20">
              <table className="w-full text-xs">
                <thead className="bg-foreground/5">
                  <tr>
                    {Object.keys(preview[0] || {}).map((header) => (
                      <th
                        key={header}
                        className="border-b border-foreground/20 px-3 py-2 text-left font-mono text-[10px] font-bold uppercase tracking-[0.14em] text-foreground"
                      >
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {preview.map((row, idx) => (
                    <tr key={idx} className="border-t border-foreground/10 even:bg-foreground/[0.02]">
                      {Object.values(row).map((value, colIdx) => (
                        <td key={colIdx} className="px-3 py-2 font-mono text-[11px] text-muted-foreground">
                          {value}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {detectedVariables.length > 0 && (
          <div className="space-y-2">
            <Label>Detected Variables ({detectedVariables.length})</Label>
            <div className="flex flex-wrap gap-1.5">
              {detectedVariables.map((variable) => (
                <Badge key={variable}>
                  {"{"}{variable}{"}"}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  )
}
