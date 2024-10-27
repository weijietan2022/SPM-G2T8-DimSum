import React, { useState, useEffect, useContext } from 'react';
import '../css/YourRequests.css';
import { AuthContext } from '../context/AuthContext';

const YourRequests = () => {
  const { staffId, dept, position } = useContext(AuthContext);
  const [requests, setRequests] = useState([]);  // To store the fetched requests
  const [loading, setLoading] = useState(true);  // To manage loading state
  const [error, setError] = useState(null);      // To handle any errors
  const [statusFilter, setStatusFilter] = useState('All');  // Default to 'All'
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

  // Function to handle approval or rejection of a request
  const updateRequestStatus = (requestId, newStatus) => {
    fetch(`${API_URL}/api/update-request`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ requestId, status: newStatus }),
    })
      .then(response => {
        if (!response.ok) throw new Error(`Failed to ${newStatus.toLowerCase()} the request`);
        return response.json();
      })
      .then(() => {
        // Update the request status locally to avoid refetching
        setRequests(prevRequests =>
          prevRequests.map(request =>
            request.Request_ID === requestId ? { ...request, Status: newStatus } : request
          )
        );
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
                <th>Request Date</th>
                <th>Apply Date</th>
                <th>Duration</th>
                <th>Reason</th>
                <th>Status</th>
                <th>Department</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {requests.map(request => (
                <tr key={request.Request_ID}>
                  <td>{request.Request_ID}</td>
                  <td>{request.Staff_ID}</td>
                  <td>{new Date(request.Request_Date).toLocaleDateString()}</td>
                  <td>{request.Apply_Date}</td>
                  <td>{request.Duration}</td>
                  <td>{request.Reason}</td>
                  <td>{request.Status}</td>
                  <td>{request.Department}</td>
                  <td>
                    <div className="action-buttons">
                      <button 
                        className="approve-button" 
                        onClick={() => updateRequestStatus(request.Request_ID, 'Approved')}
                      >
                        Approve
                      </button>
                      <button 
                        className="reject-button" 
                        onClick={() => updateRequestStatus(request.Request_ID, 'Rejected')}
                      >
                        Reject
                      </button>
                    </div>
                  </td>


                </tr>
              ))}
            </tbody>
          </table>
        </center>
      ) : (
        <p>No requests found</p>
      )}
    </div>
  );
};

export default YourRequests;
