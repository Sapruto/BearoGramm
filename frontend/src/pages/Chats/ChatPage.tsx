import { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import type { Message } from '../../shared/api/messages';
import { useGetMessages } from '../../shared/hooks/messages/getMessages';
import { useAuthStore } from '../../store/authStore';
import ChatMessage from './ChatMessage';
import MessageInput from './MessageInput';

const GROUP_WINDOW_MS = 5 * 60 * 1000;

const partnerAvatar = 'https://cdn.discordapp.com/avatars/840559505308909599/fce4743acb41490870ac34652b8ba9a6.webp?size=32';
const ownAvatar = 'https://cdn.discordapp.com/icons/822066990423605249/9942162f40a20cbc6af2344166225747.webp?size=80&quality=lossless';

const formatTime = (timestamp: number) =>
    new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

const ChatPage = () => {
    const { uuid: chatUUID } = useParams();
    const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useGetMessages(chatUUID!);
    const { userUUID } = useAuthStore();

    useEffect(() => {
        console.log(data?.pages && JSON.stringify(data.pages, null, 2));
        if (!data)
            return;

    }, [data])

    const messages = data?.pages?.flatMap((response) => response.message_entity) ?? [];

    const handleSend = (text: string) => {
        alert("send " + text);
    };

    const messageGroups = messages.reduce<Message[][]>((acc, msg, i, arr) => {
        const prev = arr[i - 1];
        const prevIsOwn = prev && prev.user_uuid == userUUID
        const isOwn = msg.user_uuid == userUUID
        const isSameGroup =
            prev &&
            prevIsOwn === isOwn &&
            Date.parse(msg.created_at) - Date.parse(prev.created_at) < GROUP_WINDOW_MS;

        const newGroup = acc.length == 0 || !isSameGroup;

        if (newGroup) {
            return [...acc, [msg]]
        }
        acc[acc.length - 1].push(msg);
        return acc;
    }, []);

    return (
        <div className="flex-1 h-screen flex flex-col bg-[#0a0a0b]">
            <div className="px-5 py-4 border-b border-[#1f1f23] flex items-center gap-2.5">
                <img src={partnerAvatar} className="w-9 h-9 rounded-full object-cover" />
                <span className="text-[15px] font-medium text-[#f4f4f5]">Alex Kim</span>
            </div>

            <div className="flex-1 overflow-y-auto min-h-0 p-5 flex flex-col gap-1">
                {messageGroups.map((group) =>
                    group.map((msg, i) => {
                        const isFirst = i === 0;
                        const isLast = i === group.length - 1;
                        const isOwn = msg.user_uuid == userUUID;

                        console.log(isOwn, msg, msg.user_uuid, userUUID)

                        return (
                            <div key={msg.uuid} className={!(isFirst) ? 'mt-0.5' : 'mt-3.5'}>
                                <ChatMessage
                                    text={msg.message_data[0].text!}
                                    time={formatTime(Date.parse(msg.created_at))}
                                    isOwn={isOwn}
                                    avatarUrl={isOwn ? ownAvatar : partnerAvatar}
                                    isFirst={isFirst}
                                    isLast={isLast}
                                />
                            </div>
                        );
                    }))}
            </div>

            <MessageInput onSend={handleSend} />
        </div>
    );
};

export default ChatPage;