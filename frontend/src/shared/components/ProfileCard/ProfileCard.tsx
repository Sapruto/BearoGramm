import * as Popover from '@radix-ui/react-popover';
import { Camera, MessageSquare } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { ProfileCardSkeleton } from './ProfileCardSkeleton';
import { useAuthStore } from '../../../store/authStore';
import type { Profile } from '../../api/profile';
import { useUploadMedia } from '../../hooks/media/useUploadMedia';
import { useGetProfileByUser } from '../../hooks/profile/useGetProfileByUser';
import { useUpdateProfile } from '../../hooks/profile/useUpdateProfile';

type ProfileCardProps = {
    profile?: Profile;
    userUUID?: string;
    onMessage?: (profile: Profile) => void;
};

export function ProfileCard({ profile: profileProp, userUUID, onMessage }: ProfileCardProps) {
    const myUUID = useAuthStore((state) => state.userUUID);
    const query = useGetProfileByUser(profileProp ? undefined : userUUID);
    const updateProfile = useUpdateProfile();
    const uploadMedia = useUploadMedia();

    const fileInputRef = useRef<HTMLInputElement>(null);
    const [isEditingName, setIsEditingName] = useState(false);
    const [nameDraft, setNameDraft] = useState<string | null>(null);
    const [avatarDraft, setAvatarDraft] = useState<{ file: File; previewUrl: string } | null>(null);

    useEffect(() => {
        return () => {
            if (avatarDraft) URL.revokeObjectURL(avatarDraft.previewUrl);
        };
    }, [avatarDraft]);

    const profile = profileProp ?? query.data;

    if (!profileProp && query.isLoading) return <ProfileCardSkeleton />;

    if (!profile) {
        return <div className="px-4 py-6 text-center text-sm text-[#71717a]">Couldn't load the profile</div>;
    }

    const isMe = profile.user_uuid === myUUID;
    const name = nameDraft ?? profile.name;
    const trimmedName = name.trim();
    const isNameDirty = nameDraft !== null && trimmedName !== profile.name;
    const isDirty = isNameDirty || avatarDraft !== null;
    const isSaving = uploadMedia.isPending || updateProfile.isPending;
    const canSave = isDirty && trimmedName.length > 0 && !isSaving;
    const hasError = uploadMedia.isError || updateProfile.isError;

    return (
        <div className="px-4 pb-4">
            {isMe ? (
                <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isSaving}
                    title="Change avatar"
                    className="group relative -mt-8 block h-16 w-16 rounded-full ring-4 ring-[#141416]"
                >
                    <img
                        src={avatarDraft?.previewUrl ?? profile.avatar_url}
                        alt={profile.name}
                        className="h-full w-full rounded-full object-cover"
                    />
                    <span className="absolute inset-0 flex items-center justify-center rounded-full bg-black/50 opacity-0 transition-opacity group-hover:opacity-100">
                        <Camera size={18} />
                    </span>
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        hidden
                        onChange={(e) => {
                            const file = e.target.files?.[0];
                            e.target.value = '';
                            if (!file) return;
                            setAvatarDraft({ file, previewUrl: URL.createObjectURL(file) });
                        }}
                    />
                </button>
            ) : (
                <img
                    src={profile.avatar_url}
                    alt={profile.name}
                    className="-mt-8 h-16 w-16 rounded-full object-cover ring-4 ring-[#141416]"
                />
            )}

            <div className="mt-2.5">
                {isMe && isEditingName ? (
                    <input
                        autoFocus
                        value={name}
                        onChange={(e) => setNameDraft(e.target.value)}
                        onFocus={(e) => e.currentTarget.select()}
                        onBlur={() => setIsEditingName(false)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter') e.currentTarget.blur();
                        }}
                        maxLength={64}
                        className="-mx-1.5 w-[calc(100%+0.75rem)] rounded-md bg-[#27272a] px-1.5 text-base font-semibold leading-tight text-[#f4f4f5] outline-none ring-1 ring-indigo-500"
                    />
                ) : isMe ? (
                    <button
                        type="button"
                        onClick={() => setIsEditingName(true)}
                        title="Click to edit"
                        className="-mx-1.5 w-[calc(100%+0.75rem)] cursor-text rounded-md px-1.5 text-left text-base font-semibold leading-tight transition-colors hover:bg-[#1f1f23]"
                    >
                        {name}
                    </button>
                ) : (
                    <div className="text-base font-semibold leading-tight">{profile.name}</div>
                )}
            </div>

            <div className="mt-3 space-y-1">
                <div className="text-sm text-[#71717a]">
                    Created {new Date(profile.updated_at).toLocaleDateString()}
                </div>
                <div className="break-all font-mono text-xs text-[#52525b]">{profile.user_uuid}</div>
            </div>

            {hasError && <div className="mt-3 text-xs text-red-400">Couldn't save changes</div>}

            {isMe && isDirty && (
                <div className="mt-4 flex justify-end gap-1.5">
                    <button
                        type="button"
                        onClick={() => {
                            setNameDraft(null);
                            setAvatarDraft(null);
                            uploadMedia.reset();
                            updateProfile.reset();
                        }}
                        disabled={isSaving}
                        className="h-7 rounded-md bg-[#27272a] px-3 text-xs font-medium transition-colors hover:bg-[#3f3f46] disabled:opacity-50"
                    >
                        Reset
                    </button>
                    <button
                        type="button"
                        onClick={async () => {
                            try {
                                const media = avatarDraft ? await uploadMedia.mutateAsync(avatarDraft.file) : null;
                                await updateProfile.mutateAsync({
                                    ...(isNameDirty && { name: trimmedName }),
                                    ...(media && { avatar_url: media.url }),
                                });
                                setNameDraft(null);
                                setAvatarDraft(null);
                            } catch {
                                // ошибка отображается через isError мутаций
                            }
                        }}
                        disabled={!canSave}
                        className="h-7 rounded-md bg-indigo-600 px-3 text-xs font-medium text-white transition-colors hover:bg-indigo-500 disabled:opacity-50"
                    >
                        {isSaving ? 'Saving…' : 'Save'}
                    </button>
                </div>
            )}

            {!isMe && (
                <div className="mt-4">
                    <Popover.Close asChild>
                        <button
                            type="button"
                            onClick={() => onMessage?.(profile)}
                            className="flex h-8 w-full items-center justify-center gap-1.5 rounded-md bg-[#27272a] text-xs font-medium transition-colors hover:bg-[#3f3f46]"
                        >
                            <MessageSquare size={14} />
                            Message
                        </button>
                    </Popover.Close>
                </div>
            )}
        </div>
    );
}