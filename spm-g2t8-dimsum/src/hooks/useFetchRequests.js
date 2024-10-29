// useFetchRequests.js
import { useEffect, useState } from 'react';
import axios from 'axios';

const useFetchRequests = (selectedDate, staffId) => {
  const [requestsData, setRequestsData] = useState({
    wfh: [],
    inOffice: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const API_URL = import.meta.env.VITE_API_URL_5000;

  useEffect(() => {
    const fetchRequests = async () => {
      setLoading(true);
      try {
        // Convert selectedDate to a string format "YYYY-MM-DD"
        console.log(selectedDate);
        const formattedDate = selectedDate.local().format("YYYY-MM-DD");
        console.log(formattedDate);
        const response = await axios.post(API_URL+'/api/getSchedule', {
          date: formattedDate,
          uid: staffId, // Attach staffId to the request body
        });
        
        // Assuming response.data is structured as required
        setRequestsData(response.data);
        console.log(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    // Ensure staffId is available before fetching
    if (selectedDate && staffId) {
      fetchRequests();
    }
  }, [selectedDate, staffId]); // Include staffId in the dependency array

  return { requestsData, loading, error };
};

export default useFetchRequests;
