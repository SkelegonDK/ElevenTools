export interface CSVRow {
  [key: string]: string
}

export function parseCSV(csvText: string): CSVRow[] {
  const lines = csvText.split('\n').filter((line) => line.trim())
  if (lines.length === 0) return []

  // Parse header
  const headers = lines[0].split(',').map((h) => h.trim().replace(/^"|"$/g, ''))
  
  // Parse rows
  const rows: CSVRow[] = []
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map((v) => v.trim().replace(/^"|"$/g, ''))
    const row: CSVRow = {}
    headers.forEach((header, index) => {
      row[header] = values[index] || ''
    })
    rows.push(row)
  }

  return rows
}

export function detectVariables(text: string): string[] {
  const regex = /\{([^}]+)\}/g
  const matches = text.matchAll(regex)
  const variables: string[] = []
  for (const match of matches) {
    if (match[1] && !variables.includes(match[1])) {
      variables.push(match[1])
    }
  }
  return variables
}

export function replaceVariables(text: string, variables: Record<string, string>): string {
  let result = text
  for (const [key, value] of Object.entries(variables)) {
    result = result.replace(new RegExp(`\\{${key}\\}`, 'g'), value)
  }
  return result
}
