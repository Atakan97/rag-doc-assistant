"use client";

/**
 * Main page of the RAG Documentation Assistant.
 */

import { useState, useCallback } from "react";
import Chat from "../components/Chat";
import SourcesPanel from "../components/SourcesPanel";
import { queryRAG } from "../lib/api";

export default function Home() {
  // Chat messages, array of {role: "user"|"assistant"}
  const [messages, setMessages] = useState([]);

  // Sources from the most recent assistant response
  const [currentSources, setCurrentSources] = useState([]);

  // Loading and error states
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Sending a new question to the RAG pipeline.
   */
  const handleSendMessage = useCallback(async (question) => {
    // Clear any previous error
    setError(null);

    // Add the user's message to the chat
    const userMessage = { role: "user", content: question };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Call the RAG backend
      const result = await queryRAG(question);

      // Add the assistant's response
      const assistantMessage = {
        role: "assistant",
        content: result.answer,
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Update the sources panel with retrieved documents
      setCurrentSources(result.sources || []);
    } catch (err) {
      // Display error in the chat
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Clicking a suggestion from the welcome screen.
   */
  const handleSuggestionClick = useCallback(
    (suggestion) => {
      handleSendMessage(suggestion);
    },
    [handleSendMessage]
  );

  /**
   * Resets the chat to the initial welcome screen.
   */
  const handleGoHome = useCallback(() => {
    setMessages([]);
    setCurrentSources([]);
    setError(null);
  }, []);

  return (
    <div className="app-container">
      {/* Header with title */}
      <header className="header">
        <div className="header-brand">
          <button className="header-title-btn" onClick={handleGoHome}>
            Documentation Assistant
          </button>
          <div className="header-subtitle">
            <span style={{ opacity: 0.6, fontSize: '0.9em', marginRight: '4px' }}>powered by</span>
            LangChain + Groq + Supabase pgvector
          </div>
        </div>
      </header>

      {/* Chat + Sources Panel side by side */}
      <main className="main-content">
        <div className="chat-section">
          <Chat
            messages={messages}
            isLoading={isLoading}
            error={error}
            onSendMessage={handleSendMessage}
            onSuggestionClick={handleSuggestionClick}
          />
        </div>

        <SourcesPanel sources={currentSources} />
      </main>
    </div>
  );
}
