import * as React from "react"
import { Check, ChevronsUpDown, Loader2 } from "lucide-react"
import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { useDebounce } from "@/hooks/use-debounce"

export function LocationAutocomplete({ 
  value, 
  onChange 
}: { 
  value: string
  onChange: (val: string) => void 
}) {
  const [open, setOpen] = React.useState(false)
  const [search, setSearch] = React.useState("")
  
  // Debounce the search term so we don't spam the API
  const debouncedSearch = useDebounce(search, 300)

  const { data: locations, isFetching } = useQuery({
    queryKey: ['locations', debouncedSearch],
    queryFn: async () => {
      if (!debouncedSearch || debouncedSearch.trim() === "") return []
      const res = await apiClient.get(`/locations/search?q=${encodeURIComponent(debouncedSearch)}`)
      return res.data
    },
    enabled: debouncedSearch.length > 0,
    staleTime: 1000 * 60 * 5, // Cache for 5 mins
  })

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-full justify-between font-normal text-left"
        >
          <span className="truncate">
            {value || "Search for a city..."}
          </span>
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[300px] p-0" align="start">
        <Command shouldFilter={false}>
          <CommandInput 
            placeholder="Type a city name..." 
            value={search}
            onValueChange={setSearch}
          />
          <CommandList>
            {isFetching && (
              <div className="flex items-center justify-center p-4">
                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                <span className="ml-2 text-sm text-muted-foreground">Searching...</span>
              </div>
            )}
            {!isFetching && debouncedSearch && locations?.length === 0 && (
              <CommandEmpty>No location found.</CommandEmpty>
            )}
            {!isFetching && locations && locations.length > 0 && (
              <CommandGroup>
                {locations.map((loc: any) => (
                  <CommandItem
                    key={loc.id}
                    value={loc.display}
                    onSelect={(currentValue) => {
                      onChange(loc.display)
                      setOpen(false)
                    }}
                  >
                    <Check
                      className={cn(
                        "mr-2 h-4 w-4",
                        value === loc.display ? "opacity-100" : "opacity-0"
                      )}
                    />
                    {loc.display}
                  </CommandItem>
                ))}
              </CommandGroup>
            )}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
