import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { queryClient } from '../shared/api/queryClient';

type AuthStore = {
    phone: string;
    setPhone: (phone: string) => void;

    justCreated: boolean;
    setJustCreated: (justCreated: boolean) => void;

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

            justCreated: false,
            setJustCreated: (justCreated: boolean) => set({ justCreated }),

            token: null,
            userUUID: null,
            setToken: (token) => set({ token }),
            setUserUUID: (userUUID) => set({ userUUID }),
            logout: () => {
                const { token } = get();
                if (token === null)
                    return;

                queryClient.removeQueries({ queryKey: ['my_profile'] });
                set({ token: null, userUUID: null, phone: '' });
            },

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