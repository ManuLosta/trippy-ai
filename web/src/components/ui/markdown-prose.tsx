"use client"

import type { ComponentProps } from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { cn } from "@/lib/utils"

/**
 * Markdown typography – shadcn-style utility classes for rendered markdown.
 * Use with ReactMarkdown via markdownTypographyComponents or the MarkdownProse wrapper.
 *
 * Elements: h1, h2, h3, h4, p, blockquote, table, list, inline code.
 * Variants: lead, large, small, muted (use via wrapper or data attributes).
 */
export const markdownTypography = {
  h1: "mt-6 scroll-m-20 text-2xl font-bold tracking-tight first:mt-0",
  h2: "mt-6 scroll-m-20 text-xl font-semibold tracking-tight first:mt-0",
  h3: "mt-4 scroll-m-20 text-lg font-semibold first:mt-0",
  h4: "mt-4 scroll-m-20 text-base font-semibold first:mt-0",
  p: "leading-7 [&:not(:first-child)]:mt-3",
  blockquote: "mt-3 border-l-4 border-primary pl-4 italic text-muted-foreground",
  ul: "my-3 ml-4 list-disc [&>li]:mt-1",
  ol: "my-3 ml-4 list-decimal [&>li]:mt-1",
  li: "leading-7",
  table: "w-full min-w-0 border-collapse text-left text-sm",
  thead: "bg-muted",
  tbody: "divide-y divide-border",
  tr: "border-b border-border transition-colors hover:bg-muted/30",
  th: "border border-border px-3 py-2 font-semibold text-foreground whitespace-nowrap",
  td: "border border-border px-3 py-2 text-foreground break-words",
  inlineCode:
    "rounded bg-muted px-1.5 py-0.5 font-mono text-sm text-foreground",
  pre: "my-3 overflow-x-auto rounded-lg border border-border bg-muted/50 p-4",
  a: "text-primary underline underline-offset-4 hover:no-underline",
  strong: "font-bold",
  em: "italic",
  // Variants (use on wrapper or specific elements)
  lead: "text-lg text-muted-foreground",
  large: "text-lg",
  small: "text-sm text-muted-foreground",
  muted: "text-muted-foreground",
} as const

type TypographyProps = { children?: React.ReactNode; className?: string }

export const markdownTypographyComponents: ComponentProps<
  typeof ReactMarkdown
>["components"] = {
  h1: ({ children, className }) => (
    <h1 className={cn(markdownTypography.h1, className)}>{children}</h1>
  ),
  h2: ({ children, className }) => (
    <h2 className={cn(markdownTypography.h2, className)}>{children}</h2>
  ),
  h3: ({ children, className }) => (
    <h3 className={cn(markdownTypography.h3, className)}>{children}</h3>
  ),
  h4: ({ children, className }) => (
    <h4 className={cn(markdownTypography.h4, className)}>{children}</h4>
  ),
  p: ({ children, className }) => (
    <p className={cn(markdownTypography.p, className)}>{children}</p>
  ),
  ul: ({ children, className }) => (
    <ul className={cn(markdownTypography.ul, className)}>{children}</ul>
  ),
  ol: ({ children, className }) => (
    <ol className={cn(markdownTypography.ol, className)}>{children}</ol>
  ),
  li: ({ children, className }) => (
    <li className={cn(markdownTypography.li, className)}>{children}</li>
  ),
  blockquote: ({ children, className }) => (
    <blockquote
      className={cn(markdownTypography.blockquote, className)}
    >
      {children}
    </blockquote>
  ),
  code: ({
    children,
    className,
  }: TypographyProps & { className?: string }) => {
    const isInline = !className
    return isInline ? (
      <code className={markdownTypography.inlineCode}>{children}</code>
    ) : (
      <code className={className}>{children}</code>
    )
  },
  pre: ({ children, className }) => (
    <pre className={cn(markdownTypography.pre, className)}>{children}</pre>
  ),
  table: ({ children, className }) => (
    <div className="my-4 w-full overflow-x-auto rounded-lg border border-border">
      <table className={cn(markdownTypography.table, className)}>
        {children}
      </table>
    </div>
  ),
  thead: ({ children, className }) => (
    <thead className={cn(markdownTypography.thead, className)}>
      {children}
    </thead>
  ),
  tbody: ({ children, className }) => (
    <tbody className={cn(markdownTypography.tbody, className)}>
      {children}
    </tbody>
  ),
  tr: ({ children, className }) => (
    <tr className={cn(markdownTypography.tr, className)}>{children}</tr>
  ),
  th: ({ children, className }) => (
    <th className={cn(markdownTypography.th, className)}>{children}</th>
  ),
  td: ({ children, className }) => (
    <td className={cn(markdownTypography.td, className)}>{children}</td>
  ),
  a: ({
    children,
    href,
    className,
  }: TypographyProps & { href?: string }) => (
    <a
      href={href}
      className={cn(markdownTypography.a, className)}
      target="_blank"
      rel="noopener noreferrer"
    >
      {children}
    </a>
  ),
  strong: ({ children, className }: TypographyProps) => (
    <strong className={cn(markdownTypography.strong, className)}>
      {children}
    </strong>
  ),
  em: ({ children, className }: TypographyProps) => (
    <em className={cn(markdownTypography.em, className)}>{children}</em>
  ),
}

type MarkdownProseProps = {
  children: string
  className?: string
  /** Base font size / line height (default: body) */
  size?: "sm" | "default" | "large"
  /** Apply muted color to all text */
  muted?: boolean
}

export function MarkdownProse({
  children,
  className,
  size = "default",
  muted,
}: MarkdownProseProps) {
  return (
    <div
      className={cn(
        "max-w-none text-foreground",
        size === "sm" && "text-sm leading-6",
        size === "default" && "text-[15px] leading-7",
        size === "large" && "text-base leading-7",
        muted && markdownTypography.muted,
        className
      )}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownTypographyComponents}>
        {children}
      </ReactMarkdown>
    </div>
  )
}
