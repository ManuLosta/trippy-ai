export type MessageRole = "user" | "assistant"

export type ChatMessage = {
  id: string
  role: MessageRole
  content: string
  createdAt: string
}

export type Conversation = {
  id: string
  title: string
  messages: ChatMessage[]
  createdAt: string
  updatedAt: string
}

export type ChatStore = {
  activeConversationId: string
  conversations: Conversation[]
}

export type LegacyConversationState = {
  conversationId: string
  messages: ChatMessage[]
}

export type ApiMessage = {
  role: MessageRole
  content: string
}

export type ApiResponse = {
  message: string
}
