import { useRef } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useGetMyProfile } from "../hooks/profile/useGetMyProfile";
import toast from "react-hot-toast";

export function ProfileRequiredRoute() {
    const { data, isLoading } = useGetMyProfile();
    const toastShownRef = useRef(false);

    if (isLoading) return null;

    const hasNoProfile = data && (!data.success || !data.profile);

    if (hasNoProfile) {
        if (!toastShownRef.current) {
            toast.error("Need to set up profile first");
            toastShownRef.current = true;
        }

        return <Navigate to="/profile/me" replace />;
    }

    return <Outlet />;
}
