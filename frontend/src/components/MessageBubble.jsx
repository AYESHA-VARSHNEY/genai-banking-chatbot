export default function MessageBubble({ message }) {
    const isUser = message.role === "user";
  
    return (
      <div className={`message ${isUser ? "user" : "assistant"}`}>
        {!isUser && <div className="avatar">🏦</div>}
        <div className="bubble-wrap">
          <div className={`bubble ${isUser ? "bubble-user" : "bubble-bot"}`}>
            {message.content}
          </div>
          {message.sources && message.sources.length > 0 && (
            <div className="sources">
              📚 Sources: {message.sources.join(", ")}
            </div>
          )}
        </div>
        {isUser && <div className="avatar user-avatar">👤</div>}
      </div>
    );
  }