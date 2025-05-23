CREATE SCHEMA IF NOT EXISTS messenger_encrypted;

-- Пользователи
CREATE TABLE messenger_encrypted."user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    public_key TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Чаты
CREATE TABLE messenger_encrypted."chat" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    chat_type VARCHAR(10) NOT NULL CHECK (chat_type IN ('private', 'group')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Участники чатов
CREATE TABLE messenger_encrypted."chat_participant" (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER NOT NULL REFERENCES messenger_encrypted."chat"(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES messenger_encrypted."user"(id) ON DELETE CASCADE,
    left_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Сообщения
CREATE TABLE messenger_encrypted."message" (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER NOT NULL REFERENCES messenger_encrypted."chat"(id) ON DELETE CASCADE,
    sender_id INTEGER NOT NULL REFERENCES messenger_encrypted."user"(id) ON DELETE CASCADE,
    encrypted_payload BYTEA NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Прочитанные сообщения
CREATE TABLE messenger_encrypted."message_read" (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL REFERENCES messenger_encrypted."message"(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES messenger_encrypted."user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (message_id, user_id)
);

-- Индекс по сообщениям
CREATE INDEX idx_message_chat_created_at ON messenger_encrypted."message" (chat_id, created_at);
