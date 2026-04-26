"use client";

/**
 * Source panel for retrieved documents.
 */

import { useState } from "react";

export default function SourcesPanel({ sources }) {

  // Track whether the panel is expanded on mobile
  const [isExpanded, setIsExpanded] = useState(false);
  const isEmpty = !sources || sources.length === 0;

  return (
    <>
      {/* Mobile toggle button */}
      <button
        className="sources-toggle"
        onClick={() => setIsExpanded(!isExpanded)}
        id="sources-toggle"
      >
        Sources ({sources?.length || 0})
        <span>{isExpanded ? "▲" : "▼"}</span>
      </button>

      <div
        className={`sources-section glass-card ${
          isExpanded ? "" : "mobile-hidden"
        }`}
        style={{
          display: isExpanded || typeof window === "undefined" ? undefined : undefined,
        }}
      >
        {/* Panel header */}
        <div className="sources-header">
          <h2 className="sources-title">
          Sources
          </h2>
        </div>

        {isEmpty ? (
          /* Empty state */
          <div className="sources-empty">
            <p className="sources-empty-text">
              Sources will appear here after you ask a question.
            </p>
          </div>
        ) : (
          /* Source list */
          <div className="sources-list">
            {sources.map((source, index) => {
              const percentage = Math.round(source.similarity * 100);
              return (
              <div
                key={index}
                className="source-card"
                id={`source-card-${index}`}
              >
                {/* Title */}
                <div className="source-card-header">
                  <span className="source-card-title">{source.title}</span>
                </div>

                {/* Similarity Progress Bar */}
                <div style={{ marginTop: '10px', marginBottom: '8px', display: 'flex', alignItems: 'center' }}>
                  <span style={{ marginRight: '10px', fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
                    Similarity:
                  </span>
                  <div style={{
                    height: '20px',
                    flex: 1,
                    backgroundColor: '#e0e0df',
                    borderRadius: '50px',
                    overflow: 'hidden'
                  }}>
                    <div style={{
                      height: '100%',
                      width: `${percentage}%`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      fontWeight: 'bold',
                      fontSize: '0.75rem',
                      backgroundColor: '#4caf50',
                      borderRadius: 'inherit',
                      transition: 'width 0.2s ease-in',
                    }}>
                      {`${percentage}%`}
                    </div>
                  </div>
                </div>

                {/* GitHub URL */}
                <a
                  href={source.source_url}
                  className="source-card-url"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {formatUrl(source.source_url)}
                </a>

                {/* Snippet preview */}
                <p className="source-card-snippet">{source.snippet}</p>
              </div>
              );
            })}
          </div>
        )}
      </div>
    </>
  );
}

/**
 * Shorten a GitHub URL for display.
 */
function formatUrl(url) {
  if (!url) return "";

  try {
    const parts = url.split("/blob/");
    if (parts.length === 2) {
      // Extract repo name from the first part
      const repoParts = parts[0].split("/");
      const repoName = repoParts[repoParts.length - 1];

      // Get the file path
      const pathAfterBranch = parts[1].split("/").slice(1).join("/");

      // Keep the URL short
      const pathSegments = pathAfterBranch.split("/");
      if (pathSegments.length > 3) {
        const shortPath = pathSegments.slice(-2).join("/");
        return `${repoName}/.../${shortPath}`;
      }
      return `${repoName}/${pathAfterBranch}`;
    }
  } catch {
  }

  return url.length > 60 ? url.substring(0, 57) + "..." : url;
}
