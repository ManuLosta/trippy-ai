import type { KeyboardEvent } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { cn } from "@/lib/utils"

type ChatComposerProps = {
  value: string
  onChange: (value: string) => void
  onSubmit: () => void
  onKeyDown: (event: KeyboardEvent<HTMLTextAreaElement>) => void
  onNewConversationClick: () => void
  disabled: boolean
  isLoading: boolean
}

export function ChatComposer({
  value,
  onChange,
  onSubmit,
  onKeyDown,
  onNewConversationClick,
  disabled,
  isLoading,
}: ChatComposerProps) {
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        onSubmit()
      }}
      className="rounded-[28px] border border-border bg-card shadow-lg"
    >
      <div className="flex items-center gap-2 px-3 py-2.5">
        <Button
          type="button"
          variant="ghost"
          size="icon"
          onClick={onNewConversationClick}
          aria-label="Nueva conversación"
        >
          <svg
            viewBox="0 0 24 24"
            className="size-4"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.2"
            strokeLinecap="round"
          >
            <path d="M12 5v14" />
            <path d="M5 12h14" />
          </svg>
        </Button>
        <label htmlFor="travel-prompt" className="sr-only">
          Prompt de viaje
        </label>
        <Textarea
          id="travel-prompt"
          rows={1}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Preguntá sobre tu viaje"
          className={cn(
            "min-h-8 max-h-56 flex-1 resize-none border-0 bg-transparent px-1 py-1 text-[17px] leading-6 shadow-none focus-visible:ring-0 placeholder:text-muted-foreground dark:bg-transparent"
          )}
        />
        <Button
          type="submit"
          size="icon"
          disabled={disabled || isLoading}
          className="rounded-full bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          aria-label="Enviar mensaje"
        >
          <svg
            viewBox="0 0 24 24"
            className="size-4"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M12 19V5" />
            <path d="m6 11 6-6 6 6" />
          </svg>
        </Button>
      </div>
    </form>
  )
}
