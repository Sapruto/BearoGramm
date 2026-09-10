import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type AuthStore = {
    phone: string;
    setPhone: (phone: string) => void;

    token: string | null;
    userUUID: string | null;
    setToken: (token: string) => void;
    setUserUUID: (userUUID: string) => void;
    logout: () => void;

    isLoggedIn: () => boolean;
};

export const useAuthStore = create<AuthStore>()(
    persist(
        (set, get) => ({
            phone: '',
            setPhone: (phone) => set({ phone }),

            token: null,
            userUUID: null,
            setToken: (token) => set({ token }),
            setUserUUID: (userUUID) => set({ userUUID }),
            logout: () => set({ token: null, userUUID: null, phone: '' }),

            isLoggedIn: () => {
                const state = get();
                return Boolean(state.token && state.userUUID);
            },
        }),
        {
            name: 'auth-storage',
            partialize: (state) => ({ token: state.token, userUUID: state.userUUID }),
        }
    )
);