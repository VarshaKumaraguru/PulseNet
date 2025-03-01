import React from "react";
import "../components/teamStyle.css";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import profileImage1 from "../assets/Varsha.JPG";
import profileImage2 from "../assets/Shevarthna.jpg";
import profileImage3 from "../assets/Harish.JPG";

// Profile data with LinkedIn URLs
const teamMembers = [
  {
    image: profileImage1,
    name: "Varsha",
    title: "Pre-Final Year Student",
    linkedin: "https://www.linkedin.com/in/varsha-kumaraguru/",
  },
  {
    image: profileImage2,
    name: "Shevarthna",
    title: "Pre-Final Year Student",
    linkedin: "https://www.linkedin.com/in/shevarthna-m-737204328/",
  },
  {
    image: profileImage3,
    name: "Harish",
    title: "Pre-Final Year Student",
    linkedin: "https://www.linkedin.com/in/harish-p-645aba317/",
  },
];

const ProfileCard = ({ image, name, title, linkedin }) => {
  return (
    <div className="profile-card">
      <div className="profile-frame">
        <img src={image} alt={name} className="profile-image" />
      </div>
      <div className="profile-info">
        <p className="profile-title">{title}</p>
        <h2 className="profile-name">{name}</h2>

        {/* LinkedIn Icon */}
        <a href={linkedin} target="_blank" rel="noopener noreferrer" className="linkedin-icon">
          <i className="fab fa-linkedin"></i>
        </a>
      </div>
    </div>
  );
};

export default function TeamSection() {
  return (
    <div className="background-page">
      <Navbar />
      
      {/* Content Wrapper */}
      <div className="team-content">
        <h1>Meet the Team</h1>
        <div className="card-container">
          {teamMembers.map((member, index) => (
            <ProfileCard
              key={index}
              image={member.image}
              name={member.name}
              title={member.title}
              linkedin={member.linkedin}
            />
          ))}
        </div>
      </div>

      {/* Footer stays at the bottom */}
      <Footer />
    </div>
  );
}