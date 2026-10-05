import { formatMessageTime } from "../../../shared/lib/formatMessageTime";

type Props = {
    text: string;
    timestamp: number;
    isOwn: boolean;
    avatarUrl?: string;
    isFirst: boolean;
    isLast: boolean;
};

const ChatMessage = ({ text, timestamp, isOwn, avatarUrl, isFirst, isLast }: Props) => {
    const { label, fullDate, iso } = formatMessageTime(timestamp);

    return (
        <div className={`flex flex-col items-start ${isFirst || isLast ? 'gap-1' : 'gap-0'}`}>
            <div className="flex gap-2 items-center min-w-0 max-w-full">
                {isFirst ? (
                    avatarUrl ? (
                        <img src={avatarUrl} className="w-7 h-7 rounded-full object-cover shrink-0" />
                    ) : (
                        <div className="w-7 h-7 shrink-0" />
                    )
                ) : (
                    <div className="w-7 shrink-0" />
                )}
                <div
                    className={`rounded-xl rounded-bl-sm px-3 py-2 max-w-[320px] min-w-0 ${isOwn ? 'bg-[#f4f4f5]' : 'bg-[#1a1a1d]'
                        }`}
                >
                    <span className={`block text-sm wrap-break-word whitespace-pre-wrap ${isOwn ? 'text-[#0a0a0b]' : 'text-[#f4f4f5]'}`}>
                        {text}
                    </span>
                </div>
            </div>
            {isLast && (
                <time
                    dateTime={iso}
                    tabIndex={0}
                    className="group relative ml-9 cursor-default text-[11px] text-[#5f5f66] outline-none"
                >
                    {label}
                    <span
                        role="tooltip"
                        className="pointer-events-none absolute bottom-full left-0 z-10 mb-1.5 whitespace-nowrap rounded-md border border-[#2a2a2e] bg-[#1a1a1d] px-2 py-1 text-[11px] text-[#f4f4f5] opacity-0 shadow-lg transition-opacity duration-150 group-hover:opacity-100 group-focus-visible:opacity-100"
                    >
                        {fullDate}
                    </span>
                </time>
            )}
        </div>
    );
};

export default ChatMessage;