type Props = {
    text: string;
    time: string;
    isOwn: boolean;
    avatarUrl?: string;
    isFirst: boolean;
    isLast: boolean;
};

const ChatMessage = ({ text, time, isOwn, avatarUrl, isFirst, isLast }: Props) => {
    return (
        <div className={`flex flex-col items-start ${isFirst || isLast ? 'gap-1' : 'gap-0'}`}>
            <div className="flex gap-2 items-center">
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
                    className={`rounded-xl rounded-bl-sm px-3 py-2 max-w-[320px] ${isOwn ? 'bg-[#f4f4f5]' : 'bg-[#1a1a1d]'
                        }`}
                >
                    <span className={`text-sm ${isOwn ? 'text-[#0a0a0b]' : 'text-[#f4f4f5]'}`}>
                        {text}
                    </span>
                </div>
            </div>
            {isLast && (
                <span className="text-[11px] text-[#5f5f66] ml-9">{time}</span>
            )}
        </div>
    );
};

export default ChatMessage;