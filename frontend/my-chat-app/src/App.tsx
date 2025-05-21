import React, { useState } from 'react';
import Login from './pages/Login/Login';
import Register from './pages/Register/Register';
import Chat from './pages/Chat/Chat';

const App: React.FC = () => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));
  const [showRegister, setShowRegister] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setToken(null);
  };

  return (
    <div>
      {!token ? (
        showRegister ? (
          <Register onLogin={setToken} onSwitchToLogin={() => setShowRegister(false)} />
        ) : (
          <Login onLogin={setToken} onSwitchToRegister={() => setShowRegister(true)} />
        )
      ) : (
        <Chat token={token} onLogout={handleLogout} />
      )}
    </div>
  );
};

export default App;
