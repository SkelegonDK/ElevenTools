"use client"

import { Info } from "lucide-react"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"

export function SectionHelp({
  title,
  description,
  children,
}: {
  title: string
  description: string
  children: React.ReactNode
}) {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <button
          type="button"
          aria-label={`${title} guide`}
          title={`${title} help`}
          className="inline-flex h-7 w-7 shrink-0 items-center justify-center border border-foreground/40 text-foreground transition-colors hover:border-primary hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background"
        >
          <Info className="h-3 w-3" aria-hidden="true" />
        </button>
      </DialogTrigger>
      <DialogContent className="max-h-[80dvh] w-[calc(100%-2rem)] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription className="leading-relaxed">{description}</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 font-mono text-xs leading-relaxed text-muted-foreground">
          {children}
        </div>
        <DialogFooter>
          <DialogClose asChild><Button variant="outline">Got it</Button></DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
