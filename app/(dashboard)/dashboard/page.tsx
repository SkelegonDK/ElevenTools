import Link from "next/link"
import { FileText, Languages, History, Settings, ArrowUpRight } from "lucide-react"

const modules = [
  {
    code: "01",
    name: "Bulk Generation",
    href: "/dashboard/bulk",
    icon: FileText,
    summary: "CSV-driven batch synthesis with {variable} personalization.",
    primary: true,
  },
  {
    code: "02",
    name: "Translation",
    href: "/dashboard/translate",
    icon: Languages,
    summary: "Pre-flight text translation via OpenRouter LLMs.",
  },
  {
    code: "03",
    name: "History",
    href: "/dashboard/history",
    icon: History,
    summary: "Recall, audition, and purge prior generations.",
  },
  {
    code: "04",
    name: "Settings",
    href: "/dashboard/settings",
    icon: Settings,
    summary: "Default model wiring & operator preferences.",
  },
]

const stats = [
  { label: "Stack", value: "Local" },
  { label: "Engine", value: "ElevenLabs" },
  { label: "Storage", value: "SQLite + FS" },
  { label: "Auth", value: "Off" },
]

export default function DashboardPage() {
  return (
    <div className="space-y-10">
      {/* HERO */}
      <section className="reg-corners border border-foreground/30 bg-card">
        <div className="grid grid-cols-12 gap-0">
          <div className="col-span-12 border-b border-foreground/20 p-8 lg:col-span-8 lg:border-b-0 lg:border-r">
            <div className="label-section mb-4">[ 00 ] // OVERVIEW</div>
            <h1 className="heading-display text-[clamp(3.5rem,9vw,8rem)] text-foreground">
              ELEVEN<br />
              <span className="text-primary">/</span>TOOLS<span className="blink text-primary">_</span>
            </h1>
            <p className="mt-6 max-w-xl font-mono text-sm leading-relaxed text-muted-foreground">
              A developer-grade console for bulk text-to-speech synthesis,
              translation, and audio dispatch. No tracking. No accounts.
              Files on disk. State in SQLite.
            </p>

            {/* Quick spec */}
            <dl className="mt-8 grid grid-cols-2 gap-px border border-foreground/25 bg-foreground/25 sm:grid-cols-4">
              {stats.map((s) => (
                <div key={s.label} className="bg-background px-4 py-3">
                  <dt className="font-mono text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
                    {s.label}
                  </dt>
                  <dd className="mt-1 font-mono text-sm font-bold uppercase text-foreground">
                    {s.value}
                  </dd>
                </div>
              ))}
            </dl>
          </div>

          {/* Right rail — manifesto block */}
          <div className="col-span-12 flex flex-col justify-between p-8 lg:col-span-4">
            <div>
              <div className="label-section mb-4 text-primary">// MANIFEST</div>
              <ul className="space-y-3 font-mono text-xs leading-relaxed text-foreground">
                <li className="flex gap-2">
                  <span className="text-primary">▸</span>
                  Bulk synthesis over CSV input
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">▸</span>
                  Variable interpolation per row
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">▸</span>
                  Local-only storage & playback
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">▸</span>
                  Translation hand-off to OpenRouter
                </li>
              </ul>
            </div>
            <div className="mt-8 border-t border-foreground/20 pt-4">
              <div className="font-mono text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
                Build · 2026.05 · NO-AUTH-EDITION
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* MODULES */}
      <section>
        <div className="mb-6 flex items-baseline justify-between border-b border-foreground/20 pb-3">
          <h2 className="label-section">[ ▼ ] // MODULES — SELECT ENTRYPOINT</h2>
          <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
            {modules.length} TOTAL
          </span>
        </div>

        <div className="grid grid-cols-1 gap-px bg-foreground/25 sm:grid-cols-2 lg:grid-cols-4">
          {modules.map((m) => (
            <Link
              key={m.code}
              href={m.href}
              className="group relative flex h-full flex-col justify-between bg-background p-6 transition-colors hover:bg-card"
            >
              {m.primary && (
                <div className="absolute right-0 top-0 hazard-band h-1 w-16" aria-hidden="true" />
              )}
              <div>
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[10px] font-bold uppercase tracking-[0.18em] text-muted-foreground">
                    [{m.code}]
                  </span>
                  <m.icon
                    className="h-5 w-5 text-foreground/40 transition-colors group-hover:text-primary"
                    strokeWidth={2}
                  />
                </div>
                <h3 className="mt-8 font-display text-2xl uppercase leading-none tracking-tight text-foreground">
                  {m.name}
                </h3>
                <p className="mt-4 font-mono text-xs leading-relaxed text-muted-foreground">
                  {m.summary}
                </p>
              </div>

              <div className="mt-8 flex items-center gap-2 border-t border-foreground/15 pt-4 font-mono text-[11px] font-bold uppercase tracking-[0.18em] text-foreground transition-colors group-hover:text-primary">
                ENTER
                <ArrowUpRight
                  className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5"
                  strokeWidth={2.5}
                />
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* OPERATOR NOTE — punched-paper bottom strip */}
      <section className="border border-foreground/20 bg-card">
        <div className="grid grid-cols-12 items-stretch">
          <div className="col-span-1 hazard-band" aria-hidden="true" />
          <div className="col-span-11 px-6 py-4">
            <p className="font-mono text-xs leading-relaxed text-muted-foreground">
              <span className="font-bold uppercase tracking-[0.16em] text-foreground">// OPERATOR NOTE.</span>{" "}
              Tool requires <span className="text-primary">ELEVENLABS_API_KEY</span> and{" "}
              <span className="text-primary">OPENROUTER_API_KEY</span> in <span className="text-foreground">.env.local</span>.
              Generated audio lives in <span className="text-foreground">/data/audio/</span>. Database in <span className="text-foreground">/data/eleventools.db</span>.
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}
