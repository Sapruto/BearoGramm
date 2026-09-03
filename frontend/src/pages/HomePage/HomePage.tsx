import Button from '@mui/material/Button'
import { useNavigate } from 'react-router-dom'

const HomePage = () => {
    const navigate = useNavigate();

    return (
        <div>
            <h1>HOMEPAGE</h1>

            <Button variant="text" onClick={() => navigate("/auth/phone")}>Auth</Button>
        </div>
    )
}

export default HomePage