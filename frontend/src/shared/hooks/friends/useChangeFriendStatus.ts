import { changeFriendStatus } from '@/shared/api/friends';
import { queryClient } from '@/shared/api/queryClient';
import { queryKeys } from '@/shared/lib/queryKeys';
import { useMutation } from '@tanstack/react-query';

export const useChangeFriendStatus = () => {
    return useMutation({
        mutationFn: changeFriendStatus,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: queryKeys.friendsAll })
        }
    });
};