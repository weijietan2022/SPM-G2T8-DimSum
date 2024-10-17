import React, { useState, useEffect, useContext } from 'react';
import '../css/YourRequests.css';
import { AuthContext } from '../context/AuthContext';


const YourRequests = () => {
  const { staffId, dept, position } = useContext(AuthContext);
  const [requests, setRequests] = useState([]);  // To store the fetched requests
  const [loading, setLoading] = useState(true);  // To manage loading state
  const [error, setError] = useState(null);      // To handle any errors
  const [statusFilter, setStatusFilter] = useState('All');  // Default to 'All'

  // useEffect with dependency array only runs when 'statusFilter' changes
  useEffect(() => {
    // Clear previous errors
    setError(null);

    // Fetch requests from the Flask API based on the selected status filter
    fetch(`http://localhost:5008/api/view-request?status=${statusFilter}&dept=${dept}&staffId=${staffId}&position=${position}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to fetch requests');  // Handle fetch errors
        }
        return response.json();  // Parse response as JSON
      })
      .then(data => {
        setRequests(data);  // Store the fetched data in state
        setLoading(false);  // Loading is complete
      })
      .catch(err => {
        setError(err.message);  // Set error message if fetch fails
        setLoading(false);      // Stop loading
      });
  }, [statusFilter]);  // Trigger fetch only when 'statusFilter' changes

  // Show loading state
  if (loading) return <p>Loading requests...</p>;

  // Show error message if there is an error
  if (error) return <p>Error: {error}</p>;

  // Render the requests in a table once they are fetched
  return (
    <div>
      <br></br>
      {/* Dropdown for status filter */}
      <select
          id="statusFilter"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}  // Update status filter when changed
        >
          <option value="All">All</option>
          <option value="Pending">Pending</option>
          <option value="Approved">Approved</option>
          <option value="Rejected">Rejected</option>
        </select>
      <br></br>
      {requests.length > 0 ? (
        <center><table className="tab-con">
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
              </tr>
            ))}
          </tbody>
        </table></center>
      ) : (
        <p>No requests found</p>
      )}
    </div>
  );
};

export default YourRequests;
