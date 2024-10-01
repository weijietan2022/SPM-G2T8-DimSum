import { createContext, useState, useEffect } from 'react';

// Create the AuthContext
export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [staffId, setStaffId] = useState(null);
  const [name, setName] = useState('');

  // Retrieve auth state from localStorage on initial load
  useEffect(() => {
    const storedAuthState = localStorage.getItem('isAuthenticated');
    const storedStaffId = localStorage.getItem('staffId');
    const storedName = localStorage.getItem('name');
    if (storedAuthState === 'true') {
      setIsAuthenticated(true);
      setStaffId(storedStaffId);
      setName(storedName);
    }
  }, []);

  const login = (uid, name) => {
    setIsAuthenticated(true);
    setStaffId(uid); // Set staffId from userData
    setName(name); // Set name from userData

    // Store the correct userData in localStorage
    localStorage.setItem('isAuthenticated', 'true');
    localStorage.setItem('staffId', uid); // Correctly save the uid
    localStorage.setItem('name', name); // Correctly save the name
  };

  const logout = () => {
    setIsAuthenticated(false);
    setStaffId(null);
    setName('');
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('staffId');
    localStorage.removeItem('name');
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout, name, staffId }}>
      {children}
    </AuthContext.Provider>
  );
};
