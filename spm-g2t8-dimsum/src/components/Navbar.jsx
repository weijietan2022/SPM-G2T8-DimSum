import React from 'react';
import { Navbar, Nav, Button, Container } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';

const WFHNavbar = ({ onLogout }) => {
  const navigate = useNavigate(); // Hook to programmatically navigate

  const handleLogout = () => {
    onLogout(); // Call the function to set authentication state to false
    navigate('/login'); // Redirect to the login page
  };

  return (
    <Navbar bg="dark" variant="dark" expand="lg" className="px-3">
      <Container fluid>
        <Navbar.Brand className="fw-bold">ALL-IN-ONE WFH PORTAL</Navbar.Brand>
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
