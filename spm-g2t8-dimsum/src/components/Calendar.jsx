import React, { useState, useEffect } from 'react';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { Form, Row, Col, Dropdown, DropdownButton, InputGroup, Container } from 'react-bootstrap';

const localizer = momentLocalizer(moment);

const CustomToolbar = ({ date, onNavigate }) => {
  const handlePrevious = () => {
    onNavigate('PREV');
  };

  const handleNext = () => {
    onNavigate('NEXT');
  };

  const handleToday = () => {
    onNavigate('TODAY');
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

const WFHCalendar = ({ events }) => {
  const [selectedDate, setSelectedDate] = useState(null);
  const [filteredEvents, setFilteredEvents] = useState([]);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [month, setMonth] = useState(new Date().getMonth());
  const [year, setYear] = useState(new Date().getFullYear());

  const handleMonthChange = (e) => setMonth(e.target.value);
  const handleYearChange = (e) => setYear(e.target.value);

  // Handle clicks on date cells (slots)
  const handleSlotClick = (slotInfo) => {
    setSelectedDate(slotInfo.start); // Set the selected date from slot
    setFilter('all'); // Reset filter to 'all'
  };

  // Filter events based on selected date, filter type, and search term
  useEffect(() => {
    if (selectedDate) {
      const filtered = events.filter((event) => {
        const isSameDay = moment(event.start).isSame(selectedDate, 'day'); // Correct comparison for same day
        const matchesFilter = filter === 'all' || event.status === filter;
        const matchesSearch = event.teamMember.toLowerCase().includes(searchTerm.toLowerCase());
        return isSameDay && matchesFilter && matchesSearch;
      });
      setFilteredEvents(filtered);
    }
  }, [filter, searchTerm, selectedDate, events]);

  // Highlight the selected date cell
  const dayPropGetter = (date) => {
    const isSelected = moment(date).isSame(selectedDate, 'day');
    return {
      className: isSelected ? 'highlighted-cell' : ''
    };
  };

  return (
    <Container fluid className="wfh-calendar" style={{ padding: '20px' }}>
      <Row>
        {/* Left Side: Calendar with Month/Year Filters */}
        <Col xs={12} md={6} className="mb-4" style={{ paddingRight: '15px' }}>
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
        <Col xs={12} md={6} style={{ paddingLeft: '15px' }}>
          <h4 className="mb-4">Schedule Details</h4>
          <InputGroup className="mb-3">
            <Form.Control
              placeholder="Search team member"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </InputGroup>
          <DropdownButton
            variant="secondary"
            title={filter === 'all' ? 'All' : filter === 'WFH' ? 'Work From Home' : 'In Office'}
            onSelect={(selected) => setFilter(selected)}
            className="mb-3"
          >
            <Dropdown.Item eventKey="all">All</Dropdown.Item>
            <Dropdown.Item eventKey="WFH">Work From Home</Dropdown.Item>
            <Dropdown.Item eventKey="office">In Office</Dropdown.Item>
          </DropdownButton>

          {selectedDate ? (
            <div>
              <h5>Details for {moment(selectedDate).format('MMMM Do YYYY')}</h5>
              {filteredEvents.length > 0 ? (
                <ul className="list-unstyled">
                  {filteredEvents.map((event) => (
                    <li key={event.id}>
                      {event.teamMember} ({event.status})
                    </li>
                  ))}
                </ul>
              ) : (
                <p>No events found for the selected day.</p>
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
