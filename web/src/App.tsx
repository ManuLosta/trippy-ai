import { useChatStore } from "@/hooks/use-chat-store"
import { Sidebar } from "@/components/chat/Sidebar"
import { ChatHeader } from "@/components/chat/ChatHeader"
import { ChatContent } from "@/components/chat/ChatContent"
import { ChatComposer } from "@/components/chat/ChatComposer"
import { NewConversationDialog } from "@/components/chat/NewConversationDialog"

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
    handleSend,
    setComposerFromPrompt,
    handleComposerKeyDown,
  } = useChatStore()

  return (
    <div className="h-screen bg-background text-foreground dark">
      <div className="mx-auto flex h-full max-w-[1600px]">
        <Sidebar
          activeConversationId={activeConversation?.id ?? ""}
          orderedConversations={orderedConversations}
          activeConversation={activeConversation}
          onNewConversation={createNewConversation}
          onSelectConversation={selectConversation}
        />

        <main className="relative flex min-w-0 flex-1 flex-col">
          <ChatHeader
            title={activeConversation?.title ?? "Nuevo chat"}
            onNewConversation={createNewConversation}
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
      </div>
    </div>
  )
}
