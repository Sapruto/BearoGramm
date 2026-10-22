import { sendFriendRequest } from '@/shared/api/friends';
import { getErrorMessage, queryClient } from '@/shared/api/queryClient';
import { queryKeys } from '@/shared/lib/queryKeys';
import { useMutation } from '@tanstack/react-query';
import { isAxiosError } from 'axios';
import toast from 'react-hot-toast';

export const useSendFriendRequest = () => {
    return useMutation({
        mutationFn: sendFriendRequest,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: queryKeys.friendsAll });
        },
        onError: (error) => {
            if (!isAxiosError(error))
                return;

            if (error.status === 404) {
                toast.error("User not found");
            } else if (error.status === 400) {
                toast.error("You cannot add yourself as a friend")
            }
            else {
                toast.error(getErrorMessage(error));
            }
        }
    });
};