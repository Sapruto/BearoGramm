const DAY_MS = 86_400_000;

export type FormattedTime = {
    label: string;
    fullDate: string;
    iso: string;
};

const getConnector = (date: Date): string => {
    const parts = new Intl.DateTimeFormat(undefined, {
        dateStyle: 'long',
        timeStyle: 'short',
    }).formatToParts(date);

    const hourIndex = parts.findIndex((p) => p.type === 'hour');
    const before = parts[hourIndex - 1];

    return before?.type === 'literal' ? before.value.trim().match(/\p{L}+$/u)?.[0] ?? '' : '';
};

export const formatMessageTime = (timestamp: number, now: Date = new Date()): FormattedTime => {
    const date = new Date(timestamp);

    const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
    const startOfDate = new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime();
    const days = Math.round((startOfToday - startOfDate) / DAY_MS);

    const rtf = new Intl.RelativeTimeFormat(undefined, { numeric: 'auto' });
    const timeLabel = new Intl.DateTimeFormat(undefined, { hour: 'numeric', minute: '2-digit' }).format(date);

    let label: string;

    if (days <= 0) {
        label = timeLabel;
    } else if (days <= 7) {
        label = [rtf.format(-days, 'day'), getConnector(date), timeLabel].filter(Boolean).join(' ');
    } else if (days <= 31) {
        label = rtf.format(-days, 'day');
    } else {
        let months = (now.getFullYear() - date.getFullYear()) * 12 + (now.getMonth() - date.getMonth());
        if (now.getDate() < date.getDate()) months -= 1;
        months = Math.max(1, months);

        label = months < 12
            ? rtf.format(-months, 'month')
            : rtf.format(-Math.floor(months / 12), 'year');
    }

    const fullDate = new Intl.DateTimeFormat(undefined, {
        dateStyle: 'full',
        timeStyle: 'medium',
    }).format(date);

    return { label, fullDate, iso: date.toISOString() };
};