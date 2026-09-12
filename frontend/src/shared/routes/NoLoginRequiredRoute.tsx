import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuthStore } from "../../store/authStore";
import { useState } from "react";

export function NoLoginRequiredRoute() {
    const { isLoggedIn } = useAuthStore();
    const location = useLocation();
    const [wasLoggedInOnMount] = useState(isLoggedIn());

    if (wasLoggedInOnMount) {
        const from = location.state?.from?.pathname || "/";
        return <Navigate to={from} replace />;
    }

    return <Outlet />;
}