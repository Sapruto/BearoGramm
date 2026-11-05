import ProfileTrigger from "../../../shared/components/ProfileCard/ProfileTrigger";
import { useGetMyProfile } from "../../../shared/hooks/profile/useGetMyProfile";

const ProfileWidget = () => {
    const { data, isLoading } = useGetMyProfile();
    const profile = data?.profile;

    return (
        <div className="bg-[#1a1a1d] border border-[#27272c] rounded-xl px-3 py-2.5 flex items-center gap-2.5">
            <div className="w-full flex items-center justify-between gap-5">
                {profile ? (
                    <ProfileTrigger profile={profile}>
                        <button className="flex items-center gap-3 text-left flex-1 min-w-0 rounded-lg px-1.5 py-1.5 -mx-1.5 -my-1 hover:bg-[#242427] transition-colors cursor-pointer">
                            <img
                                src={profile.avatar?.url ?? profile.avatar_url}
                                alt={profile.name}
                                className="w-10 h-10 rounded-full object-cover shrink-0 bg-[#27272c]"
                            />
                            <div className="min-w-0 flex flex-col gap-0.5">
                                <span className="text-sm text-[#f4f4f5] truncate">{profile.name}</span>
                                <span className="text-xs text-[#8b8b93] truncate">{profile.gender}</span>
                            </div>
                        </button>
                    </ProfileTrigger>
                ) : (
                    <div className="flex items-center gap-3 flex-1 min-w-0 px-1.5 py-1.5">
                        <div className="w-10 h-10 rounded-full bg-[#27272c] animate-pulse shrink-0" />
                        <div className="flex flex-col gap-1.5 min-w-0 flex-1">
                            <div className="h-3 w-24 bg-[#27272c] rounded animate-pulse" />
                            <div className="h-2.5 w-16 bg-[#27272c] rounded animate-pulse" />
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ProfileWidget;