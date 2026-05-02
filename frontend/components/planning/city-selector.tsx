'use client'

import { useState } from 'react'
import { MapPinIcon, ChevronDownIcon, CheckIcon } from '@/components/ui/icons'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import type { City } from '@/lib/types'

interface CitySelectorProps {
  cities: City[]
  selectedCity: City | null
  onSelect: (city: City) => void
  isLoading?: boolean
}

export function CitySelector({
  cities,
  selectedCity,
  onSelect,
  isLoading = false,
}: CitySelectorProps) {
  const [open, setOpen] = useState(false)

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-full justify-between h-11 bg-card border-border hover:bg-muted text-foreground"
          disabled={isLoading}
        >
          <span className="flex items-center gap-2.5 truncate">
            <MapPinIcon className="h-4 w-4 text-primary" />
            {selectedCity ? (
              <div className="text-left">
                <span className="font-medium">{selectedCity.name}</span>
                <span className="text-muted-foreground ml-1.5 text-sm">{selectedCity.region}</span>
              </div>
            ) : (
              <span className="text-muted-foreground">Выберите город...</span>
            )}
          </span>
          <ChevronDownIcon className="ml-2 h-4 w-4 shrink-0 text-muted-foreground" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[350px] p-0" align="start">
        <Command>
          <CommandInput placeholder="Поиск города..." className="h-10" />
          <CommandList>
            <CommandEmpty>Город не найден</CommandEmpty>
            <CommandGroup>
              {cities.map((city) => (
                <CommandItem
                  key={city.id}
                  value={city.name}
                  onSelect={() => {
                    onSelect(city)
                    setOpen(false)
                  }}
                  className="py-2.5"
                >
                  <div className={cn(
                    'flex items-center justify-center w-5 h-5 rounded border mr-2.5 transition-colors',
                    selectedCity?.id === city.id 
                      ? 'bg-primary border-primary' 
                      : 'border-border'
                  )}>
                    {selectedCity?.id === city.id && (
                      <CheckIcon className="h-3 w-3 text-primary-foreground" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-foreground">{city.name}</div>
                    <div className="text-xs text-muted-foreground">
                      {city.region}, {city.country}
                    </div>
                  </div>
                  <div className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded">
                    {city.pois_count} мест
                  </div>
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
