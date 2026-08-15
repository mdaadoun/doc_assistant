import React, { useState, useEffect } from "react";
import { Header } from "./components/Header";
import { QueryInput } from "./components/QueryInput";
import { CitationDrawer } from "./components/CitationDrawer";
import { ResponseView } from "./components/ResponseView";
import { streamChat } from "./services/api";
import {
  ChatMessage,
  Citation,
  SSEMetaDataPayload,
} from "./types";

export const App: React.FC = () => {
  const [conversationId] = useState<string>(() => {
    return "session-" + Math.random().toString(36).substring(2, 11);
  });
  const [isBackendConnected, setIsBackendConnected] = useState<boolean>(true);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [citations, setCitations] = useState<Citation[]>([]);
  const [activeCitation, setActiveCitation] = useState<Citation | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    // Quick probe to verify backend availability
    fetch("/api/v1/debug/retrieval?query=ping&top_k=1")
      .then((res) => setIsBackendConnected(res.ok))
      .catch(() => setIsBackendConnected(false));
  }, []);

  const handleQuerySubmit = async (query: string, topK: number) => {
    setIsLoading(true);

    const userMessage: ChatMessage = {
      id: "usr-" + Date.now(),
      sender: "user",
      content: query,
      timestamp: new Date().toLocaleTimeString(),
    };

    const assistantMsgId = "ast-" + Date.now();
    const assistantMessage: ChatMessage = {
      id: assistantMsgId,
      sender: "assistant",
      content: "",
      timestamp: new Date().toLocaleTimeString(),
      isStreaming: true,
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);

    try {
      await streamChat(
        { query, conversation_id: conversationId, top_k: topK },
        {
          onMetadata: (meta: SSEMetaDataPayload) => {
            if (meta.citations && meta.citations.length > 0) {
              setCitations(meta.citations);
            }
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMsgId
                  ? {
                      ...msg,
                      confidenceScore: meta.confidence_score,
                      grounded: meta.grounded,
                      citations: meta.citations,
                    }
                  : msg
              )
            );
          },
          onToken: (token: string) => {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMsgId
                  ? { ...msg, content: msg.content + token }
                  : msg
              )
            );
          },
          onDone: () => {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMsgId
                  ? { ...msg, isStreaming: false }
                  : msg
              )
            );
            setIsLoading(false);
          },
          onError: (err: Error) => {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMsgId
                  ? {
                      ...msg,
                      content: msg.content + `\n\n[Error: ${err.message}]`,
                      isStreaming: false,
                    }
                  : msg
              )
            );
            setIsLoading(false);
          },
        }
      );
    } catch (err) {
      setIsLoading(false);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMsgId
            ? {
                ...msg,
                content:
                  msg.content ||
                  `Unable to complete request: ${
                    err instanceof Error ? err.message : "Unknown error"
                  }`,
                isStreaming: false,
              }
            : msg
        )
      );
    }
  };

  return (
    <div className="app-container">
      <Header
        conversationId={conversationId}
        isBackendConnected={isBackendConnected}
      />

      <main className="main-content">
        <section className="chat-panel">
          <ResponseView messages={messages} isStreaming={isLoading} />
          <QueryInput onSubmit={handleQuerySubmit} isLoading={isLoading} />
        </section>

        <CitationDrawer
          citations={citations}
          activeCitation={activeCitation}
          onSelectCitation={(c) => setActiveCitation(c)}
        />
      </main>
    </div>
  );
};

export default App;
