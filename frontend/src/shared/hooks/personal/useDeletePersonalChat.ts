import { useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { deletePersonalChat, type DeletePersonalChatResponse } from '../../api/personal';
import { queryKeys } from '../../lib/queryKeys';

export const useDeletePersonalChat = () => {
    const queryClient = useQueryClient();

    return useMutation<DeletePersonalChatResponse, Error, string>({
        mutationFn: (chatUUID) => deletePersonalChat(chatUUID),
        onSuccess: (data) => {
            queryClient.removeQueries({ queryKey: queryKeys.messagesChat(data.chat_uuid) });
            queryClient.removeQueries({ queryKey: queryKeys.chatPartner(data.chat_uuid) });
            queryClient.invalidateQueries({ queryKey: queryKeys.personalChats });
            toast.success('Chat deleted');
        },
    });
};