import { useQuery } from '@tanstack/react-query';
import { getMyProfile } from '../../api/profile.ts';
import { useAuthStore } from '../../../store/authStore.ts';
import { queryKeys } from '../../lib/queryKeys.ts';

export const useGetMyProfile = () => {
    const token = useAuthStore((s) => s.token);
    
    return useQuery({
        queryKey: queryKeys.myProfile,
        queryFn: getMyProfile,
        enabled: !!token,
    });
};