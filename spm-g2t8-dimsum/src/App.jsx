import { useState } from 'react';
import './css/App.css';
import Navbar from './components/Navbar';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import WFHCalendar from './components/Calendar';
import YourRequests from './components/YourRequests';  // Import your other components

const events = [
  { id: 1, teamMember: 'John Doe', start: new Date(2024, 8, 20), end: new Date(2024, 8, 20), status: 'WFH' },
  { id: 2, teamMember: 'Jane Doe', start: new Date(2024, 8, 21), end: new Date(2024, 8, 21), status: 'office' },
  { id: 3, teamMember: 'Jack', start: new Date(2024, 8, 21), end: new Date(2024, 8, 21), status: 'WFH' },
  { id: 4, teamMember: 'Jolene', start: new Date(2024, 8, 21), end: new Date(2024, 8, 21), status: 'WFH' },
  // More events here
];

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
          <Route path="/calendar" element={<><Navbar onLogout={handleLogout} /><WFHCalendar events={events}/></>} />
        </>
      ) : (
        <Route path="*" element={<Navigate to="/login" />} />
      )}
    </Routes>
  );
};

export default App;
