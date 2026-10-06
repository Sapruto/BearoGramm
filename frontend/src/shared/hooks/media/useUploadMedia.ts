import { useMutation } from '@tanstack/react-query';
import { uploadMedia } from '../../api/media';

export const useUploadMedia = () => {
    return useMutation({ mutationFn: uploadMedia });
};