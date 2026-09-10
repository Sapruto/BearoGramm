import { apiClient } from "./client";

export type Message = {
    uuid: string;
    message_data: [
        {
            data_type: string;
            text?: string;
        }
    ];
    created_at: string;
    updated_at: string;
    chat_uuid: string;
    user_uuid: string;
}

export type GetMessagesParams = {
    chat_uuid: string;
    limit: number;
    offset: number,
    show_new: true
};

export type GetMessagesResponse = {
    success: boolean;
    message_entity: Message[];
};

export const getMessages = async (params: GetMessagesParams, chatUUID: string): Promise<GetMessagesResponse> => {
    const res = await apiClient.get('/api/messages/get/' + chatUUID, { params });
    return res.data;
};
