import { useState, useContext } from 'react';
import './css/App.css';
import Navbar from './components/Navbar';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import WFHCalendar from './components/Calendar';
import YourRequests from './components/YourRequests';  
import { AuthContext } from './context/AuthContext';
import ApplicationForm from './components/ApplicationForm';
import ViewApplication from './components/ViewApplication';

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
];

const App = () => {
  // const [isAuthenticated, setIsAuthenticated] = useState(false);
  const { isAuthenticated, logout } = useContext(AuthContext);  

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
  };

  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      {isAuthenticated ? (
        <>
          <Route path="/" element={<Navigate to="/calendar" />} />
          <Route path="/yourrequests" element={<><Navbar/><YourRequests /></>} />
          <Route path="/calendar" element={<><Navbar  /><WFHCalendar events={events}/></>} />
        </>
      ) : (
        <Route path="*" element={<Navigate to="/login" />} />
      )}
        <Route path="/applicationform" element={<><Navbar/><ApplicationForm /></>} />
        <Route path="/view-application" element={<><Navbar /><ViewApplication /></>} />
    </Routes>
  );
};

export default App;
