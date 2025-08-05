import React from "react";

const About: React.FC = () => (
    <div className="fade-in" style={{ fontFamily: "sans-serif", background: "#f7f7fa", minHeight: "100vh" }}>
        <header style={{ background: "#222", color: "#fff", padding: "2rem 1rem", textAlign: "center" }}>
            <h1>About Void AI</h1>
        </header>
        <main style={{ maxWidth: 700, margin: "2rem auto", background: "#fff", borderRadius: 8, boxShadow: "0 2px 8px #0001", padding: 32 }}>
            <h2>What is Void AI?</h2>
            <p>Void AI is your personal AI chat and training platform. Chat with an AI, train it on your own data, and explore the future of conversational AI.</p>
            <h2>Features</h2>
            <ul style={{ textAlign: "left", lineHeight: 2 }}>
                <li>Secure authentication</li>
                <li>Personal chat history</li>
                <li>Custom AI training</li>
                <li>Modern, responsive UI</li>
            </ul>
            <h2>Open Source</h2>
            <p>This project is open source and contributions are welcome!</p>
        </main>
    </div>
);

export default About;
