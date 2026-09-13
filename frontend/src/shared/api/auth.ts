import { apiClient } from "./client";

export type SendCodeRequest = {
    phone_number: string;
};

export type SendCodeResponse = {
    success: boolean;
    just_created: boolean;
};

export const sendCode = async (data: SendCodeRequest): Promise<SendCodeResponse> => {
    const res = await apiClient.post('/api/auth/send_verify_code', data);
    return res.data;
};

export type VerifyCodeRequest = {
    phone_number: string;
    code: string;
};

export type VerifyCodeResponse = {
    token: string;
    user_uuid: string;
    user: {
        uuid: string,
        phone_number: string,
        created_at: string,
        updated_at: string,
    };
    has_profile: boolean;
};

export const verifyCode = async (data: VerifyCodeRequest): Promise<VerifyCodeResponse> => {
    const res = await apiClient.post('/api/auth/verify_phone', data);
    return res.data;
};