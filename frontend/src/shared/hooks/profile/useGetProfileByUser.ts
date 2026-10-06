import { useQuery } from '@tanstack/react-query';
import { getProfileByUser } from '../../api/profile';
import { queryKeys } from '../../lib/queryKeys';

export const useGetProfileByUser = (userUUID?: string) => {
    return useQuery({
        queryKey: queryKeys.profileByUser(userUUID ?? ''),
        queryFn: () => getProfileByUser(userUUID as string),
        select: (data) => data.profile,
        enabled: !!userUUID,
        staleTime: 60_000,
    });
};