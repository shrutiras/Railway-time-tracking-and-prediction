import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => (
  <nav>
    <ul>
      <li><Link to="/">Login</Link></li>
      <li><Link to="/register">Register</Link></li>
      <li><Link to="/user/trains">View Trains</Link></li>
      <li><Link to="/admin/add-train">Add Train</Link></li>
      <li><Link to="/admin/view-users">View Users</Link></li>
    </ul>
  </nav>
);

export default Navbar;
 
