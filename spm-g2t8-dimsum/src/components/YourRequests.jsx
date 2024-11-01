import React, { useState, useEffect, useContext } from 'react';
import '../css/YourRequests.css';
import { AuthContext } from '../context/AuthContext';

const YourRequests = () => {
  const { staffId, dept, position } = useContext(AuthContext);
  const [requests, setRequests] = useState([]);  // To store the fetched requests
  const [loading, setLoading] = useState(true);  // To manage loading state
  const [error, setError] = useState(null);      // To handle any errors
  const [statusFilter, setStatusFilter] = useState('All');  // Default to 'All'
  const [ModalVisible, ModalVisi] = useState(false); 
  const [reason, setReason] = useState(''); 
  const [Request, setRequest] = useState(null)

  const API_URL = import.meta.env.VITE_API_URL_5008;
  // Fetch requests whenever statusFilter changes
  useEffect(() => {
    setError(null);
    fetch(`${API_URL}/api/view-request?status=${statusFilter}&dept=${dept}&staffId=${staffId}&position=${position}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then(response => {
        if (!response.ok) throw new Error('Failed to fetch requests');
        return response.json();
      })
      .then(data => {
        setRequests(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [statusFilter]);

    const handleReject = (request) =>{
      setRequest(request)
      ModalVisi(true);
    }

    const handleCloseModal = () => {
      ModalVisi(false); 
      setReason(''); 
    };

    const handleSubmit = (e) => {
      e.preventDefault(); 
      if (reason) {
        alert(`Rejection Reason: ${reason}`);
        updateRequestStatus(Request.Request_ID, 'Rejected', Request.Apply_Date, Request.Duration);
        submitRejection(Request, reason);
        ModalVisi(false); 
        setReason(''); 
      } else {
        alert('Please provide a reason for rejection');
      }
    };


    const submitRejection = (request, reason) => {
      fetch(`${API_URL}/api/reject-request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ...request, rejectionReason: reason }),
      })
        .then(response => {
          if (!response.ok) throw new Error('Failed to submit rejection');
          return response.json();
        })
        .then(data => {
          console.log('Rejection submitted:', data);
        })
        .catch(err => setError(err.message));
    };

  const updateRequestStatus = (requestId, newStatus, date, duration) => {
    fetch(`${API_URL}/api/update-request`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ requestId, status: newStatus, date: date, duration: duration }),
    })
      .then(response => {
        if (!response.ok) throw new Error(`Failed to ${newStatus.toLowerCase()} the request`);
        return response.json();
      })
      .then(() => {
        // Update the status of the request in the UI based on the request ID and request DATE
        setRequests(prevRequests =>
          prevRequests.map(request =>
            request.Request_ID === requestId && request.Apply_Date === date
              ? { ...request, Status: newStatus }
              : request
          )
        );        
        if(newStatus == 'Approved'){
          fetch(`${API_URL}/api/approve-request`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ requestId, date: date, duration: duration}),
          })
            .then(response => {
              if (!response.ok) throw new Error('Failed to process approval request');
              return response.json();
            })
            .then(data => {
              alert('Approval Successful!');
              console.log('Approval request processed:', data);
            })
            .catch(err => setError(err.message));
        }
      })
      .catch(err => setError(err.message));
  };

  // Show loading state
  if (loading) return <p>Loading requests...</p>;

  // Show error message if there is an error
  if (error) return <p>Error: {error}</p>;

  // Render the requests in a table once they are fetched
  return (
    <div className="main-div">
      <br />
      <select
        id="statusFilter"
        value={statusFilter}
        className='select'
        onChange={(e) => setStatusFilter(e.target.value)}
      >
        <option value="All">All</option>
        <option value="Pending">Pending</option>
        <option value="Approved">Approved</option>
        <option value="Rejected">Rejected</option>
      </select>
      <br />
      {requests.length > 0 ? (
        <center>
          <table className="tab-con">
            <thead>
              <tr>
                <th>Request ID</th>
                <th>Staff ID</th>
                <th>Staff Name</th>
                <th>Request Date</th>
                <th>Apply Date</th>
                <th>Duration</th>
                <th>Reason</th>
                <th>Status</th>
                <th>Department</th>
                <th>Manager</th>
                <th>File</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {requests.map(request => (
                <tr key={request.Request_ID}>
                  <td>{request.Request_ID}</td>
                  <td>{request.Staff_ID}</td>
                  <td>{request.name}</td>
                  <td>{new Date(request.Request_Date).toLocaleDateString()}</td>
                  <td>{request.Apply_Date}</td>
                  <td>{request.Duration}</td>
                  <td>{request.Reason}</td>
                  <td>{request.Status}</td>
                  <td>{request.Department}</td>
                  <td>{request.Manager_ID}</td>
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
                    <div className="action-buttons">
                      <button 
                        className="approve-button" 
                        onClick={() => updateRequestStatus(request.Request_ID, 'Approved', request.Apply_Date, request.Duration)}
                      >
                        Approve
                      </button>
                      <button 
                        className="reject-button" 
                        // onClick={() => updateRequestStatus(request.Request_ID, 'Rejected')}
                        onClick={()=>handleReject(request)}
                      >
                        Reject
                      </button>
                    </div>
                  </td>


                </tr>
              ))}
            </tbody>
          </table>
          {ModalVisible && (
            <div className="custom">
              <div className="custom-cont slide-down-animation">
                <h3>Enter Rejection Reason</h3>
                <br></br>
                <form onSubmit={handleSubmit}>
                  <textarea row='5' cols='50' style={{borderRadius:'10px',border: '1px solid rgba(0, 0, 0, 0.2)' }}
                    placeholder=""
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                  />
                  <br />
                  <br></br>
                  <button type="submit" className="green-button">Submit</button>
                  <button type="button" className="red-button" onClick={handleCloseModal}>Cancel</button>
                </form>
              </div>
            </div>
          )}
        </center>
          
      ) : (
        <p>No requests found</p>
      )}
    </div>
  );
};

export default YourRequests;
