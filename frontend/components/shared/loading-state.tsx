'use client'

import { LoaderIcon } from '@/components/ui/icons'
import { cn } from '@/lib/utils'

interface LoadingStateProps {
  message?: string
  className?: string
}

export function LoadingState({
  message = 'Загрузка...',
  className,
}: LoadingStateProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center py-16 px-6 text-center', className)}>
      <div className="flex items-center justify-center w-14 h-14 rounded-xl bg-primary/10 mb-4">
        <LoaderIcon className="h-7 w-7 text-primary" />
      </div>
      <p className="text-sm text-muted-foreground">{message}</p>
    </div>
  )
}
