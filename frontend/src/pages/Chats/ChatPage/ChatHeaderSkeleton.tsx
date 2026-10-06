import Skeleton from "@mui/material/Skeleton";

export const ChatHeaderSkeleton = () => (
    <div className="px-5 py-4 border-b border-[#1f1f23] flex items-center gap-2.5">
        <Skeleton variant="circular" width={36} height={36} />
        <Skeleton variant="text" width={120} sx={{ fontSize: 15 }} />
    </div>
);