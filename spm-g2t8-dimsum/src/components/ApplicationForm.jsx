import React, { useState } from 'react';
import '../css/ApplicationForm.css';

const ApplicationForm = () => {
  // State for form data
  const [date, setDate] = useState('');  // Holds the currently selected date
  const [session, setSession] = useState('Whole Day');  // Holds the session for the selected date
  const [cart, setCart] = useState([]);  // Holds all selected dates
  const [reason, setReason] = useState('');  // Holds the WFH reason
  const [attachments, setAttachments] = useState(null);  // Holds the uploaded file(s)

  // Handle adding a selected date to the cart
  const addDateToCart = () => {
    if (date) {
      setCart([...cart, { date, session }]);
      setDate('');  // Clear the date after adding
    }
  };

  // Handle file upload
  const handleFileChange = (e) => {
    if (e.target.files) {
      setAttachments(e.target.files);
    }
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    console.log({
      cart,
      reason,
      attachments,
    });
    alert('Form Submitted! Check the console for the form data.');
  };

  return (
    <div>
      <h1>Apply for WFH</h1>
      <form onSubmit={handleSubmit}>
        {/* Date Picker Section */}
        <div>
          <label>Select Date:</label>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
          />
        </div>

        {/* AM/PM/Whole Day Section */}
        <div>
          <label>Select Session:</label>
          <select value={session} onChange={(e) => setSession(e.target.value)}>
            <option value="AM">AM</option>
            <option value="PM">PM</option>
            <option value="Whole Day">Whole Day</option>
          </select>
          <button type="button" onClick={addDateToCart}>Add to Cart</button>
        </div>

        {/* Cart to show selected dates */}
        <div>
          <h2>Selected WFH Dates</h2>
          <ul style={{ padding: 0 }}> {/* Added inline style to reset padding */}
            {cart.length > 0 ? (
              cart.map((item, index) => (
                <li key={index} style={{ textAlign: 'left' }}> {/* Ensure text is left-aligned */}
                  {item.date} - {item.session}
                </li>
              ))
            ) : (
              <p>No dates selected yet</p>
            )}
          </ul>
        </div>

        {/* Reason for WFH */}
        <div>
          <label>Reason for WFH:</label>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Provide a reason for applying WFH"
            required
          />
        </div>

        {/* Attachments field */}
        <div>
          <label>Supporting Documents:</label>
          <input type="file" onChange={handleFileChange} multiple />
        </div>

        {/* Submit Button */}
        <button type="submit">Submit</button>
      </form>
    </div>
  );
};

export default ApplicationForm;
