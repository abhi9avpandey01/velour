import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "./api";

// --- Types ---

export interface ChatMessageItem {
  role: "user" | "assistant";
  content: string;
}

export interface ChatReply {
  reply: string;
}

// --- Hooks ---

/**
 * Fetch the current chat session history.
 * Returns an array of user and assistant messages.
 */
export function useChatHistory() {
  return useQuery({
    queryKey: ["chat-history"],
    queryFn: async () => {
      const res = await api.get("/chat/history");
      return res.data.data as ChatMessageItem[];
    },
  });
}

/**
 * Send a message to the Velour AI Stylist and receive a response.
 * Automatically invalidates the chat history cache on success.
 */
export function useSendMessage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (content: string) => {
      const res = await api.post("/chat/", { content });
      return res.data.data as ChatReply;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["chat-history"] });
    },
  });
}
