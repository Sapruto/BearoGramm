import { useQueryClient } from '@tanstack/react-query';
import { useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { chatSocket } from '../api/wsClient';
import { addMessageToCache } from '../lib/addMessageToCache';
import { messageNotify } from '../lib/messageNotify';
import { queryKeys } from '../lib/queryKeys';
import { useRemovePersonalChat } from '../lib/useRemovePersonalChat';

export function ChatSocketProvider({ children }: { children: React.ReactNode }) {
    const queryClient = useQueryClient();
    const token = useAuthStore((state) => state.token);
    const { uuid: chatUUID } = useParams();

    const chatUUIDRef = useRef(chatUUID);
    chatUUIDRef.current = chatUUID;

    const removePersonalChat = useRemovePersonalChat();

    useEffect(() => {
        if (Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }, []);

    useEffect(() => {
        if (!token) return;

        chatSocket.connect();

        const unsubscribe = chatSocket.subscribe((msg) => {
            switch (msg.type) {
                case 'message_created':
                    messageNotify(chatUUIDRef.current, msg.data);
                    addMessageToCache(queryClient, msg.data.chat_uuid, msg.data);
                    break;
                case 'chat_created':
                    queryClient.invalidateQueries({ queryKey: queryKeys.personalChats });
                    break;
                case 'chat_deleted':
                    removePersonalChat(msg.data.chat_uuid);
                    break;
            }
        });

        return () => {
            unsubscribe();
            chatSocket.disconnect();
        };
    }, [token, queryClient, removePersonalChat]);

    return <>{children}</>;
}