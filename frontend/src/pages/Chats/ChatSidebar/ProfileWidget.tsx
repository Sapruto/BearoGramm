import { useGetMyProfile } from "../../../shared/hooks/profile/useGetMyProfile";

const ProfileWidget = () => {
    const { data } = useGetMyProfile();

    return (
        <div className="bg-[#1a1a1d] border border-[#27272c] rounded-xl px-3 py-2.5 flex items-center gap-2.5">
            <div className="w-full flex items-center justify-between gap-5">
                <button className="flex items-center gap-3 text-left flex-1 min-w-0 rounded-lg px-1.5 py-1.5 -mx-1.5 -my-1 hover:bg-[#242427] transition-colors cursor-pointer">
                    {data?.profile ? (
                        <>
                            <img
                                src={data.profile.avatar_url}
                                className="w-10 h-10 rounded-full object-cover shrink-0 bg-[#27272c]"
                            />
                            <div className="min-w-0 flex flex-col gap-0.5">
                                <span className="text-sm text-[#f4f4f5] truncate">{data.profile.name}</span>
                                <span className="text-xs text-[#8b8b93] truncate">{new Date(Date.parse(data.profile.updated_at)).toLocaleString()}</span>
                            </div>
                        </>
                    ) : (
                        <span className="text-sm text-[#8b8b93]">Loading...</span>
                    )}
                </button>

                {/* <button className="w-8 h-8 flex items-center justify-center rounded-lg text-[#8b8b93] hover:bg-[#242427] hover:text-[#f4f4f5] transition-colors cursor-pointer shrink-0">
                    <Settings size={18} />
                </button> */}
            </div>
        </div>
    )
}

export default ProfileWidget