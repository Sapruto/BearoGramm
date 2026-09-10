import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuthStore } from "../../store/authStore";

export function NoLoginRequiredRoute() {
    const { isLoggedIn } = useAuthStore();
    const location = useLocation();

    if (isLoggedIn()) {
        const from = location.state?.from?.pathname || "/";
        return <Navigate to={from} replace />;
    }

    return <Outlet />
}