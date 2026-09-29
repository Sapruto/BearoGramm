import ReconnectingWebSocket from 'reconnecting-websocket';
import { useAuthStore } from '../../store/authStore';
import type { MessageEntity } from './messages';

export type WSMessage =
    | { type: 'message_created'; data: MessageEntity }
    | { type: 'message_updated'; data: MessageEntity }
    | { type: 'message_deleted'; data: MessageEntity }
    | {
        type: 'typing';
        data: { user_uuid: string, chat_uuid: string }
    }
    | {
        type: 'user_online';
        data: { user_uuid: string, online: boolean }
    }

type WSHandler = (msg: WSMessage) => void;

class ChatSocket {
    private ws: ReconnectingWebSocket | null = null;
    private handlers = new Set<WSHandler>();
    private url: string;

    constructor(url: string) {
        this.url = url;
    }

    connect() {
        if (this.ws) return;

        this.ws = new ReconnectingWebSocket(this.url, [], {
            minReconnectionDelay: 1000,
            maxReconnectionDelay: 15000,
            reconnectionDelayGrowFactor: 1.5,
            maxRetries: Infinity,
        });

        this.ws.onmessage = (event: MessageEvent) => {
            try {
                const data: WSMessage = JSON.parse(event.data);
                this.handlers.forEach((h) => h(data));
            } catch (e) {
                console.error('Failed to parse WS message', e);
            }
        };

        this.ws.onopen = this.handleOpen;

        this.ws.onerror = (event) => {
            console.error('WS error', event);
        };
    }

    disconnect() {
        this.ws?.close();
        this.ws = null;
        this.handlers.clear();
    }

    subscribe(handler: WSHandler) {
        this.handlers.add(handler);
        return () => this.handlers.delete(handler);
    }

    send(data: unknown) {
        if (this.ws?.readyState === this.ws?.OPEN) {
            this.ws?.send(JSON.stringify(data));
        } else {
            console.warn('WS not open, message dropped', data);
        }
    }

    private handleOpen = () => {
        this.send({ "auth": useAuthStore.getState().token })
    }
}

export const chatSocket = new ChatSocket(import.meta.env.VITE_WS_URL);