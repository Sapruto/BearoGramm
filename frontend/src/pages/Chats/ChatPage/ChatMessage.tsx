type Props = {
    text: string;
    time: string;
    isOwn: boolean;
    avatarUrl?: string;
    isFirst: boolean;
    isLast: boolean;
};

const ChatMessage = ({ text, time, avatarUrl, isFirst, isLast }: Props) => {
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
                    className={`rounded-xl rounded-bl-sm px-3 py-2 max-w-[320px] bg-[linear-gradient(to_bottom,rgba(0,0,0,0.6),rgba(0,0,0,0.6)),url('https://iv.okcdn.ru/getVideoPreview?id=8052769098399&idx=7&type=39&tkn=PpKyej2HVeLYEG3bwrb_2rMmLvY&fn=vid_w')] bg-cover bg-center`}
                >
                    <span className={`text-sm ${false ? 'text-[#0a0a0b]' : 'text-[#f4f4f5]'}`}>
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