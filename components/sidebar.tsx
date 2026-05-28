"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import {
  LayoutDashboard,
  FileText,
  Languages,
  History,
  Settings,
} from "lucide-react"

const navigation = [
  { code: "00", name: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { code: "01", name: "Bulk", href: "/dashboard/bulk", icon: FileText },
  { code: "02", name: "Translate", href: "/dashboard/translate", icon: Languages },
  { code: "03", name: "History", href: "/dashboard/history", icon: History },
  { code: "04", name: "Settings", href: "/dashboard/settings", icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="relative flex h-full w-72 flex-col border-r border-foreground/25 bg-background">
      {/* Hazard band at top */}
      <div className="h-2 hazard-band" aria-hidden="true" />

      {/* Wordmark */}
      <div className="border-b border-foreground/25 px-5 py-6">
        <div className="flex items-baseline gap-2">
          <span className="font-display text-3xl leading-none tracking-tighter text-foreground">
            ELEVEN<span className="text-primary">/</span>TOOLS
          </span>
        </div>
        <div className="mt-2 flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
          <span className="inline-block h-1.5 w-1.5 bg-primary blink" />
          <span>CONSOLE v2.0 // LOCAL</span>
        </div>
      </div>

      {/* Section label */}
      <div className="px-5 pt-6 pb-2">
        <p className="label-section">// MODULES</p>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3">
        {navigation.map((item) => {
          const isActive =
            item.href === "/dashboard"
              ? pathname === "/dashboard"
              : pathname === item.href || pathname.startsWith(item.href + "/")
          return (
            <Link
              key={item.code}
              href={item.href}
              className={cn(
                "group relative flex items-center gap-3 border border-transparent px-3 py-2.5 font-mono text-xs uppercase tracking-[0.14em] transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground border-primary"
                  : "text-muted-foreground hover:text-foreground hover:border-foreground/20"
              )}
            >
              <span
                className={cn(
                  "text-[10px] font-bold tabular-nums",
                  isActive ? "text-primary-foreground" : "text-foreground/40"
                )}
              >
                {item.code}
              </span>
              <item.icon className="h-3.5 w-3.5" strokeWidth={2.5} />
              <span className="font-bold">{item.name}</span>
              {isActive && (
                <span className="ml-auto text-[10px] font-bold">●</span>
              )}
            </Link>
          )
        })}
      </nav>

      {/* Footer block */}
      <div className="border-t border-foreground/25 px-5 py-4">
        <div className="space-y-1.5 font-mono text-[10px] uppercase tracking-[0.16em]">
          <div className="flex items-center justify-between text-muted-foreground">
            <span>STACK</span>
            <span className="text-foreground">LOCAL · SQLITE</span>
          </div>
          <div className="flex items-center justify-between text-muted-foreground">
            <span>AUTH</span>
            <span className="text-foreground">NONE</span>
          </div>
          <div className="flex items-center justify-between text-muted-foreground">
            <span>STATUS</span>
            <span className="flex items-center gap-1.5 text-primary">
              <span className="inline-block h-1.5 w-1.5 bg-primary" />
              ONLINE
            </span>
          </div>
        </div>
      </div>
    </aside>
  )
}
