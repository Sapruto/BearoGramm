import type { Profile } from '@/shared/api/profile';
import { useTypingUsers } from '@/shared/lib/useTypingUsers';
import { useRef } from 'react';
import './TypingIndicator.css';

type Props = {
    chatUUID: string;
    membersByUUID: Record<string, Profile>;
};

const nameClass = 'font-semibold text-[#f4f4f5]';

const TypingIndicator = ({ chatUUID, membersByUUID }: Props) => {
    const typingUUIDs = useTypingUsers(chatUUID);
    const usernames = typingUUIDs.map((uuid) => membersByUUID[uuid]?.name).filter(Boolean);
    const visible = usernames.length > 0;

    const lastNames = useRef(usernames);
    if (visible) lastNames.current = usernames;
    const names = visible ? usernames : lastNames.current;

    return (
        <div
            role="status"
            aria-live="polite"
            className={`flex h-6 items-center gap-2 px-1 text-xs text-[#8b8b93] transition-opacity duration-150 ${visible ? 'opacity-100' : 'opacity-0'}`}
        >
            <span aria-hidden className="flex shrink-0 items-center gap-0.75">
                <span className="typing-dot h-1.5 w-1.5 rounded-full bg-[#f4f4f5]" />
                <span className="typing-dot h-1.5 w-1.5 rounded-full bg-[#f4f4f5]" />
                <span className="typing-dot h-1.5 w-1.5 rounded-full bg-[#f4f4f5]" />
            </span>

            <span className="min-w-0 truncate">
                {names.length === 1 && (
                    <>
                        <strong className={nameClass}>{names[0]}</strong> is typing...
                    </>
                )}
                {names.length === 2 && (
                    <>
                        <strong className={nameClass}>{names[0]}</strong> and <strong className={nameClass}>{names[1]}</strong> are typing...
                    </>
                )}
                {names.length === 3 && (
                    <>
                        <strong className={nameClass}>{names[0]}</strong>, <strong className={nameClass}>{names[1]}</strong>, and{' '}
                        <strong className={nameClass}>{names[2]}</strong> are typing...
                    </>
                )}
                {names.length > 3 && 'Several people are typing...'}
            </span>
        </div>
    );
};

export default TypingIndicator;