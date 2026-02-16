import { useChatStore } from "@/hooks/use-chat-store"
import { AppSidebar } from "@/components/chat/AppSidebar"
import { ChatHeader } from "@/components/chat/ChatHeader"
import { ChatContent } from "@/components/chat/ChatContent"
import { ChatComposer } from "@/components/chat/ChatComposer"
import { NewConversationDialog } from "@/components/chat/NewConversationDialog"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"

export default function App() {
  const {
    composer,
    setComposer,
    isLoading,
    error,
    isNewConversationModalOpen,
    openNewConversationModal,
    closeNewConversationModal,
    confirmNewConversation,
    orderedConversations,
    activeConversation,
    createNewConversation,
    selectConversation,
    deleteConversation,
    handleSend,
    setComposerFromPrompt,
    handleComposerKeyDown,
  } = useChatStore()

  return (
    <SidebarProvider className="h-screen w-full bg-background text-foreground">
      <AppSidebar
        activeConversationId={activeConversation?.id ?? ""}
        orderedConversations={orderedConversations}
        activeConversation={activeConversation}
        onNewConversation={createNewConversation}
        onSelectConversation={selectConversation}
        onDeleteConversation={deleteConversation}
      />

      <SidebarInset className="min-h-0">
        <main className="relative flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
          <ChatHeader
            title={activeConversation?.title ?? "Nuevo chat"}
          />

          <ChatContent
            activeConversation={activeConversation}
            isLoading={isLoading}
            onSelectPrompt={setComposerFromPrompt}
          />

          <footer className="pointer-events-none absolute inset-x-0 bottom-0 bg-gradient-to-t from-background via-background to-transparent px-4 pb-5 pt-12 md:px-8">
            <div className="pointer-events-auto mx-auto w-full max-w-3xl">
              <ChatComposer
                value={composer}
                onChange={setComposer}
                onSubmit={() => void handleSend()}
                onKeyDown={handleComposerKeyDown}
                onNewConversationClick={openNewConversationModal}
                disabled={!composer.trim() || !activeConversation}
                isLoading={isLoading}
              />
              {error ? (
                <p className="mt-2 text-xs text-destructive">
                  Error de API: {error}
                </p>
              ) : null}
            </div>
          </footer>

          <NewConversationDialog
            open={isNewConversationModalOpen}
            onOpenChange={(open) => {
              if (!open) closeNewConversationModal()
            }}
            onConfirm={confirmNewConversation}
            onCancel={closeNewConversationModal}
          />
        </main>
      </SidebarInset>
    </SidebarProvider>
  )
}
