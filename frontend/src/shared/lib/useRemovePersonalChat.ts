import { useQueryClient } from '@tanstack/react-query';
import { useCallback, useRef } from 'react';
import { useMatch, useNavigate } from 'react-router-dom';
import { queryKeys } from './queryKeys';

export const useRemovePersonalChat = () => {
    const queryClient = useQueryClient();
    const navigate = useNavigate();
    const openedChatUUID = useMatch('/chats/:uuid')?.params.uuid;

    const openedChatUUIDRef = useRef(openedChatUUID);
    openedChatUUIDRef.current = openedChatUUID;

    const navigateRef = useRef(navigate);
    navigateRef.current = navigate;

    return useCallback(
        (chatUUID: string) => {
            if (openedChatUUIDRef.current === chatUUID) {
                navigateRef.current('/chats', { replace: true });
            }

            queryClient.removeQueries({ queryKey: queryKeys.messagesChat(chatUUID) });
            queryClient.removeQueries({ queryKey: queryKeys.chatPartner(chatUUID) });
            queryClient.invalidateQueries({ queryKey: queryKeys.personalChats });
        },
        [queryClient],
    );
};