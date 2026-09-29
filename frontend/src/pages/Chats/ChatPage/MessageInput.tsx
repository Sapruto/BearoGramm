import { Send } from 'lucide-react';
import { useState } from 'react';

type Props = {
    onSend: (text: string) => void;
};

const MessageInput = ({ onSend }: Props) => {
    const [value, setValue] = useState('');

    const handleSend = () => {
        const trimmed = value.trim();
        if (!trimmed) return;

        onSend(trimmed);
        setValue('');
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
                type="text"
                value={value}
                onChange={(e) => setValue(e.target.value)}
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