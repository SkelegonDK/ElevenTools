"use client"

export const AUDIO_TAGS = [
  '[whispers]',
  '[laughs]',
  '[sighs]',
  '[excited]',
  '[curious]',
  '[sarcastic]',
  '[interrupting]',
  '[hesitates]',
  '[footsteps]',
  '[applause]',
] as const

interface AudioTagPickerProps {
  onInsert: (tag: string) => void
  className?: string
}

export function AudioTagPicker({ onInsert, className = '' }: AudioTagPickerProps) {
  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-baseline justify-between">
        <span className="font-mono text-[10px] font-bold uppercase tracking-[0.18em] text-foreground">
          // AUDIO TAGS (v3)
        </span>
        <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-muted-foreground">
          CLICK TO INSERT
        </span>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {AUDIO_TAGS.map((tag) => (
          <button
            key={tag}
            type="button"
            onClick={() => onInsert(tag)}
            className="border border-foreground/30 bg-background px-2 py-1 font-mono text-[10px] font-bold uppercase tracking-[0.12em] text-foreground transition-colors hover:border-primary hover:bg-primary hover:text-primary-foreground"
          >
            {tag}
          </button>
        ))}
      </div>
    </div>
  )
}
