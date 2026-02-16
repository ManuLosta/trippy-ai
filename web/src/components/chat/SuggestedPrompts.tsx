import { Button } from "@/components/ui/button"

type SuggestedPromptsProps = {
  prompts: readonly string[]
  onSelectPrompt: (prompt: string) => void
}

export function SuggestedPrompts({
  prompts,
  onSelectPrompt,
}: SuggestedPromptsProps) {
  return (
    <div className="mt-[16vh]">
      <h1 className="text-center text-3xl font-medium text-foreground">
        ¿Qué viaje querés planear hoy?
      </h1>
      <p className="mt-3 text-center text-sm text-muted-foreground">
        Pedime vuelos, clima, actividades, itinerario y presupuesto.
      </p>
      <div className="mx-auto mt-8 grid max-w-2xl grid-cols-1 gap-3 sm:grid-cols-2 sm:gap-x-4 sm:gap-y-3">
        {prompts.map((prompt) => (
          <Button
            key={prompt}
            type="button"
            variant="outline"
            className="h-auto min-w-0 cursor-pointer justify-start rounded-xl px-4 py-3 text-left font-normal whitespace-normal transition-colors hover:bg-accent/50 [&>span]:block [&>span]:break-words [&>span]:text-wrap"
            onClick={() => onSelectPrompt(prompt)}
          >
            <span className="text-sm text-foreground">{prompt}</span>
          </Button>
        ))}
      </div>
    </div>
  )
}
