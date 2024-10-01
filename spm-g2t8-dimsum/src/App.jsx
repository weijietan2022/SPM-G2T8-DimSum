import { useState } from 'react';
import './css/App.css';
import Navbar from './components/Navbar';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import WFHCalendar from './components/Calendar';
import YourRequests from './components/YourRequests';  // Import your other components

const events = [
  { wfh:[
    {name: 'Jack Sim', type:'am'},
    {name: 'Carrington', type: 'fullDay'},
    {name: 'Tony Lopez', type: 'fullDay'}
  ], 
    inOffice: [
    {name: 'Jack Sim', type:'pm'},
    {name: 'Aravind', type: 'fullDay'},
    ]}
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
