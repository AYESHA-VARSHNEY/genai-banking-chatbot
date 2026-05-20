import { useState, useRef, useEffect } from "react";
import ChatWindow from "./components/ChatWindow";
import UploadPanel from "./components/UploadPanel";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hello! I'm your Banking Support Assistant. I can help you with loans, credit cards, savings accounts, and general banking queries. How can I assist you today?",
    },
  ]);
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("chat");

  const sendMessage = async (text) => {
    if (!text.trim()) return;
    const userMsg = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, session_id: sessionId }),
      });
      const data = await res.json();
      setSessionId(data.session_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.reply, sources: data.sources },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "⚠️ Sorry, I couldn't connect to the server. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <div className="header-logo">
          <span className="logo-icon">🏦</span>
          <div>
            <h1>BankAssist AI</h1>
            <p>Powered by RAG · Always here to help</p>
          </div>
        </div>
        <div className="header-tabs">
          <button className={`tab-btn ${activeTab === "chat" ? "active" : ""}`} onClick={() => setActiveTab("chat")}>
            💬 Chat
          </button>
          <button className={`tab-btn ${activeTab === "upload" ? "active" : ""}`} onClick={() => setActiveTab("upload")}>
            📄 Upload Docs
          </button>
        </div>
      </header>
      <main className="main">
        {activeTab === "chat" ? (
          <ChatWindow messages={messages} loading={loading} onSend={sendMessage} />
        ) : (
          <UploadPanel apiBase={API_BASE} />
        )}
      </main>
    </div>
  );
}