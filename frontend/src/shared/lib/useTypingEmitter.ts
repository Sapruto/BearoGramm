import { useCallback, useRef } from 'react';

type Options = {
    onTyping: () => void;
    interval?: number;
};

export const useTypingEmitter = ({ onTyping, interval = 4000 }: Options) => {
    const onTypingRef = useRef(onTyping);
    onTypingRef.current = onTyping;

    const lastSentAt = useRef(0);

    const handleChange = useCallback(
        (value: string) => {
            if (!value.trim()) return;

            const now = Date.now();
            if (now - lastSentAt.current < interval) return;

            lastSentAt.current = now;
            onTypingRef.current();
        },
        [interval],
    );

    const reset = useCallback(() => {
        lastSentAt.current = 0;
    }, []);

    return { handleChange, reset };
};