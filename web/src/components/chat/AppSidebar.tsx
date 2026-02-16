"use client"

import { useState } from "react"
import type { Conversation } from "@/types/chat"
import { HugeiconsIcon } from "@hugeicons/react"
import { Add01Icon } from "@hugeicons/core-free-icons"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuAction,
  SidebarRail,
} from "@/components/ui/sidebar"

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

type AppSidebarProps = {
  activeConversationId: string
  orderedConversations: Conversation[]
  activeConversation: Conversation | undefined
  onNewConversation: () => void
  onSelectConversation: (id: string) => void
  onDeleteConversation: (id: string) => void
}

export function AppSidebar({
  activeConversationId,
  orderedConversations,
  activeConversation,
  onNewConversation,
  onSelectConversation,
  onDeleteConversation,
}: AppSidebarProps) {
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
    <>
      <Sidebar collapsible="offcanvas">
        <SidebarHeader>
          <div className="flex items-center gap-2 px-2 py-2">
            <img src="./logo.svg" className="size-7 shrink-0" />
            <span className="truncate text-sm font-bold text-sidebar-foreground">
              Trippy AI
            </span>
          </div>
          <Button
            type="button"
            variant="outline"
            className="w-full justify-center gap-2 rounded-full"
            onClick={onNewConversation}
          >
            <HugeiconsIcon icon={Add01Icon} strokeWidth={2} className="size-4 shrink-0" />
            <span>Nuevo chat</span>
          </Button>
        </SidebarHeader>

        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupLabel>Tus chats</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu className="gap-1">
                {orderedConversations.length === 0 ? (
                  <p className="px-2 py-2 text-xs text-muted-foreground">
                    Sin conversaciones todavía.
                  </p>
                ) : (
                  orderedConversations.map((conversation) => (
                    <SidebarMenuItem key={conversation.id}>
                      <SidebarMenuButton
                        isActive={activeConversationId === conversation.id}
                        onClick={() => onSelectConversation(conversation.id)}
                        tooltip={conversation.title}
                      >
                        <span className="truncate">{conversation.title}</span>
                      </SidebarMenuButton>
                      <SidebarMenuAction
                        showOnHover
                        onClick={(e) => handleDeleteClick(e, conversation.id)}
                        aria-label={`Eliminar ${conversation.title}`}
                      >
                        <TrashIcon className="size-4" />
                      </SidebarMenuAction>
                    </SidebarMenuItem>
                  ))
                )}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>

        <SidebarFooter>
          <div className="px-2 py-2 text-xs text-muted-foreground">
            Conversación: {activeConversation?.id.slice(0, 8) ?? "-"} ·{" "}
            {activeConversation?.messages.length ?? 0} mensajes
          </div>
        </SidebarFooter>

        <SidebarRail />
      </Sidebar>

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
            <Button variant="destructive" onClick={handleConfirmDelete}>
              Eliminar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
