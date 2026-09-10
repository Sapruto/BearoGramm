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
    success: false;
    profile: Profile;
};

export const getMyProfile = async (): Promise<GetMyProfileResponse> => {
    const res = await apiClient.get('/api/profile-custom/get_my_profile');
    return res.data;
};