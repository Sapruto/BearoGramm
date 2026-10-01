import { useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { chatSocket } from '../api/wsClient';
import { useGetChatPartner } from '../hooks/personal/useGetChatPartner';
import { addMessageToCache } from '../lib/addMessageToCache';
import { messageNotify } from '../lib/messageNotify';

export function ChatSocketProvider({ children }: { children: React.ReactNode }) {
    const queryClient = useQueryClient();
    const token = useAuthStore((state) => state.token);
    const { uuid: chatUUID } = useParams();

    const { data: partnerData } = useGetChatPartner(chatUUID);
    const partnerProfile = partnerData && partnerData?.partner_profile;

    if (Notification.permission === 'default') {
        Notification.requestPermission();
    }

    useEffect(() => {
        if (!token) return;

        chatSocket.connect();

        const unsubscribe = chatSocket.subscribe((msg) => {
            switch (msg.type) {
                case 'message_created':
                    messageNotify(chatUUID, partnerProfile, msg.data);
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
    }, [token, chatUUID, queryClient]);

    return <>{children}</>;
}