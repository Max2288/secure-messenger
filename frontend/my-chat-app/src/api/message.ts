import axios from 'axios';
import config from '../config';

export const fetchMessagesByChat = (chatId: number, token: string) =>
  axios.get(`${config.apiBaseUrl}/message/by-chat/${chatId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });

export const sendMessage = (chatId: number, senderId: number, message: string, token: string) =>
  axios.post(`${config.apiBaseUrl}/message`, {
    chat_id: chatId,
    sender_id: senderId,
    encrypted_payload: message,
  }, {
    headers: { Authorization: `Bearer ${token}` },
  });

export const markMessagesAsRead = (messageIds: number[], userId: number, token: string) =>
  axios.post(`${config.apiBaseUrl}/message-read/bulk`, {
    message_ids: messageIds,
    user_id: userId,
  }, {
    headers: { Authorization: `Bearer ${token}` },
  });
