import { useEffect, useMemo, useRef, useState } from "react"
import type { FormEvent, KeyboardEvent } from "react"

type MessageRole = "user" | "assistant"

type ChatMessage = {
  id: string
  role: MessageRole
  content: string
  createdAt: string
}

type Conversation = {
  id: string
  title: string
  messages: ChatMessage[]
  createdAt: string
  updatedAt: string
}

type ChatStore = {
  activeConversationId: string
  conversations: Conversation[]
}

type LegacyConversationState = {
  conversationId: string
  messages: ChatMessage[]
}

type ApiMessage = {
  role: MessageRole
  content: string
}

type ApiResponse = {
  message: string
}

const STORAGE_KEY = "trippy-ai-conversation-v1"
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api"

const SUGGESTED_PROMPTS = [
  "Quiero viajar a Madrid 3 días desde Buenos Aires con un presupuesto de 5000 USD.",
  "Armame un plan de viaje a Roma en pareja, con enfoque cultural y gastronómico.",
  "Necesito opciones de vuelo y actividades para un fin de semana en Santiago de Chile.",
  "Dame una propuesta para Londres 5 días con foco en museos y bajo costo.",
]

function createId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID()
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function summarizeChatTitle(content: string) {
  const compact = content.replace(/\s+/g, " ").trim()
  if (compact.length <= 40) {
    return compact
  }
  return `${compact.slice(0, 40)}...`
}

function buildConversationTitle(messages: ChatMessage[]) {
  const firstUserMessage = messages.find(
    (message) => message.role === "user" && message.content.trim().length > 0
  )

  if (!firstUserMessage) {
    return "Nuevo chat"
  }

  return summarizeChatTitle(firstUserMessage.content)
}

function normalizeMessages(raw: unknown): ChatMessage[] {
  if (!Array.isArray(raw)) {
    return []
  }

  return raw.flatMap((candidate) => {
    if (!candidate || typeof candidate !== "object") {
      return []
    }

    const message = candidate as Partial<ChatMessage>
    if (message.role !== "user" && message.role !== "assistant") {
      return []
    }

    if (typeof message.content !== "string") {
      return []
    }

    return [
      {
        id: typeof message.id === "string" ? message.id : createId(),
        role: message.role,
        content: message.content,
        createdAt:
          typeof message.createdAt === "string"
            ? message.createdAt
            : new Date().toISOString(),
      },
    ]
  })
}

function createConversation(messages: ChatMessage[] = []): Conversation {
  const now = new Date().toISOString()
  return {
    id: createId(),
    title: buildConversationTitle(messages),
    messages,
    createdAt: now,
    updatedAt: now,
  }
}

function createInitialStore(): ChatStore {
  const initialConversation = createConversation()
  return {
    activeConversationId: initialConversation.id,
    conversations: [initialConversation],
  }
}

function normalizeConversation(raw: unknown): Conversation | null {
  if (!raw || typeof raw !== "object") {
    return null
  }

  const candidate = raw as Partial<Conversation>
  if (typeof candidate.id !== "string") {
    return null
  }

  const messages = normalizeMessages(candidate.messages)
  const now = new Date().toISOString()

  return {
    id: candidate.id,
    title:
      typeof candidate.title === "string" && candidate.title.trim().length > 0
        ? candidate.title
        : buildConversationTitle(messages),
    messages,
    createdAt:
      typeof candidate.createdAt === "string" ? candidate.createdAt : now,
    updatedAt:
      typeof candidate.updatedAt === "string"
        ? candidate.updatedAt
        : messages.at(-1)?.createdAt ?? now,
  }
}

function migrateLegacyState(parsed: unknown): ChatStore | null {
  if (!parsed || typeof parsed !== "object") {
    return null
  }

  const legacy = parsed as Partial<LegacyConversationState>
  if (typeof legacy.conversationId !== "string") {
    return null
  }

  const messages = normalizeMessages(legacy.messages)
  const now = new Date().toISOString()
  const conversation: Conversation = {
    id: legacy.conversationId,
    title: buildConversationTitle(messages),
    messages,
    createdAt: now,
    updatedAt: messages.at(-1)?.createdAt ?? now,
  }

  return {
    activeConversationId: conversation.id,
    conversations: [conversation],
  }
}

function loadStore(): ChatStore {
  if (typeof window === "undefined") {
    return createInitialStore()
  }

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) {
      return createInitialStore()
    }

    const parsed = JSON.parse(raw) as unknown

    const migrated = migrateLegacyState(parsed)
    if (migrated) {
      return migrated
    }

    if (!parsed || typeof parsed !== "object") {
      return createInitialStore()
    }

    const candidate = parsed as Partial<ChatStore>
    const conversations = Array.isArray(candidate.conversations)
      ? candidate.conversations
          .map((conversation) => normalizeConversation(conversation))
          .filter((conversation): conversation is Conversation => conversation !== null)
      : []

    if (conversations.length === 0) {
      return createInitialStore()
    }

    const activeConversationId =
      typeof candidate.activeConversationId === "string" &&
      conversations.some((conversation) => conversation.id === candidate.activeConversationId)
        ? candidate.activeConversationId
        : conversations[0].id

    return {
      activeConversationId,
      conversations,
    }
  } catch {
    return createInitialStore()
  }
}

function toApiMessages(messages: ChatMessage[]): ApiMessage[] {
  return messages.map(({ role, content }) => ({ role, content }))
}

function formatTime(timestamp: string) {
  return new Date(timestamp).toLocaleTimeString("es-AR", {
    hour: "2-digit",
    minute: "2-digit",
  })
}

export default function App() {
  const [store, setStore] = useState<ChatStore>(() => loadStore())
  const [composer, setComposer] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isNewConversationModalOpen, setIsNewConversationModalOpen] =
    useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

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
        (conversation) => conversation.id === store.activeConversationId
      ) ?? orderedConversations[0],
    [orderedConversations, store.activeConversationId, store.conversations]
  )

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(store))
  }, [store])

  useEffect(() => {
    const container = scrollRef.current
    if (!container) {
      return
    }
    container.scrollTop = container.scrollHeight
  }, [activeConversation?.messages, isLoading])

  const createNewConversation = () => {
    const newConversation = createConversation()
    setStore((previous) => ({
      activeConversationId: newConversation.id,
      conversations: [newConversation, ...previous.conversations],
    }))
    setComposer("")
    setError(null)
  }

  const selectConversation = (conversationId: string) => {
    setStore((previous) => ({
      ...previous,
      activeConversationId: conversationId,
    }))
    setError(null)
  }

  const openNewConversationModal = () => {
    setIsNewConversationModalOpen(true)
  }

  const closeNewConversationModal = () => {
    setIsNewConversationModalOpen(false)
  }

  const confirmNewConversation = () => {
    createNewConversation()
    setIsNewConversationModalOpen(false)
  }

  const handleSend = async (event?: FormEvent) => {
    event?.preventDefault()

    const text = composer.trim()
    if (!text || isLoading || !activeConversation) {
      return
    }

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

    setStore((previous) => ({
      ...previous,
      conversations: previous.conversations.map((conversation) =>
        conversation.id === conversationId
          ? {
              ...conversation,
              title: updatedTitle,
              messages: updatedMessages,
              updatedAt: timestamp,
            }
          : conversation
      ),
    }))

    setComposer("")
    setError(null)
    setIsLoading(true)

    try {
      const response = await fetch(`${API_BASE_URL.replace(/\/$/, "")}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: toApiMessages(updatedMessages),
        }),
      })

      if (!response.ok) {
        const payload = (await response.json().catch(() => ({}))) as {
          detail?: string
        }
        throw new Error(payload.detail ?? "No se pudo generar el plan de viaje.")
      }

      const payload = (await response.json()) as ApiResponse
      const assistantMessage: ChatMessage = {
        id: createId(),
        role: "assistant",
        content: payload.message,
        createdAt: new Date().toISOString(),
      }

      setStore((previous) => ({
        ...previous,
        conversations: previous.conversations.map((conversation) =>
          conversation.id === conversationId
            ? {
                ...conversation,
                messages: [...conversation.messages, assistantMessage],
                updatedAt: assistantMessage.createdAt,
              }
            : conversation
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

      setStore((previous) => ({
        ...previous,
        conversations: previous.conversations.map((conversation) =>
          conversation.id === conversationId
            ? {
                ...conversation,
                messages: [...conversation.messages, fallbackMessage],
                updatedAt: fallbackMessage.createdAt,
              }
            : conversation
        ),
      }))
    } finally {
      setIsLoading(false)
    }
  }

  const handleComposerKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      void handleSend()
    }
  }

  return (
    <div className="h-screen bg-[#212121] text-[#ececec]">
      <div className="mx-auto flex h-full max-w-[1600px]">
        <aside className="hidden w-[260px] shrink-0 flex-col border-r border-white/10 bg-[#171717] md:flex">
          <div className="flex h-14 items-center gap-3 px-3">
            <div className="flex size-7 items-center justify-center rounded-full bg-[#10a37f] text-xs font-semibold text-black">
              T
            </div>
            <p className="text-sm font-medium text-[#f0f0f0]">Trippy AI</p>
          </div>

          <div className="space-y-2 px-3 pb-4">
            <button
              type="button"
              onClick={createNewConversation}
              className="flex h-10 w-full items-center justify-start rounded-lg border border-white/10 bg-[#2a2a2a] px-3 text-sm text-[#ececec] transition hover:bg-[#333333]"
            >
              + Nuevo chat
            </button>
          </div>

          <div className="flex-1 overflow-y-auto px-2 pb-4">
            <p className="px-2 pb-2 text-xs font-medium text-[#9a9a9a]">Tus chats</p>
            {orderedConversations.length === 0 ? (
              <p className="px-2 text-xs text-[#7b7b7b]">Sin conversaciones todavía.</p>
            ) : (
              orderedConversations.map((conversation) => (
                <button
                  key={conversation.id}
                  type="button"
                  onClick={() => selectConversation(conversation.id)}
                  className={`mb-1 flex w-full items-center rounded-lg px-2 py-2 text-left text-sm transition ${
                    store.activeConversationId === conversation.id
                      ? "bg-[#2d2d2d] text-[#f1f1f1]"
                      : "text-[#d7d7d7] hover:bg-[#2a2a2a]"
                  }`}
                >
                  {conversation.title}
                </button>
              ))
            )}
          </div>

          <div className="border-t border-white/10 p-3 text-xs text-[#8b8b8b]">
            Conversación: {activeConversation?.id.slice(0, 8) ?? "-"} ·{" "}
            {activeConversation?.messages.length ?? 0} mensajes
          </div>
        </aside>

        <main className="relative flex min-w-0 flex-1 flex-col">
          <header className="flex h-14 items-center justify-between border-b border-white/10 px-4 md:px-6">
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={createNewConversation}
                className="rounded-md px-2 py-1 text-xs text-[#c9c9c9] hover:bg-white/10 md:hidden"
              >
                Nuevo
              </button>
              <p className="text-sm text-[#e4e4e4]">{activeConversation?.title ?? "Nuevo chat"}</p>
            </div>
            <p className="text-xs text-[#9a9a9a]">Travel planner mode</p>
          </header>

          <section
            ref={scrollRef}
            className="flex-1 overflow-y-auto px-4 pb-44 pt-6 md:px-8"
          >
            <div className="mx-auto w-full max-w-3xl">
              {!activeConversation || activeConversation.messages.length === 0 ? (
                <div className="mt-[16vh]">
                  <h1 className="text-center text-3xl font-medium text-[#e9e9e9]">
                    ¿Qué viaje querés planear hoy?
                  </h1>
                  <p className="mt-3 text-center text-sm text-[#9f9f9f]">
                    Pedime vuelos, clima, actividades, itinerario y presupuesto.
                  </p>
                  <div className="mx-auto mt-8 grid max-w-2xl gap-2 sm:grid-cols-2">
                    {SUGGESTED_PROMPTS.map((prompt) => (
                      <button
                        key={prompt}
                        type="button"
                        onClick={() => setComposer(prompt)}
                        className="rounded-xl border border-white/10 bg-[#2a2a2a] px-4 py-3 text-left text-sm text-[#dadada] transition hover:bg-[#343434]"
                      >
                        {prompt}
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="space-y-6">
                  {activeConversation.messages.map((message) =>
                    message.role === "user" ? (
                      <article key={message.id} className="flex justify-end">
                        <div className="max-w-[88%] rounded-[22px] bg-[#303030] px-4 py-3 text-[15px] leading-7 text-[#f2f2f2] md:max-w-[80%]">
                          <p className="whitespace-pre-wrap">{message.content}</p>
                        </div>
                      </article>
                    ) : (
                      <article key={message.id} className="flex gap-3">
                        <div className="mt-1 flex size-7 shrink-0 items-center justify-center rounded-full bg-[#10a37f] text-xs font-semibold text-black">
                          T
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="whitespace-pre-wrap text-[15px] leading-7 text-[#e7e7e7]">
                            {message.content}
                          </p>
                          <p className="mt-2 text-xs text-[#8f8f8f]">
                            {formatTime(message.createdAt)}
                          </p>
                        </div>
                      </article>
                    )
                  )}

                  {isLoading ? (
                    <article className="flex gap-3">
                      <div className="mt-1 flex size-7 shrink-0 items-center justify-center rounded-full bg-[#10a37f] text-xs font-semibold text-black">
                        T
                      </div>
                      <div className="flex h-8 items-center gap-1 text-[#b8b8b8]">
                        <span className="size-1.5 animate-pulse rounded-full bg-[#b8b8b8]" />
                        <span
                          className="size-1.5 animate-pulse rounded-full bg-[#b8b8b8]"
                          style={{ animationDelay: "140ms" }}
                        />
                        <span
                          className="size-1.5 animate-pulse rounded-full bg-[#b8b8b8]"
                          style={{ animationDelay: "280ms" }}
                        />
                      </div>
                    </article>
                  ) : null}
                </div>
              )}
            </div>
          </section>

          <footer className="pointer-events-none absolute inset-x-0 bottom-0 bg-gradient-to-t from-[#212121] via-[#212121] to-transparent px-4 pb-5 pt-12 md:px-8">
            <div className="pointer-events-auto mx-auto w-full max-w-3xl">
              <form
                onSubmit={handleSend}
                className="rounded-[28px] border border-white/10 bg-[#2f2f2f] shadow-[0_10px_30px_rgba(0,0,0,0.28)]"
              >
                <div className="flex items-center gap-2 px-3 py-2.5">
                  <button
                    type="button"
                    onClick={openNewConversationModal}
                    className="flex size-8 shrink-0 items-center justify-center rounded-full bg-transparent text-[#bcbcbc] transition hover:bg-white/10 hover:text-white"
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
                  </button>
                  <label htmlFor="travel-prompt" className="sr-only">
                    Prompt de viaje
                  </label>
                  <textarea
                    id="travel-prompt"
                    rows={1}
                    value={composer}
                    onChange={(event) => setComposer(event.target.value)}
                    onKeyDown={handleComposerKeyDown}
                    placeholder="Preguntá lo que quieras sobre tu viaje"
                    className="max-h-56 min-h-8 flex-1 resize-none bg-transparent px-1 py-1 text-[17px] leading-6 text-[#efefef] outline-none placeholder:text-[#9b9b9b]"
                  />
                  <button
                    type="submit"
                    disabled={isLoading || composer.trim().length === 0 || !activeConversation}
                    className="flex size-8 shrink-0 items-center justify-center rounded-full bg-white text-black transition disabled:bg-[#696969] disabled:text-[#c9c9c9]"
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
                  </button>
                </div>
              </form>

              {error ? (
                <p className="mt-2 text-xs text-[#ff8e8e]">Error de API: {error}</p>
              ) : null}


            </div>
          </footer>

          {isNewConversationModalOpen ? (
            <div
              className="absolute inset-0 z-50 flex items-center justify-center bg-black/60 px-4"
              onClick={closeNewConversationModal}
            >
              <div
                className="w-full max-w-md rounded-2xl border border-white/10 bg-[#202020] p-5 shadow-2xl"
                onClick={(event) => event.stopPropagation()}
              >
                <h2 className="text-lg font-medium text-[#f1f1f1]">
                  Crear nueva conversación
                </h2>
                <p className="mt-2 text-sm text-[#b5b5b5]">
                  ¿Querés iniciar un chat nuevo? Vas a mantener el historial actual y
                  cambiar a una conversación vacía.
                </p>
                <div className="mt-5 flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={closeNewConversationModal}
                    className="rounded-lg border border-white/12 px-3 py-2 text-sm text-[#d4d4d4] transition hover:bg-white/10"
                  >
                    Cancelar
                  </button>
                  <button
                    type="button"
                    onClick={confirmNewConversation}
                    className="rounded-lg bg-[#10a37f] px-3 py-2 text-sm font-medium text-black transition hover:bg-[#0f8f70]"
                  >
                    Sí, crear
                  </button>
                </div>
              </div>
            </div>
          ) : null}
        </main>
      </div>
    </div>
  )
}
