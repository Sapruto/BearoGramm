import { useMutation } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { sendCode } from '../../api/auth';

export const useSendCode = () => {
    return useMutation({
        mutationFn: sendCode,
        onError: () => {
            toast.error("Couldn't send the code!");
            return;
        }
    });
};