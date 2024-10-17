import { createContext, useState, useEffect } from 'react';

// Create the AuthContext
export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [staffId, setStaffId] = useState(null);
  const [name, setName] = useState('');
  const [role, setRole] = useState('');
  const [managerId, setManagerId] = useState('');
  const [dept, setDept] = useState('');
  const [position, setPosition] = useState('');


  // Retrieve auth state from localStorage on initial load
  useEffect(() => {
    const storedAuthState = localStorage.getItem('isAuthenticated');
    const storedStaffId = localStorage.getItem('staffId');
    const storedName = localStorage.getItem('name');
    const storedRole = localStorage.getItem('role');
    const storedManagerId = localStorage.getItem('storedManagerId');
    const storedDept = localStorage.getItem('dept');
    const storedPosition = localStorage.getItem('position');


    if (storedAuthState === 'true') {
      setIsAuthenticated(true);
      setStaffId(storedStaffId);
      setName(storedName);
      setRole(storedRole);
      setManagerId(storedManagerId);
      setDept(storedDept);
      setPosition(storedPosition);
    }
  }, []);

  const login = (uid, name, role, managerId, dept,position) => {
    setIsAuthenticated(true);
    setStaffId(uid);
    setName(name);
    setRole(role);
    setManagerId(managerId);
    setDept(dept);
    setPosition(position);


    // Store the correct userData in localStorage
    localStorage.setItem('isAuthenticated', 'true');
    localStorage.setItem('staffId', uid);
    localStorage.setItem('name', name);
    localStorage.setItem('role', role); 
    localStorage.setItem('managerId', managerId);
    localStorage.setItem('dept', dept);
    localStorage.setItem('position', position);
  };

  const logout = () => {
    setIsAuthenticated(false);
    setStaffId(null);
    setName('');
    setRole('');
    setManagerId('');
    setDept('');
    setPosition('')
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('staffId');
    localStorage.removeItem('name');
    localStorage.removeItem('role');
    localStorage.removeItem('managerId');
    localStorage.removeItem('dept');
    localStorage.removeItem('position');
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout, name, staffId, role, managerId, dept, position }}>
      {children}
    </AuthContext.Provider>
  );
};
