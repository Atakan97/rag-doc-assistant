import "./globals.css";

/**
 * Layout for the RAG Documentation Assistant.
 */
export const metadata = {
  title: "RAG Documentation Assistant",
  description:
    "Ask questions about FastAPI documentation. Powered by LangChain, Groq, and Supabase pgvector.",
  openGraph: {
    title: "RAG Documentation Assistant",
    description:
      "AI-powered FastAPI docs assistant with source citations. Built with LangChain + FastAPI + Next.js.",
    type: "website",
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📚</text></svg>" />
      </head>
      <body>{children}</body>
    </html>
  );
}
