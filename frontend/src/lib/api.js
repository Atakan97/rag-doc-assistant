/**
 * API client for communicating with the RAG backend.
 */

// Backend API URL
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:7860";

/**
 * Send a question to the RAG pipeline and get an answer with sources.
 */
export async function queryRAG(question, topK = 6) {
  try {
    const response = await fetch(`${API_BASE_URL}/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question,
        collection: "fastapi",
        top_k: topK,
      }),
    });

    // HTTP error codes
    if (!response.ok) {
      if (response.status === 429) {
        throw new Error(
          "Rate limit reached. Please try again."
        );
      }
      if (response.status === 400) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Invalid request. Please check your question.");
      }
      if (response.status >= 500) {
        throw new Error(
          "The backend service is currently unavailable. Please try again."
        );
      }
      throw new Error(`Request failed with status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    // Network errors
    if (error.name === "TypeError" && error.message.includes("fetch")) {
      throw new Error(
        "Unable to reach the backend. The service may be starting up. Please try again."
      );
    }
    throw error;
  }
}

/**
 * Backend health check
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    const data = await response.json();
    return data.ok === true;
  } catch {
    return false;
  }
}
