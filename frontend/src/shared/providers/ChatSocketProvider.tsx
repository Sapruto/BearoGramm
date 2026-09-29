import { useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { useAuthStore } from '../../store/authStore';
import { chatSocket } from '../api/wsClient';
import { addMessageToCache } from '../lib/addMessageToCache';

export function ChatSocketProvider({ children }: { children: React.ReactNode }) {
    const queryClient = useQueryClient();
    const token = useAuthStore((state) => state.token);

    useEffect(() => {
        if (!token) return;

        chatSocket.connect();

        const unsubscribe = chatSocket.subscribe((msg) => {
            switch (msg.type) {
                case 'message_created':
                    addMessageToCache(queryClient, msg.data.chat_uuid, msg.data);
                    break;
                // case 'typing':
                    // TODO: implement typing bubble
                    // break;
            }
        });

        return () => {
            unsubscribe();
            chatSocket.disconnect();
        };
    }, [token, queryClient]);

    return <>{children}</>;
}