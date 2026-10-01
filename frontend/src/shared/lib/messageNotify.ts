import { useAuthStore } from "../../store/authStore";
import type { MessageEntity } from "../api/messages";
import type { GetChatPartnerResponse } from "../api/personal";
import { queryClient } from "../api/queryClient";
import { queryKeys } from "./queryKeys";


const messageNotifySound = new Audio('/messageNotifySound.mp3');

export function messageNotify(chatUUID: string | undefined, msg: MessageEntity) {
    if (msg.user_uuid === useAuthStore.getState().userUUID)
        return;

    if (document.hasFocus() && msg.chat_uuid === chatUUID)
        return;

    const partnerProfileData = queryClient.getQueryData(queryKeys.chatPartner(msg.chat_uuid)) as GetChatPartnerResponse | undefined;

    if (Notification.permission === 'granted') {
        const notification = new Notification((partnerProfileData?.partner_profile.name) || "New message", {
            body: msg.message_text,
            icon: partnerProfileData?.partner_profile.avatar_url || "/favicon.ico",
            tag: msg.chat_uuid,
        });

        notification.onclick = () => {
            window.focus();
            notification.close();
        };
    }

    messageNotifySound.play();
}