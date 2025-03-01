import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../components/AuthStyles.css"; // Import the common style

const Login = () => {
    const [user, setUser] = useState({ username: "", password: "" });
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleChange = (e) => {
        setUser({ ...user, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post("http://127.0.0.1:5000/login", user, { withCredentials: true });
            sessionStorage.setItem("username", response.data.username); // Store username in session
            navigate("/home");
        } catch (err) {
            setError(err.response?.data.error || "Invalid credentials");
        }
    };    

    return (
        <div className="auth-container">
            <form className="auth-form" onSubmit={handleSubmit}>
                <h2>Login</h2>
                {error && <p className="error-message">{error}</p>}
                <input type="text" name="username" placeholder="Username" onChange={handleChange} required />
                <input type="password" name="password" placeholder="Password" onChange={handleChange} required />
                <button type="submit">Login</button>
                <p>Don't have an account? <a href="/">Sign Up</a></p>
            </form>
        </div>
    );
};

export default Login;
