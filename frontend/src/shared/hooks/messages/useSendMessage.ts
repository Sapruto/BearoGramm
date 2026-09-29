import { useMutation } from '@tanstack/react-query';
import { sendMessage } from '../../api/messages';

export const useSendMessage = () => {
    return useMutation({
        mutationFn: sendMessage,
    });
};