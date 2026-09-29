import { useInfiniteQuery, type InfiniteData } from '@tanstack/react-query';
import { getMessages, type GetMessagesResponse } from '../../api/messages';
import { queryKeys } from '../../lib/queryKeys';

export function useGetMessages(chatUUID: string, initialCount = 30, historyCount = 20) {
    return useInfiniteQuery<GetMessagesResponse, Error, InfiniteData<GetMessagesResponse, number>, ReturnType<typeof queryKeys.messagesChat>, number>({
        queryKey: queryKeys.messagesChat(chatUUID),
        refetchOnMount: false,
        refetchOnWindowFocus: false,
        queryFn: ({ pageParam }) => {
            const isHistory = pageParam < 0;
            return getMessages(
                {
                    chat_uuid: chatUUID,
                    limit: isHistory ? historyCount : initialCount,
                    offset: isHistory ? -pageParam : 0,
                    show_new: true,
                },
                chatUUID
            );
        },
        initialPageParam: 0,
        getNextPageParam: () => undefined,
        getPreviousPageParam: (firstPage, allPages) => {
            if (firstPage.messages.length < historyCount) return undefined;
            const loaded = allPages.flatMap((p) => p.messages).length;
            return -loaded;
        },
    });
}