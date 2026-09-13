import { UserRound } from 'lucide-react';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { useGetMyProfile } from '../../shared/hooks/profile/useGetMyProfile';
import { useUpdateProfile } from '../../shared/hooks/profile/useUpdateProfile';
import { withPreventDefault } from '../../shared/lib/withPreventDefault';

const ProfileSettingsPage = () => {
    const { isPending: isLoadingProfile } = useGetMyProfile();
    const { mutate: updateProfile, isPending: isUpdating } = useUpdateProfile();

    const navigate = useNavigate();

    const [name, setName] = useState('');


    const handleSave = () => {
        const trimmedName = name.trim();
        if (!trimmedName) return;

        updateProfile(
            { name: trimmedName },
            {
                onSuccess: () => {
                    navigate("/", { replace: true })
                    toast.success('Successfully signed in!');
                }
            });
    };

    if (isLoadingProfile) {
        return (
            <div className="flex-1 h-screen flex items-center justify-center bg-[#0a0a0b]">
                <span className="text-sm text-[#8b8b93]">Loading...</span>
            </div>
        );
    }

    return (
        <div className="flex-1 h-screen flex items-center justify-center bg-[#0a0a0b]">
            <div className="w-120 bg-[#131316] border border-[#1f1f23] rounded-2xl px-14 py-12">
                <div className="w-12 h-12 rounded-full bg-[#14243d] flex items-center justify-center mb-6">
                    <UserRound size={22} className="stroke-[#5b9bd8]" />
                </div>

                <h1 className="text-[22px] font-medium text-[#f4f4f5] mb-1.5">
                    Create your profile
                </h1>
                <p className="text-sm text-[#8b8b93] mb-8 leading-relaxed">
                    Choose a name so friends can recognize you.
                </p>

                <form onSubmit={withPreventDefault(handleSave)}>
                    <label className="text-[13px] text-[#8b8b93] block mb-1.5">Name</label>
                    <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Your name"
                        className="w-full h-10 rounded-[10px] bg-[#0e0e10] border border-[#27272c] text-[#f4f4f5] px-3.5 text-sm outline-none focus:border-[#3a3a40] mb-6"
                    />

                    <button
                        type="submit"
                        disabled={isUpdating}
                        className="w-full h-10.5 rounded-[10px] bg-[#f4f4f5] text-[#0a0a0b] text-[15px] font-medium hover:bg-[#d4d4d8] transition-colors cursor-pointer"
                    >
                        Create profile
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ProfileSettingsPage;