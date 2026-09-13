import { apiClient } from "./client";

export type Profile = {
    uuid: string;
    name: string;
    avatar_url: string;
    data: any[];
    updated_at: string;
    user_uuid: string;
};

export type GetMyProfileResponse = {
    success: boolean;
    profile: Profile | null;
};

export const getMyProfile = async (): Promise<GetMyProfileResponse> => {
    const res = await apiClient.get('/api/profile/me');
    return res.data;
};

export type CreateProfileRequest = {
    name?: string;
    avatar_url?: string;
};

export type CreateProfileResponse = {
    success: boolean;
    message: string;
    profile: Profile;
};

export const createProfile = async (data: CreateProfileRequest): Promise<CreateProfileResponse> => {
    const res = await apiClient.post('/api/profile/me', data);
    return res.data;
};

export type UpdateProfileRequest = {
    name?: string;
    avatar_url?: string;
};

export type UpdateProfileResponse = {
    success: boolean;
    message: string;
    profile: Profile;
};

export const updateProfile = async (data: UpdateProfileRequest): Promise<UpdateProfileResponse> => {
    const res = await apiClient.patch('/api/profile/me', data);
    return res.data;
};