import Button from '@mui/material/Button';
import { LogOut, MessageCircle, UserRound } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useGetMyProfile } from '../../shared/hooks/profile/useGetMyProfile';
import { useAuthStore } from '../../store/authStore';

const buttonSx = {
    color: '#f4f4f5',
    borderColor: '#27272c',
    justifyContent: 'flex-start',
    gap: '10px',
    '&:hover': { borderColor: '#3a3a40', backgroundColor: '#1a1a1d' },
};

const HomePage = () => {
    const navigate = useNavigate();
    const { data } = useGetMyProfile();
    const { token, userUUID, logout, isLoggedIn } = useAuthStore();

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-[#0a0a0b] gap-8 px-4">
            <h1 className="text-2xl font-medium text-[#f4f4f5]">Homepage</h1>

            <div className="flex flex-col gap-3 w-80">
                <Button
                    variant="outlined"
                    onClick={() => navigate("/auth/phone")}
                    startIcon={<UserRound size={17} />}
                    sx={buttonSx}
                >
                    Auth
                </Button>
                <Button
                    variant="outlined"
                    onClick={() => navigate("/chats")}
                    startIcon={<MessageCircle size={17} />}
                    sx={buttonSx}
                >
                    Chats
                </Button>
                <Button
                    variant="outlined"
                    onClick={() => logout()}
                    startIcon={<LogOut size={17} />}
                    sx={buttonSx}
                >
                    Logout
                </Button>

                <div className="bg-[#131316] border border-[#1f1f23] rounded-xl p-4">
                    <p className="text-[13px] text-[#8b8b93] mb-2">Auth status</p>
                    {isLoggedIn() ? (
                        <div className="flex flex-col gap-1">
                            <span className="inline-flex items-center gap-1.5 text-sm text-[#6fbf6f] mb-1">
                                <span className="w-1.5 h-1.5 rounded-full bg-[#6fbf6f]" />
                                Logged in
                            </span>
                            <p className="text-xs text-[#8b8b93] truncate">
                                <span className="text-[#f4f4f5]">UUID:</span> {userUUID}
                            </p>
                            <p className="text-xs text-[#8b8b93] truncate">
                                <span className="text-[#f4f4f5]">Token:</span> {token}
                            </p>
                        </div>
                    ) : (
                        <span className="inline-flex items-center gap-1.5 text-sm text-[#8b8b93]">
                            <span className="w-1.5 h-1.5 rounded-full bg-[#5f5f66]" />
                            Not logged in
                        </span>
                    )}
                </div>

                <div className="bg-[#131316] border border-[#1f1f23] rounded-xl p-4">
                    <p className="text-[13px] text-[#8b8b93] mb-2">Profile</p>
                    {data?.success && data.profile ? (
                        <div className="flex items-center gap-3">
                            <img
                                src={data.profile.avatar_url}
                                className="w-10 h-10 rounded-full object-cover shrink-0 bg-[#27272c]"
                            />
                            <div className="min-w-0 flex flex-col gap-0.5">
                                <span className="text-sm text-[#f4f4f5] truncate">{data.profile.name}</span>
                                <span className="text-xs text-[#8b8b93] truncate">{data.profile.uuid}</span>
                            </div>
                        </div>
                    ) : (
                        <span className="text-sm text-[#8b8b93]">No profile</span>
                    )}
                </div>
            </div>
        </div>
    )
}

export default HomePage