import type { ChatMessage as ChatMessageType } from "@/types/chat"
import ReactMarkdown from "react-markdown"
import { formatTime } from "@/lib/chat-utils"
import { cn } from "@/lib/utils"

const markdownComponents = {
  h1: ({ children }: { children?: React.ReactNode }) => (
    <h1 className="mt-4 mb-2 text-2xl font-bold first:mt-0">{children}</h1>
  ),
  h2: ({ children }: { children?: React.ReactNode }) => (
    <h2 className="mt-3 mb-2 text-xl font-semibold first:mt-0">{children}</h2>
  ),
  h3: ({ children }: { children?: React.ReactNode }) => (
    <h3 className="mt-2 mb-1 text-lg font-semibold first:mt-0">{children}</h3>
  ),
  h4: ({ children }: { children?: React.ReactNode }) => (
    <h4 className="mt-2 mb-1 text-base font-semibold first:mt-0">{children}</h4>
  ),
  p: ({ children }: { children?: React.ReactNode }) => (
    <p className="mb-3 last:mb-0">{children}</p>
  ),
  ul: ({ children }: { children?: React.ReactNode }) => (
    <ul className="ml-4 mb-3 list-disc space-y-1">{children}</ul>
  ),
  ol: ({ children }: { children?: React.ReactNode }) => (
    <ol className="ml-4 mb-3 list-decimal space-y-1">{children}</ol>
  ),
  li: ({ children }: { children?: React.ReactNode }) => (
    <li className="ml-1">{children}</li>
  ),
  blockquote: ({ children }: { children?: React.ReactNode }) => (
    <blockquote className="my-3 border-l-4 border-primary pl-4 italic">
      {children}
    </blockquote>
  ),
  code: ({
    children,
    className,
  }: {
    children?: React.ReactNode
    className?: string
  }) => {
    const isInline = !className
    return isInline ? (
      <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-sm">
        {children}
      </code>
    ) : (
      <code className={className}>{children}</code>
    )
  },
  pre: ({ children }: { children?: React.ReactNode }) => (
    <pre className="my-3 overflow-x-auto rounded-lg border border-border bg-muted/50 p-4">
      {children}
    </pre>
  ),
  table: ({ children }: { children?: React.ReactNode }) => (
    <div className="my-3 overflow-x-auto">
      <table className="w-full border-collapse border border-border">
        {children}
      </table>
    </div>
  ),
  thead: ({ children }: { children?: React.ReactNode }) => (
    <thead className="bg-muted">{children}</thead>
  ),
  tbody: ({ children }: { children?: React.ReactNode }) => (
    <tbody>{children}</tbody>
  ),
  tr: ({ children }: { children?: React.ReactNode }) => (
    <tr className="border-b border-border">{children}</tr>
  ),
  th: ({ children }: { children?: React.ReactNode }) => (
    <th className="border border-border px-3 py-2 text-left font-semibold">
      {children}
    </th>
  ),
  td: ({ children }: { children?: React.ReactNode }) => (
    <td className="border border-border px-3 py-2">{children}</td>
  ),
  a: ({
    children,
    href,
  }: {
    children?: React.ReactNode
    href?: string
  }) => (
    <a
      href={href}
      className="text-primary hover:underline"
      target="_blank"
      rel="noopener noreferrer"
    >
      {children}
    </a>
  ),
  strong: ({ children }: { children?: React.ReactNode }) => (
    <strong className="font-bold">{children}</strong>
  ),
  em: ({ children }: { children?: React.ReactNode }) => (
    <em className="italic">{children}</em>
  ),
}

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
      <div className="mt-1 flex size-7 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">
        T
      </div>
      <div className="min-w-0 flex-1">
        <div className="prose prose-invert max-w-none text-[15px] leading-7">
          <ReactMarkdown components={markdownComponents}>
            {message.content}
          </ReactMarkdown>
        </div>
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
      <div className="mt-1 flex size-7 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">
        T
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
