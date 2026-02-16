import type { Conversation } from "@/types/chat"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { cn } from "@/lib/utils"

type SidebarProps = {
  activeConversationId: string
  orderedConversations: Conversation[]
  activeConversation: Conversation | undefined
  onNewConversation: () => void
  onSelectConversation: (id: string) => void
}

export function Sidebar({
  activeConversationId,
  orderedConversations,
  activeConversation,
  onNewConversation,
  onSelectConversation,
}: SidebarProps) {
  return (
    <aside className="hidden w-[260px] shrink-0 flex-col border-r border-border bg-sidebar md:flex">
      <div className="flex h-14 items-center gap-3 px-3">
        <div className="flex size-7 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">
          T
        </div>
        <p className="text-sm font-medium text-sidebar-foreground">Trippy AI</p>
      </div>

      <div className="space-y-2 px-3 pb-4">
        <Button
          type="button"
          variant="outline"
          className="w-full justify-start"
          onClick={onNewConversation}
        >
          + Nuevo chat
        </Button>
      </div>

      <ScrollArea className="flex-1 px-2 pb-4">
        <p className="px-2 pb-2 text-xs font-medium text-muted-foreground">
          Tus chats
        </p>
        {orderedConversations.length === 0 ? (
          <p className="px-2 text-xs text-muted-foreground">
            Sin conversaciones todavía.
          </p>
        ) : (
          <div className="space-y-1">
            {orderedConversations.map((conversation) => (
              <button
                key={conversation.id}
                type="button"
                onClick={() => onSelectConversation(conversation.id)}
                className={cn(
                  "mb-1 flex w-full items-center rounded-lg px-2 py-2 text-left text-sm transition",
                  activeConversationId === conversation.id
                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                    : "text-muted-foreground hover:bg-sidebar-accent/50"
                )}
              >
                {conversation.title}
              </button>
            ))}
          </div>
        )}
      </ScrollArea>

      <Separator />
      <div className="p-3 text-xs text-muted-foreground">
        Conversación: {activeConversation?.id.slice(0, 8) ?? "-"} ·{" "}
        {activeConversation?.messages.length ?? 0} mensajes
      </div>
    </aside>
  )
}
