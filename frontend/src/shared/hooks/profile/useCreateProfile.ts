import { useMutation } from '@tanstack/react-query';
import { createProfile } from '../../api/profile';

export const useCreateProfile = () => {
    return useMutation({
        mutationFn: createProfile,
    });
};