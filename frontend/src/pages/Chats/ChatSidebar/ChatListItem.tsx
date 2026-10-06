import * as ContextMenu from '@radix-ui/react-context-menu';
import { Trash2, User, X } from 'lucide-react';
import { useState } from 'react';
import type { PersonalChat } from '../../../shared/api/personal';
import { ConfirmDialog } from '../../../shared/components/ConfirmDialog';
import ProfileTrigger from '../../../shared/components/ProfileTrigger';
import { useDeletePersonalChat } from '../../../shared/hooks/personal/useDeletePersonalChat';
interface ChatListItemProps {
    chat: PersonalChat;
    isActive: boolean;
    onSelect: (uuid: string) => void;
}

export function ChatListItem({ chat, isActive, onSelect }: ChatListItemProps) {
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [profileOpen, setProfileOpen] = useState(false);
    const { mutate: deleteChat, isPending } = useDeletePersonalChat();

    const handleDelete = () => {
        deleteChat(chat.uuid, {
            onSuccess: () => setDeleteDialogOpen(false),
        });
    };

    return (
        <>
            <ContextMenu.Root>
                <ProfileTrigger
                    userUUID={chat.partner_uuid}
                    open={profileOpen}
                    onOpenChange={setProfileOpen}
                >
                    <ContextMenu.Trigger asChild>
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
                                    setDeleteDialogOpen(true);
                                }}
                                className="shrink-0 w-7 h-7 flex items-center justify-center rounded-md text-[#71717a] opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto transition-colors duration-200 hover:text-red-400 hover:bg-[#27272a]"
                                title="Delete chat"
                            >
                                <X size={16} />
                            </button>
                        </div>
                    </ContextMenu.Trigger>
                </ProfileTrigger>

                <ContextMenu.Portal>
                    <ContextMenu.Content
                        collisionPadding={8}
                        onCloseAutoFocus={(e) => {
                            if (profileOpen) e.preventDefault();
                        }}
                        className="z-50 min-w-52 rounded-xl border border-[#27272a] bg-[#141416] p-1 shadow-2xl shadow-black/50"
                    >
                        <ContextMenu.Item
                            onSelect={() => setProfileOpen(true)}
                            className="flex cursor-pointer items-center gap-2.5 rounded-md px-2.5 py-1.5 text-sm text-[#f4f4f5] outline-none data-highlighted:bg-[#27272a]"
                        >
                            <User size={16} className="text-[#71717a]" />
                            <span className="flex-1">Profile</span>
                        </ContextMenu.Item>

                        <ContextMenu.Separator className="my-1 h-px bg-[#27272a]" />

                        <ContextMenu.Item
                            onSelect={() => setDeleteDialogOpen(true)}
                            className="flex cursor-pointer items-center gap-2.5 rounded-md px-2.5 py-1.5 text-sm text-red-400 outline-none data-highlighted:bg-red-500/10"
                        >
                            <Trash2 size={16} />
                            <span className="flex-1">Delete chat</span>
                        </ContextMenu.Item>
                    </ContextMenu.Content>
                </ContextMenu.Portal>
            </ContextMenu.Root>

            <ConfirmDialog
                open={deleteDialogOpen}
                title="Delete this chat?"
                description="This will permanently delete the chat and all its messages."
                icon={Trash2}
                confirmLabel="Delete"
                pendingLabel="Deleting..."
                tone='danger'
                isPending={isPending}
                onConfirm={handleDelete}
                onClose={() => setDeleteDialogOpen(false)}
            />
        </>
    );
}