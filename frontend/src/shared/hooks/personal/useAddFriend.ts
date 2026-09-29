import { useMutation } from '@tanstack/react-query';
import type { AxiosError } from 'axios';
import axios from 'axios';
import toast from 'react-hot-toast';
import { addFriend } from '../../api/personal';
import { queryClient } from '../../api/queryClient';
import { queryKeys } from '../../lib/queryKeys';

export const useAddFriend = () => {
    return useMutation({
        mutationFn: addFriend,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: queryKeys.personalChats });
        },
        onError: (error: AxiosError) => {
            if (error.response && axios.isAxiosError<{ code: number, error: string }>(error)) {
                toast.error(error.response.data.error)
            }
        }
    });
};