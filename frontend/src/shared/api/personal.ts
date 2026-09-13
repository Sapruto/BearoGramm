import { apiClient } from "./client";
import type { Profile } from "./profile";

export type PersonalChat = {
    uuid: string;
    chat_type: 'personal';
    partner_uuid: string;
    partner_profile: Profile;
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

export const getPersonalChats = async (params: GetPersonalChatsParams): Promise<GetPersonalChatsResponse> => {
    const res = await apiClient.get('/api/personal/', { params });
    return res.data;
};

export type AddPersonalRequest = {
    other_user_phone: string;
};

export type AddPersonalResponse = {
    uuid: string;
    chat_type: 'personal';
    partner_uuid: string;
    created_at: string;
    updated_at: string;
    partner_profile: Profile;
};

export const addFriend = async (data: AddPersonalRequest): Promise<AddPersonalResponse> => {
    const res = await apiClient.post('/api/personal/create', data);
    return res.data;
};

export type GetChatPartnerResponse = {
    partner_uuid: string;
    partner_profile: Profile;
};

export const getChatPartner = async (chatUUID: string): Promise<GetChatPartnerResponse> => {
    const res = await apiClient.get(`/api/personal/${chatUUID}/partner`);
    return res.data;
};