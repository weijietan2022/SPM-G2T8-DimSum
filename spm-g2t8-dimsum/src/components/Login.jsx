import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';  // Import the context
import '../css/Login.css';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);  // Access the login method from context

  const API_URL = import.meta.env.VITE_API_URL_5001;

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch(API_URL+'/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          password: password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccessMessage(data.message);  // Set success message from Flask
        setErrorMessage('');  // Clear error message
        const { uid, name, role, mid, dept, position } = data;
        login(uid, name, role, mid, dept, position);  // Call the login function from context
        navigate('/calendar');  // Redirect to the calendar page
      } else {
        setErrorMessage(data.message);  // Set error message from Flask
        setSuccessMessage('');  // Clear success message
      }
    } catch (error) {
      setErrorMessage('An error occurred. Please try again.');
    }
  };

  return (
    <div className="login-container">
      <h1>ALL-IN-ONE WFH PORTAL</h1>
      <div className="login-form">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              required
            />
          </div>

          {errorMessage && <p className="error-message">{errorMessage}</p>}
          {successMessage && <p className="success-message">{successMessage}</p>}

          <button type="submit" className="login-button">Login</button>
        </form>
      </div>
    </div>
  );
};

export default Login;
