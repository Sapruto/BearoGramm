import { Trash2, X } from 'lucide-react';
import { useState } from 'react';
import type { PersonalChat } from '../../../shared/api/personal';
import { ConfirmDialog } from '../../../shared/components/ConfirmDialog';
import { useDeletePersonalChat } from '../../../shared/hooks/personal/useDeletePersonalChat';

interface ChatListItemProps {
    chat: PersonalChat;
    isActive: boolean;
    onSelect: (uuid: string) => void;
}

export function ChatListItem({ chat, isActive, onSelect }: ChatListItemProps) {
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const { mutate: deleteChat, isPending } = useDeletePersonalChat();

    const handleDelete = () => {
        deleteChat(chat.uuid, {
            onSuccess: () => setIsDialogOpen(false),
        });
    };

    return (
        <>
            <div
                onClick={() => onSelect(chat.uuid)}
                className={`group flex items-center gap-2.5 px-2 py-2 rounded-lg cursor-pointer transition-colors min-w-0 ${isActive ? 'bg-[#1a1a1d]' : 'hover:bg-[#1a1a1d]'
                    }`}
            >
                <img
                    src={chat.partner_profile.avatar_url}
                    className="w-9 h-9 rounded-full object-cover shrink-0"
                />
                <span className="text-sm text-[#f4f4f5] truncate flex-1" title={chat.uuid}>
                    {chat.partner_profile.name}
                </span>
                <button
                    type="button"
                    onClick={(e) => {
                        e.stopPropagation();
                        setIsDialogOpen(true);
                    }}
                    className="shrink-0 w-7 h-7 flex items-center justify-center rounded-md text-[#71717a] opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto transition-colors duration-200 hover:text-red-400 hover:bg-[#27272a]"
                    title="Delete chat"
                >
                    <X size={16} />
                </button>
            </div>

            <ConfirmDialog
                open={isDialogOpen}
                title="Delete this chat?"
                description="This will permanently delete the chat and all its messages."
                icon={Trash2}
                confirmLabel="Delete"
                pendingLabel="Deleting..."
                tone='danger'
                isPending={isPending}
                onConfirm={handleDelete}
                onClose={() => setIsDialogOpen(false)}
            />
        </>
    );
}