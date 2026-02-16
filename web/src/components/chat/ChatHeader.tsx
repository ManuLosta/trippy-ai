import { Button } from "@/components/ui/button"

type ChatHeaderProps = {
  title: string
  onNewConversation: () => void
}

export function ChatHeader({ title, onNewConversation }: ChatHeaderProps) {
  return (
    <header className="flex h-14 items-center justify-between border-b border-border px-4 md:px-6">
      <div className="flex items-center gap-3">
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="md:hidden"
          onClick={onNewConversation}
        >
          Nuevo
        </Button>
        <p className="text-sm text-foreground">{title}</p>
      </div>
    </header>
  )
}
