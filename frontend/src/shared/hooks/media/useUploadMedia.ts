import { useMutation } from '@tanstack/react-query';
import { uploadMedia, type MediaType } from '../../api/media';
import axios from 'axios';
import toast from 'react-hot-toast';

export const useUploadMedia = (mediaType: MediaType) => {
    return useMutation({
        mutationFn: (file: File) => uploadMedia(file, mediaType),
        onError: (error) => {
            if (axios.isAxiosError<{ error?: string }>(error)) {
                const message = error.response?.data?.error;
                if (message && message.includes('is not allowed for media type: MediaType.IMAGE')) {
                    toast.error(`Unsupported extension for image`);
                    return;
                }
            }

            toast.error("Couldn't upload media");
        }
    });
};