import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"

type NewConversationDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  onConfirm: () => void
  onCancel: () => void
}

export function NewConversationDialog({
  open,
  onOpenChange,
  onConfirm,
  onCancel,
}: NewConversationDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent showCloseButton={false} className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Crear nueva conversación</DialogTitle>
          <DialogDescription>
            ¿Querés iniciar un chat nuevo? Vas a mantener el historial actual y
            cambiar a una conversación vacía.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="sm:justify-end">
          <Button variant="outline" onClick={onCancel}>
            Cancelar
          </Button>
          <Button onClick={onConfirm}>Sí, crear</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
