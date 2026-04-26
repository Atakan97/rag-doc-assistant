"use client";

import { useRef, useEffect } from "react";

/**
 * Chat screen
 */

// Suggested questions shown in the welcome screen
const SUGGESTIONS = [
  "How do I create background tasks in FastAPI?",
  "Explain FastAPI dependency injection",
  "How to handle file uploads in FastAPI?",
  "What are path parameters vs query parameters?",
];

function renderMarkdown(text) {
  if (!text) return "";

  let html = text;

  // Surrounded code blocks: ```language\ncode\n```
  html = html.replace(
    /```(\w*)\n([\s\S]*?)```/g,
    '<pre><code class="language-$1">$2</code></pre>'
  );

  // Inline code: `code`
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

  // Bold: **text**
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

  // Links: [text](url)
  html = html.replace(
    /\[([^\]]+)\]\(([^)]+)\)/g,
    '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
  );

  // Unordered list items
  html = html.replace(/^[\-\*]\s+(.+)$/gm, "<li>$1</li>");

  // Wrap consecutive <li> items in <ul>
  html = html.replace(/((?:<li>.*<\/li>\n?)+)/g, "<ul>$1</ul>");

  // Numbered list items
  html = html.replace(/^\d+\.\s+(.+)$/gm, "<li>$1</li>");

  // Line breaks for remaining newlines
  html = html.replace(/\n/g, "<br/>");

  // Clean up double <br/> tags
  html = html.replace(/(<br\/>){3,}/g, "<br/><br/>");

  return html;
}

export default function Chat({
  messages,
  isLoading,
  error,
  onSendMessage,
  onSuggestionClick,
}) {
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to the bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    const input = inputRef.current;
    const question = input.value.trim();

    if (question && !isLoading) {
      onSendMessage(question);
      input.value = "";
    }
  };

  // Enter key (submit) and Shift+Enter (new line)
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Welcome screen when there are no messages
  const showWelcome = messages.length === 0;

  return (
    <div className="chat-container glass-card">
      {showWelcome ? (
        /* Welcome screen with suggested questions */
        <div className="welcome-container">
          <h1 className="welcome-title">RAG Documentation Assistant</h1>
          <p className="welcome-description">
            Please ask questions about FastAPI documentation.<br />
            The relevant sections will be found and cited in the sources.
          </p>
          
          <div style={{ marginTop: '20px', width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <h2 className="welcome-title" style={{ fontSize: '1.2rem', marginBottom: '15px' }}>Sample Questions:</h2>
            <div className="welcome-suggestions">
            {SUGGESTIONS.map((suggestion, index) => (
              <button
                key={index}
                className="suggestion-chip"
                onClick={() => onSuggestionClick(suggestion)}
                id={`suggestion-${index}`}
              >
                {suggestion}
              </button>
            ))}
            </div>
          </div>
        </div>
      ) : (
        /* Message list */
        <div className="messages-area">
          {messages.map((msg, index) => (
            <div key={index} className={`message message-${msg.role}`}>
              <div className="message-bubble">
                {msg.role === "assistant" ? (
                  <div
                    dangerouslySetInnerHTML={{
                      __html: renderMarkdown(msg.content),
                    }}
                  />
                ) : (
                  msg.content
                )}
              </div>
            </div>
          ))}

          {/* Typing indicator while waiting for response */}
          {isLoading && (
            <div className="message message-assistant">
              <div className="message-bubble">
                <div className="typing-indicator">
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                </div>
              </div>
            </div>
          )}

          {/* Error message display */}
          {error && (
            <div className="error-banner">
              <span className="error-icon" role="img" aria-label="warning">&#9888;</span>
              {error}
            </div>
          )}

          {/* Invisible element for auto-scroll anchor */}
          <div ref={messagesEndRef} />
        </div>
      )}

      {/* Input bar */}
      <form className="chat-input-bar" onSubmit={handleSubmit}>
        <input
          ref={inputRef}
          className="chat-input"
          type="text"
          placeholder="Please ask questions about FastAPI docs."
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          id="chat-input"
          autoComplete="off"
        />
        <button
          type="submit"
          className="send-button"
          disabled={isLoading}
          id="send-button"
        >
          Submit
        </button>
      </form>
    </div>
  );
}
