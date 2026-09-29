import { apiClient } from "./client";

export type MessageEntity = {
    uuid: string;
    message_text: string;

    created_at: string;
    updated_at?: string;

    has_extra_data: boolean;

    chat_uuid: string;
    user_uuid: string;

    extra_data?: MessageDataEntity;
    references: MessageReferenceEntity[];
}

export type GetMessagesParams = {
    chat_uuid: string;
    limit: number;
    offset: number,
    show_new: boolean
};

export type GetMessagesResponse = {
    success: boolean;
    messages: MessageEntity[];
};

export const getMessages = async (params: GetMessagesParams, chatUUID: string): Promise<GetMessagesResponse> => {
    const res = await apiClient.get('/api/messages/get/' + chatUUID, { params });
    return res.data;
};

export type SendMessageRequest = {
    chat_uuid: string;
    message_text?: string;
    extra_data?: MessageDataEntity;
    references: MessageReferenceEntity[];
};

export type PollExtraData = {
    extra_data_type: 'poll';
    question: string;
    options: string[];
    multi: boolean;
    anonymous: boolean;
};

export type InlineKeyboardExtraData = {
    extra_data_type: 'inline_keyboard';
    rows: any[][];
};

export type ReactionsExtraData = {
    extra_data_type: 'reactions';
    allowed: string[];
};

export type EmbedExtraData = {
    extra_data_type: 'embed';
    url: string;
    title?: string;
    description?: string;
    image?: string;
};

export type CustomExtraData = {
    extra_data_type: 'custom';
    data: any;
};

export type MediaExtraData = {
    extra_data_type: 'media';
    media_uuid: string;
};

export type MessageDataEntity = {
    message_uuid: string;
    extra_data_type: 'poll' | 'inline_keyboard' | 'reactions' | 'embed' | 'custom' | 'media'
    payload: PollExtraData | InlineKeyboardExtraData | ReactionsExtraData | EmbedExtraData | CustomExtraData | MediaExtraData;
};

export type MessageReferenceEntity = {
    uuid: string;
    reference_type: 'answer' | 'remember' | 'quote';
    source_uuid: string;
    target_uuid: string;
    span_start?: number;
    span_end?: number;
    span_all?: boolean;
    created_at: string;
};

export type SendMessageResponse = {
    success: boolean;
    message_text: string;
    extra_data?: MessageDataEntity;
    references: MessageReferenceEntity[];
};

export const sendMessage = async (data: SendMessageRequest): Promise<SendMessageResponse> => {
    const res = await apiClient.post('/api/messages/send/', data);
    return res.data;
};