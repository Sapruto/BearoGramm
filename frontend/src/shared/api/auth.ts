import { apiClient } from "./client";

export type SendCodeRequest = {
    phone_number: string;
};

export type SendCodeResponse = {
    success: boolean;
    error_message: string;
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
    success: boolean;
    token: string;
    user_uuid: string;
    user: any;
    error_message: string;
};

export const verifyCode = async (data: VerifyCodeRequest): Promise<VerifyCodeResponse> => {
    const res = await apiClient.post('/api/auth/verify_phone', data);
    return res.data;
};