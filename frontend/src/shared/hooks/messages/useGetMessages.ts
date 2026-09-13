import { useInfiniteQuery } from '@tanstack/react-query';
import { getMessages } from '../../api/messages';
import { queryKeys } from '../../lib/queryKeys';

export function useGetMessages(chatUUID: string) {
    return useInfiniteQuery({
        queryKey: queryKeys.messagesChat(chatUUID),
        queryFn: ({ pageParam = 0 }) =>
            getMessages({ chat_uuid: chatUUID, limit: 30, offset: pageParam, show_new: true }, chatUUID),
        initialPageParam: 0,
        getNextPageParam: (lastPage, allPages) => {
            const loaded = allPages.flatMap(p => p.message_entity).length;
            return lastPage.message_entity.length < 30 ? undefined : loaded;
        },
    });
}