import { createContext, useState, useEffect } from 'react';

// Create the AuthContext
export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [staffId, setStaffId] = useState(null);
  const [name, setName] = useState('');
  const [role, setRole] = useState('');

  // Retrieve auth state from localStorage on initial load
  useEffect(() => {
    const storedAuthState = localStorage.getItem('isAuthenticated');
    const storedStaffId = localStorage.getItem('staffId');
    const storedName = localStorage.getItem('name');
    const storedRole = localStorage.getItem('role');
    if (storedAuthState === 'true') {
      setIsAuthenticated(true);
      setStaffId(storedStaffId);
      setName(storedName);
      setRole(storedRole);
    }
  }, []);

  const login = (uid, name, role) => {
    setIsAuthenticated(true);
    setStaffId(uid);
    setName(name);
    setRole(role);

    // Store the correct userData in localStorage
    localStorage.setItem('isAuthenticated', 'true');
    localStorage.setItem('staffId', uid); // Correctly save the uid
    localStorage.setItem('name', name); // Correctly save the name
    localStorage.setItem('role', role); // Correctly save
  };

  const logout = () => {
    setIsAuthenticated(false);
    setStaffId(null);
    setName('');
    setRole('');
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('staffId');
    localStorage.removeItem('name');
    localStorage.removeItem('role');
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout, name, staffId, role }}>
      {children}
    </AuthContext.Provider>
  );
};
