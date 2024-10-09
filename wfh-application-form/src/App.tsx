import React, { useState } from 'react';

// Define the structure for the dates cart
interface WFHDate {
  date: string;
  session: 'AM' | 'PM' | 'Whole Day';
}

const App: React.FC = () => {
  // State for form data
  const [date, setDate] = useState('');  // Holds the currently selected date
  const [session, setSession] = useState<'AM' | 'PM' | 'Whole Day'>('Whole Day');  // Holds the session for the selected date
  const [cart, setCart] = useState<WFHDate[]>([]);  // Holds all selected dates
  const [reason, setReason] = useState('');  // Holds the WFH reason
  const [attachments, setAttachments] = useState<FileList | null>(null);  // Holds the uploaded file(s)

  // Handle adding a selected date to the cart
  const addDateToCart = () => {
    if (date) {
      setCart([...cart, { date, session }]);
      setDate('');  // Clear the date after adding
    }
  };

  // Handle file upload
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setAttachments(e.target.files);
    }
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
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
            required
          />
        </div>

        {/* AM/PM/Whole Day Section */}
        <div>
          <label>Select Session:</label>
          <select value={session} onChange={(e) => setSession(e.target.value as 'AM' | 'PM' | 'Whole Day')}>
            <option value="AM">AM</option>
            <option value="PM">PM</option>
            <option value="Whole Day">Whole Day</option>
          </select>
          <button type="button" onClick={addDateToCart}>Add to Cart</button>
        </div>

        {/* Cart to show selected dates */}
        <div>
          <h2>Selected WFH Dates</h2>
          <ul>
            {cart.length > 0 ? (
              cart.map((item, index) => (
                <li key={index}>
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

export default App;
