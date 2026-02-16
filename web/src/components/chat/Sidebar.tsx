import { useState } from "react"
import type { Conversation } from "@/types/chat"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { cn } from "@/lib/utils"

type SidebarProps = {
  activeConversationId: string
  orderedConversations: Conversation[]
  activeConversation: Conversation | undefined
  onNewConversation: () => void
  onSelectConversation: (id: string) => void
  onDeleteConversation: (id: string) => void
}

function TrashIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M3 6h18" />
      <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
      <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
      <line x1="10" x2="10" y1="11" y2="17" />
      <line x1="14" x2="14" y1="11" y2="17" />
    </svg>
  )
}

export function Sidebar({
  activeConversationId,
  orderedConversations,
  activeConversation,
  onNewConversation,
  onSelectConversation,
  onDeleteConversation,
}: SidebarProps) {
  const [conversationIdToDelete, setConversationIdToDelete] = useState<
    string | null
  >(null)

  const handleDeleteClick = (e: React.MouseEvent, conversationId: string) => {
    e.stopPropagation()
    setConversationIdToDelete(conversationId)
  }

  const handleConfirmDelete = () => {
    if (conversationIdToDelete) {
      onDeleteConversation(conversationIdToDelete)
      setConversationIdToDelete(null)
    }
  }

  const handleCancelDelete = () => setConversationIdToDelete(null)

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
              <div
                key={conversation.id}
                className={cn(
                  "group mb-1 flex w-full items-center gap-1 rounded-lg pr-1",
                  activeConversationId === conversation.id
                    ? "bg-sidebar-accent"
                    : "hover:bg-sidebar-accent/50"
                )}
              >
                <button
                  type="button"
                  onClick={() => onSelectConversation(conversation.id)}
                  className={cn(
                    "min-w-0 flex-1 px-2 py-2 text-left text-sm transition",
                    activeConversationId === conversation.id
                      ? "text-sidebar-accent-foreground"
                      : "text-muted-foreground"
                  )}
                >
                  <span className="block truncate">{conversation.title}</span>
                </button>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon-xs"
                  className="shrink-0 opacity-0 group-hover:opacity-100 group-focus-within:opacity-100"
                  onClick={(e) => handleDeleteClick(e, conversation.id)}
                  aria-label={`Eliminar conversación ${conversation.title}`}
                >
                  <TrashIcon className="size-3.5" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </ScrollArea>

      <Separator />
      <div className="p-3 text-xs text-muted-foreground">
        Conversación: {activeConversation?.id.slice(0, 8) ?? "-"} ·{" "}
        {activeConversation?.messages.length ?? 0} mensajes
      </div>

      <Dialog
        open={conversationIdToDelete !== null}
        onOpenChange={(open) => !open && handleCancelDelete()}
      >
        <DialogContent showCloseButton={false} className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Eliminar conversación</DialogTitle>
            <DialogDescription>
              ¿Querés eliminar esta conversación? No se puede deshacer.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="sm:justify-end">
            <Button variant="outline" onClick={handleCancelDelete}>
              Cancelar
            </Button>
            <Button
              variant="destructive"
              onClick={handleConfirmDelete}
            >
              Eliminar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </aside>
  )
}
