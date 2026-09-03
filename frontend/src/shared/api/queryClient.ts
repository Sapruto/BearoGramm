import { MutationCache, QueryClient } from '@tanstack/react-query';
import axios from 'axios';
import toast from 'react-hot-toast';

function getErrorMessage(error: unknown) {
    if (axios.isAxiosError<{ error?: { message?: string } }>(error)) {
        const message = error.response?.data?.error?.message;
        if (message) {
            return message;
        }
    }

    return 'Something went wrong.\nPlease try again'
}

export const queryClient = new QueryClient({
    mutationCache: new MutationCache({
        onError: (error, _variables, _context, mutation) => {
            if (mutation.options.onError) return;

            toast.error(getErrorMessage(error));
        },
    }),
});