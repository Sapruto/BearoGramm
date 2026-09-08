// ChatSidebar.tsx
import { UserPlus } from 'lucide-react';

type Friend = {
    id: string;
    name: string;
    initials: string;
    bgColor: string;
    textColor: string;
};

const friends: Friend[] = [
    { id: '1', name: 'Alex Kim', initials: 'AK', bgColor: '#1a1a2e', textColor: '#a5a0e8' },
    { id: '2', name: 'Maya Rodriguez', initials: 'MR', bgColor: '#0f2a24', textColor: '#5dcaa5' },
    { id: '3', name: 'Daniel Petrov', initials: 'DP', bgColor: '#2a1810', textColor: '#f0997b' },
    { id: '4', name: 'Sofia Novak', initials: 'SN', bgColor: '#2a1420', textColor: '#ed93b1' },
    { id: '5', name: 'James Wu', initials: 'JW', bgColor: '#1f1f1f', textColor: '#b4b2a9' },
];

const ChatSidebar = () => {
    return (
        <div className="w-[280px] bg-[#131316] border border-[#1f1f23] rounded-xl p-4">
            <button className="w-full h-9 flex items-center justify-center gap-1.5 rounded-lg border border-[#27272c] text-[#f4f4f5] text-sm font-medium hover:bg-[#1a1a1d] transition-colors cursor-pointer mb-4">
                <UserPlus size={16} />
                Add friend
            </button>

            <div className="flex items-center gap-2 mb-3">
                <span className="text-[13px] text-[#8b8b93] whitespace-nowrap">Friends</span>
                <div className="flex-1 h-px bg-[#27272c]" />
            </div>

            <div className="flex flex-col gap-0.5">
                {friends.map((friend) => (
                    <div
                        key={friend.id}
                        className="flex items-center gap-2.5 px-2 py-2 rounded-lg cursor-pointer hover:bg-[#1a1a1d] transition-colors"
                    >
                        <div
                            className="w-9 h-9 rounded-full flex items-center justify-center text-[13px] font-medium flex-shrink-0"
                            style={{ backgroundColor: friend.bgColor, color: friend.textColor }}
                        >
                            {friend.initials}
                        </div>
                        <span className="text-sm text-[#f4f4f5]">{friend.name}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ChatSidebar;