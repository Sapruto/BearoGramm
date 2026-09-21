import { apiClient } from "./client";

export type Message = {
    uuid: string;
    message_data: [
        {
            data_type: string;
            text?: string;
        }
    ];
    message_text: string;
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

export type SendMessageRequest = {
    chat_uuid: string;
    typing_to_data: [
        [
            dataType: 'text_type' | 'media_type',
            rawData: string,
        ]
    ];
};

export type SendMessageResponse = {
    success: boolean;
    message_entity: Message;
};

export const sendMessage = async (data: SendMessageRequest): Promise<SendMessageResponse> => {
    const res = await apiClient.post('/api/messages/send/', data);
    return res.data;
};