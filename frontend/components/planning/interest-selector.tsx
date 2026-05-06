'use client'

import {
  HistoryIcon,
  CultureIcon,
  FoodIcon,
  NatureIcon,
  ArchitectureIcon,
  EntertainmentIcon,
  ShoppingIcon,
  NightlifeIcon,
} from '@/components/ui/icons'
import { cn } from '@/lib/utils'
import { INTERESTS } from '@/lib/types'

const iconMap = {
  landmark: HistoryIcon,
  palette: CultureIcon,
  utensils: FoodIcon,
  trees: NatureIcon,
  building: ArchitectureIcon,
  'party-popper': EntertainmentIcon,
  'shopping-bag': ShoppingIcon,
  moon: NightlifeIcon,
}

// Light backgrounds with dark text for good contrast
const colorMap: Record<string, { bg: string; border: string; selectedBg: string; icon: string; selectedIcon: string }> = {
  history: {
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    selectedBg: 'bg-amber-100 border-amber-400',
    icon: 'text-amber-600',
    selectedIcon: 'text-amber-700'
  },
  culture: {
    bg: 'bg-purple-50',
    border: 'border-purple-200',
    selectedBg: 'bg-purple-100 border-purple-400',
    icon: 'text-purple-600',
    selectedIcon: 'text-purple-700'
  },
  food: {
    bg: 'bg-orange-50',
    border: 'border-orange-200',
    selectedBg: 'bg-orange-100 border-orange-400',
    icon: 'text-orange-600',
    selectedIcon: 'text-orange-700'
  },
  nature: {
    bg: 'bg-emerald-50',
    border: 'border-emerald-200',
    selectedBg: 'bg-emerald-100 border-emerald-400',
    icon: 'text-emerald-600',
    selectedIcon: 'text-emerald-700'
  },
  architecture: {
    bg: 'bg-slate-50',
    border: 'border-slate-200',
    selectedBg: 'bg-slate-100 border-slate-400',
    icon: 'text-slate-600',
    selectedIcon: 'text-slate-700'
  },
  entertainment: {
    bg: 'bg-pink-50',
    border: 'border-pink-200',
    selectedBg: 'bg-pink-100 border-pink-400',
    icon: 'text-pink-600',
    selectedIcon: 'text-pink-700'
  },
  shopping: {
    bg: 'bg-cyan-50',
    border: 'border-cyan-200',
    selectedBg: 'bg-cyan-100 border-cyan-400',
    icon: 'text-cyan-600',
    selectedIcon: 'text-cyan-700'
  },
  nightlife: {
    bg: 'bg-indigo-50',
    border: 'border-indigo-200',
    selectedBg: 'bg-indigo-100 border-indigo-400',
    icon: 'text-indigo-600',
    selectedIcon: 'text-indigo-700'
  },
}

interface InterestSelectorProps {
  selected: string[]
  onChange: (interests: string[]) => void
}

export function InterestSelector({ selected, onChange }: InterestSelectorProps) {
  const toggleInterest = (interestId: string) => {
    if (selected.includes(interestId)) {
      onChange(selected.filter((id) => id !== interestId))
    } else {
      onChange([...selected, interestId])
    }
  }

  return (
    <div className="grid grid-cols-2 gap-2">
      {INTERESTS.map((interest) => {
        const Icon = iconMap[interest.icon as keyof typeof iconMap]
        const isSelected = selected.includes(interest.id)
        const colors = colorMap[interest.id]

        return (
          <button
            key={interest.id}
            type="button"
            onClick={() => toggleInterest(interest.id)}
            className={cn(
              'flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
              'border-2',
              isSelected
                ? `${colors.selectedBg} text-stone-900`
                : `${colors.bg} ${colors.border} text-stone-700 hover:text-stone-900`
            )}
          >
            <Icon className={cn('h-5 w-5 shrink-0', isSelected ? colors.selectedIcon : colors.icon)} />
            <span className="truncate">{interest.label}</span>
          </button>
        )
      })}
    </div>
  )
}
