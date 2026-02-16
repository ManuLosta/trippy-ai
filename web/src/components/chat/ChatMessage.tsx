import type { ChatMessage as ChatMessageType } from "@/types/chat"
import { formatTime } from "@/lib/chat-utils"
import { cn } from "@/lib/utils"
import { MarkdownProse } from "@/components/ui/markdown-prose"

export function UserMessage({ message }: { message: ChatMessageType }) {
  return (
    <article className="flex justify-end">
      <div className="max-w-[88%] rounded-[22px] bg-muted px-4 py-3 text-[15px] leading-7 text-foreground md:max-w-[80%]">
        <p className="whitespace-pre-wrap">{message.content}</p>
      </div>
    </article>
  )
}

export function AssistantMessage({ message }: { message: ChatMessageType }) {
  return (
    <article className="flex gap-3">
      <img src="./logo.svg" className="size-7 shrink-0" />
      <div className="min-w-0 flex-1">
        <MarkdownProse size="default">{message.content}</MarkdownProse>
        <p className="mt-2 text-xs text-muted-foreground">
          {formatTime(message.createdAt)}
        </p>
      </div>
    </article>
  )
}

export function LoadingIndicator() {
  return (
    <article className="flex gap-3">
      <div className="mt-1 hidden size-7 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground md:flex p-1">
        <img src="./logo.svg" />
      </div>
      <div className="flex h-8 items-center gap-1 text-muted-foreground">
        <span
          className={cn(
            "size-1.5 animate-pulse rounded-full bg-muted-foreground"
          )}
        />
        <span
          className={cn(
            "size-1.5 animate-pulse rounded-full bg-muted-foreground"
          )}
          style={{ animationDelay: "140ms" }}
        />
        <span
          className={cn(
            "size-1.5 animate-pulse rounded-full bg-muted-foreground"
          )}
          style={{ animationDelay: "280ms" }}
        />
      </div>
    </article>
  )
}
