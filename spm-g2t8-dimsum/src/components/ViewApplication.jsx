import React, { useState, useEffect, useContext } from 'react';
import { Table, Dropdown, DropdownButton, Col, Row, Container, Modal, Button, Spinner } from 'react-bootstrap';
import moment from 'moment-timezone';
import '../css/viewApplication.css';
import { AuthContext } from '../context/AuthContext';

const ViewApplication = () => {
  const [requests, setRequests] = useState([]);
  const [filter, setFilter] = useState('Pending');
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');
  const [loadingReason, setLoadingReason] = useState(false); // Loading state for the rejection reason
  const { staffId, managerId } = useContext(AuthContext);
  const API_URL = import.meta.env.VITE_API_URL_5002;

  const fetchRequests = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/requests?staff_id=${staffId}`, {
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

  useEffect(() => {
    fetchRequests();
  }, []);

  const filteredRequests = filter === 'All'
    ? requests
    : requests.filter(request => request.Status === filter);

  const handleCancelRequest = async (requestId, applyDate, duration, status, managerId, staffId) => {
    const confirmCancel = window.confirm("Are you sure you want to withdraw this request?");
    
    if (confirmCancel) {
      try {
        const response = await fetch(`${API_URL}/api/withdraw`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            requestId,
            applyDate,
            managerId,
            status,
            duration,
            staffId,
          }),
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

  const handleRejectedClick = async (requestId, applyDate) => {
    setLoadingReason(true);
    setShowModal(true);
    setRejectionReason(''); // Clear previous reason

    try {
      const response = await fetch(`${API_URL}/api/getRejectionReason`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ request_id: requestId, apply_date: applyDate }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch rejection reason.');
      }

      const data = await response.json();
      setRejectionReason(data.reason);
    } catch (error) {
      console.error('Error fetching rejection reason:', error);
      setRejectionReason('Failed to load rejection reason.');
    } finally {
      setLoadingReason(false);
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setRejectionReason('');
  };

  return (
    <Container fluid className="view-application" style={{ padding: '30px' }}>
      <h3 className="mb-4">View WFH Applications</h3>

      <Row className="mb-3">
        <Col md={4}>
          <DropdownButton
            title={filter}
            variant="secondary"
            onSelect={(selected) => setFilter(selected)}
          >
            <Dropdown.Item eventKey="All">All</Dropdown.Item>
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
        <Table striped bordered hover responsive className='custom-table'>
          <thead>
            <tr>
              <th style={{ width: '8%' }}>Request ID</th>
              <th>Applied For</th>
              <th>Duration</th>
              <th>Reason</th>
              <th>Status</th>
              <th>File</th>
              <th>Cancel</th>
            </tr>
          </thead>
          <tbody>
            {filteredRequests.length > 0 ? (
              filteredRequests.map((request, index) => (
                <tr key={index}>
                  <td style={{ fontWeight: 'bold' }}>{request.Request_ID}</td>
                  <td>{moment(request.Apply_Date).format('D MMMM YYYY')}</td>
                  <td>{request.Duration}</td>
                  <td>{request.Reason}</td>
                  <td>
                    {request.Status === 'Rejected' ? (
                      <span
                        className="status-rejected"
                        onClick={() => handleRejectedClick(request.Request_ID, request.Apply_Date)}
                        style={{ cursor: 'pointer', textDecoration: 'underline' }}
                      >
                        {request.Status}
                      </span>
                    ) : (
                      <span
                        className={
                          request.Status === 'Pending' ? 'status-pending' :
                          request.Status === 'Approved' ? 'status-approved' :
                          request.Status === 'Withdrawn' ? 'status-withdrawn' :
                          ''
                        }
                      >
                        {request.Status}
                      </span>
                    )}
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
                  <td>
                    {(request.Status === 'Pending' || request.Status === 'Approved') && (
                      <button
                        className="btn btn-danger"
                        onClick={() => handleCancelRequest(request.Request_ID, request.Apply_Date, request.Duration, request.Status, managerId, staffId)}
                      >
                        Cancel
                      </button>
                    )}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7" className="text-center">No requests found.</td>
              </tr>
            )}
          </tbody>
        </Table>
      )}

      {/* Modal for displaying rejection reason */}
      <Modal show={showModal} onHide={handleCloseModal}>
        <Modal.Header closeButton>
          <Modal.Title>Rejection Reason</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {loadingReason ? (
            <div className="text-center">
              <Spinner animation="border" variant="primary" />
              <p>Loading...</p>
            </div>
          ) : (
            <p>{rejectionReason}</p>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseModal}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default ViewApplication;
