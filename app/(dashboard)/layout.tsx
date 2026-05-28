import { Sidebar } from "@/components/sidebar"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // Tickertape strings — pure ornament, evoke broadcast equipment
  const tickerItems = [
    "ELEVENTOOLS // CONSOLE v2.0",
    "LOCAL STACK · SQLITE · FILESYSTEM",
    "ZERO TELEMETRY",
    "BULK TTS · TRANSLATION · HISTORY",
    "DEVELOPER-GRADE AUDIO SYNTHESIS",
  ]

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="relative flex flex-1 flex-col overflow-hidden">
        {/* Header bar */}
        <header className="relative flex h-14 items-center justify-between border-b border-foreground/25 bg-background px-6">
          <div className="flex items-center gap-4 font-mono text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
            <span className="text-primary">┌</span>
            <span>SESSION</span>
            <span className="text-foreground">{`ET-${Math.random().toString(36).slice(2, 8).toUpperCase()}`}</span>
            <span className="text-foreground/30">·</span>
            <span>MODE</span>
            <span className="text-foreground">LOCAL</span>
          </div>

          {/* Tickertape */}
          <div className="hidden flex-1 overflow-hidden md:block">
            <div className="marquee flex whitespace-nowrap font-mono text-[10px] uppercase tracking-[0.18em] text-foreground/40">
              {[...tickerItems, ...tickerItems].map((t, i) => (
                <span key={i} className="mx-8 inline-flex items-center gap-2">
                  <span className="text-primary">▸</span>
                  {t}
                </span>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-3 font-mono text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
            <span>{new Date().toISOString().slice(0, 10)}</span>
            <span className="text-primary">┐</span>
          </div>
        </header>

        {/* Main content area */}
        <main className="relative flex-1 overflow-y-auto bg-background">
          <div className="mx-auto max-w-7xl p-8">{children}</div>
        </main>

        {/* Footer rail */}
        <footer className="flex h-8 items-center justify-between border-t border-foreground/25 bg-background px-6 font-mono text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5 text-primary">
              <span className="inline-block h-1.5 w-1.5 bg-primary blink" />
              READY
            </span>
            <span className="text-foreground/30">|</span>
            <span>BUF 0 KB</span>
            <span className="text-foreground/30">|</span>
            <span>QUEUE EMPTY</span>
          </div>
          <div className="flex items-center gap-3">
            <span>└ END OF FRAME</span>
            <span className="text-primary">┘</span>
          </div>
        </footer>
      </div>
    </div>
  )
}
