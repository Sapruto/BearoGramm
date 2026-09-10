import { useQuery } from '@tanstack/react-query';
import { getMyProfile } from '../../api/profile.ts';

export const useGetMyProfile = () => {
    return useQuery({
        queryKey: ['my_profile'],
        queryFn: getMyProfile,
    });
};