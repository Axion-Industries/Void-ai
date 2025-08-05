import { User } from "@supabase/supabase-js";
import React, { useEffect, useRef, useState } from "react";
import { getTrainingStatus, sendChatMessage, trainAI } from "./api";
import { Auth } from "./auth";
import { Profile, supabase } from "./supabase";

const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);

  // Chat state
  const [chatInput, setChatInput] = useState("");
  const [chatHistory, setChatHistory] = useState<{ user: string; ai: string }[]>([]);
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Training state
  const [trainText, setTrainText] = useState("");
  const [trainStatus, setTrainStatus] = useState<string>("");
  const [trainLoading, setTrainLoading] = useState(false);

  // Check authentication status and fetch profile on mount
  useEffect(() => {
    const initializeSession = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      const user = session?.user;
      setUser(user ?? null);
      if (user) {
        await fetchProfile(user);
      }
      setLoading(false);
    }

    initializeSession();

    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (_event, session) => {
      const currentUser = session?.user ?? null;
      setUser(currentUser);
      if (currentUser) {
        await fetchProfile(currentUser);
      } else {
        setProfile(null);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  // Load chat history when user is authenticated
  useEffect(() => {
    if (user) {
      loadChatHistory();
    }
  }, [user]);

  // Status polling
  useEffect(() => {
    if (!user) return;

    const interval = setInterval(async () => {
      const status = await getTrainingStatus();
      setTrainStatus(status.message || status.status || "");
    }, 2000);
    return () => clearInterval(interval);
  }, [user]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  const loadChatHistory = async () => {
    if (!user) return;

    try {
      const { data, error } = await supabase
        .from('chats')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: true });

      if (error) throw error;

      if (data) {
        setChatHistory(data.map(chat => ({
          user: chat.message,
          ai: chat.response
        })));
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const saveTrainingSession = async (text: string) => {
    if (!user) return;

    try {
      const { error } = await supabase
        .from('training_sessions')
        .insert({
          user_id: user.id,
          text,
          status: 'pending'
        });

      if (error) throw error;
    } catch (error) {
      console.error('Error saving training session:', error);
    }
  };

  const handleSendChat = async () => {
    if (!chatInput.trim() || !user) return;
    setChatLoading(true);
    setChatHistory((h) => [...h, { user: chatInput, ai: "..." }]);
    try {
      const aiResponse = await sendChatMessage(chatInput, user.id);
      setChatHistory((h) => [
        ...h.slice(0, -1),
        { user: chatInput, ai: aiResponse },
      ]);
    } catch (e: any) {
      setChatHistory((h) => [
        ...h.slice(0, -1),
        { user: chatInput, ai: e.message || "Error" },
      ]);
    }
    setChatInput("");
    setChatLoading(false);
  };

  const handleTrain = async () => {
    if (!trainText.trim() || !user) return;
    setTrainLoading(true);
    setTrainStatus("Training started...");
    await saveTrainingSession(trainText);
    await trainAI(trainText);
    setTrainText("");
    setTrainLoading(false);
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    setChatHistory([]);
  };

  // --> NEW: Function to fetch user profile
  const fetchProfile = async (user: User) => {
    try {
      const { data, error, status } = await supabase
        .from('profiles')
        .select(`*`)
        .eq('id', user.id)
        .single();

      if (error && status !== 406) {
        throw error;
      }

      if (data) {
        setProfile(data);
      }
    } catch (error: any) {
      console.error('Error fetching profile:', error.message);
    }
  };

  if (loading) {
    return (
      <div className="fade-in" style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontFamily: "sans-serif"
      }}>
        Loading...
      </div>
    );
  }

  if (!user) {
    return (
      <div className="fade-in" style={{ fontFamily: "sans-serif", background: "#f7f7fa", minHeight: "100vh" }}>
        <header style={{ background: "#222", color: "#fff", padding: "1rem", textAlign: "center" }}>
          <h1>Void AI Chat & Trainer</h1>
        </header>
        <Auth onAuthSuccess={() => { }} />
      </div>
    );
  }

  return (
    <div className="fade-in" style={{ fontFamily: "sans-serif", background: "#f7f7fa", minHeight: "100vh" }}>
      <header style={{ background: "#222", color: "#fff", padding: "1rem", textAlign: "center", position: "relative" }}>
        <h1>Void AI Chat & Trainer</h1>
        <div style={{ position: "absolute", top: "1rem", right: "1rem" }}>
          <span style={{ marginRight: "1rem" }}>Welcome, {profile?.username || user.email}</span>
          <button
            onClick={handleSignOut}
            className="button-animate"
            style={{
              padding: "4px 8px",
              borderRadius: 4,
              background: "#666",
              color: "#fff",
              border: 0,
              cursor: "pointer",
              fontSize: 12
            }}
          >
            Sign Out
          </button>
        </div>
      </header>
      <main className="card-animate" style={{ maxWidth: 700, margin: "2rem auto", background: "#fff", borderRadius: 8, boxShadow: "0 2px 8px #0001", padding: 24 }}>
        {/* Chat Section */}
        <section>
          <h2>Chat</h2>
          <div style={{ minHeight: 200, maxHeight: 300, overflowY: "auto", background: "#f3f3f7", borderRadius: 6, padding: 12, marginBottom: 12, border: "1px solid #eee" }}>
            {chatHistory.length === 0 && <div style={{ color: "#888" }}>No messages yet.</div>}
            {chatHistory.map((msg, i) => (
              <div key={i} style={{ marginBottom: 10 }} className="fade-in">
                <div style={{ fontWeight: 600, color: "#333" }}>You:</div>
                <div style={{ marginBottom: 4 }}>{msg.user}</div>
                <div style={{ fontWeight: 600, color: "#4b0082" }}>Void AI:</div>
                <div style={{ marginBottom: 4, whiteSpace: "pre-wrap" }}>{msg.ai}</div>
                <hr style={{ border: 0, borderTop: "1px solid #eee" }} />
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendChat()}
              placeholder="Type your message..."
              style={{ flex: 1, padding: 8, borderRadius: 4, border: "1px solid #ccc" }}
              disabled={chatLoading}
              className="fade-in"
            />
            <button
              onClick={handleSendChat}
              disabled={chatLoading || !chatInput.trim()}
              className="button-animate"
              style={{ padding: "8px 16px", borderRadius: 4, background: "#4b0082", color: "#fff", border: 0, fontWeight: 600, cursor: chatLoading ? "not-allowed" : "pointer" }}
            >
              {chatLoading ? "..." : "Send"}
            </button>
          </div>
        </section>
        <hr style={{ margin: "2rem 0" }} />
        {/* Training Section */}
        <section>
          <h2>Train AI</h2>
          <textarea
            value={trainText}
            onChange={(e) => setTrainText(e.target.value)}
            placeholder="Paste training text here..."
            rows={4}
            style={{ width: "100%", padding: 8, borderRadius: 4, border: "1px solid #ccc", marginBottom: 8 }}
            disabled={trainLoading}
            className="fade-in"
          />
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <button
              onClick={handleTrain}
              disabled={trainLoading || !trainText.trim()}
              className="button-animate"
              style={{ padding: "8px 16px", borderRadius: 4, background: "#00824b", color: "#fff", border: 0, fontWeight: 600, cursor: trainLoading ? "not-allowed" : "pointer" }}
            >
              {trainLoading ? "Training..." : "Train"}
            </button>
            <span style={{ color: trainLoading ? "#888" : "#333" }}>
              {trainStatus}
            </span>
          </div>
        </section>
      </main>
      <footer style={{ textAlign: "center", color: "#888", padding: 16 }}>
        &copy; {new Date().getFullYear()} Void AI
      </footer>
    </div>
  );
};

export default App;
