import { create } from 'zustand';

const TTL = 6000;
export const EMPTY: string[] = [];
const timers = new Map<string, ReturnType<typeof setTimeout>>();

type TypingState = {
    usernamesByChat: Record<string, string[]>;
    add: (chatId: string, username: string) => void;
    remove: (chatId: string, username: string) => void;
    clear: () => void;
};

export const useTypingStore = create<TypingState>((set, get) => ({
    usernamesByChat: {},

    add: (chatId, username) => {
        const key = `${chatId}:${username}`;
        clearTimeout(timers.get(key));
        timers.set(key, setTimeout(() => get().remove(chatId, username), TTL));

        const current = get().usernamesByChat[chatId] ?? EMPTY;
        if (current.includes(username)) return;

        set((s) => ({ usernamesByChat: { ...s.usernamesByChat, [chatId]: [...current, username] } }));
    },

    remove: (chatId, username) => {
        const key = `${chatId}:${username}`;
        clearTimeout(timers.get(key));
        timers.delete(key);

        const current = get().usernamesByChat[chatId] ?? EMPTY;
        if (!current.includes(username)) return;

        const next = current.filter((u) => u !== username);
        set((s) => {
            const usernamesByChat = { ...s.usernamesByChat };
            if (next.length > 0) usernamesByChat[chatId] = next;
            else delete usernamesByChat[chatId];
            return { usernamesByChat };
        });
    },

    clear: () => {
        timers.forEach(clearTimeout);
        timers.clear();
        set({ usernamesByChat: {} });
    },
}));