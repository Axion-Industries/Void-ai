import React from "react";
import { Link } from "react-router-dom";

const NotFound: React.FC = () => (
    <div className="fade-in" style={{ fontFamily: "sans-serif", background: "#f7f7fa", minHeight: "100vh", textAlign: "center" }}>
        <header style={{ background: "#222", color: "#fff", padding: "2rem 1rem" }}>
            <h1>404 - Page Not Found</h1>
        </header>
        <main style={{ maxWidth: 700, margin: "2rem auto", background: "#fff", borderRadius: 8, boxShadow: "0 2px 8px #0001", padding: 32 }}>
            <p>Sorry, the page you are looking for does not exist.</p>
            <Link to="/">
                <button style={{ padding: "10px 24px", borderRadius: 6, background: "#4b0082", color: "#fff", border: 0, fontWeight: 600, cursor: "pointer", marginTop: 16 }}>
                    Go Home
                </button>
            </Link>
        </main>
    </div>
);

export default NotFound;
