import { Skeleton } from '@mui/material';

const skeletonSx = { bgcolor: '#27272a' };

export function ProfileCardSkeleton() {
    return (
        <div className="px-4 pb-4">
            <Skeleton
                variant="circular"
                width={64}
                height={64}
                sx={skeletonSx}
                className="-mt-8 ring-4 ring-[#141416]"
            />
            <Skeleton variant="text" width="50%" height={24} sx={skeletonSx} className="mt-2.5" />
            <div className="mt-3 space-y-1">
                <Skeleton variant="text" width="65%" height={18} sx={skeletonSx} />
                <Skeleton variant="text" width="90%" height={18} sx={skeletonSx} />
            </div>
            <Skeleton variant="rounded" height={36} sx={skeletonSx} className="mt-4" />
        </div>
    );
}