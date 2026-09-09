import { apiClient } from "./client";

export type PersonalChat = {
    uuid: string;
    chat_type: 'personal';
    partner_uuid: string;
    updated_at: string;
};

export type GetPersonalChatsResponse = {
    items: PersonalChat[];
    total: number;
    limit: number;
    offset: number;
};

export type GetPersonalChatsParams = {
    limit: number;
    offset: number;
};

export const getPersonalChats = async (
    params: GetPersonalChatsParams
): Promise<GetPersonalChatsResponse> => {
    const res = await apiClient.get('/api/personal/', { params });
    return res.data;
};

export type AddPersonalRequest = {
    other_user_phone: string;
};

export type AddPersonalResponse = {
    uuid: string,
    chat_type: 'personal',
    partner_uuid: string,
};

export const addFriend = async (data: AddPersonalRequest): Promise<AddPersonalResponse> => {
    const res = await apiClient.post('/api/personal/create', data);
    return res.data;
};