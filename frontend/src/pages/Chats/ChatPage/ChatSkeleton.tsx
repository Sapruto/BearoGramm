import { ChatMessageSkeleton } from "./ChatMessageSkeleton";

type Bubble = {
    isOwn: boolean;
    width: number;
    lines: 1 | 2 | 3;
};

const SCENARIO: Bubble[] = [
    { isOwn: false, width: 220, lines: 2 },
    { isOwn: false, width: 120, lines: 1 },
    { isOwn: false, width: 260, lines: 3 },
    { isOwn: true, width: 180, lines: 1 },
    { isOwn: true, width: 240, lines: 2 },
    { isOwn: false, width: 150, lines: 1 },
    { isOwn: true, width: 100, lines: 1 },
];

const LINE_HEIGHT = 20;
const PADDING_Y = 16;

export const ChatSkeleton = () => (
    <div className="flex flex-col gap-2" aria-busy aria-hidden>
        {SCENARIO.map((bubble, i) => {
            const prev = SCENARIO[i - 1];
            const next = SCENARIO[i + 1];
            const isFirst = !prev || prev.isOwn !== bubble.isOwn;
            const isLast = !next || next.isOwn !== bubble.isOwn;

            return (
                <ChatMessageSkeleton
                    key={i}
                    isFirst={isFirst}
                    isLast={isLast}
                    width={bubble.width}
                    height={bubble.lines * LINE_HEIGHT + PADDING_Y}
                />
            );
        })}
    </div>
);