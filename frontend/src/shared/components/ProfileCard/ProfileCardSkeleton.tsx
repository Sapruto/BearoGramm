import { Skeleton } from '@mui/material';

const skeletonSx = { bgcolor: '#27272a' };

export function ProfileCardSkeleton() {
    return (
        <>
            <Skeleton variant="rectangular" height={64} sx={{ bgcolor: '#1f1f23' }} />

            <div className="flow-root px-4 pb-4">
                <Skeleton
                    variant="circular"
                    width={64}
                    height={64}
                    sx={skeletonSx}
                    className="-mt-8 ring-4 ring-[#141416]"
                />

                <Skeleton variant="text" width="45%" height={22} sx={skeletonSx} className="mt-2.5" />

                <Skeleton variant="text" width="30%" height={18} sx={skeletonSx} className="mt-0.5" />

                <Skeleton variant="text" width="20%" height={18} sx={skeletonSx} className="mt-1" />

                <div className="mt-2 space-y-1">
                    <Skeleton variant="text" width="90%" height={18} sx={skeletonSx} />
                    <Skeleton variant="text" width="80%" height={18} sx={skeletonSx} />
                    <Skeleton variant="text" width="55%" height={18} sx={skeletonSx} />
                </div>
            </div>
        </>
    );
}