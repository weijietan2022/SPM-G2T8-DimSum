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

  // Retrieve auth state from localStorage on initial load
  useEffect(() => {
    const storedAuthState = localStorage.getItem('isAuthenticated');
    const storedStaffId = localStorage.getItem('staffId');
    const storedName = localStorage.getItem('name');
    const storedRole = localStorage.getItem('role');
    const storedManagerId = localStorage.getItem('storedManagerId');
    const storedDept = localStorage.getItem('dept');

    if (storedAuthState === 'true') {
      setIsAuthenticated(true);
      setStaffId(storedStaffId);
      setName(storedName);
      setRole(storedRole);
      setManagerId(storedManagerId);
      setDept(storedDept);
    }
  }, []);

  const login = (uid, name, role, managerId, dept) => {
    setIsAuthenticated(true);
    setStaffId(uid);
    setName(name);
    setRole(role);
    setManagerId(managerId);
    setDept(dept);


    // Store the correct userData in localStorage
    localStorage.setItem('isAuthenticated', 'true');
    localStorage.setItem('staffId', uid);
    localStorage.setItem('name', name);
    localStorage.setItem('role', role); 
    localStorage.setItem('managerId', managerId);
    localStorage.setItem('dept', dept);
  };

  const logout = () => {
    setIsAuthenticated(false);
    setStaffId(null);
    setName('');
    setRole('');
    setManagerId('');
    setDept('');
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('staffId');
    localStorage.removeItem('name');
    localStorage.removeItem('role');
    localStorage.removeItem('managerId');
    localStorage.removeItem('dept');
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout, name, staffId, role, managerId, dept }}>
      {children}
    </AuthContext.Provider>
  );
};
