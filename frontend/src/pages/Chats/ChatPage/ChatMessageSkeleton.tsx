import Skeleton from "@mui/material/Skeleton";

type Props = {
    isFirst: boolean;
    isLast: boolean;
    width: number;
    height: number;
};

export const ChatMessageSkeleton = ({ isFirst, isLast, width, height }: Props) => (
    <div className={`flex flex-col items-start ${isFirst || isLast ? 'gap-1' : 'gap-0'}`}>
        <div className="flex gap-2 items-center">
            {isFirst ? (
                <Skeleton variant="circular" width={28} height={28} />
            ) : (
                <div className="w-7 shrink-0" />
            )}
            <Skeleton
                variant="rounded"
                width={width}
                height={height}
                sx={{ borderRadius: '12px', borderBottomLeftRadius: '2px' }}
            />
        </div>
        {isLast && <Skeleton variant="text" width={32} sx={{ ml: '36px', fontSize: 11 }} />}
    </div>
);