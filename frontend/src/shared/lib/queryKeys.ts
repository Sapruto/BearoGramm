export const queryKeys = {
    messagesAll: ['messages'] as const,
    messagesChat: (chatUUID: string) => [...queryKeys.messagesAll, chatUUID] as const,
    personalChats: ['personal-chats'] as const,
    myProfile: ['my-profile'] as const,
    chatPartnerAll: ['chat-partner'] as const,
    chatPartner: (chatUUID: string) => [...queryKeys.chatPartnerAll, chatUUID] as const,
}