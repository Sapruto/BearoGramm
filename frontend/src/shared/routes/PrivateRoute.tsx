import { Navigate, Outlet } from "react-router-dom";
import { useShallow } from 'zustand/react/shallow';
import { useAuthStore } from "../../store/authStore";

export function PrivateRoute() {
    const { token, userUUID } = useAuthStore(
        useShallow((state) => ({ token: state.token, userUUID: state.userUUID }))
    );

    if (!token || !userUUID) {
        return <Navigate to="/auth/phone" replace />
    }

    return <Outlet />
}