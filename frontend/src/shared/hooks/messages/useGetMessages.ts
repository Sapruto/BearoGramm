import { useInfiniteQuery, type InfiniteData } from '@tanstack/react-query';
import { getMessages, type GetMessagesResponse } from '../../api/messages';
import { queryKeys } from '../../lib/queryKeys';

const PAGE_SIZE = 10;

export function useGetMessages(chatUUID: string) {
    return useInfiniteQuery<GetMessagesResponse, Error, InfiniteData<GetMessagesResponse, number>, ReturnType<typeof queryKeys.messagesChat>, number>({
        queryKey: queryKeys.messagesChat(chatUUID),
        refetchOnMount: false,
        refetchOnWindowFocus: false,
        queryFn: ({ pageParam }) =>
            getMessages({ chat_uuid: chatUUID, limit: PAGE_SIZE, offset: pageParam, show_new: true }, chatUUID),
        initialPageParam: 0,
        getNextPageParam: () => undefined,
        getPreviousPageParam: (firstPage, allPages) => {
            const loaded = allPages.flatMap((p) => p.message_entity).length;
            return firstPage.message_entity.length < PAGE_SIZE ? undefined : loaded;
        },
    });
}