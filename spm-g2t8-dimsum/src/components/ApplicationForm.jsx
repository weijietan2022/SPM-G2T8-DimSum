import React, { useState } from 'react';
import '../css/ApplicationForm.css';
import { useNavigate } from 'react-router-dom';


const ApplicationForm = () => {
  const [date, setDate] = useState('');
  const [session, setSession] = useState('AM');
  const [cart, setCart] = useState([]);
  const [reason, setReason] = useState('');
  const [attachments, setAttachments] = useState(null);
  const navigate = useNavigate();

  const addDateToCart = () => {
    if (date && session) {
      setCart([...cart, { date, session }]);
      setDate('');
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files) {
      setAttachments(e.target.files);
    }
  };

  const handleSubmit = async(e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('date', JSON.stringify(cart))
    formData.append('reason', reason);
    formData.append('attachment', attachments)

    try {
      const response = await fetch(`http://localhost:5002/api/process_request`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (response.ok) {
        // setSuccessMessage(data.message);
        // setErrorMessage('')

        setDate('');
        setSession('AM');
        setCart([]);
        setReason('');
        setAttachments(null);

        console.log("success inserting into database")
        alert("successful application")
        navigate('/applicationform')

      } else {
        // setErrorMessage(data.message);
        // setSuccessMessage('');

        setDate('');
        setSession('AM');
        setCart([]);
        setReason('');
        setAttachments(null);

        console.error(data.message)
        if (data.message && Array.isArray(data.message)) {
          data.message.forEach(msg => {
            alert(msg);
          });
        } else {
          console.error('Unknown error: ', data.message)
        }
      }

    //   setRequests(data); // Set the fetched requests to state
    //   setLoading(false);
    } catch (error) {
        console.error('Error fetching requests:', error);
        // setLoading(false);
    };
  };




  return (
    // <div>
    //   <h1>Apply for WFH</h1>
    //   <form onSubmit={handleSubmit} encType="multipart/form-data">

    //     <div>
    //       <label>Select Date:</label>
    //       <input
    //         id="dateInput"
    //         type="date"
    //         value={date}
    //         onChange={(e) => setDate(e.target.value)}
    //         onClick={(e) => e.target.showPicker()}
    //         style={{ cursor: 'pointer' }}
    //       />
    //     </div>

    //     <div>
    //       <label>Select Session:</label>
    //       <select value={session} onChange={(e) => setSession(e.target.value)}>
    //         <option value="AM">AM</option>
    //         <option value="PM">PM</option>
    //         <option value="Full Day">Full Day</option>
    //       </select>
    //       <button type="button" onClick={addDateToCart}>Add to Cart</button>
    //     </div>

    //     <div>
    //       <h2>Selected WFH Dates</h2>
    //       <ul style={{ padding: 0 }}>
    //         {cart.length > 0 ? (
    //           cart.map((item, index) => (
    //             <li key={index} style={{ textAlign: 'left' }}>
    //               {item.date} - {item.session}
    //             </li>
    //           ))
    //         ) : (
    //           <p>No dates selected yet</p>
    //         )}
    //       </ul>
    //     </div>

    //     <div>
    //       <label>Reason for WFH:</label>
    //       <textarea
    //         value={reason}
    //         onChange={(e) => setReason(e.target.value)}
    //         placeholder="Provide a reason for applying WFH"
    //         required
    //       />
    //     </div>

    //     <div>
    //       <label>Supporting Documents:</label>
    //       <input type="file" onChange={handleFileChange} multiple />
    //     </div>

    //     <button type="submit">Submit</button>
    //   </form>
    // </div>

    <div className="wfh-application">
    <h1 className="wfh-heading">Apply for WFH</h1>
    <form onSubmit={handleSubmit} encType="multipart/form-data" className="wfh-form">

      <div className="wfh-date">
        <label className="wfh-label">Select Date:</label>
        <input
          id="dateInput"
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          onClick={(e) => e.target.showPicker()}
          style={{ cursor: 'pointer' }}
          className="wfh-date-input"
        />
      </div>

      <div className="wfh-session">
        <label className="wfh-label">Select Session:</label>
        <select value={session} onChange={(e) => setSession(e.target.value)} className="wfh-session-select">
          <option value="AM">AM</option>
          <option value="PM">PM</option>
          <option value="Full Day">Full Day</option>
        </select>
        <button type="button" onClick={addDateToCart} className="wfh-add-to-cart-btn">Add to Cart</button>
      </div>

      <div className="wfh-cart">
        <h2 className="wfh-cart-heading">Selected WFH Dates</h2>
        <ul className="wfh-cart-list">
          {cart.length > 0 ? (
            cart.map((item, index) => (
              <li key={index} className="wfh-cart-item">
                {item.date} - {item.session}
              </li>
            ))
          ) : (
            <p className="wfh-no-dates">No dates selected yet</p>
          )}
        </ul>
      </div>

      <div className="wfh-reason">
        <label className="wfh-label">Reason for WFH:</label>
        <textarea
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="Provide a reason for applying WFH"
          required
          className="wfh-reason-input"
        />
      </div>

      <div className="wfh-documents">
        <label className="wfh-label">Supporting Documents:</label>
        <input type="file" onChange={handleFileChange} multiple className="wfh-file-input" />
      </div>

      <button type="submit" className="wfh-submit-btn">Submit</button>
    </form>
  </div>
  );
};

export default ApplicationForm;
