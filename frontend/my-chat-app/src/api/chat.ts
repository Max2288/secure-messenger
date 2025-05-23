import axios from 'axios';
import config from '../config';

export const fetchChatsByUser = (userId: number, token: string) =>
  axios.get(`${config.apiBaseUrl}/chat/by-user/${userId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });

export const createChat = (name: string, token: string) =>
  axios.post(`${config.apiBaseUrl}/chat`, { name, chat_type: 'private' }, {
    headers: { Authorization: `Bearer ${token}` },
  });

export const addParticipant = (chatId: number, userId: number, token: string) =>
  axios.post(`${config.apiBaseUrl}/chat_participant`, { chat_id: chatId, user_id: userId }, {
    headers: { Authorization: `Bearer ${token}` },
  });
