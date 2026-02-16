import type { ApiMessage, ApiResponse } from "@/types/chat"
import { API_BASE_URL } from "./constants"

export async function sendChatMessage(
  messages: ApiMessage[]
): Promise<ApiResponse> {
  const response = await fetch(`${API_BASE_URL.replace(/\/$/, "")}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ messages }),
  })
  if (!response.ok) {
    const payload = (await response.json().catch(() => ({}))) as {
      detail?: string
    }
    throw new Error(payload.detail ?? "No se pudo generar el plan de viaje.")
  }
  return response.json() as Promise<ApiResponse>
}
