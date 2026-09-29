import { UserPlus } from 'lucide-react';
import { useEffect, useRef } from 'react';
import type { PersonalChat } from '../../../shared/api/personal';
import { useGetPersonalChats } from '../../../shared/hooks/personal/useGetPersonalChats';
import ProfileWidget from './ProfileWidget';
import { ChatListItem } from './ChatListItem';

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
            <div className='h-full flex flex-col overflow-y-auto min-h-0'>
                <div>
                    <button
                        onClick={onSelectAddFriend}
                        className="w-full h-9 flex items-center justify-center gap-1.5 rounded-lg border border-[#27272c] text-[#f4f4f5] text-sm font-medium hover:bg-[#1a1a1d] transition-colors cursor-pointer mb-4"
                    >
                        <UserPlus size={16} />
                        Add friend
                    </button>
                </div>


                <div className="flex items-center gap-2 mb-3">
                    <span className="text-[13px] text-[#8b8b93] whitespace-nowrap">Friends</span>
                    <div className="flex-1 h-px bg-[#27272c]" />
                </div>

                <div
                    ref={scrollContainerRef}
                    className="flex flex-col gap-0.5 flex-1"
                >
                    {chats.map((chat: PersonalChat) => (
                        <ChatListItem
                            key={chat.uuid}
                            chat={chat}
                            isActive={activeChatId === chat.uuid}
                            onSelect={onSelectChat}
                        />
                    ))}

                    <div ref={sentinelRef} className="h-8 flex items-center justify-center shrink-0">
                        {isFetchingNextPage && (
                            <span className="text-xs text-[#8b8b93]">Loading more...</span>
                        )}
                    </div>
                </div>
            </div>

            <ProfileWidget />
        </div>
    );
};

export default ChatSidebar;