import { apiClient } from "./client";

export type Profile = {
    uuid: string;
    name: string;
    avatar_url: string;
    data: [
        {
            data_type: string;
        }
    ];
    updated_at: string;
    user_uuid: string;
};

export type GetMyProfileResponse = {
    success: boolean;
    profile: Profile | null;
};

export const getMyProfile = async (): Promise<GetMyProfileResponse> => {
    const res = await apiClient.get('/api/profile-custom/get_my_profile');
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
    const res = await apiClient.post('/api/profile-custom/create_profile', data);
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
    const res = await apiClient.put('/api/profile-custom/update_profile', data);
    return res.data;
};