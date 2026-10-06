type Props = {
    avatarUrl?: string;
    name?: string;
};

const ChatHeader = ({ avatarUrl, name }: Props) => (
    <div className="px-5 py-4 border-b border-[#1f1f23] flex items-center gap-2.5">
        <img src={avatarUrl} className="w-9 h-9 rounded-full object-cover" />
        <span className="text-[15px] font-medium text-[#f4f4f5]">{name}</span>
    </div>
);

export default ChatHeader;