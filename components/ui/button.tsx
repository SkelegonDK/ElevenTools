import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap font-mono text-[11px] font-bold uppercase tracking-[0.18em] border transition-[transform,box-shadow,background-color] duration-75 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-40 [&_svg]:size-3.5 [&_svg]:shrink-0 select-none",
  {
    variants: {
      variant: {
        // Primary: hazard-yellow slab. Hard offset shadow on hover.
        default:
          "bg-primary text-primary-foreground border-primary hover:-translate-x-[2px] hover:-translate-y-[2px] hover:shadow-[4px_4px_0_0_hsl(var(--foreground))] active:translate-x-0 active:translate-y-0 active:shadow-[1px_1px_0_0_hsl(var(--foreground))]",
        // Destructive: burning orange
        destructive:
          "bg-destructive text-destructive-foreground border-destructive hover:-translate-x-[2px] hover:-translate-y-[2px] hover:shadow-[4px_4px_0_0_hsl(var(--foreground))]",
        // Outline: bone border, ink fill, yellow on hover
        outline:
          "bg-transparent text-foreground border-foreground/60 hover:border-primary hover:text-primary",
        // Secondary: dark slab, lighter on hover
        secondary:
          "bg-secondary text-secondary-foreground border-border hover:border-foreground/60",
        // Ghost: invisible until hovered
        ghost:
          "bg-transparent text-foreground border-transparent hover:bg-foreground/5 hover:text-primary",
        // Link: underlined inline
        link:
          "bg-transparent text-primary border-transparent underline underline-offset-4 hover:opacity-80",
      },
      size: {
        default: "h-10 px-5 py-2",
        sm: "h-8 px-3 text-[10px]",
        lg: "h-12 px-7 text-xs",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
