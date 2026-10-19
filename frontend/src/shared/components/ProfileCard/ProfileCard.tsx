import { ColorPicker, ColorPickerArea, ColorPickerContent, ColorPickerEyeDropper, ColorPickerHueSlider, ColorPickerTrigger } from '@/vendor/ui/color-picker';
import { Editable, EditableArea, EditableInput, EditablePreview } from '@/vendor/ui/editable';
import * as Popover from '@radix-ui/react-popover';
import { getColor } from 'colorthief';
import { Camera, MessageSquare } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { useAuthStore } from '../../../store/authStore';
import type { Gender, Profile } from '../../api/profile';
import { useUploadMedia } from '../../hooks/media/useUploadMedia';
import { useGetProfileByUser } from '../../hooks/profile/useGetProfileByUser';
import { useUpdateProfile } from '../../hooks/profile/useUpdateProfile';
import { ProfileCardSkeleton } from './ProfileCardSkeleton';

const GENDER_LABELS: Record<Gender, string> = {
    bear: 'Bear',
    male: 'Male',
    female: 'Female',
    ameba: 'Ameba',
    troll_face: 'Troll face',
    communist: 'Communist',
    cock: 'Cock',
};

const GENDERS = Object.keys(GENDER_LABELS) as Gender[];

const fieldClass =
    '-mx-1.5 w-[calc(100%+0.75rem)] rounded-md bg-transparent px-1.5 py-0.5 outline-none transition-colors hover:bg-[#1f1f23] focus:bg-[#27272a] focus:ring-1 focus:ring-indigo-500';

type ProfileCardProps = {
    profile?: Profile;
    userUUID?: string;
    onMessage?: (profile: Profile) => void;
};

export function ProfileCard({ profile: profileProp, userUUID, onMessage }: ProfileCardProps) {
    const myUUID = useAuthStore((state) => state.userUUID);
    const query = useGetProfileByUser(profileProp ? undefined : userUUID);
    const updateProfile = useUpdateProfile();
    const uploadMedia = useUploadMedia('image');

    const fileInputRef = useRef<HTMLInputElement>(null);
    const [nameDraft, setNameDraft] = useState<string | null>(null);
    const [bioDraft, setBioDraft] = useState<string | null>(null);
    const [genderDraft, setGenderDraft] = useState<Gender | null>(null);
    const [avatarDraft, setAvatarDraft] = useState<{ file: File; previewUrl: string } | null>(null);
    const [bannerDraft, setBannerDraft] = useState<string | null>(null);
    const [hexText, setHexText] = useState<string | null>(null);
    const [pickerKey, setPickerKey] = useState(0);
    const [pickerOpen, setPickerOpen] = useState(false);

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
    const bio = bioDraft ?? profile.bio;
    const trimmedBio = bio.trim();
    const gender = genderDraft ?? profile.gender;
    const bannerColor = bannerDraft ?? profile.banner_color;

    const isNameDirty = nameDraft !== null && trimmedName !== profile.name;
    const isBioDirty = bioDraft !== null && trimmedBio !== profile.bio;
    const isGenderDirty = genderDraft !== null && genderDraft !== profile.gender;
    const isBannerDirty = bannerDraft !== null && bannerDraft.toLowerCase() !== profile.banner_color.toLowerCase();
    const isDirty = isNameDirty || isBioDirty || isGenderDirty || isBannerDirty || avatarDraft !== null;
    const isSaving = uploadMedia.isPending || updateProfile.isPending;
    const canSave = isDirty && trimmedName.length > 0 && !isSaving;
    const hasError = uploadMedia.isError || updateProfile.isError;

    return (
        <>
            {isMe ? (
                <ColorPicker
                    key={pickerKey}
                    defaultValue={bannerColor}
                    defaultFormat="hex"
                    open={pickerOpen}
                    onOpenChange={setPickerOpen}
                    onValueChange={(value) => {
                        setBannerDraft(value);
                        setHexText(null);
                    }}
                    disabled={isSaving}
                >
                    <ColorPickerTrigger asChild>
                        <button
                            type="button"
                            title="Change banner color"
                            className="block h-16 w-full cursor-pointer transition-[filter] hover:brightness-110"
                            style={{ backgroundColor: bannerColor }}
                        />
                    </ColorPickerTrigger>
                    <ColorPickerContent>
                        <ColorPickerArea />
                        <div className="flex items-center gap-2">
                            <ColorPickerEyeDropper />
                            <ColorPickerHueSlider className="flex-1" />
                        </div>
                        <div className="flex h-8 items-center rounded-md border border-input px-2 text-sm focus-within:ring-1 focus-within:ring-ring">
                            <span className="text-muted-foreground">#</span>
                            <input
                                value={hexText ?? bannerColor.slice(1).toUpperCase()}
                                onChange={(e) => setHexText(e.target.value.replace(/[^0-9a-f]/gi, '').slice(0, 6))}
                                onBlur={() => {
                                    if (hexText === null) return;
                                    if (/^[0-9a-f]{6}$/i.test(hexText)) {
                                        setBannerDraft(`#${hexText.toLowerCase()}`);
                                        setPickerKey((k) => k + 1);
                                    }
                                    setHexText(null);
                                }}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter') e.currentTarget.blur();
                                }}
                                spellCheck={false}
                                className="w-full bg-transparent pl-1 font-mono uppercase outline-none"
                            />
                        </div>
                    </ColorPickerContent>
                </ColorPicker>
            ) : (
                <div className="h-16" style={{ backgroundColor: profile.banner_color }} />
            )}

            <div className="flow-root px-4 pb-4">
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
                            onChange={async (e) => {
                                const file = e.target.files?.[0];
                                e.target.value = '';
                                if (!file) return;

                                const previewUrl = URL.createObjectURL(file);
                                setAvatarDraft({ file, previewUrl });

                                try {
                                    const bitmap = await createImageBitmap(file);
                                    const color = await getColor(bitmap);
                                    bitmap.close();

                                    if (color) {
                                        setBannerDraft(color.hex());
                                        setPickerKey((k) => k + 1); 
                                    }
                                } catch (err) {
                                    console.warn('Failed to extract color', err);
                                }
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

                {isMe ? (
                    <Editable
                        value={name}
                        onValueChange={setNameDraft}
                        disabled={isSaving}
                        maxLength={64}
                        required
                        triggerMode="click"
                        className="mt-2.5"
                    >
                        <EditableArea>
                            <EditablePreview
                                className={`${fieldClass} cursor-text border-transparent text-base font-semibold leading-tight text-[#f4f4f5]`}
                            />
                            <EditableInput
                                className={`${fieldClass} border-transparent bg-[#27272a] text-base font-semibold leading-tight text-[#f4f4f5] ring-1 ring-indigo-500`}
                            />
                        </EditableArea>
                    </Editable>
                ) : (
                    <div className="mt-2.5 text-base font-semibold leading-tight">{profile.name}</div>
                )}

                <div className="mt-0.5 px-0 text-sm text-[#71717a]">@username</div>

                {isMe ? (
                    <select
                        value={gender}
                        onChange={(e) => setGenderDraft(e.target.value as Gender)}
                        disabled={isSaving}
                        className={`${fieldClass} mt-1 cursor-pointer text-sm text-[#a1a1aa]`}
                    >
                        {GENDERS.map((value) => (
                            <option key={value} value={value} className="bg-[#18181b]">
                                {GENDER_LABELS[value]}
                            </option>
                        ))}
                    </select>
                ) : (
                    <div className="mt-1 text-sm text-[#a1a1aa]">{GENDER_LABELS[profile.gender]}</div>
                )}

                {isMe ? (
                    <textarea
                        value={bio}
                        onChange={(e) => setBioDraft(e.target.value)}
                        disabled={isSaving}
                        placeholder="About me"
                        maxLength={256}
                        rows={3}
                        className={`${fieldClass} mt-2 resize-none text-sm text-[#d4d4d8] placeholder:text-[#52525b]`}
                    />
                ) : (
                    profile.bio && (
                        <div className="mt-2.5 whitespace-pre-wrap wrap-break-word text-sm text-[#d4d4d8]">
                            {profile.bio}
                        </div>
                    )
                )}

                {isMe ? (
                    <div className="mt-3 flex h-7 items-center justify-between gap-2">
                        <span className="text-xs text-red-400">{hasError && "Couldn't save changes"}</span>
                        <div className={`flex items-center gap-1 ${isDirty ? '' : 'invisible'}`}>
                            <button
                                type="button"
                                onClick={() => {
                                    setNameDraft(null);
                                    setBioDraft(null);
                                    setGenderDraft(null);
                                    setBannerDraft(null);
                                    setAvatarDraft(null);
                                    uploadMedia.reset();
                                    updateProfile.reset();
                                }}
                                disabled={isSaving}
                                className="h-7 rounded-md px-2.5 text-xs font-medium text-[#a1a1aa] transition-colors hover:bg-[#27272a] hover:text-[#f4f4f5] disabled:opacity-50"
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
                                            ...(isBioDirty && { bio: trimmedBio }),
                                            ...(isGenderDirty && { gender }),
                                            ...(isBannerDirty && { banner_color: bannerColor }),
                                            ...(media && { avatar_url: media.castrated_url }),
                                        });
                                        setNameDraft(null);
                                        setBioDraft(null);
                                        setGenderDraft(null);
                                        setBannerDraft(null);
                                        setAvatarDraft(null);
                                    } catch { }
                                }}
                                disabled={!canSave}
                                className="h-7 rounded-md bg-indigo-600 px-3 text-xs font-medium text-white transition-colors hover:bg-indigo-500 disabled:opacity-40"
                            >
                                {isSaving ? 'Saving…' : 'Save'}
                            </button>
                        </div>
                    </div>
                ) : (
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
        </>
    );
}