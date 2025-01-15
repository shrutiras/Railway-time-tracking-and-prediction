import React, { useState } from 'react';
import axios from 'axios';

const AddTrain = () => {
  const [train, setTrain] = useState({
    train_name: '',
    source: '',
    destination: '',
    departure_time: '',
    arrival_time: '',
  });

  const handleAddTrain = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://localhost:5000/admin/add-train', train, {
        headers: { Authorization: `Bearer ${token}` },
      });
      alert('Train added successfully!');
    } catch (error) {
      alert('Failed to add train! ' + error.response.data.error);
    }
  };

  return (
    <form onSubmit={handleAddTrain}>
      <input type="text" placeholder="Train Name" onChange={(e) => setTrain({ ...train, train_name: e.target.value })} />
      <input type="text" placeholder="Source" onChange={(e) => setTrain({ ...train, source: e.target.value })} />
      <input type="text" placeholder="Destination" onChange={(e) => setTrain({ ...train, destination: e.target.value })} />
      <input type="text" placeholder="Departure Time" onChange={(e) => setTrain({ ...train, departure_time: e.target.value })} />
      <input type="text" placeholder="Arrival Time" onChange={(e) => setTrain({ ...train, arrival_time: e.target.value })} />
      <button type="submit">Add Train</button>
    </form>
  );
};

export default AddTrain;
 
