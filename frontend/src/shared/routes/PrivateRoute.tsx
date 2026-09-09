import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "../../store/authStore";

export function PrivateRoute() {
    const token = useAuthStore((state) => state.token);

    if (!token) {
        return <Navigate to="/auth/phone" replace />
    }

    return <Outlet />
}