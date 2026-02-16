import type { ChatMessage, Conversation, ChatStore, LegacyConversationState } from "@/types/chat"
import { STORAGE_KEY } from "./constants"

export function createId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID()
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

export function summarizeChatTitle(content: string): string {
  const compact = content.replace(/\s+/g, " ").trim()
  if (compact.length <= 40) {
    return compact
  }
  return `${compact.slice(0, 40)}...`
}

export function buildConversationTitle(messages: ChatMessage[]): string {
  const firstUserMessage = messages.find(
    (message) => message.role === "user" && message.content.trim().length > 0
  )
  if (!firstUserMessage) {
    return "Nuevo chat"
  }
  return summarizeChatTitle(firstUserMessage.content)
}

export function normalizeMessages(raw: unknown): ChatMessage[] {
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

export function createConversation(messages: ChatMessage[] = []): Conversation {
  const now = new Date().toISOString()
  return {
    id: createId(),
    title: buildConversationTitle(messages),
    messages,
    createdAt: now,
    updatedAt: now,
  }
}

export function createInitialStore(): ChatStore {
  const initialConversation = createConversation()
  return {
    activeConversationId: initialConversation.id,
    conversations: [initialConversation],
  }
}

export function normalizeConversation(raw: unknown): Conversation | null {
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

export function migrateLegacyState(parsed: unknown): ChatStore | null {
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

export function loadStore(): ChatStore {
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
          .filter((c): c is Conversation => c !== null)
      : []
    if (conversations.length === 0) {
      return createInitialStore()
    }
    const activeConversationId =
      typeof candidate.activeConversationId === "string" &&
      conversations.some((c) => c.id === candidate.activeConversationId)
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

export function toApiMessages(messages: ChatMessage[]): { role: ChatMessage["role"]; content: string }[] {
  return messages.map(({ role, content }) => ({ role, content }))
}

export function formatTime(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString("es-AR", {
    hour: "2-digit",
    minute: "2-digit",
  })
}
