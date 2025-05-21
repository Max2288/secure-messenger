import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Centrifuge, Subscription } from 'centrifuge';
import styles from './Chat.module.css';

interface Message {
  id: number;
  sender_id: number;
  encrypted_payload: string;
  is_read?: boolean;
}

interface ChatProps {
  token: string;
  onLogout: () => void;
}

const getUserIdFromToken = (token: string): number | null => {
  try {
    const payloadBase64 = token.split('.')[1];
    const decoded = JSON.parse(atob(payloadBase64));
    return decoded.sub ? parseInt(decoded.sub) : null;
  } catch {
    return null;
  }
};

const Chat: React.FC<ChatProps> = ({ token, onLogout }) => {
  const userId = getUserIdFromToken(token);
  const [chats, setChats] = useState<any[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [message, setMessage] = useState('');
  const [activeChat, setActiveChat] = useState<number | null>(null);
  const [isAutoScrollEnabled, setIsAutoScrollEnabled] = useState(true);

  const centrifugeRef = useRef<Centrifuge | null>(null);
  const subscriptionRef = useRef<Subscription | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const messageListRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const fetchChats = async () => {
      try {
        const response = await axios.get(`http://localhost:1026/api/v1/chat/by-user/${userId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setChats(response.data);
      } catch (error) {
        console.error('Error fetching chats:', error);
      }
    };
    if (userId) fetchChats();
  }, [userId, token]);

  useEffect(() => {
    const initCentrifuge = async () => {
      try {
        const response = await axios.get(`http://localhost:1026/api/v1/message/centrifugo/token`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        const { token: centrifugoToken } = response.data;

        centrifugeRef.current = new Centrifuge(
          'wss://a085-18-153-55-148.ngrok-free.app/connection/websocket?format=json',
          { token: centrifugoToken }
        );

        centrifugeRef.current.connect();
      } catch (error) {
        console.error('Error initializing Centrifuge:', error);
      }
    };

    if (!centrifugeRef.current && token) {
      initCentrifuge();
    }

    return () => {
      centrifugeRef.current?.disconnect();
    };
  }, [token]);

  useEffect(() => {
    const setup = async () => {
      if (activeChat && centrifugeRef.current) {
        try {
          const response = await axios.get(`http://localhost:1026/api/v1/message/by-chat/${activeChat}`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          setMessages(response.data);

          const channel = `chat_${activeChat}`;
          const sub = centrifugeRef.current.newSubscription(channel);

          sub.on('publication', (ctx) => {
            const newMsg = {
              id: ctx.data.id,
              sender_id: ctx.data.sender,
              encrypted_payload: ctx.data.message,
            };

            setMessages((prev) => [...prev, newMsg]);
          });

          sub.subscribe();
          subscriptionRef.current = sub;
        } catch (error) {
          console.error('Error setting up chat subscription:', error);
        }
      }
    };

    if (activeChat) setup();

    return () => {
      subscriptionRef.current?.unsubscribe();
      subscriptionRef.current = null;
    };
  }, [activeChat, token]);

  useEffect(() => {
    if (isAutoScrollEnabled) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isAutoScrollEnabled]);

  useEffect(() => {
    const inputField = document.getElementById('chatInput');
    if (!inputField) return;

    const handleFocus = async () => {
      if (!userId || messages.length === 0) return;

      const unreadIds = messages
        .filter((msg) => msg.sender_id !== userId)
        .map((msg) => msg.id);

      if (unreadIds.length > 0) {
        try {
          await axios.post(
            'http://localhost:1026/api/v1/message-read/bulk',
            {
              message_ids: unreadIds,
              user_id: userId,
            },
            {
              headers: { Authorization: `Bearer ${token}` },
            }
          );
          console.log('Marked messages as read:', unreadIds);
        } catch (error) {
          console.error('Error marking messages as read:', error);
        }
      }
    };

    inputField.addEventListener('focus', handleFocus);
    return () => inputField.removeEventListener('focus', handleFocus);
  }, [messages, userId, token]);

  const handleSendMessage = async () => {
    if (message && activeChat) {
      try {
        await axios.post(
          'http://localhost:1026/api/v1/message',
          {
            chat_id: activeChat,
            sender_id: userId,
            encrypted_payload: message,
          },
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        setMessage('');
      } catch (error) {
        console.error('Error sending message:', error);
      }
    }
  };

  const handleScroll = () => {
    const container = messageListRef.current;
    if (!container) return;
    const isAtBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 50;
    setIsAutoScrollEnabled(isAtBottom);
  };

  const handleCreateChat = async () => {
    const chatName = prompt('Enter name for the new chat:');
    if (!chatName || !userId) return;

    try {
      const response = await axios.post(
        'http://localhost:1026/api/v1/chat',
        { name: chatName, chat_type: 'private' },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const newChat = response.data;
      setChats((prev) => [...prev, newChat]);

      await axios.post(
        `http://localhost:1026/api/v1/chat_participant`,
        { chat_id: newChat.id, user_id: userId },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const secondUserId = prompt('Enter ID of another user to add:');
      if (secondUserId) {
        await axios.post(
          `http://localhost:1026/api/v1/chat-participant`,
          { chat_id: newChat.id, user_id: parseInt(secondUserId) },
          { headers: { Authorization: `Bearer ${token}` } }
        );
      }
    } catch (error) {
      console.error('Error creating chat or adding participants:', error);
    }
  };

  if (!userId) return <div>Ошибка: токен недействителен</div>;

  return (
    <div className={styles.chatContainer}>
      <div className={styles.sidebar}>
        <h3>Chats</h3>
        <button onClick={handleCreateChat} className={styles.createChatButton}>Create Chat</button>
        <button onClick={onLogout} className={styles.logoutButton}>Logout</button>
        <div className={styles.chatList}>
          {chats.map((chat) => (
            <div
              key={chat.id}
              onClick={() => setActiveChat(chat.id)}
              className={`${styles.chatItem} ${chat.id === activeChat ? styles.active : ''}`}
            >
              {chat.name}
            </div>
          ))}
        </div>
      </div>

      <div className={styles.mainChat}>
        {activeChat ? (
          <div className={styles.messageSection}>
            <div className={styles.messageList} ref={messageListRef} onScroll={handleScroll}>
              {messages.map((msg) => (
                  <div
                      key={msg.id}
                      className={`${styles.message} ${msg.sender_id === userId ? styles.sent : styles.received}`}
                      data-status={msg.sender_id === userId ? (msg.is_read ? '✓✓' : '✓') : ''} // <--- вот это
                  >
                    <strong>{msg.sender_id === userId ? 'You' : `User ${msg.sender_id}`}:</strong>{' '}
                    {msg.encrypted_payload}
                  </div>

              ))}
              <div ref={messagesEndRef}/>
            </div>
            <div className={styles.messageInput}>
              <input
                  id="chatInput"
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Type a message..."
                className={styles.inputField}
              />
              <button onClick={handleSendMessage} className={styles.sendButton}>Send</button>
            </div>
          </div>
        ) : (
          <div>📭 Выберите чат, чтобы начать общение</div>
        )}
      </div>
    </div>
  );
};

export default Chat;
