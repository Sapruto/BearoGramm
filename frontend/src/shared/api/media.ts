import { apiClient } from "./client";

export type MediaDTO = {
    uuid: string;
    filename: string;
    url: string;
    content_type: string | null;
    size: number;
    uploaded_at: string;
    castrated_url: string;
};

export type MediaUploadResponse = {
    success: boolean;
    media: MediaDTO | null;
    error: string | null;
};

export type MediaType = "image" | "attachment";

export const uploadMedia = async (file: File, mediaType: MediaType): Promise<MediaDTO> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('media_type', mediaType);

    const res = await apiClient.post<MediaUploadResponse>('/api/medias/upload', formData);

    if (!res.data.success || !res.data.media) {
        throw new Error(res.data.error ?? 'Upload failed');
    }
    return res.data.media;
};