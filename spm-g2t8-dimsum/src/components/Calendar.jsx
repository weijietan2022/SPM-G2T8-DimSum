import React, { useState, useContext } from 'react';
import { Calendar, momentLocalizer } from 'react-big-calendar';
// import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { Form, Row, Col, Dropdown, DropdownButton, InputGroup, Container } from 'react-bootstrap';
import { AuthContext } from '../context/AuthContext';
import useFetchRequests from '../hooks/useFetchRequests.js';
import moment from 'moment-timezone';
import '../css/calendar.css';



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

const WFHCalendar = () => {
  const [selectedDate, setSelectedDate] = useState(moment());
  const { staffId } = useContext(AuthContext);
  const { requestsData, loading, error } = useFetchRequests(selectedDate, staffId);
  
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [month, setMonth] = useState(new Date().getMonth());
  const [year, setYear] = useState(new Date().getFullYear());

  const handleSlotClick = (slotInfo) => {
    const localDate = moment(slotInfo.start).local(); // Convert to local time
    setSelectedDate(localDate.startOf('day')); // Set to start of the day to avoid time issues
    setFilter('all');
    console.log("Selected date:", localDate.format("YYYY-MM-DD")); // Log the selected date
};

  const dayPropGetter = (date) => {
    const isSelected = moment(date).isSame(selectedDate, 'day');
    return { className: isSelected ? 'highlighted-cell' : '' };
  };

  const filterMembers = (members) => {
    return members.filter((person) => 
      person.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  };

  const filteredWFH = filter === 'WFH' ? filterMembers(requestsData.wfh) : filter === 'office' ? [] : filterMembers(requestsData.wfh);
  const filteredInOffice = filter === 'office' ? filterMembers(requestsData.inOffice) : filter === 'WFH' ? [] : filterMembers(requestsData.inOffice);

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
        <Col xs={12} md={6} className="mb-4 p-3">
          <Row className="mb-3">
            <Col>
              <Form.Control as="select" value={month} onChange={(e) => setMonth(e.target.value)}>
                {moment.months().map((m, index) => (
                  <option key={index} value={index}>{m}</option>
                ))}
              </Form.Control>
            </Col>
            <Col>
              <Form.Control as="select" value={year} onChange={(e) => setYear(e.target.value)}>
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
            events={[]} 
            startAccessor="start"
            endAccessor="end"
            style={{ height: 500, borderRadius: '10px', border: '1px solid #ddd', padding: '15px' }}
            onSelectSlot={handleSlotClick}
            selectable 
            defaultView="month"
            views={['month']}
            date={new Date(year, month)}
            dayPropGetter={dayPropGetter}
            components={{ toolbar: CustomToolbar }}
            onNavigate={(date) => {
              setMonth(date.getMonth());
              setYear(date.getFullYear());
              if (moment(date).isSame(moment(), 'day')) {
                setSelectedDate(moment());
              }
            }}
          />
        </Col>

        <Col xs={12} md={6} className="p-3" style={{ paddingLeft: '25px' }}>
          <h4 className="mb-4">Schedule Details for {moment(selectedDate).format('MMMM Do YYYY')}</h4>

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

          {loading ? (
            <p>Loading...</p> // Show loading message while fetching data
          ) : selectedDate ? (
            <div>
              <br />
              {filter !== 'office' && (
                <>
                  <h5>Working from Home</h5>
                  {filteredWFH.length > 0 ? (
                    <table className="table">
                      <thead>
                        <tr>
                          <th >S/No.</th>
                          <th>Name</th>
                          <th>Type</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredWFH.map((person, index) => (
                          <tr
                            key={index}
                            className={person.id === staffId ? 'highlighted-row' : ''} // Apply highlight class conditionally
                          >
                            <td>{index + 1}</td>
                            <td>{person.name}</td>
                            <td>{formatType(person.type)}</td>
                            <td>{person.status}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : <p>No results found.</p>}
                </>
              )}
              <br />
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
                          console.log(person.id, staffId),
                          <tr
                            key={index}
                            className={person.id === staffId ? 'highlighted-row' : ''} // Apply highlight class conditionally
                          >
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
