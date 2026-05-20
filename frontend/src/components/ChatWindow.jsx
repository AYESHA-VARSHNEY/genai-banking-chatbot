import { useRef, useEffect, useState } from "react";
import MessageBubble from "./MessageBubble";

export default function ChatWindow({ messages, loading, onSend }) {
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSubmit = () => {
    if (input.trim()) {
      onSend(input.trim());
      setInput("");
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const suggestions = [
    "What is a personal loan?",
    "What is the interest rate for credit cards?",
    "How to improve my CIBIL score?",
    "What documents do I need for a home loan?",
  ];

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}
        {loading && (
          <div className="message assistant">
            <div className="bubble typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {messages.length === 1 && (
        <div className="suggestions">
          <p className="suggestions-label">Quick questions:</p>
          <div className="suggestions-grid">
            {suggestions.map((s, i) => (
              <button key={i} className="suggestion-chip" onClick={() => onSend(s)}>
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="chat-input-area">
        <textarea
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask me about loans, credit cards, savings..."
          rows={1}
        />
        <button className="send-btn" onClick={handleSubmit} disabled={loading || !input.trim()}>
          ➤
        </button>
      </div>
    </div>
  );
}