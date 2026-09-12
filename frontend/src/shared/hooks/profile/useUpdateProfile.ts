import { useMutation } from '@tanstack/react-query';
import { updateProfile } from '../../api/profile';

export const useUpdateProfile = () => {
    return useMutation({
        mutationFn: updateProfile,
    });
};