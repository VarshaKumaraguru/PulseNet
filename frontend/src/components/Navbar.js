import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import "../components/navbarStyle.css";
import logoImage from "../assets/logo.jpg";

const Navbar = () => {
  const [username, setUsername] = useState(sessionStorage.getItem("username")); // Get username from sessionStorage
  const navigate = useNavigate();

  // ✅ Ensure state updates when user navigates back
  useEffect(() => {
    const handleBackNavigation = () => {
      setUsername(sessionStorage.getItem("username")); // Refresh username from sessionStorage
    };

    window.addEventListener("popstate", handleBackNavigation); // Detect back button click
    return () => window.removeEventListener("popstate", handleBackNavigation); // Cleanup
  }, []);

  // ✅ Handle Logout
  const handleLogout = async () => {
    try {
      await axios.post("http://127.0.0.1:5000/logout", {}, { withCredentials: true });
      sessionStorage.removeItem("username"); // Clear session storage
      setUsername(null);
      navigate("/"); // Redirect to SignUp page
    } catch (err) {
      console.error("Logout failed:", err);
    }
  };

  return (
    <nav className="navbar">
      <div className="logo">
        <img src={logoImage} alt="Logo" className="logo-image" />
      </div>
      <ul>
        <li><Link to="/home">Home</Link></li>
        <li><Link to="/visualize">Visualize</Link></li>
        <li><Link to="/team">Team</Link></li>
        <li><Link to="/Chat">Chat</Link></li>
        {username && (
          <li>
            <button onClick={handleLogout} className="signout-btn">
              Sign Out
            </button>
          </li>
        )}
      </ul>
    </nav>
  );
};

export default Navbar;
