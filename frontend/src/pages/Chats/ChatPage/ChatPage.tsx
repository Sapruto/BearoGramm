import { useParams } from 'react-router-dom';
import type { Message } from '../../../shared/api/messages';
import { useGetMessages } from '../../../shared/hooks/messages/useGetMessages';
import { useSendMessage } from '../../../shared/hooks/messages/useSendMessage';
import { useGetChatPartner } from '../../../shared/hooks/personal/useGetChatPartner';
import { useGetMyProfile } from '../../../shared/hooks/profile/useGetMyProfile';
import { useAuthStore } from '../../../store/authStore';
import ChatMessage from './ChatMessage';
import MessageInput from './MessageInput';

const GROUP_WINDOW_MS = 5 * 60 * 1000;

const formatTime = (timestamp: number) =>
    new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

const ChatPage = () => {
    const { uuid: chatUUID } = useParams();
    const { data } = useGetMessages(chatUUID!);
    const { userUUID } = useAuthStore();
    const { data: myProfile } = useGetMyProfile();
    const { mutate: sendMessage } = useSendMessage(chatUUID!);
    const { data: partnerProfile } = useGetChatPartner(chatUUID!);

    const partnerAvatar = partnerProfile?.partner_profile.avatar_url;
    const partnerName = partnerProfile?.partner_profile.name;

    const messages = data?.pages.flatMap((response) => response.message_entity) ?? [];

    const handleSend = (text: string) => {
        sendMessage(
            { chat_uuid: chatUUID!, typing_to_data: [['text_type', text]] },
        );
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
                <span className="text-[15px] font-medium text-[#f4f4f5]">{partnerName}</span>
            </div>

            <div className="flex-1 overflow-y-auto min-h-0 p-5 flex flex-col gap-1">
                {messageGroups.map((group) =>
                    group.map((msg, i) => {
                        const isFirst = i === 0;
                        const isLast = i === group.length - 1;
                        const isOwn = msg.user_uuid == userUUID;

                        return (
                            <div key={msg.uuid} className={!(isFirst) ? 'mt-0.5' : 'mt-3.5'}>
                                <ChatMessage
                                    text={msg.message_data[0].text!}
                                    time={formatTime(Date.parse(msg.created_at))}
                                    isOwn={isOwn}
                                    avatarUrl={isOwn ? myProfile?.profile?.avatar_url : partnerAvatar}
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