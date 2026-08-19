import * as React from "react"

import { cn } from "@/lib/utils"

const Input = React.forwardRef<HTMLInputElement, React.ComponentProps<"input">>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full border border-foreground/30 bg-background px-3 py-2 font-mono text-sm text-foreground",
          "placeholder:text-muted-foreground placeholder:lowercase",
          "focus-visible:outline-none focus-visible:border-primary focus-visible:ring-1 focus-visible:ring-primary",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "file:border-0 file:bg-transparent file:text-xs file:font-bold file:uppercase file:tracking-[0.12em] file:text-foreground file:mr-3",
          "selection:bg-primary selection:text-primary-foreground",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input }
