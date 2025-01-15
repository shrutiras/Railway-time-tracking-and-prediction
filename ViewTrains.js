import React, { useEffect, useState } from 'react';
import axios from 'axios';

const ViewTrains = () => {
  const [trains, setTrains] = useState([]);

  useEffect(() => {
    const fetchTrains = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get('http://localhost:5000/user/view-trains', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setTrains(response.data);
      } catch (error) {
        alert('Failed to fetch trains! ' + error.response.data.error);
      }
    };
    fetchTrains();
  }, []);

  return (
    <div>
      <h2>Train Schedule</h2>
      <ul>
        {trains.map((train) => (
          <li key={train.id}>
            {train.train_name} - {train.source} to {train.destination} | {train.departure_time} - {train.arrival_time}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ViewTrains;
 
