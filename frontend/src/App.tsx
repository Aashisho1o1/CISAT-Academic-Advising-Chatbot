import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate, Link } from 'react-router-dom';
import Login from './components/Login';
import AdvisingSheet from './components/AdvisingSheet';
import JourneyMap from './components/JourneyMap';
import Chatbot from './components/Chatbot';
import { getCurrentUser, logout as apiLogout, User } from './api';
import './App.css';

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const bootstrapSession = async () => {
      try {
        const response = await getCurrentUser();
        setUser(response.data.user);
      } catch {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    void bootstrapSession();
  }, []);

  const handleLogin = (userData: User) => {
    setUser(userData);
  };

  const handleLogout = async () => {
    try {
      await apiLogout();
    } catch {
      // Even if backend logout fails, clear local session state.
    } finally {
      setUser(null);
    }
  };

  if (loading) {
    return <div className="App">Loading...</div>;
  }

  return (
    <Router>
      <div className="App">
        <nav>
          {user ? (
            <>
              <span>Welcome, {user.username}!</span>
              <Link to="/chatbot">Chatbot</Link>
              <Link to="/journey">Journey Map</Link>
              <Link to="/advising">Advising Sheet</Link>
              <button onClick={handleLogout}>Logout</button>
            </>
          ) : (
            <Link to="/login">Login</Link>
          )}
        </nav>
        <Routes>
          <Route path="/chatbot" element={user ? <Chatbot /> : <Navigate to="/login" />} />
          <Route path="/journey" element={user ? <JourneyMap /> : <Navigate to="/login" />} />
          <Route path="/advising" element={user ? <AdvisingSheet /> : <Navigate to="/login" />} />
          <Route path="/login" element={user ? <Navigate to="/advising" /> : <Login onLogin={handleLogin} />} />
          <Route path="/" element={<Navigate to={user ? '/advising' : '/login'} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
