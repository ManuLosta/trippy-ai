import { useEffect, useMemo, useState } from "react"
import type { FormEvent, KeyboardEvent } from "react"
import type { ChatMessage, ChatStore } from "@/types/chat"
import {
  loadStore,
  createConversation,
  buildConversationTitle,
  toApiMessages,
  createId,
} from "@/lib/chat-utils"
import { sendChatMessage } from "@/lib/api"
import { STORAGE_KEY } from "@/lib/constants"

export function useChatStore() {
  const [store, setStore] = useState<ChatStore>(() => loadStore())
  const [composer, setComposer] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isNewConversationModalOpen, setIsNewConversationModalOpen] =
    useState(false)

  const orderedConversations = useMemo(
    () =>
      [...store.conversations].sort((a, b) =>
        b.updatedAt.localeCompare(a.updatedAt)
      ),
    [store.conversations]
  )

  const activeConversation = useMemo(
    () =>
      store.conversations.find(
        (c) => c.id === store.activeConversationId
      ) ?? orderedConversations[0],
    [orderedConversations, store.activeConversationId, store.conversations]
  )

  useEffect(() => {
    if (typeof window === "undefined") return
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(store))
  }, [store])

  const createNewConversation = () => {
    const newConversation = createConversation()
    setStore((prev) => ({
      activeConversationId: newConversation.id,
      conversations: [newConversation, ...prev.conversations],
    }))
    setComposer("")
    setError(null)
  }

  const selectConversation = (conversationId: string) => {
    setStore((prev) => ({
      ...prev,
      activeConversationId: conversationId,
    }))
    setError(null)
  }

  const openNewConversationModal = () => setIsNewConversationModalOpen(true)
  const closeNewConversationModal = () => setIsNewConversationModalOpen(false)

  const confirmNewConversation = () => {
    createNewConversation()
    closeNewConversationModal()
  }

  const handleSend = async (event?: FormEvent) => {
    event?.preventDefault()
    const text = composer.trim()
    if (!text || isLoading || !activeConversation) return

    const timestamp = new Date().toISOString()
    const conversationId = activeConversation.id
    const userMessage: ChatMessage = {
      id: createId(),
      role: "user",
      content: text,
      createdAt: timestamp,
    }
    const updatedMessages = [...activeConversation.messages, userMessage]
    const updatedTitle = buildConversationTitle(updatedMessages)

    setStore((prev) => ({
      ...prev,
      conversations: prev.conversations.map((c) =>
        c.id === conversationId
          ? {
              ...c,
              title: updatedTitle,
              messages: updatedMessages,
              updatedAt: timestamp,
            }
          : c
      ),
    }))
    setComposer("")
    setError(null)
    setIsLoading(true)

    try {
      const payload = await sendChatMessage(toApiMessages(updatedMessages))
      const assistantMessage: ChatMessage = {
        id: createId(),
        role: "assistant",
        content: payload.message,
        createdAt: new Date().toISOString(),
      }
      setStore((prev) => ({
        ...prev,
        conversations: prev.conversations.map((c) =>
          c.id === conversationId
            ? {
                ...c,
                messages: [...c.messages, assistantMessage],
                updatedAt: assistantMessage.createdAt,
              }
            : c
        ),
      }))
    } catch (sendError) {
      const message =
        sendError instanceof Error
          ? sendError.message
          : "Error desconocido al contactar el backend."
      setError(message)
      const fallbackMessage: ChatMessage = {
        id: createId(),
        role: "assistant",
        content:
          "No pude generar la respuesta en este momento. Revisá que el backend esté levantado y volvé a intentar.",
        createdAt: new Date().toISOString(),
      }
      setStore((prev) => ({
        ...prev,
        conversations: prev.conversations.map((c) =>
          c.id === conversationId
            ? {
                ...c,
                messages: [...c.messages, fallbackMessage],
                updatedAt: fallbackMessage.createdAt,
              }
            : c
        ),
      }))
    } finally {
      setIsLoading(false)
    }
  }

  const setComposerFromPrompt = (prompt: string) => setComposer(prompt)

  const handleComposerKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      void handleSend()
    }
  }

  return {
    store,
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
  }
}

export type UseChatStoreReturn = ReturnType<typeof useChatStore>
