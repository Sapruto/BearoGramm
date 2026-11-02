import type { QueryClient, InfiniteData } from "@tanstack/react-query";
import type { GetPersonalChatsResponse } from "../api/personal";
import { queryKeys } from "./queryKeys";

export const updatePersonalChatLastMessageAt = (
    queryClient: QueryClient,
    chatUuid: string,
    lastMessageAt: string,
) => {
    queryClient.setQueryData<InfiniteData<GetPersonalChatsResponse, number>>(
        queryKeys.personalChats,
        (oldData) => {
            if (!oldData) return oldData;

            return {
                ...oldData,
                pages: oldData.pages.map((page) => {
                    if (!page.items.some((chat) => chat.uuid === chatUuid)) return page;

                    return {
                        ...page,
                        items: page.items.map((chat) =>
                            chat.uuid === chatUuid
                                ? { ...chat, last_message_at: lastMessageAt }
                                : chat,
                        ),
                    };
                }),
            };
        },
    );
};