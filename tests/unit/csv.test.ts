import { describe, expect, it } from 'vitest'
import { detectVariables, parseCSV, replaceVariables } from '@/lib/utils/csv'

describe('csv parsing', () => {
  it('parses a header + two rows', () => {
    const csv = 'text,name\nHello {name},Alice\nHi {name},Bob'
    const rows = parseCSV(csv)
    expect(rows).toHaveLength(2)
    expect(rows[0]).toEqual({ text: 'Hello {name}', name: 'Alice' })
    expect(rows[1]).toEqual({ text: 'Hi {name}', name: 'Bob' })
  })

  it('returns [] for empty input', () => {
    expect(parseCSV('')).toEqual([])
    expect(parseCSV('   \n  ')).toEqual([])
  })

  it('detects variables in {braces}', () => {
    expect(detectVariables('Hi {first} {last}')).toEqual(['first', 'last'])
    expect(detectVariables('no vars here')).toEqual([])
    // De-duplicates within one cell.
    expect(detectVariables('{x} and {x}')).toEqual(['x'])
  })

  it('replaces variables case-sensitively, leaves unknowns intact', () => {
    expect(replaceVariables('Hello {name}', { name: 'Alice' })).toBe('Hello Alice')
    expect(replaceVariables('Hello {Name}', { name: 'Alice' })).toBe('Hello {Name}')
    expect(replaceVariables('{a} and {b}', { a: 'X', b: 'Y' })).toBe('X and Y')
  })
})
