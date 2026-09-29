/**
 * The bordered section used across the dashboard: numbered code, title, and an
 * optional right-hand hint. Previously copied verbatim into three pages.
 */
export function Panel({
  code,
  title,
  hint,
  action,
  children,
  className = "",
}: {
  code: string
  title: string
  hint?: string
  action?: React.ReactNode
  children: React.ReactNode
  className?: string
}) {
  return (
    <section className={`relative border border-foreground/25 bg-card ${className}`}>
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-foreground/15 px-5 py-3">
        <div className="flex items-baseline gap-3">
          <span className="font-mono text-[10px] font-bold tracking-[0.18em] text-muted-foreground">
            [{code}]
          </span>
          <h2 className="font-mono text-xs font-bold uppercase tracking-[0.18em] text-foreground">
            {title}
          </h2>
        </div>
        <div className="flex flex-wrap items-center gap-3">
        {hint && (
          <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
            {hint}
          </span>
        )}
        {action}
        </div>
      </div>
      <div className="p-5">{children}</div>
    </section>
  )
}
