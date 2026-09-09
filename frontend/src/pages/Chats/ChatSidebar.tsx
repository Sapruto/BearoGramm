import { UserPlus } from 'lucide-react';
import { useEffect, useRef } from 'react';
import type { PersonalChat } from '../../shared/api/personal';
import { useGetPersonalChats } from '../../shared/hooks/personal/useGetPersonalChats';

type Props = {
    activeChatId: string | null;
    onSelectAddFriend: () => void;
    onSelectChat: (id: string) => void;
}

const ChatSidebar = ({ activeChatId, onSelectAddFriend, onSelectChat }: Props) => {
    const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useGetPersonalChats();
    const scrollContainerRef = useRef<HTMLDivElement>(null);
    const sentinelRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const root = scrollContainerRef.current;
        const sentinel = sentinelRef.current;
        if (!root || !sentinel) return;

        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting && hasNextPage && !isFetchingNextPage) {
                    fetchNextPage();
                }
            },
            { root, threshold: 0 }
        );

        observer.observe(sentinel);
        return () => observer.disconnect();
    }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

    const chats = data?.pages.flatMap((page) => page.items) ?? [];

    return (
        <div className="w-full h-screen bg-[#131316] border-r border-[#1f1f23] p-4 flex flex-col">
            <button
                onClick={onSelectAddFriend}
                className="w-full h-9 flex items-center justify-center gap-1.5 rounded-lg border border-[#27272c] text-[#f4f4f5] text-sm font-medium hover:bg-[#1a1a1d] transition-colors cursor-pointer mb-4"
            >
                <UserPlus size={16} />
                Add friend
            </button>

            <div className="flex items-center gap-2 mb-3">
                <span className="text-[13px] text-[#8b8b93] whitespace-nowrap">Friends</span>
                <div className="flex-1 h-px bg-[#27272c]" />
            </div>

            <div
                ref={scrollContainerRef}
                className="flex flex-col gap-0.5 flex-1 overflow-y-auto min-h-0"
            >
                {chats.map((chat: PersonalChat) => (
                    <div
                        key={chat.uuid}
                        onClick={() => onSelectChat(chat.uuid)}
                        className={`flex items-center gap-2.5 px-2 py-2 rounded-lg cursor-pointer transition-colors min-w-0 ${activeChatId === chat.uuid ? 'bg-[#1a1a1d]' : 'hover:bg-[#1a1a1d]'
                            }`}
                    >
                        <img
                            src="https://cdn.discordapp.com/avatars/840559505308909599/fce4743acb41490870ac34652b8ba9a6.webp?size=32"
                            className="w-9 h-9 rounded-full object-cover shrink-0"
                        />
                        <span className="text-sm text-[#f4f4f5] truncate" title={chat.uuid}>
                            {chat.uuid}
                        </span>
                    </div>
                ))}

                <div ref={sentinelRef} className="h-8 flex items-center justify-center shrink-0">
                    {isFetchingNextPage && (
                        <span className="text-xs text-[#8b8b93]">Loading more...</span>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ChatSidebar;