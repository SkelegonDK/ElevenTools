"use client"

import { useState, useCallback } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { parseCSV, detectVariables, type CSVRow } from "@/lib/utils/csv"
import { Upload, FileText, X } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface CSVUploadProps {
  onDataLoaded: (data: CSVRow[], variables: string[]) => void
}

export function CSVUpload({ onDataLoaded }: CSVUploadProps) {
  const [file, setFile] = useState<File | null>(null)
  const [csvText, setCsvText] = useState("")
  const [preview, setPreview] = useState<CSVRow[]>([])
  const [detectedVariables, setDetectedVariables] = useState<string[]>([])

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
    []
  )

  const handleTextChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = e.target.value
    setCsvText(text)
    if (text.trim()) {
      processCSV(text)
    } else {
      setPreview([])
      setDetectedVariables([])
      onDataLoaded([], [])
    }
  }, [onDataLoaded])

  const processCSV = useCallback((text: string) => {
    try {
      const rows = parseCSV(text)
      setPreview(rows.slice(0, 5)) // Show first 5 rows as preview

      // Detect variables from all text cells
      const allVariables = new Set<string>()
      rows.forEach((row) => {
        Object.values(row).forEach((value) => {
          const vars = detectVariables(value)
          vars.forEach((v) => allVariables.add(v))
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
  }, [onDataLoaded])

  const clearFile = useCallback(() => {
    setFile(null)
    setCsvText("")
    setPreview([])
    setDetectedVariables([])
    onDataLoaded([], [])
  }, [onDataLoaded])

  return (
    <Card>
      <CardHeader>
        <CardTitle>CSV Upload</CardTitle>
        <CardDescription>
          Upload a CSV file with text and optional filename columns. Use {"{"}variable{"}"} syntax for personalization.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="csv-file">Upload CSV File</Label>
          <div className="flex items-center gap-2">
            <Input
              id="csv-file"
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="flex-1"
            />
            {file && (
              <Button variant="ghost" size="icon" onClick={clearFile}>
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="csv-text">Or paste CSV content</Label>
          <textarea
            id="csv-text"
            value={csvText}
            onChange={handleTextChange}
            placeholder="text,filename&#10;Hello {name},audio_{name}.mp3&#10;Welcome {user},welcome_{user}.mp3"
            className="w-full min-h-[120px] rounded-md border border-input bg-background px-3 py-2 text-sm font-mono"
          />
        </div>

        {preview.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              <Label>Preview ({preview.length} rows shown)</Label>
            </div>
            <div className="rounded-md border border-border overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-muted">
                    <tr>
                      {Object.keys(preview[0] || {}).map((header) => (
                        <th key={header} className="px-3 py-2 text-left font-medium">
                          {header}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {preview.map((row, idx) => (
                      <tr key={idx} className="border-t border-border">
                        {Object.values(row).map((value, colIdx) => (
                          <td key={colIdx} className="px-3 py-2 font-mono text-xs">
                            {value}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {detectedVariables.length > 0 && (
          <div className="space-y-2">
            <Label>Detected Variables</Label>
            <div className="flex flex-wrap gap-2">
              {detectedVariables.map((variable) => (
                <Badge key={variable} variant="secondary">
                  {"{"}{variable}{"}"}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
