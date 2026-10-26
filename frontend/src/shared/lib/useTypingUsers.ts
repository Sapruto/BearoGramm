import { EMPTY, useTypingStore } from "@/store/typingStore";

export const useTypingUsers = (chatId: string) => useTypingStore((s) => s.usernamesByChat[chatId] ?? EMPTY);