import React, { useState } from 'react';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { Form, Row, Col, Dropdown, DropdownButton, InputGroup, Container } from 'react-bootstrap';

const localizer = momentLocalizer(moment);

const CustomToolbar = ({ date, onNavigate }) => {
  const handlePrevious = () => {
    onNavigate('PREV'); // Move to the previous month
  };

  const handleNext = () => {
    onNavigate('NEXT'); // Move to the next month
  };

  const handleToday = () => {
    onNavigate('TODAY'); // Move to the current date
  };

  return (
    <div className="rbc-toolbar">
      <span className="rbc-btn-group">
        <button type="button" onClick={handlePrevious}>Previous Month</button>
        <button type="button" onClick={handleNext}>Next Month</button>
        <button type="button" onClick={handleToday}>Today</button>
      </span>
      <span className="rbc-toolbar-label"><b>{moment(date).format('MMMM YYYY')}</b></span>
    </div>
  );
};

const WFHCalendar = () => {
  const [selectedDate, setSelectedDate] = useState(moment()); 
  const [eventData, setEventData] = useState({
    wfh: [
      { name: 'Jack Sim', type: 'am' },
      { name: 'Carrington', type: 'fullDay' },
      { name: 'Tony Lopez', type: 'fullDay' }
    ],
    inOffice: [
      { name: 'Jack Sim', type: 'pm' },
      { name: 'Aravind', type: 'fullDay' },
    ]
  }); // Store API data
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [month, setMonth] = useState(new Date().getMonth());
  const [year, setYear] = useState(new Date().getFullYear());

  const handleMonthChange = (e) => setMonth(e.target.value);
  const handleYearChange = (e) => setYear(e.target.value);

  // Handle clicks on date cells (slots)
  const handleSlotClick = (slotInfo) => {
    setSelectedDate(slotInfo.start); // Set the selected date
    setFilter('all'); // Reset filter to 'all'
  };

  // Highlight the selected date cell
  const dayPropGetter = (date) => {
    const isSelected = moment(date).isSame(selectedDate, 'day');
    return { className: isSelected ? 'highlighted-cell' : '' };
  };

  // Function to filter team members based on search term and filter
  const filterMembers = (members) => {
    return members.filter((person) => 
      person.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  };

  // Compute filtered results
  const filteredWFH = filter === 'WFH' ? filterMembers(eventData.wfh) : filter === 'office' ? [] : filterMembers(eventData.wfh);
  const filteredInOffice = filter === 'office' ? filterMembers(eventData.inOffice) : filter === 'WFH' ? [] : filterMembers(eventData.inOffice);

  // Function to format the type display
  const formatType = (type) => {
    switch(type) {
      case 'am': return 'AM';
      case 'pm': return 'PM';
      case 'fullDay': return 'Full Day';
      default: return type;
    }
  };

  return (
    <Container fluid className="wfh-calendar" style={{ padding: '50px' }}>
      <Row>
        {/* Left Side: Calendar with Month/Year Filters */}
        <Col xs={12} md={6} className="mb-4 p-3">
          <Row className="mb-3">
            <Col>
              <Form.Control as="select" value={month} onChange={handleMonthChange}>
                {moment.months().map((m, index) => (
                  <option key={index} value={index}>
                    {m}
                  </option>
                ))}
              </Form.Control>
            </Col>
            <Col>
              <Form.Control as="select" value={year} onChange={handleYearChange}>
                {Array.from({ length: 10 }, (_, i) => (
                  <option key={i} value={new Date().getFullYear() - i}>
                    {new Date().getFullYear() - i}
                  </option>
                ))}
              </Form.Control>
            </Col>
          </Row>
          <Calendar
            localizer={localizer}
            events={[]} // No events displayed on the calendar
            startAccessor="start"
            endAccessor="end"
            style={{ height: 500, borderRadius: '10px', border: '1px solid #ddd', padding: '15px' }}
            onSelectSlot={handleSlotClick} // Handles clicks on empty dates
            selectable // Allows selecting empty dates
            defaultView="month"
            views={['month']}
            date={new Date(year, month)}
            dayPropGetter={dayPropGetter} // Use to apply styles to date cells
            components={{
              toolbar: CustomToolbar // Use custom toolbar
            }}
            onNavigate={(date) => {
              setMonth(date.getMonth());
              setYear(date.getFullYear());
              // If navigating to today, set selected date to today
              if (moment(date).isSame(moment(), 'day')) {
                setSelectedDate(moment()); // Set selected date to today's date
              }
            }}
          />
        </Col>

        {/* Right Side: Schedule Information */}
        <Col xs={12} md={6} className="p-3" style={{ paddingLeft: '25px' }}>
          <h4 className="mb-4">Schedule Details for {moment(selectedDate).format('MMMM Do YYYY')}</h4>

          {/* Row to hold both search bar and dropdown */}
          <Row className="mb-3">
            <Col xs={12} md={8}>
              <InputGroup>
                <Form.Control
                  placeholder="Search team member"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </InputGroup>
            </Col>
            <Col xs={12} md={4}>
              <DropdownButton
                variant="secondary"
                title={filter === 'all' ? 'All' : filter === 'WFH' ? 'Work From Home' : 'In Office'}
                onSelect={(selected) => setFilter(selected)}
                className="w-100"
              >
                <Dropdown.Item eventKey="all">All</Dropdown.Item>
                <Dropdown.Item eventKey="WFH">Work From Home</Dropdown.Item>
                <Dropdown.Item eventKey="office">In Office</Dropdown.Item>
              </DropdownButton>
            </Col>
          </Row>

          {selectedDate ? (
            <div>
              <br></br>
              {filter !== 'office' && (
                <>
                  <h5 >Working from Home</h5>
                  {filteredWFH.length > 0 ? (
                    <table className="table">
                      <thead>
                        <tr>
                          <th>S/No.</th>
                          <th>Name</th>
                          <th>Type</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredWFH.map((person, index) => (
                          <tr key={index}>
                            <td>{index + 1}</td>
                            <td>{person.name}</td>
                            <td>{formatType(person.type)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : <p>No results found.</p>}
                </>
              )}
              <br></br>
              {filter !== 'WFH' && (
                <>
                  <h5>In Office</h5>
                  {filteredInOffice.length > 0 ? (
                    <table className="table">
                      <thead>
                        <tr>
                          <th>S/No.</th>
                          <th>Name</th>
                          <th>Type</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredInOffice.map((person, index) => (
                          <tr key={index}>
                            <td>{index + 1}</td>
                            <td>{person.name}</td>
                            <td>{formatType(person.type)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : <p>No results found.</p>}
                </>
              )}
            </div>
          ) : (
            <p>Select a date to view schedule details.</p>
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default WFHCalendar;
