/**
 * Text processing utilities for variable detection and replacement
 */

/**
 * Detects string variables in text enclosed in curly braces.
 * @param text - The input text to search for variables
 * @returns Array of variable names found (without curly braces)
 * @example detectVariables("Hello {name}") // returns ["name"]
 */
export function detectVariables(text: string): string[] {
  const regex = /\{([^}]+)\}/g
  const matches: string[] = []
  let match
  
  while ((match = regex.exec(text)) !== null) {
    matches.push(match[1])
  }
  
  return [...new Set(matches)] // Remove duplicates
}

/**
 * Detects phonetic conversion markers in format [[language:word]]
 * @param text - The input text to search for phonetic markers
 * @returns Array of objects with lang and word properties
 * @example detectPhoneticMarkers("[[english:hello]]") // returns [{lang: "english", word: "hello"}]
 */
export function detectPhoneticMarkers(text: string): Array<{ lang: string; word: string }> {
  const regex = /\[\[([^:]+):([^\]]+)\]\]/g
  const matches: Array<{ lang: string; word: string }> = []
  let match
  
  while ((match = regex.exec(text)) !== null) {
    matches.push({
      lang: match[1],
      word: match[2],
    })
  }
  
  return matches
}

/**
 * Replaces variables in text with provided values
 * @param text - The text containing variables
 * @param values - Object mapping variable names to their values
 * @returns Text with variables replaced
 * @example replaceVariables("Hello {name}", {name: "Alice"}) // returns "Hello Alice"
 */
export function replaceVariables(text: string, values: Record<string, string>): string {
  let result = text
  for (const [key, value] of Object.entries(values)) {
    const regex = new RegExp(`\\{${key}\\}`, 'g')
    result = result.replace(regex, value)
  }
  return result
}
