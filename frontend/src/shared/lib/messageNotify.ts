import { useAuthStore } from "../../store/authStore";
import type { MessageEntity } from "../api/messages";
import type { Profile } from "../api/profile";


const messageNotifySound = new Audio('/messageNotifySound.mp3');

export function messageNotify(chatUUID: string | undefined, partnerProfile: Profile | undefined, msg: MessageEntity) {
    if (msg.user_uuid === useAuthStore.getState().userUUID)
        return;

    if (document.hasFocus() && msg.chat_uuid === chatUUID)
        return;

    if (Notification.permission === 'granted') {
        const notification = new Notification((msg.chat_uuid === chatUUID && partnerProfile?.name) || "New message", {
            body: msg.message_text,
            icon: '/favicon.ico',
            tag: msg.chat_uuid,
        });

        notification.onclick = () => {
            window.focus();
            notification.close();
        };
    }

    messageNotifySound.play();
}