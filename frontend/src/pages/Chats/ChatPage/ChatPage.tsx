import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Virtuoso, type VirtuosoHandle } from 'react-virtuoso';
import type { Message } from '../../../shared/api/messages';
import { useGetMessages } from '../../../shared/hooks/messages/useGetMessages';
import { useSendMessage } from '../../../shared/hooks/messages/useSendMessage';
import { useGetChatPartner } from '../../../shared/hooks/personal/useGetChatPartner';
import { useGetMyProfile } from '../../../shared/hooks/profile/useGetMyProfile';
import { useAuthStore } from '../../../store/authStore';
import ChatMessage from './ChatMessage';
import { ChatSkeleton } from './ChatSkeleton';
import MessageInput from './MessageInput';

const INITIAL_COUNT = 30;
const HISTORY_COUNT = 20;

const GROUP_WINDOW_MS = 5 * 60 * 1000;
const START_INDEX = 100000;

const formatTime = (timestamp: number) =>
    new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

const ChatHeader = ({ avatarUrl, name }: { avatarUrl?: string; name?: string }) => (
    <div className="px-5 py-4 border-b border-[#1f1f23] flex items-center gap-2.5">
        <img src={avatarUrl} className="w-9 h-9 rounded-full object-cover" />
        <span className="text-[15px] font-medium text-[#f4f4f5]">{name}</span>
    </div>
);

const Header = ({ context }: { context?: { hasPreviousPage: boolean; partnerName: string | undefined } }) => {
    const isHistoryEnd = !context?.hasPreviousPage;

    return (
        <div className="relative w-full">
            <div className={isHistoryEnd ? "invisible" : "visible"}>
                <ChatSkeleton />
            </div>

            {isHistoryEnd && (
                <div className="absolute bottom-0 left-0 right-0 p-3 text-[#999]">
                    This is the beginning of your direct message history with <strong>{context?.partnerName ?? "Loading..."}</strong>.
                </div>
            )}
        </div>
    );
};


const ChatRoom = ({ chatUUID }: { chatUUID: string }) => {
    const { data, fetchPreviousPage, hasPreviousPage, isFetchingPreviousPage } = useGetMessages(
        chatUUID,
        INITIAL_COUNT,
        HISTORY_COUNT
    );
    const { userUUID } = useAuthStore();
    const { data: myProfile } = useGetMyProfile();
    const { mutate: sendMessage } = useSendMessage();
    const { data: partnerProfile } = useGetChatPartner(chatUUID);
    const virtuosoRef = useRef<VirtuosoHandle>(null);

    const partnerAvatar = partnerProfile?.partner_profile.avatar_url;
    const partnerName = partnerProfile?.partner_profile.name;

    const messages = useMemo(() => {
        const map = new Map<string, Message>();
        for (const page of data?.pages ?? []) {
            for (const msg of page.message_entity) {
                map.set(msg.uuid, msg);
            }
        }
        return [...map.values()].sort((a, b) => Date.parse(a.created_at) - Date.parse(b.created_at));
    }, [data]);

    const messageGroups = useMemo(() => {
        return messages.reduce<Message[][]>((acc, msg, i, arr) => {
            const prev = arr[i - 1];
            const prevIsOwn = prev && prev.user_uuid == userUUID;
            const isOwn = msg.user_uuid == userUUID;
            const isSameGroup =
                prev &&
                prevIsOwn === isOwn &&
                Date.parse(msg.created_at) - Date.parse(prev.created_at) < GROUP_WINDOW_MS;

            const newGroup = acc.length === 0 || !isSameGroup;
            if (newGroup) return [...acc, [msg]];
            acc[acc.length - 1].push(msg);
            return acc;
        }, []);
    }, [messages, userUUID]);

    const flatItems = useMemo(() => {
        return messageGroups.flatMap((group) =>
            group.map((msg, i) => ({
                msg,
                isFirst: i === 0,
                isLast: i === group.length - 1,
            }))
        );
    }, [messageGroups]);

    const [firstItemIndex, setFirstItemIndex] = useState(START_INDEX);
    const [anchorId, setAnchorId] = useState<string | null>(null);

    const firstId = flatItems[0]?.msg.uuid ?? null;

    if (firstId !== anchorId) {
        if (anchorId !== null) {
            const shift = flatItems.findIndex((item) => item.msg.uuid === anchorId);
            if (shift > 0) setFirstItemIndex((index) => index - shift);
        }
        setAnchorId(firstId);
    }

    const prevCountRef = useRef(flatItems.length);
    const scrollerRef = useRef<HTMLElement | null>(null);
    const scrollerCbRef = useCallback((el: HTMLElement | Window | null) => {
        scrollerRef.current = el instanceof HTMLElement ? el : null;
    }, []);

    useEffect(() => {
        const grew = flatItems.length > prevCountRef.current;
        prevCountRef.current = flatItems.length;
        if (!grew) return;
        const settle = () => {
            const sc = scrollerRef.current;
            if (!sc) return;
            const gap = sc.scrollHeight - sc.scrollTop - sc.clientHeight;
            if (gap <= 0 || gap > 300) return;
            sc.scrollTop = sc.scrollHeight;
        };
        const list = scrollerRef.current?.querySelector('[data-item-index]')?.parentElement;
        const observer = new ResizeObserver(() => requestAnimationFrame(settle));
        if (list) observer.observe(list);
        const raf = requestAnimationFrame(settle);
        const stop = setTimeout(() => observer.disconnect(), 2000);
        return () => {
            observer.disconnect();
            cancelAnimationFrame(raf);
            clearTimeout(stop);
        };
    }, [flatItems.length]);

    const handleSend = (text: string) => {
        sendMessage({ chat_uuid: chatUUID, typing_to_data: [['text_type', text]] });
    };

    const loadMore = useCallback(() => {
        if (hasPreviousPage && !isFetchingPreviousPage) {
            fetchPreviousPage();
        }
    }, [hasPreviousPage, isFetchingPreviousPage, fetchPreviousPage]);

    if (!data) {
        return (
            <div className="flex-1 h-screen flex flex-col bg-[#0a0a0b]">
                <ChatHeader avatarUrl={partnerAvatar} name={partnerName} />
                <MessageInput onSend={handleSend} />
            </div>
        );
    }

    return (
        <div className="flex-1 h-screen flex flex-col bg-[#0a0a0b]">
            <ChatHeader avatarUrl={partnerAvatar} name={partnerName} />

            <Virtuoso
                ref={virtuosoRef}
                className="flex-1"
                data={flatItems}
                computeItemKey={(_, { msg }) => msg.uuid}
                firstItemIndex={firstItemIndex}
                initialTopMostItemIndex={{ index: 'LAST' }}
                startReached={loadMore}
                increaseViewportBy={{ top: 600, bottom: 0 }}
                alignToBottom
                followOutput
                skipAnimationFrameInResizeObserver
                scrollerRef={scrollerCbRef}
                itemContent={(_, { msg, isFirst, isLast }) => {
                    const isOwn = msg.user_uuid == userUUID;
                    return (
                        <div className={`px-5 ${!isFirst ? 'pt-0.5' : 'pt-3.5'}`}>
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
                }}
                context={{ hasPreviousPage, partnerName }}
                components={{ Header }}
            />

            <MessageInput onSend={handleSend} />
        </div>
    );
};

const ChatPage = () => {
    const { uuid: chatUUID } = useParams();

    return <ChatRoom key={chatUUID} chatUUID={chatUUID!} />;
};

export default ChatPage;
