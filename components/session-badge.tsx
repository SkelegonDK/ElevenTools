"use client"

import { useEffect, useState } from "react"

export function SessionId() {
  const [sessionId, setSessionId] = useState<string>("--------")

  useEffect(() => {
    setSessionId(`ET-${Math.random().toString(36).slice(2, 8).toUpperCase()}`)
  }, [])

  return (
    <div className="flex items-center gap-4 font-mono text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
      <span className="text-primary">┌</span>
      <span>SESSION</span>
      <span className="text-foreground">{sessionId}</span>
      <span className="text-foreground/30">·</span>
      <span>MODE</span>
      <span className="text-foreground">LOCAL</span>
    </div>
  )
}

export function TodayDate() {
  const [date, setDate] = useState<string>("----------")

  useEffect(() => {
    setDate(new Date().toISOString().slice(0, 10))
  }, [])

  return (
    <div className="flex items-center gap-3 font-mono text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
      <span>{date}</span>
      <span className="text-primary">┐</span>
    </div>
  )
}
