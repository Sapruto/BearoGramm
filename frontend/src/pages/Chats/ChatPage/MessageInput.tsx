import { chatSocket } from '@/shared/api/wsClient';
import { useTypingEmitter } from '@/shared/lib/useTypingEmitter';
import { useAuthStore } from '@/store/authStore';
import { Send } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

type Props = {
    onSend: (text: string) => void;
    chatUUID: string;
};

const MessageInput = ({ onSend, chatUUID }: Props) => {
    const [value, setValue] = useState('');
    const inputRef = useRef<HTMLInputElement>(null);
    const { userUUID } = useAuthStore();
    const { handleChange, reset } = useTypingEmitter({
        onTyping: () => chatSocket.send({
            type: "typing", data: {
                user_uuid: userUUID,
                chat_uuid: chatUUID
            }
        })
    });

    useEffect(() => {
        const handleGlobalKeyDown = (e: KeyboardEvent) => {
            if (e.ctrlKey || e.metaKey || e.altKey) return;

            if (e.key.length !== 1 && e.key !== 'Backspace') return;

            const active = document.activeElement as HTMLElement | null;
            const isEditable =
                active instanceof HTMLInputElement ||
                active instanceof HTMLTextAreaElement ||
                active instanceof HTMLSelectElement ||
                active?.isContentEditable;

            if (isEditable) return;

            inputRef.current?.focus();
        };

        const handleGlobalPaste = () => {
            const active = document.activeElement;
            if (active instanceof HTMLInputElement || active instanceof HTMLTextAreaElement) return;

            inputRef.current?.focus();
        };

        window.addEventListener('keydown', handleGlobalKeyDown);
        window.addEventListener('paste', handleGlobalPaste);

        return () => {
            window.removeEventListener('keydown', handleGlobalKeyDown);
            window.removeEventListener('paste', handleGlobalPaste);
        };
    }, []);

    const handleSend = () => {
        const trimmed = value.trim();
        if (!trimmed) return;

        onSend(trimmed);
        setValue('');
        reset();
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="px-4 py-3.5 border-t border-[#1f1f23] flex items-center gap-2.5">
            <input
                ref={inputRef}
                type="text"
                value={value}
                onChange={(e) => {
                    setValue(e.target.value);
                    handleChange(e.target.value);
                }}
                onKeyDown={handleKeyDown}
                placeholder="Message"
                className="flex-1 h-10 rounded-[10px] bg-[#131316] border border-[#27272c] text-[#f4f4f5] px-3.5 text-sm outline-none focus:border-[#3a3a40]"
            />
            <button
                onClick={handleSend}
                className="w-10 h-10 rounded-[10px] bg-[#f4f4f5] flex items-center justify-center shrink-0 hover:bg-[#d4d4d8] transition-colors cursor-pointer"
            >
                <Send size={17} className="stroke-[#0a0a0b]" />
            </button>
        </div>
    );
};

export default MessageInput;