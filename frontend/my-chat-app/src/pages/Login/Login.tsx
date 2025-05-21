import React, { useState } from 'react';
import axios from 'axios';
import styles from './Login.module.css';
import { hashPassword } from '../../utils/security/hashPassword';

interface LoginProps {
  onLogin: (token: string) => void;
  onSwitchToRegister: () => void;
}

const Login: React.FC<LoginProps> = ({ onLogin, onSwitchToRegister }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async () => {
    try {
      const passwordHash = await hashPassword(password);
      const response = await axios.post('http://localhost:1026/api/v1/user/login', {
        username,
        password_hash: passwordHash,
      });

      const token = response.data.access_token;

      if (!token) {
        setError('Token not returned from server');
        return;
      }

      localStorage.setItem('access_token', token);
      onLogin(token);
    } catch (error: any) {
      console.error('Login failed:', error);
      setError('Неверный логин или пароль.');
    }
  };

  return (
    <div className={styles.modal}>
      <div className={styles.card}>
        <h2 className={styles.title}>Вход</h2>
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
        <button onClick={handleLogin} className={styles.button}>
          Войти
        </button>
        {error && <p className={styles.error}>{error}</p>}
        <p className={styles.switch}>
          Нет аккаунта?{' '}
          <span onClick={onSwitchToRegister} className={styles.link}>
            Зарегистрируйтесь
          </span>
        </p>
      </div>
    </div>
  );
};

export default Login;
