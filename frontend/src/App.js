import React from "react";
import { BrowserRouter as Router, Routes, Route, useLocation, Navigate } from "react-router-dom";
import SignUp from "./components/SignUp";
import Login from "./components/Login";
import Home from "./components/Home";
import TeamSection from "./components/TeamSection";
import Visualize from "./components/Visualize";
import Navbar from "./components/Navbar"; 
import Chat from "./components/Chatbot";

const App = () => {
    return (
        <Router>
            <MainLayout />
        </Router>
    );
};

const MainLayout = () => {
    const location = useLocation();

    return (
        <>
            <Routes>
                <Route path="/" element={<SignUp />} />
                <Route path="/login" element={<Login />} />
                <Route path="/home" element={<Home />} />
                <Route path="/team" element={<TeamSection />} />
                <Route path="/visualize" element={<Visualize />} />
                <Route path="/chat" element={<Chat />} /> 
                
                {/* Redirect unknown routes to Home */}
                <Route path="*" element={<Navigate to="/home" />} />
            </Routes>
        </>
    );
};

export default App;