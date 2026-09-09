import Button from '@mui/material/Button';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
    const navigate = useNavigate();

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
            </div>
        </div>
    )
}

export default HomePage