import * as Popover from '@radix-ui/react-popover';
import type { ReactNode } from 'react';
import type { Profile } from '../../api/profile';
import { ProfileCard } from './ProfileCard';

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

export function ProfileTrigger({
    children,
    open,
    onOpenChange,
    side = 'bottom',
    align = 'start',
    sideOffset = 6,
    profile,
    userUUID,
    onMessage,
}: ProfileTriggerProps) {
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
                    <ProfileCard profile={profile} userUUID={userUUID} onMessage={onMessage} />
                </Popover.Content>
            </Popover.Portal>
        </Popover.Root>
    );
}

export default ProfileTrigger;