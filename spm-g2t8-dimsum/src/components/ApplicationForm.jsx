import React, { useState, useContext } from 'react';
import '../css/ApplicationForm.css';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const ApplicationForm = () => {
  const { staffId, managerId } = useContext(AuthContext);
  const [formType, setFormType] = useState('adhoc');
  const [date, setDate] = useState('');
  const [session, setSession] = useState('AM');
  const [cart, setCart] = useState([]);
  const [reason, setReason] = useState('');
  const [attachment, setAttachment] = useState(null);
  const [numRecurrences, setNumRecurrences] = useState(0);
  const navigate = useNavigate();

  const minDate = () => {
    const today = new Date();
    today.setDate(today.getDate() + 1);
    return today.toISOString().split('T')[0];
  };

  const addDateToCart = () => {
    // check if date is empty or session is empty or date is already in cart or date is on a weekend
    if (date === '') {
      alert('Please select a date');
      return;
    }
    if (session === '') {
      alert('Please select a session');
      return;
    }
    if (cart.some((item) => item.date === date)) {
      alert('Date already selected');
      return;
    }
    const selectedDate = new Date(date);
    if (selectedDate.getDay() === 0 || selectedDate.getDay() === 6) {
      alert('Cannot select a weekend date');
      return;
    }

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

  const handleSubmit = async (e) => {

    e.preventDefault();

    const API_URL = import.meta.env.VITE_API_URL_5002;
    const formData = new FormData();

    // Check if recurring form is selected
    if (formType === 'recurring') {
     if (!date || !session) {
      alert('Please fill in all the fields');
      return;
    }
    // check if the date is on a weekend
    const selectedDate = new Date(date);
    if (selectedDate.getDay() === 0 || selectedDate.getDay() === 6) {
      alert('Cannot select a weekend date');
      return;
    }

    const recurringCart = [];
    let tempDate = new Date(date);

    for (let i = 0; i <= numRecurrences; i++) {
      // Format the date and add to the recurring cart
      recurringCart.push({ date: tempDate.toISOString().split('T')[0], session });
      
      // Update tempDate to be 7 days later for the next recurrence
      tempDate.setDate(tempDate.getDate() + 7);
    }

    formData.append('date', JSON.stringify(recurringCart));
    formData.append('reason', reason);
    formData.append('attachment', attachment);
    formData.append('staffId', staffId);
    formData.append('managerId', managerId);

    }else if (formType === 'adhoc'){

    formData.append('date', JSON.stringify(cart));
    formData.append('reason', reason);
    formData.append('attachment', attachment);
    formData.append('staffId', staffId);
    formData.append('managerId', managerId);
    }

    try {
      const response = await fetch(`${API_URL}/api/process_request`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setDate('');
        setSession('AM');
        setCart([]);
        setReason('');
        setAttachment('');
        document.querySelector('.wfh-file-input').value = '';

        console.log("success inserting into database");
        alert("successful application");
        navigate('/applicationform');
      } else {
        setDate('');
        setSession('AM');
        setCart([]);
        setReason('');
        setAttachment('');
        document.querySelector('.wfh-file-input').value = '';

        console.error(data.message);

        let errorMsg = "Errors:\n";
        if (Array.isArray(data.message)) {
          data.message.forEach((msg) => { errorMsg += msg + "\n"; });
        } else if (data.message) {
          errorMsg += data.message;
        } else {
          errorMsg += "An unknown error occurred.";
        }

        alert(errorMsg.trim());
      }
    } catch (error) {
      console.error('Error fetching requests:', error);
    }
  };

  const renderAdhocForm = () => (
    <>
      <div className="wfh-date">
        <label className="wfh-label">Select Date:</label>
        <input
          id="dateInput"
          type="date"
          value={date}
          min={minDate()}
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
    </>
  );

  const renderRecurringForm = () => (
    <div className="wfh-recurring">
      <label className="wfh-label">Select Start Date for Recurrence:</label><br />
      <label className="description"> Please select the date of the day you want to start the recurrence. This day will be recurred for subsequent weeks based on the number you input. </label>
      <input
        type="date"
        value={date}
        min={minDate()}
        onChange={(e) => setDate(e.target.value)}
        className="wfh-recurring-input"
      />

      <label className="wfh-label mt-3">Select Session:</label>
      <select value={session} onChange={(e) => setSession(e.target.value)} className="wfh-session-select">
        <option value="AM">AM</option>
        <option value="PM">PM</option>
        <option value="Full Day">Full Day</option>
      </select>

      <label className="wfh-label mt-3">Select number of recurrences</label>
      <label className="description"> Number of recurrences refers to how many times you want it to recur. If you select one, the selected date, and the same day on the next week will be submitted for WFH. </label>
      <input
        type="number"
        value={numRecurrences}
        onChange={(e) => setNumRecurrences(e.target.value)}
        className="wfh-recurring-input"
      />
    </div>
  );

  return (
    <div className="wfh-application">
      <h1 className="wfh-heading">Apply for WFH</h1>
      <div className="wfh-form-type">
      <div className="form-group mb-4">
        <label className="font-weight-bold">Form Type:</label>
        <select 
          value={formType} 
          onChange={(e) => setFormType(e.target.value)} 
          className="form-control w-50"
        >
          <option value="adhoc">Adhoc</option>
          <option value="recurring">Recurring</option>
        </select>
      </div>
      </div>

      <form onSubmit={handleSubmit} encType="multipart/form-data" className="wfh-form">
        {formType === 'adhoc' ? renderAdhocForm() : renderRecurringForm()}

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
