import React from "react";
import { Link } from "react-router-dom"; // Import Link from react-router-dom
import "../components/heroStyle.css";

const HeroSection = () => {
  return (
    <div className="hero">
      <div className="hero-text-box"> {/* Changed class to className */}
        <h1>Welcome to PulseNet</h1>
        <h2>A flexible, wireless ECG PCB for seamless and real-time heart monitoring anytime, anywhere</h2>
      </div>
      
      {/* Wrap button inside Link for navigation */}
      <Link to="/visualize">
        <button className="hero-button">Visualize</button> {/* Changed class to className */}
      </Link>
    </div>
  );
};

export default HeroSection;
