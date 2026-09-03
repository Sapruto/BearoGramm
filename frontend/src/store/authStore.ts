import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type AuthStore = {
    phone: string;
    setPhone: (phone: string) => void;

    token: string | null;
    setToken: (token: string) => void;
    logout: () => void;
};

export const useAuthStore = create<AuthStore>()(
    persist(
        (set) => ({
            phone: '',
            setPhone: (phone) => set({ phone }),

            token: null,
            setToken: (token) => set({ token }),
            logout: () => set({ token: null, phone: '' }),
        }),
        {
            name: 'auth-storage',
            partialize: (state) => ({ token: state.token }),
        }
    )
);