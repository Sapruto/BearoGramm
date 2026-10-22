import { getFriends } from '@/shared/api/friends';
import { queryKeys } from '@/shared/lib/queryKeys';
import { useInfiniteQuery } from '@tanstack/react-query';

export const useGetFriends = (limit = 20) => {
    return useInfiniteQuery({
        queryKey: queryKeys.friendsInfinite(limit),
        queryFn: ({ pageParam }) => getFriends({ limit, offset: pageParam }),
        initialPageParam: 0,
        getNextPageParam: (lastPage, _allPages, lastPageParam) => {
            const nextOffset = lastPageParam + limit;
            return nextOffset < lastPage.total ? nextOffset : undefined;
        },
    });
};