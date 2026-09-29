import type { InfiniteData, QueryClient } from "@tanstack/react-query";
import type { GetMessagesResponse, Message } from "../api/messages";
import { queryKeys } from "./queryKeys";

export function addMessageToCache(queryClient: QueryClient, chatUUID: string, message: Message) {
    queryClient.setQueryData<InfiniteData<GetMessagesResponse>>(
        queryKeys.messagesChat(chatUUID),
        (old) => {
            if (!old) return old;

            const exists = old.pages.some(p =>
                p.message_entity.some(m => m.uuid === message.uuid)
            );
            if (exists) return old;

            const pages = [...old.pages];
            const firstPage = pages[0];

            pages[0] = {
                ...firstPage,
                message_entity: [message, ...firstPage.message_entity],
            };

            return { ...old, pages };
        }
    );
}