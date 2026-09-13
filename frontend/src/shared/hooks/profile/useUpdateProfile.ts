import { useMutation } from '@tanstack/react-query';
import { updateProfile } from '../../api/profile';
import { queryClient } from '../../api/queryClient';
import { queryKeys } from '../../lib/queryKeys';

export const useUpdateProfile = () => {
    return useMutation({
        mutationFn: updateProfile,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: queryKeys.myProfile });
        },
    });
};