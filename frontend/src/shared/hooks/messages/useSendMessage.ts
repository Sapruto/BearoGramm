import { useMutation } from '@tanstack/react-query';
import { sendMessage } from '../../api/messages';
import { queryClient } from '../../api/queryClient';
import { queryKeys } from '../../lib/queryKeys';

export const useSendMessage = (chatUUID: string) => {
    return useMutation({
        mutationFn: sendMessage,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: queryKeys.messagesChat(chatUUID) })
        },
    });
};