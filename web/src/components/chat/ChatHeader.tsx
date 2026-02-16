import { SidebarTrigger } from "@/components/ui/sidebar"
import { ThemeSwitcher } from "@/components/theme-switcher"

type ChatHeaderProps = {
  title: string
}

export function ChatHeader({ title }: ChatHeaderProps) {
  return (
    <header className="flex h-14 items-center justify-between border-b border-border px-4 md:px-6">
      <div className="flex items-center gap-2">
        <SidebarTrigger />
        <p className="min-w-0 truncate text-sm text-foreground">{title}</p>
      </div>
      <ThemeSwitcher />
    </header>
  )
}
