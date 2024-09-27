import { useState } from 'react';
import './css/App.css';
import Navbar from './components/Navbar';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Calendar from './components/Calendar';
import YourRequests from './components/YourRequests';  // Import your other components

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(true);

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
  };

  return (
    <Routes>
      <Route path="/login" element={<Login onLogin={handleLogin} />} />

      {isAuthenticated ? (
        <>
          <Route path="/" element={<Navigate to="/calendar" />} />
          <Route path="/yourrequests" element={<><Navbar onLogout={handleLogout} /><YourRequests /></>} />
          <Route path="/calendar" element={<><Navbar onLogout={handleLogout} /><Calendar /></>} />
        </>
      ) : (
        <Route path="*" element={<Navigate to="/login" />} />
      )}
    </Routes>
  );
};

export default App;
