import React, { useState, useEffect, useContext } from 'react';
import { Table, Dropdown, DropdownButton, Form, InputGroup, Col, Row, Container } from 'react-bootstrap';
import axios from 'axios';
import moment from 'moment-timezone';
import '../css/viewApplication.css';
import { AuthContext } from '../context/AuthContext';

const ViewApplication = () => {
  const [requests, setRequests] = useState([]);
  const [filteredRequests, setFilteredRequests] = useState([]);
  const [filter, setFilter] = useState('Pending');
  const [loading, setLoading] = useState(true);
  const { staffId } = useContext(AuthContext);
  const API_URL = import.meta.env.VITE_API_URL_5002;

  const fetchRequests = async () => {
    try {
      setLoading(true);
      
      const response = await fetch(`${API_URL}/api/requests?status=${filter}&staff_id=${staffId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
  
      if (!response.ok) {
        throw new Error('Failed to fetch requests.');
      }
  
      const data = await response.json();
      setRequests(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching requests:', error);
      setLoading(false);
    }
  };
  

  // Handle filter logic
  useEffect(() => {
    let filtered = requests;

    filtered = filtered.filter(request => request.Staff_ID === staffId);
    
    if (filter !== 'Pending') {
      filtered = filtered.filter(request => request.Status === filter);
    }

    setFilteredRequests(filtered);
  }, [filter, requests]);

  // Fetch data on component mount
  useEffect(() => {
    fetchRequests();
  }, [filter]);


  const handleCancelRequest = async (requestId, applyDate) => {

    const confirmCancel = window.confirm("Are you sure you want to withdraw this request?");
    
    if (confirmCancel) {
      try {
        const encodedApplyDate = encodeURIComponent(applyDate);
  
        const response = await fetch(`${API_URL}/api/withdraw/${requestId}/${encodedApplyDate}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ status: 'Withdrawn' }),
        });
  
        if (response.ok) {
          setRequests((prevRequests) =>
            prevRequests.map((req) =>
              req.Request_ID === requestId && req.Apply_Date === applyDate ? { ...req, Status: 'Withdrawn' } : req
            )
          );
          alert("Successfully withdrawn the request.");

          fetchRequests();
        } else {
          console.error('Failed to withdraw the request.');
          alert("Failed to withdraw the request.");
        }
      } catch (error) {
        console.error('Error withdrawing request:', error);
      }
    }
  };


  return (
    <Container fluid className="view-application" style={{ padding: '50px' }}>
      <h3 className="mb-4">View WFH Applications</h3>

      <Row className="mb-3">
        <Col md={4}>
          <DropdownButton
            title={filter}
            variant="secondary"
            onSelect={(selected) => setFilter(selected)}
          >
            <Dropdown.Item eventKey="Pending">Pending</Dropdown.Item>
            <Dropdown.Item eventKey="Approved">Approved</Dropdown.Item>
            <Dropdown.Item eventKey="Rejected">Rejected</Dropdown.Item>
            <Dropdown.Item eventKey="Withdrawn">Withdrawn</Dropdown.Item>
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
              {(filter !== 'Rejected') &&
                <th>File</th>
              }
              {(filter === 'Pending' || filter === 'Approved') && <th>Cancel</th>}
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
                        request.Status === 'Withdrawn' ? 'status-withdrawn' :
                        ''
                      }
                    >
                      {request.Status}
                    </span>
                  </td>
                  <td>
                  {request.File ? (
                      <a href={`${API_URL}/api/files/${request.File}`} download>
                        Download File
                      </a>
                    ) : (
                      '-'
                    )}
                  </td>
                  {(request.Status === 'Pending' || request.Status === 'Approved') && (
                    <td>
                      <button
                        className="btn btn-danger"
                        onClick={() => handleCancelRequest(request.Request_ID, request.Apply_Date)}
                      >
                        Cancel
                      </button>
                    </td>
                  )}
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
