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
};

export const addFriend = async (data: AddPersonalRequest): Promise<AddPersonalResponse> => {
    const res = await apiClient.post('/api/personal/create', data);
    return res.data;
};

export type GetChatPartnerParams = {
    chat_uuid: string;
};

export type GetChatPartnerResponse = {
    partner_uuid: string;
    partner_profile: Profile;
};

export const getChatPartner = async (params: GetChatPartnerParams): Promise<GetChatPartnerResponse> => {
    const res = await apiClient.get(`/api/personal/${params.chat_uuid}/partner`, { params });
    return res.data;
};