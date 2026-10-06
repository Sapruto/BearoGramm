import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState, type RefObject } from 'react';
import { useParams } from 'react-router-dom';
import { Virtuoso, type VirtuosoHandle } from 'react-virtuoso';
import type { MessageEntity } from '../../../shared/api/messages';
import { useGetMessages } from '../../../shared/hooks/messages/useGetMessages';
import { useSendMessage } from '../../../shared/hooks/messages/useSendMessage';
import { useGetChatPartner } from '../../../shared/hooks/personal/useGetChatPartner';
import { useGetMyProfile } from '../../../shared/hooks/profile/useGetMyProfile';
import { useAuthStore } from '../../../store/authStore';
import ChatMessage from './ChatMessage';
import { ChatSkeleton } from './ChatSkeleton';
import MessageInput from './MessageInput';
import ChatHeader from './ChatHeader';
import { ChatHeaderSkeleton } from './ChatHeaderSkeleton';

const INITIAL_COUNT = 30;
const HISTORY_COUNT = 20;

const GROUP_WINDOW_MS = 5 * 60 * 1000;
const START_INDEX = 100000;

const HistoryBeginLabel = ({ name }: { name?: string }) => (
    <div className="px-5 py-3 text-[#999]">
        This is the beginning of your direct message history with <strong>{name ?? 'Loading...'}</strong>.
    </div>
);

type HeaderContext = {
    hasPreviousPage: boolean;
    partnerName: string | undefined;
    scrollerRef: RefObject<HTMLElement | null>;
};

const Header = ({ context }: { context?: HeaderContext }) => {
    const isHistoryEnd = !context?.hasPreviousPage;
    const rootRef = useRef<HTMLDivElement | null>(null);
    const prevHeightRef = useRef<number | null>(null);

    useLayoutEffect(() => {
        const el = rootRef.current;
        if (!el) return;
        const h = el.offsetHeight;
        const prev = prevHeightRef.current;
        prevHeightRef.current = h;
        if (prev === null || prev === h) return;
        const sc = context?.scrollerRef.current;
        if (sc) sc.scrollTop += h - prev;
    });

    return (
        <div ref={rootRef}>
            {isHistoryEnd ? <HistoryBeginLabel name={context?.partnerName} /> : null}
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
        const map = new Map<string, MessageEntity>();
        for (const page of data?.pages ?? []) {
            for (const msg of page.messages) {
                map.set(msg.uuid, msg);
            }
        }
        return [...map.values()].sort((a, b) => Date.parse(a.created_at) - Date.parse(b.created_at));
    }, [data]);

    const messageGroups = useMemo(() => {
        return messages.reduce<MessageEntity[][]>((acc, msg, i, arr) => {
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

    const prevCountRef = useRef<number | null>(null);
    const scrollerRef = useRef<HTMLElement | null>(null);
    const settleBottom = useCallback(() => {
        const sc = scrollerRef.current;
        if (!sc) return;
        const gap = sc.scrollHeight - sc.scrollTop - sc.clientHeight;
        if (gap <= 0 || gap > 300) return;
        sc.scrollTop = sc.scrollHeight;
    }, []);

    const snapLoopRef = useRef(0);
    const scrollerCbRef = useCallback((el: HTMLElement | Window | null) => {
        scrollerRef.current = el instanceof HTMLElement ? el : null;
        cancelAnimationFrame(snapLoopRef.current);
        if (!el) return;
        let n = 0;
        const tick = () => {
            settleBottom();
            if (++n < 30) snapLoopRef.current = requestAnimationFrame(tick);
        };
        snapLoopRef.current = requestAnimationFrame(tick);
    }, [settleBottom]);

    useEffect(() => {
        prevCountRef.current = flatItems.length;
        const list = scrollerRef.current?.querySelector('[data-item-index]')?.parentElement;
        const observer = new ResizeObserver(() => requestAnimationFrame(settleBottom));
        if (list) observer.observe(list);
        const raf = requestAnimationFrame(settleBottom);
        const stop = setTimeout(() => observer.disconnect(), 2000);
        return () => {
            observer.disconnect();
            cancelAnimationFrame(raf);
            clearTimeout(stop);
        };
    }, [flatItems.length, settleBottom]);

    useEffect(() => () => cancelAnimationFrame(snapLoopRef.current), []);

    const handleSend = (text: string) => {
        sendMessage({ chat_uuid: chatUUID, message_text: text, references: [] });
    };

    const loadMore = useCallback(() => {
        if (hasPreviousPage && !isFetchingPreviousPage) {
            fetchPreviousPage();
        }
    }, [hasPreviousPage, isFetchingPreviousPage, fetchPreviousPage]);

    if (!data) {
        return (
            <div className="flex-1 h-screen flex flex-col bg-[#0a0a0b]">
                <ChatHeaderSkeleton />
                <div className='flex-1 px-5 overflow-y-hidden'>
                    {new Array(10).fill(0).map(() => (
                        <ChatSkeleton />
                    ))}
                </div>
                <MessageInput onSend={handleSend} />
            </div>
        );
    }

    if (flatItems.length === 0) {
        return (
            <div className="flex-1 h-screen flex flex-col bg-[#0a0a0b]">
                <ChatHeader avatarUrl={partnerAvatar} name={partnerName} />
                <div className="flex-1 min-h-0">
                    <HistoryBeginLabel name={partnerName} />
                </div>
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
                                text={msg.message_text}
                                timestamp={Date.parse(msg.created_at)}
                                isOwn={isOwn}
                                avatarUrl={isOwn ? myProfile?.profile.avatar_url : partnerAvatar}
                                isFirst={isFirst}
                                isLast={isLast}
                                userUUID={msg.user_uuid}
                            />
                        </div>
                    );
                }}
                context={{ hasPreviousPage, partnerName, scrollerRef }}
                components={{ Header }}
                defaultItemHeight={60}
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
