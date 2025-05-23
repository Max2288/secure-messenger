import React, { useState, useEffect, useRef } from 'react';
import { Centrifuge, Subscription } from 'centrifuge';
import styles from './Chat.module.css';
import { fetchChatsByUser, createChat, addParticipant } from '../../api/chat';
import { fetchMessagesByChat, sendMessage, markMessagesAsRead } from '../../api/message';
import { fetchCentrifugoToken, getCentrifugoWsUrl } from '../../api/centrifugo';

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
  const [isSending, setIsSending] = useState(false);

  const centrifugeRef = useRef<Centrifuge | null>(null);
  const subscriptionRef = useRef<Subscription | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const messageListRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!userId) return;
    fetchChatsByUser(userId, token)
      .then(res => setChats(res.data))
      .catch(err => console.error('Error fetching chats:', err));
  }, [userId, token]);

  useEffect(() => {
    const initCentrifuge = async () => {
      try {
        const { data } = await fetchCentrifugoToken(token);
        centrifugeRef.current = new Centrifuge(getCentrifugoWsUrl(), { token: data.token });
        centrifugeRef.current.connect();
      } catch (error) {
        console.error('Error initializing Centrifuge:', error);
      }
    };

    if (!centrifugeRef.current && token) {
      initCentrifuge();
    }

    return () => centrifugeRef.current?.disconnect();
  }, [token]);

  useEffect(() => {
    if (!activeChat || !centrifugeRef.current) return;

    fetchMessagesByChat(activeChat, token)
      .then(res => setMessages(res.data))
      .catch(err => console.error('Error fetching messages:', err));

    const channel = `chat_${activeChat}`;
    const sub = centrifugeRef.current.newSubscription(channel);
    sub.on('publication', ctx => {
      const newMsg = {
        id: ctx.data.id,
        sender_id: ctx.data.sender,
        encrypted_payload: ctx.data.message,
      };
      setMessages(prev => [...prev, newMsg]);
    });
    sub.subscribe();
    subscriptionRef.current = sub;

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
    const input = document.getElementById('chatInput');
    if (!input) return;

    const onFocus = async () => {
      if (!userId || messages.length === 0) return;
      const unreadIds = messages.filter(m => m.sender_id !== userId).map(m => m.id);
      if (unreadIds.length) {
        try {
          await markMessagesAsRead(unreadIds, userId, token);
        } catch (err) {
          console.error('Mark read error:', err);
        }
      }
    };

    input.addEventListener('focus', onFocus);
    return () => input.removeEventListener('focus', onFocus);
  }, [messages, userId, token]);

  const handleSendMessage = async () => {
    if (!message.trim() || !activeChat || !userId || isSending) return;
    setIsSending(true);
    try {
      await sendMessage(activeChat, userId, message.trim(), token);
      setMessage('');
    } catch (err) {
      console.error('Send message error:', err);
    } finally {
      setTimeout(() => setIsSending(false), 500);
    }
  };

  const handleScroll = () => {
    const container = messageListRef.current;
    if (!container) return;
    const atBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 50;
    setIsAutoScrollEnabled(atBottom);
  };

  const handleCreateChat = async () => {
    const chatName = prompt('Chat name?');
    if (!chatName || !userId) return;
    try {
      const { data: newChat } = await createChat(chatName, token);
      setChats(prev => [...prev, newChat]);
      await addParticipant(newChat.id, userId, token);

      const secondUserId = prompt('Enter ID of another user to add:');
      if (secondUserId) {
        const secondIdParsed = parseInt(secondUserId);
        if (!isNaN(secondIdParsed)) {
          await addParticipant(newChat.id, secondIdParsed, token);
        } else {
          alert('Invalid user ID');
        }
      }
    } catch (err) {
      console.error('Create chat error:', err);
    }
  };

  if (!userId) return <div>Invalid token</div>;

  return (
    <div className={styles.chatContainer}>
      <div className={styles.sidebar}>
        <h3>Chats</h3>
        <button onClick={handleCreateChat} className={styles.createChatButton}>Create Chat</button>
        <button onClick={onLogout} className={styles.logoutButton}>Logout</button>
        <div className={styles.chatList}>
          {chats.map(chat => (
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
              {messages.map(msg => (
                <div
                  key={msg.id}
                  className={`${styles.message} ${msg.sender_id === userId ? styles.sent : styles.received}`}
                  data-status={msg.sender_id === userId ? (msg.is_read ? '✓✓' : '✓') : ''}
                >
                  <strong>{msg.sender_id === userId ? 'You' : `User ${msg.sender_id}`}:</strong>{' '}
                  {msg.encrypted_payload}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            <div className={styles.messageInput}>
              <textarea
                id="chatInput"
                value={message}
                onChange={e => setMessage(e.target.value)}
                placeholder="Type a message..."
                className={styles.inputField}
                rows={2}
                onKeyDown={e => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
              />
              <button
                onClick={handleSendMessage}
                className={styles.sendButton}
                disabled={isSending || !message.trim()}
              >
                {isSending ? 'Sending...' : 'Send'}
              </button>
            </div>
          </div>
        ) : (
          <div>📭 Выбери чат чтобы начать общение</div>
        )}
      </div>
    </div>
  );
};

export default Chat;
