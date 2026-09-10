import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "../../store/authStore";
import { useRef } from "react";
import toast from "react-hot-toast";

export function LoginRequiredRoute() {
    const { isLoggedIn } = useAuthStore();
    const toastShownRef = useRef(false);

    if (!isLoggedIn()) {
        if (!toastShownRef.current) {
            toast.error("Need to login first");
            toastShownRef.current = true;
        }

        return <Navigate to="/auth/phone" replace />
    }

    return <Outlet />
}