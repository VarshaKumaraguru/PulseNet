import React, { useState } from "react";
import Navbar from "../components/Navbar"; // Import Navbar
import "../components/chatStyle.css"; // Import Chat styles
import sendIcon from "../assets/send.png"; // Import send button icon

const Chat = () => {
    const [messages, setMessages] = useState([]); // Store chat messages
    const [query, setQuery] = useState(""); // Store user's input
    const [isLoading, setIsLoading] = useState(false); // Track loading state

    // Function to handle sending messages
    const handleSendMessage = async () => {
        if (query.trim() === "") return; // Prevent sending empty messages

        setIsLoading(true); // Show loader
        const userMessage = { text: query, sender: "user" };
        setMessages((prevMessages) => [...prevMessages, userMessage]);

        try {
            // Send query to backend
            const response = await fetch("http://localhost:5000/query", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ query }),
            });

            if (!response.ok) {
                throw new Error("Failed to fetch response from the backend.");
            }

            const data = await response.json();
            const botMessage = { text: data.response, sender: "bot" };
            setMessages((prevMessages) => [...prevMessages, botMessage]);
        } catch (error) {
            console.error("Error:", error);
            const botMessage = { text: "Sorry, something went wrong. Please try again.", sender: "bot" };
            setMessages((prevMessages) => [...prevMessages, botMessage]);
        } finally {
            setIsLoading(false); // Hide loader
            setQuery(""); // Clear input box after sending
        }
    };

    return (
        <div>
            <Navbar /> {/* Include Navbar */}
            <div className="chat-container">
                {/* Chat Messages */}
                <div className="chat-text">
                    <div className="chat-box">
                        {messages.map((msg, index) => (
                            <div key={index} className={`message-container ${msg.sender}`}>
                                <div className={`chat-message ${msg.sender}`}>
                                    {msg.text}
                                </div>
                            </div>
                        ))}
                        {isLoading && (
                            <div className="message-container bot">
                                <div className="chat-message bot">Loading...</div>
                            </div>
                        )}
                    </div>

                    {/* Chat Input */}
                    <div className="chat-input-container">
                        <input
                            type="text"
                            placeholder="Type your message..."
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            className="chat-input"
                        />
                        <button onClick={handleSendMessage} className="send-button" disabled={isLoading}>
                            <img src={sendIcon} alt="Send" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Chat;