import { apiClient } from "./client";
import type { Profile } from "./profile";

export type SendFriendRequest = {
    target_value: string;
    target_type: 'uuid' | 'username' | 'email' | 'phone';
};

export type FriendStatus = "accept" | "rejected" | "process" | "blocked";

export type FriendItemResponse = {
    user_uuid: string;
    status: FriendStatus;
    is_initiator: boolean;
    created_at: string;
    profile: Profile;
}

export type SendFriendResponse = {
    success: boolean;
    just_created_chat: boolean;
    uuid?: string;
    other_uuid?: string;
    message?: string;
};

export const sendFriendRequest = async (data: SendFriendRequest): Promise<SendFriendResponse> => {
    const res = await apiClient.post('/api/friends/request', data);
    return res.data;
};

export type GetFriendsParams = {
    limit: number;
    offset: number,
};

export type GetFriendsResponse = {
    items: FriendItemResponse[];
    total: number;
};

export const getFriends = async (params: GetFriendsParams): Promise<GetFriendsResponse> => {
    const res = await apiClient.get('/api/friends/friends', { params });
    return res.data;
};

export type ChangeFriendStatusRequest = {
    target_uuid: string;
    status: FriendStatus;
};

export type ChangeFriendStatusResponse = {
    success: boolean;
    just_created_chat: boolean;
    uuid?: string;
    other_uuid?: string;
    message?: string;
};

export const changeFriendStatus = async (data: ChangeFriendStatusRequest): Promise<ChangeFriendStatusResponse> => {
    const res = await apiClient.post('/api/friends/status', data);
    return res.data;
};