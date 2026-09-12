import { useQuery } from '@tanstack/react-query';
import { getMyProfile } from '../../api/profile.ts';
import { useAuthStore } from '../../../store/authStore.ts';

export const useGetMyProfile = () => {
    const token = useAuthStore((s) => s.token);
    
    return useQuery({
        queryKey: ['my_profile'],
        queryFn: getMyProfile,
        enabled: !!token,
    });
};