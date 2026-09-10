import Button from '@mui/material/Button';
import { useNavigate } from 'react-router-dom';
import { useGetMyProfile } from '../../shared/hooks/profile/useGetMyProfile';
import { useAuthStore } from '../../store/authStore';

const HomePage = () => {
    const navigate = useNavigate();
    const { data } = useGetMyProfile();
    const { logout } = useAuthStore();

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-[#0a0a0b] gap-6">
            <h1 className="text-2xl font-medium text-[#f4f4f5]">Homepage</h1>

            <div className="flex flex-col gap-3 w-60">
                <Button
                    variant="outlined"
                    onClick={() => navigate("/auth/phone")}
                    sx={{
                        color: '#f4f4f5',
                        borderColor: '#27272c',
                        '&:hover': { borderColor: '#3a3a40', backgroundColor: '#1a1a1d' },
                    }}
                >
                    Auth
                </Button>
                <Button
                    variant="outlined"
                    onClick={() => navigate("/chats")}
                    sx={{
                        color: '#f4f4f5',
                        borderColor: '#27272c',
                        '&:hover': { borderColor: '#3a3a40', backgroundColor: '#1a1a1d' },
                    }}
                >
                    Chats
                </Button>

                <Button
                    variant="outlined"
                    onClick={() => logout()}
                    sx={{
                        color: '#f4f4f5',
                        borderColor: '#27272c',
                        '&:hover': { borderColor: '#3a3a40', backgroundColor: '#1a1a1d' },
                    }}
                >
                    Logout
                </Button>

                {data?.success && data.profile && (
                    <div>
                        <p>Name: {data.profile.name}</p>
                        <p>User UUID: {data.profile.user_uuid}</p>
                        <p>Profile UUID: {data.profile.uuid}</p>
                        <img src={data.profile.avatar_url} />
                    </div>
                )}
            </div>
        </div>
    )
}

export default HomePage