import { useCallback, useRef, useState } from "react";
import type { VirtuosoHandle } from "react-virtuoso";
import { Virtuoso } from "react-virtuoso";
import ChatMessage from "./ChatMessage";
import { ChatSkeleton } from "./ChatSkeleton";

interface Message {
    id: number;
    author: string;
    text: string;
}

function createMessage(id: number, author: string, text: string): Message {
    return { id: id, author, text: text + ` (${id})` };
}

function generateInitialMessages(count: number): Message[] {
    return Array.from({ length: count }, (_, i) =>
        createMessage(i, "User" + (i % 2), `Сообщение #${i + 1}`)
    );
}

function fetchOlderMessages(beforeId: number, count: number): Promise<Message[]> {
    return new Promise((resolve) => {
        if (beforeId > 100) {
            resolve([]);
        }

        setTimeout(() => {
            const older = Array.from({ length: count }, (_, i) => {
                const num = beforeId + i;
                return createMessage(num, "User" + (num % 2), `Сообщение #${num + 1}`);
            });
            resolve(older);
        }, 1000);
    });
}

const START_COUNT = 30;

export default function ChatList() {
    const [messages, setMessages] = useState<Message[]>(() =>
        generateInitialMessages(START_COUNT)
    );
    const [hasMore, setHasMore] = useState(true);

    const virtuosoRef = useRef<VirtuosoHandle>(null);

    const [firstItemIndex, setFirstItemIndex] = useState(10000);

    const loadOlderMessages = useCallback(() => {
        if (!hasMore) return;

        const oldestId = messages[messages.length - 1]?.id ?? 0;

        fetchOlderMessages(oldestId + 1, 20).then((older) => {
            if (older.length === 0) {
                setHasMore(false);
                return;
            }

            setFirstItemIndex((prev) => prev - older.length);
            setMessages((prev) => [...prev, ...older]);
        });
    }, [messages, hasMore]);


    const addNewMessage = useCallback(() => {
        const firstId = messages[0]?.id ?? 0;

        setMessages((prev) => [
            createMessage(firstId - 1, "User0", `Новое сообщение ${Date.now()}`),
            ...prev,
        ]);

        requestAnimationFrame(() => {
            virtuosoRef.current?.scrollToIndex({
                index: "LAST",
                align: "end",
                behavior: "smooth",
            });
        });
    }, [messages]);

    const messages2 = messages.toReversed()

    return (
        <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
            <div style={{ flex: 1 }}>
                <Virtuoso
                    ref={virtuosoRef}
                    style={{ height: "100%" }}
                    data={messages2}
                    firstItemIndex={firstItemIndex}
                    initialTopMostItemIndex={messages2.length - 1}
                    startReached={loadOlderMessages}
                    followOutput="smooth"
                    alignToBottom
                    itemContent={(_, message) => (
                        <ChatMessage
                            text={message.text}
                            time="67:69"
                            isOwn={message.author === "User0"}
                            isFirst={true}
                            isLast={true}
                        />
                    )}
                    components={{
                        Header: () =>
                            hasMore ? (
                                <ChatSkeleton />
                            )
                                : (
                                    <div style={{ padding: 12, color: "#999" }}>
                                        This is the beginning of your direct message history with <strong>{"USER"}</strong>.
                                    </div>
                                )
                    }}
                />
            </div>

            <button onClick={addNewMessage} style={{ padding: 12 }}>
                Отправить новое сообщение
            </button>
        </div>
    );
}