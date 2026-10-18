import { apiClient } from "./client";

export type Gender = 'bear' | 'male' | 'female' | 'ameba' | 'troll_face' | 'communist' | 'cock';

export type Profile = {
    uuid: string;
    name: string;
    avatar_url: string;
    banner_color: string;
    gender: Gender;
    bio: string;
    updated_at?: string;
    user_uuid: string;
};

export type GetProfileResponse = {
    success: boolean;
    profile: Profile;
};

export const getMyProfile = async (): Promise<GetProfileResponse> => {
    const res = await apiClient.get('/api/profile/me');
    return res.data;
};

export type UpdateProfileRequest = {
    name?: string;
    avatar_url?: string;
    banner_color?: string;
    gender?: string;
    bio?: string;

    email?: string;
    username?: string;
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

export type GetProfileByUserResponse = {
    success: boolean;
    profile: Profile;
};

export const getProfileByUser = async (userUUID: string): Promise<GetProfileByUserResponse> => {
    const res = await apiClient.get(`/api/profile/user/${userUUID}`);
    return res.data;
};