import { cn } from '@/lib/utils'

interface IconProps extends React.SVGProps<SVGSVGElement> {
  className?: string
}

export function CompassIcon({ className, ...props }: IconProps) {
  return (
    <svg
      viewBox="0 0 32 32"
      fill="none"
      className={cn("h-6 w-6", className)}
      {...props}
    >
      <circle cx="16" cy="16" r="14" stroke="currentColor" strokeWidth="2" />
      <path
        d="M16 6v2M16 24v2M6 16h2M24 16h2"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d="M20 12l-6 3-2 5 6-3 2-5z"
        fill="currentColor"
      />
      <circle cx="16" cy="16" r="2" fill="currentColor" />
    </svg>
  )
}

export function MapPinIcon({ className, ...props }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={cn("h-5 w-5", className)}
      {...props}
    >
      <path
        d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
      />
      <circle cx="12" cy="9" r="2.5" fill="currentColor" />
    </svg>
  )
}

export function RouteIcon({ className, ...props }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={cn("h-5 w-5", className)}
      {...props}
    >
      <circle cx="6" cy="6" r="3" stroke="currentColor" strokeWidth="2" />
      <circle cx="18" cy="18" r="3" stroke="currentColor" strokeWidth="2" />
      <path
        d="M9 6h3c3 0 3 3 3 6v0c0 3 0 6 3 6h0"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  )
}

export function SparkleIcon({ className, ...props }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={cn("h-5 w-5", className)}
      {...props}
    >
      <path
        d="M12 2l2 6 6 2-6 2-2 6-2-6-6-2 6-2 2-6z"
        fill="currentColor"
      />
      <circle cx="19" cy="5" r="1.5" fill="currentColor" opacity="0.6" />
      <circle cx="5" cy="19" r="1" fill="currentColor" opacity="0.4" />
    </svg>
  )
}

export function LightbulbIcon({ className, ...props }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={cn("h-5 w-5", className)}
      {...props}
    >
      <path
        d="M9 21h6M10 17h4M12 3a6 6 0 0 0-4 10.5V17h8v-3.5A6 6 0 0 0 12 3z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M12 3v1M17 5l-1 1M19 10h-1M7 5l1 1M5 10h1"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  )
}

export function WalletIcon({ className, ...props }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={cn("h-4 w-4", className)}
      {...props}
    >
      <rect x="2" y="6" width="20" height="14" rx="2" stroke="currentColor" strokeWidth="2" />
      <path d="M2 10h20" stroke="currentColor" strokeWidth="2" />
      <circle cx="17" cy="14" r="1.5" fill="currentColor" />
    </svg>
  )
}

export function ClockIcon({ className, ...props }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={cn("h-4 w-4", className)}
      {...props}
    >
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" />
      <path d="M12 7v5l3 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  )
}

export function FootprintsIcon({ className, ...props }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={cn("h-4 w-4", className)}
      {...props}
    >
      <ellipse cx="8" cy="6" rx="2.5" ry="3.5" fill="currentColor" />
      <ellipse cx="16" cy="10" rx="2.5" ry="3.5" fill="currentColor" />
      <ellipse cx="8" cy="17" rx="2" ry="2.5" fill="currentColor" opacity="0.6" />
      <ellipse cx="16" cy="20" rx="2" ry="2.5" fill="currentColor" opacity="0.6" />
    </svg>
  )
}

export function TrendingIcon({ className, ...props }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={cn("h-4 w-4", className)}
      {...props}
    >
      <path
        d="M3 17l6-6 4 4 8-8"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M17 7h4v4"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export function StarIcon({ className, filled = false, ...props }: IconProps & { filled?: boolean }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill={filled ? "currentColor" : "none"}
      className={cn("h-4 w-4", className)}
      {...props}
    >
      <path
        d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export function CameraIcon({ className, ...props }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={cn("h-4 w-4", className)}
      {...props}
    >
      <path
        d="M4 8h3l1.5-2h7L17 8h3a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
      />
      <circle cx="12" cy="13" r="4" stroke="currentColor" strokeWidth="2" />
    </svg>
  )
}

// Interest icons with unique designs
export function HistoryIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={cn("h-5 w-5", className)} {...props}>
      <path d="M3 21h18M5 21V10l7-7 7 7v11" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M9 21v-6h6v6M9 13h6" stroke="currentColor" strokeWidth="2" />
    </svg>
  )
}

export function CultureIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={cn("h-5 w-5", className)} {...props}>
      <circle cx="12" cy="8" r="5" stroke="currentColor" strokeWidth="2" />
      <path d="M4 21c0-4 3.5-7 8-7s8 3 8 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      <path d="M12 3v2M9 6h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  )
}

export function FoodIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={cn("h-5 w-5", className)} {...props}>
      <path d="M18 8c0-3.5-2.5-5-4-5s-2 1.5-2 3c0 1.5-2 3-2 3s-2-1.5-2-3c0-1.5-.5-3-2-3S2 4.5 2 8c0 4 6 5 8 11 2-6 8-7 8-11z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
      <path d="M22 3v7c0 1-1 2-2 2h-2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      <path d="M22 7h-4" stroke="currentColor" strokeWidth="2" />
    </svg>
  )
}

export function NatureIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={cn("h-5 w-5", className)} {...props}>
      <path d="M12 22V12" stroke="currentColor" strokeWidth="2" />
      <path d="M12 12c-4 0-7-3-7-7 0 0 3-1 7-1s7 1 7 1c0 4-3 7-7 7z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
      <path d="M8 22h8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      <circle cx="12" cy="8" r="2" fill="currentColor" />
    </svg>
  )
}

export function ArchitectureIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={cn("h-5 w-5", className)} {...props}>
      <rect x="4" y="10" width="16" height="11" stroke="currentColor" strokeWidth="2" />
      <path d="M12 3l8 7H4l8-7z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
      <rect x="9" y="14" width="6" height="7" stroke="currentColor" strokeWidth="2" />
      <circle cx="12" cy="7" r="1" fill="currentColor" />
    </svg>
  )
}

export function EntertainmentIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={cn("h-5 w-5", className)} {...props}>
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" />
      <path d="M8 14s1.5 2 4 2 4-2 4-2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      <circle cx="9" cy="9" r="1.5" fill="currentColor" />
      <circle cx="15" cy="9" r="1.5" fill="currentColor" />
    </svg>
  )
}

export function ShoppingIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={cn("h-5 w-5", className)} {...props}>
      <path d="M6 6h15l-1.5 9H7.5L6 6z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
      <path d="M6 6l-1-4H2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      <circle cx="9" cy="19" r="2" stroke="currentColor" strokeWidth="2" />
      <circle cx="18" cy="19" r="2" stroke="currentColor" strokeWidth="2" />
    </svg>
  )
}

export function NightlifeIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={cn("h-5 w-5", className)} {...props}>
      <path d="M12 3a9 9 0 1 0 9 9c0-1-.2-2-.5-3A7 7 0 0 1 15 9a7 7 0 0 1 0-6z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
      <circle cx="8" cy="10" r="1" fill="currentColor" />
      <circle cx="12" cy="8" r="0.5" fill="currentColor" />
      <circle cx="10" cy="14" r="0.5" fill="currentColor" />
    </svg>
  )
}

export function ArrowDownIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={cn("h-4 w-4", className)} {...props}>
      <path d="M12 5v14M5 12l7 7 7-7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

export function LoaderIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={cn("h-5 w-5 animate-spin", className)} {...props}>
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" opacity="0.2" />
      <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  )
}

export function ChevronDownIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={cn("h-4 w-4", className)} {...props}>
      <path d="M6 9l6 6 6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

export function CheckIcon({ className, ...props }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={cn("h-4 w-4", className)} {...props}>
      <path d="M5 12l5 5L20 7" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}
