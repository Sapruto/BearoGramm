import { apiClient } from "./client";
import type { Profile } from "./profile";

export type SendCodeRequest = {
    phone_number: string;
};

export type SendCodeResponse = {
    success: boolean;
};

export const sendCode = async (data: SendCodeRequest): Promise<SendCodeResponse> => {
    const res = await apiClient.post('/api/auth/send_verify_code', data);
    return res.data;
};

export type UserEntity = {
    uuid: string,
    phone_number: string,
    created_at: string,
    updated_at: string,
};

export type VerifyCodeRequest = {
    phone_number: string;
    code: string;
};

export type VerifyCodeResponse = {
    token: string;
    user_uuid: string;
    user: UserEntity;
    just_created_profile: boolean;
    just_created: boolean;
    profile?: Profile;
};

export const verifyCode = async (data: VerifyCodeRequest): Promise<VerifyCodeResponse> => {
    const res = await apiClient.post('/api/auth/verify_phone', data);
    return res.data;
};