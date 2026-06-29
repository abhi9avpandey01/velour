import * as React from "react"
import { cn } from "./button"

export interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: number
}

const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  ({ className, value, ...props }, ref) => {
    const percentage = value ? Math.max(0, Math.min(100, value)) : 0
    return (
      <div
        ref={ref}
        className={cn(
          "relative h-2 w-full overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-800",
          className
        )}
        {...props}
      >
        <div
          className="h-full w-full flex-1 bg-zinc-900 transition-all dark:bg-zinc-50"
          style={{ transform: `translateX(-${100 - percentage}%)` }}
        />
      </div>
    )
  }
)
Progress.displayName = "Progress"

export { Progress }
