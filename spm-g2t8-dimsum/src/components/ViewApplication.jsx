import React, { useState, useEffect } from 'react';
import { Table, Dropdown, DropdownButton, Form, InputGroup, Col, Row, Container } from 'react-bootstrap';
import axios from 'axios';
import moment from 'moment-timezone';
import '../css/viewApplication.css';

const ViewApplication = () => {
  const [requests, setRequests] = useState([]);
  const [filteredRequests, setFilteredRequests] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const staffID = 10; // Mock Staff ID for filtering

  // Fetch data from the API
  const fetchRequests = async () => {
    try {
      setLoading(true);
      
      // Construct the URL with query parameters
      const response = await fetch(`http://localhost:5002/api/requests?status=${filter === 'all' ? '' : filter}&staff_id=${staffID}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
  
      if (!response.ok) {
        throw new Error('Failed to fetch requests.');
      }
  
      const data = await response.json(); // Parse the JSON response
      setRequests(data); // Set the fetched requests to state
      setLoading(false);
    } catch (error) {
      console.error('Error fetching requests:', error);
      setLoading(false);
    }
  };
  

  // Handle filter logic
  useEffect(() => {
    let filtered = requests;

    // Filter by Staff ID and Status
    filtered = filtered.filter(request => request.Staff_ID === staffID);
    
    if (filter !== 'all') {
      filtered = filtered.filter(request => request.Status === filter);
    }

    setFilteredRequests(filtered);
  }, [filter, requests]);

  // Fetch data on component mount
  useEffect(() => {
    fetchRequests();
  }, []);

  return (
    <Container fluid className="view-application" style={{ padding: '50px' }}>
      <h3 className="mb-4">View WFH Applications</h3>

      <Row className="mb-3">
        <Col md={4}>
          <DropdownButton
            title={filter === 'all' ? 'All Statuses' : filter}
            variant="secondary"
            onSelect={(selected) => setFilter(selected)}
          >
            <Dropdown.Item eventKey="all">All Statuses</Dropdown.Item>
            <Dropdown.Item eventKey="Pending">Pending</Dropdown.Item>
            <Dropdown.Item eventKey="Approved">Approved</Dropdown.Item>
            <Dropdown.Item eventKey="Rejected">Rejected</Dropdown.Item>
          </DropdownButton>
        </Col>
      </Row>

      {loading ? (
        <p>Loading...</p>
      ) : (
        <Table striped bordered hover responsive className='table-cell-spacing'>
          <thead>
            <tr>
              <th style={{ width: '8%', textAlign: 'center' }}>Request ID</th>
              <th>Request Date</th>
              <th>Apply Date</th>
              <th>Duration</th>
              <th>Reason</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {filteredRequests.length > 0 ? (
              filteredRequests.map((request, index) => (
                <tr key={index}>
                  <td style={{ textAlign: 'center', fontWeight: 'bold' }}>{request.Request_ID}</td>
                  <td>{moment(request.Request_Date).format('YYYY-MM-DD')}</td>
                  <td>{request.Apply_Date}</td>
                  <td>{request.Duration}</td>
                  <td>{request.Reason}</td>
                  <td style={{  fontWeight: 'bold', }}>
                    <span
                      className={
                        request.Status == 'Pending' ? 'status-pending' :
                        request.Status === 'Approved' ? 'status-approved' :
                        request.Status === 'Rejected' ? 'status-rejected' :
                        ''
                      }
                    >
                      {request.Status}
                    </span>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="8" className="text-center">No requests found.</td>
              </tr>
            )}
          </tbody>
        </Table>
      )}
    </Container>
  );
};

export default ViewApplication;
