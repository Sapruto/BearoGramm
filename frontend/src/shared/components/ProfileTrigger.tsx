import { Skeleton } from '@mui/material';
import * as Popover from '@radix-ui/react-popover';
import { MessageSquare } from 'lucide-react';
import type { ReactNode } from 'react';
import { useAuthStore } from '../../store/authStore';
import type { Profile } from '../api/profile';
import { useGetProfileByUser } from '../hooks/profile/useGetProfileByUser';

type ProfileTriggerProps = {
    children: ReactNode;
    open?: boolean;
    onOpenChange?: (open: boolean) => void;
    side?: 'top' | 'right' | 'bottom' | 'left';
    align?: 'start' | 'center' | 'end';
    sideOffset?: number;
    onMessage?: (profile: Profile) => void;
} & (
    | { profile: Profile; userUUID?: never }
    | { userUUID: string; profile?: never }
);

const skeletonSx = { bgcolor: '#27272a' };

export function ProfileTrigger({
    children,
    open,
    onOpenChange,
    side = 'bottom',
    align = 'start',
    sideOffset = 6,
    profile: profileProp,
    userUUID,
    onMessage,
}: ProfileTriggerProps) {
    const myUUID = useAuthStore((state) => state.userUUID);

    const query = useGetProfileByUser(profileProp ? undefined : userUUID);

    const profile = profileProp ?? query.data;
    const isLoading = !profileProp && query.isLoading;
    const isMe = !!profile && profile.user_uuid === myUUID;

    return (
        <Popover.Root open={open} onOpenChange={onOpenChange}>
            {open === undefined ? (
                <Popover.Trigger asChild>{children}</Popover.Trigger>
            ) : (
                <Popover.Anchor asChild>{children}</Popover.Anchor>
            )}

            <Popover.Portal>
                <Popover.Content
                    side={side}
                    align={align}
                    sideOffset={sideOffset}
                    collisionPadding={8}
                    className="z-50 w-80 overflow-hidden rounded-2xl border border-[#27272a] bg-[#141416] text-[#f4f4f5] shadow-2xl shadow-black/60 outline-none"
                >
                    <div className="h-16 bg-linear-to-r from-indigo-600/70 via-violet-600/60 to-fuchsia-600/50" />

                    <div className="px-4 pb-4">
                        {isLoading ? (
                            <>
                                <Skeleton
                                    variant="circular"
                                    width={64}
                                    height={64}
                                    sx={skeletonSx}
                                    className="-mt-8 ring-4 ring-[#141416]"
                                />
                                <Skeleton variant="text" width="50%" height={24} sx={skeletonSx} className="mt-2.5" />
                                <div className="mt-3 space-y-1">
                                    <Skeleton variant="text" width="65%" height={18} sx={skeletonSx} />
                                    <Skeleton variant="text" width="90%" height={18} sx={skeletonSx} />
                                </div>
                                <Skeleton variant="rounded" height={36} sx={skeletonSx} className="mt-4" />
                            </>
                        ) : !profile ? (
                            <div className="py-6 text-center text-sm text-[#71717a]">Couldn't load the profile</div>
                        ) : (
                            <>
                                <img
                                    src={profile.avatar_url}
                                    alt={profile.name}
                                    className="-mt-8 h-16 w-16 rounded-full object-cover ring-4 ring-[#141416]"
                                />
                                <div className="mt-2.5 text-base font-semibold leading-tight">{profile.name}</div>

                                <div className="mt-3 space-y-1">
                                    <div className="text-sm text-[#71717a]">
                                        Created {new Date(profile.updated_at).toLocaleDateString()}
                                    </div>
                                    <div className="break-all font-mono text-xs text-[#52525b]">{profile.user_uuid}</div>
                                </div>

                                {!isMe && (
                                    <div className="mt-4">
                                        <Popover.Close asChild>
                                            <button
                                                type="button"
                                                onClick={() => onMessage?.(profile)}
                                                className="flex w-full items-center justify-center gap-2 rounded-lg bg-[#27272a] py-2 text-sm font-medium transition-colors hover:bg-[#3f3f46]"
                                            >
                                                <MessageSquare size={16} />
                                                Message
                                            </button>
                                        </Popover.Close>
                                    </div>
                                )}
                            </>
                        )}
                    </div>
                </Popover.Content>
            </Popover.Portal>
        </Popover.Root>
    );
}

export default ProfileTrigger;