import type { Conversation } from "@/types/chat"
import { useRef, useEffect } from "react"
import { SUGGESTED_PROMPTS } from "@/lib/constants"
import { SuggestedPrompts } from "./SuggestedPrompts"
import { UserMessage, AssistantMessage, LoadingIndicator } from "./ChatMessage"

type ChatContentProps = {
  activeConversation: Conversation | undefined
  isLoading: boolean
  onSelectPrompt: (prompt: string) => void
}

export function ChatContent({
  activeConversation,
  isLoading,
  onSelectPrompt,
}: ChatContentProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const container = scrollRef.current
    if (!container) return
    container.scrollTop = container.scrollHeight
  }, [activeConversation?.messages, isLoading])

  const isEmpty =
    !activeConversation || activeConversation.messages.length === 0

  return (
    <section
      ref={scrollRef}
      className="flex-1 overflow-y-auto px-4 pb-44 pt-6 md:px-8"
    >
      <div className="mx-auto w-full max-w-3xl">
        {isEmpty ? (
          <SuggestedPrompts
            prompts={SUGGESTED_PROMPTS}
            onSelectPrompt={onSelectPrompt}
          />
        ) : (
          <div className="space-y-6">
            {activeConversation.messages.map((message) =>
              message.role === "user" ? (
                <UserMessage key={message.id} message={message} />
              ) : (
                <AssistantMessage key={message.id} message={message} />
              )
            )}
            {isLoading ? <LoadingIndicator /> : null}
          </div>
        )}
      </div>
    </section>
  )
}
