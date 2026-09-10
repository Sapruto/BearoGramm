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
};

export const useAuthStore = create<AuthStore>()(
    persist(
        (set) => ({
            phone: '',
            setPhone: (phone) => set({ phone }),

            token: null,
            userUUID: null,
            setToken: (token) => set({ token }),
            setUserUUID: (userUUID) => set({ userUUID }),
            logout: () => set({ token: null, userUUID: null, phone: '' }),
        }),
        {
            name: 'auth-storage',
            partialize: (state) => ({ token: state.token }),
        }
    )
);