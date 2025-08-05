import React from "react";
import { Link } from "react-router-dom";


const Home: React.FC = () => (
  <div className="fade-in" style={{ fontFamily: "sans-serif", background: "#f7f7fa", minHeight: "100vh" }}>
    <header style={{ background: "#222", color: "#fff", padding: "2rem 1rem", textAlign: "center" }}>
      <h1 style={{ fontSize: 40, margin: 0 }}>Void AI</h1>
      <p style={{ fontSize: 20, margin: "1rem 0 0 0" }}>Your personal AI chat and trainer platform</p>
    </header>
    <main className="card-animate" style={{ maxWidth: 700, margin: "2rem auto", background: "#fff", borderRadius: 8, boxShadow: "0 2px 8px #0001", padding: 32, textAlign: "center" }}>
      <h2>Welcome!</h2>
      <p>Void AI lets you chat with an AI and train it on your own data.</p>
      <div style={{ margin: "2rem 0" }}>
        <Link to="/auth">
          <button className="button-animate" style={{ padding: "12px 32px", fontSize: 18, borderRadius: 6, background: "#4b0082", color: "#fff", border: 0, fontWeight: 600, cursor: "pointer" }}>
            Get Started
          </button>
        </Link>
      </div>
      <p style={{ color: "#888" }}>&copy; {new Date().getFullYear()} Void AI</p>
    </main>
  </div>
);

export default Home;
