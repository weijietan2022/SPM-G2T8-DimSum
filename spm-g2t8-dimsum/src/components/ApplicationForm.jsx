import React, { useState, useContext } from 'react';
import '../css/ApplicationForm.css';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';


const ApplicationForm = () => {
  const { staffId, managerId } = useContext(AuthContext);
  const [date, setDate] = useState('');
  const [session, setSession] = useState('AM');
  const [cart, setCart] = useState([]);
  const [reason, setReason] = useState('');
  const [attachment, setAttachment] = useState(null);
  const navigate = useNavigate();

  const addDateToCart = () => {
    if (date && session) {
      setCart([...cart, { date, session }]);
      setDate('');
    }
  };

  const handleDelete = (index) => {
    const newCart = cart.filter((item, i) => i !== index);
    setCart(newCart);
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setAttachment(e.target.files[0]);
      console.log("Selected file:", e.target.files[0]);
    }
  };

  const handleSubmit = async(e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('date', JSON.stringify(cart))
    formData.append('reason', reason);
    formData.append('attachment', attachment)
    formData.append('staffId', staffId)
    formData.append("managerId", managerId)

    try {
      const response = await fetch(`http://localhost:5002/api/process_request`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (response.ok) {
        setDate('');
        setSession('AM');
        setCart([]);
        setReason('');
        setAttachment('');
        document.querySelector('.wfh-file-input').value = ''

        console.log("success inserting into database")
        alert("successful application")
        navigate('/applicationform')

      } else {
        setDate('');
        setSession('AM');
        setCart([]);
        setReason('');
        setAttachment('');
        document.querySelector('.wfh-file-input').value = ''

        console.error(data.message)
        if (Array.isArray(data.message)) {
          data.message.forEach((msg => alert(msg)))
        } else if (data.message) {
          alert(data.message);
        } else {
          alert("An unknown error occurred.");
        }
      }

    } catch (error) {
        console.error('Error fetching requests:', error);
    };
  };


  return (
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
                <span className="wfh-cart-item-text">
                  {item.date} - {item.session}
                </span>
                <button
                  type="button"
                  className="wfh-delete-btn"
                  onClick={() => handleDelete(index)}
                >
                  Delete
                </button>
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
        <input type="file" onChange={handleFileChange} className="wfh-file-input" />
      </div>

      <button type="submit" className="wfh-submit-btn">Submit</button>
    </form>
  </div>
  );
};

export default ApplicationForm;
