import React, { useState, useEffect } from 'react';

const YourRequests = () => {
  const [requests, setRequests] = useState([]);  // To store the fetched requests
  const [loading, setLoading] = useState(true);  // To manage loading state
  const [error, setError] = useState(null);      // To handle any errors

  useEffect(() => {
    // Fetch requests from the Flask API
    fetch('http://localhost:5008/api/view-request', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // credentials: 'include'  // Ensures cookies are sent with the request
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
  }, []);  // Empty dependency array means this will only run once, after component mounts

  // Show loading state
  if (loading) return <p>Loading requests...</p>;

  // Show error message if there is an error
  if (error) return <p>Error: {error}</p>;

  // Render the requests in a table once they are fetched
  return (
    <div>
      <h1>Your Requests</h1>
      {requests.length > 0 ? (
        <table>
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
        </table>
      ) : (
        <p>No requests found</p>
      )}
    </div>
  );
};

export default YourRequests;
