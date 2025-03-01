import React, { useEffect } from "react";
import infoImage1 from "../assets/home_pic1.png";
import infoImage2 from "../assets/home_pic2.png";
import "../components/infoStyle.css";

const InfoSection = () => {
  useEffect(() => {
    const infoSections = document.querySelectorAll(".info-container");

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("show");
          }
        });
      },
      { threshold: 0.3 } // Trigger animation when 30% of the section is visible
    );

    infoSections.forEach((section) => observer.observe(section));

    return () => {
      infoSections.forEach((section) => observer.unobserve(section));
    };
  }, []);

  return (
    <div className="info-section">
      {/* First Section (Image Left, Text Right) */}
      <div className="info-container left">
        <img src={infoImage1} alt="Info1" />
        <p>
        Our flexible, wireless ECG PCB provides a lightweight and comfortable solution for real-time heart monitoring. Designed for mobility and ease of use, Perfect for remote health monitoring, early detection, and improved accessibility in cardiac care
        </p>
      </div>

      {/* Second Section (Image Right, Text Left) */}
      <div className="info-container right reverse">
      <img src={infoImage2} alt="Info2" />
        <p>
          Enables continuous heart monitoring by capturing real-time ECG signals and wirelessly transmitting them to a connected device. 
        </p>
      </div>
    </div>
  );
};

export default InfoSection;