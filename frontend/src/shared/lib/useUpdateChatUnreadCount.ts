import { useQueryClient, type InfiniteData, type QueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';
import type { GetPersonalChatsResponse, PersonalChat } from '../api/personal';
import { queryKeys } from './queryKeys';

type PersonalChatsData = InfiniteData<GetPersonalChatsResponse, number>;

type UnreadUpdater = number | ((prev: number) => number);

export function updateChatUnreadCount(
    queryClient: QueryClient,
    chatUuid: string,
    updater: UnreadUpdater,
) {
    queryClient.setQueryData<PersonalChatsData>(queryKeys.personalChats, (old) => {
        if (!old) return old;

        return {
            ...old,
            pages: old.pages.map((page) => ({
                ...page,
                items: page.items.map((chat): PersonalChat => {
                    if (chat.uuid !== chatUuid) return chat;

                    const next =
                        typeof updater === 'function' ? updater(chat.unread_count) : updater;

                    return { ...chat, unread_count: Math.max(0, next) };
                }),
            })),
        };
    });
}

export const useUpdateChatUnreadCount = () => {
    const queryClient = useQueryClient();

    return useCallback(
        (chatUuid: string, updater: number | ((prev: number) => number)) =>
            updateChatUnreadCount(queryClient, chatUuid, updater),
        [queryClient],
    );
};

export function findChatInData(
    data: PersonalChatsData | undefined,
    chatUuid: string,
): PersonalChat | undefined {
    if (!data) return undefined;

    for (const page of data.pages) {
        const chat = page.items.find((item) => item.uuid === chatUuid);
        if (chat) return chat;
    }
    return undefined;
}

export function getChatUnreadCount(queryClient: QueryClient, chatUuid: string): number {
    const data = queryClient.getQueryData<PersonalChatsData>(queryKeys.personalChats);
    return findChatInData(data, chatUuid)?.unread_count ?? 0;
}