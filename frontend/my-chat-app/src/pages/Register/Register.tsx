import React, { useState } from 'react';
import axios from 'axios';
import styles from './Register.module.css';
import { hashPassword } from '../../utils/security/hashPassword';
import { generateKeyPair } from '../../utils/security/generateKeyPair';

interface RegisterProps {
  onLogin: (token: string) => void;
  onSwitchToLogin: () => void;
}

const Register: React.FC<RegisterProps> = ({ onLogin, onSwitchToLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleRegister = async () => {
    try {
      const passwordHash = await hashPassword(password);
      const publicKey = await generateKeyPair();

      await axios.post('http://localhost:1026/api/v1/user', {
        username,
        password_hash: passwordHash,
        public_key: publicKey,
      });

      const loginResponse = await axios.post('http://localhost:1026/api/v1/user/login', {
        username,
        password_hash: passwordHash,
      });

      const token = loginResponse.data.access_token;

      if (!token) {
        setError('Token not returned from login response');
        return;
      }

      localStorage.setItem('access_token', token);
      onLogin(token);
    } catch (err) {
      console.error('Registration or login failed:', err);
      setError('Ошибка регистрации или входа. Попробуйте ещё раз.');
    }
  };

  return (
    <div className={styles.modal}>
      <div className={styles.card}>
        <h2 className={styles.title}>Регистрация</h2>
        <input
          type="text"
          placeholder="Имя пользователя"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className={styles.input}
        />
        <input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className={styles.input}
        />
        <button onClick={handleRegister} className={styles.button}>
          Зарегистрироваться
        </button>
        {error && <p className={styles.error}>{error}</p>}
        <p className={styles.switch}>
          Уже есть аккаунт?{' '}
          <span onClick={onSwitchToLogin} className={styles.link}>
            Войти
          </span>
        </p>
      </div>
    </div>
  );
};

export default Register;
