import { useMutation } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { deletePersonalChat, type DeletePersonalChatResponse } from '../../api/personal';
import { useRemovePersonalChat } from '../../lib/useRemovePersonalChat';

export const useDeletePersonalChat = () => {
    const removePersonalChat = useRemovePersonalChat();

    return useMutation<DeletePersonalChatResponse, Error, string>({
        mutationFn: (chatUUID) => deletePersonalChat(chatUUID),
        onSuccess: (data) => {
            removePersonalChat(data.chat_uuid);
            toast.success('Chat deleted');
        },
    });
};