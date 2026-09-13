import { useQuery } from '@tanstack/react-query';
import { getChatPartner } from '../../api/personal.ts';
import { queryKeys } from '../../lib/queryKeys.ts';

export const useGetChatPartner = (chatUUID: string) => {
    return useQuery({
        queryKey: queryKeys.chatPartner(chatUUID),
        queryFn: () => getChatPartner({ chat_uuid: chatUUID }),
    });
};