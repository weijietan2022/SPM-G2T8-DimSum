import React, {useContext} from 'react';
import { Navbar, Nav, Button, Container } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const WFHNavbar = () => {
  const {logout, name} = useContext(AuthContext); 
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login'); // Redirect to the login page
  };

  return (
    <Navbar bg="dark" variant="dark" expand="lg" className="px-3">
      <Container fluid>
        <Navbar.Brand className="fw-bold">ALL-IN-ONE WFH PORTAL
        </Navbar.Brand>
        <span className="text-light ms-2">Welcome, {name}!</span>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="ms-auto">
            <Link to="/yourrequests" className="nav-link">
              <Button variant="dark" className="me-2">
                Your Requests
              </Button>
            </Link>
            <Link to="/calendar" className="nav-link">
              <Button variant="dark" className="me-2">
                Team Schedule
              </Button>
            </Link>
            <Button variant="dark" onClick={handleLogout}>
              Logout
            </Button>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default WFHNavbar;
