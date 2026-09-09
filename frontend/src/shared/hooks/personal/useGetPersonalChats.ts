import { useInfiniteQuery } from '@tanstack/react-query';
import { getPersonalChats } from '../../api/personal';

const PAGE_SIZE = 50;

export const useGetPersonalChats = () => {
    return useInfiniteQuery({
        queryKey: ['personal-chats'],
        queryFn: ({ pageParam }) => getPersonalChats({ limit: PAGE_SIZE, offset: pageParam }),
        initialPageParam: 0,
        getNextPageParam: (lastPage, allPages) => {
            const loadedCount = allPages.reduce((sum, page) => sum + page.items.length, 0);
            if (loadedCount >= lastPage.total) return undefined;
            return loadedCount;
        },
    });
};