import React, { useState, useEffect } from "react";
import { Header } from "./components/Header";
import { QueryInput } from "./components/QueryInput";
import { CitationDrawer } from "./components/CitationDrawer";
import { ResponseView } from "./components/ResponseView";
import { ErrorBanner } from "./components/ErrorBanner";
import { streamChat, ApiClientError } from "./services/api";
import {
  ChatMessage,
  Citation,
  ErrorInfo,
  RetrievalPhase,
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
  const [retrievalPhase, setRetrievalPhase] = useState<RetrievalPhase>("idle");
  const [globalError, setGlobalError] = useState<ErrorInfo | null>(null);
  const [lastQueryInfo, setLastQueryInfo] = useState<{ query: string; topK: number } | null>(null);

  useEffect(() => {
    fetch("/api/v1/debug/retrieval?query=ping&top_k=1")
      .then((res) => setIsBackendConnected(res.ok))
      .catch(() => setIsBackendConnected(false));
  }, []);

  const handleQuerySubmit = async (query: string, topK: number) => {
    setIsLoading(true);
    setRetrievalPhase("retrieving");
    setGlobalError(null);
    setLastQueryInfo({ query, topK });

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
      retrievalPhase: "retrieving",
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);

    try {
      await streamChat(
        { query, conversation_id: conversationId, top_k: topK },
        {
          onMetadata: (meta: SSEMetaDataPayload) => {
            setRetrievalPhase("generating");
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
                      retrievalPhase: "generating",
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
            setRetrievalPhase("complete");
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMsgId
                  ? { ...msg, isStreaming: false, retrievalPhase: "complete" }
                  : msg
              )
            );
            setIsLoading(false);
          },
          onError: (err: Error) => {
            const errCode = err instanceof ApiClientError ? err.code : "STREAM_ERROR";
            const errorObj: ErrorInfo = {
              message: err.message,
              code: errCode,
              retryable: true,
              timestamp: new Date().toLocaleTimeString(),
              query,
              topK,
            };
            setRetrievalPhase("error");
            setGlobalError(errorObj);
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMsgId
                  ? {
                      ...msg,
                      content: msg.content,
                      isStreaming: false,
                      error: errorObj,
                      retrievalPhase: "error",
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
      setRetrievalPhase("error");
      const errorMsg = err instanceof Error ? err.message : "Unknown error occurred";
      const errCode = err instanceof ApiClientError ? err.code : "HTTP_ERROR";
      const errorObj: ErrorInfo = {
        message: errorMsg,
        code: errCode,
        retryable: true,
        timestamp: new Date().toLocaleTimeString(),
        query,
        topK,
      };
      setGlobalError(errorObj);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMsgId
            ? {
                ...msg,
                isStreaming: false,
                error: errorObj,
                retrievalPhase: "error",
              }
            : msg
        )
      );
    }
  };

  const handleRetry = (queryToRetry?: string, topKToRetry?: number) => {
    const q = queryToRetry || lastQueryInfo?.query;
    const k = topKToRetry || lastQueryInfo?.topK || 5;
    if (q) {
      handleQuerySubmit(q, k);
    }
  };

  return (
    <div className="app-container">
      <Header
        conversationId={conversationId}
        isBackendConnected={isBackendConnected}
      />

      {globalError && (
        <ErrorBanner
          error={globalError}
          onRetry={() => handleRetry()}
          onDismiss={() => setGlobalError(null)}
        />
      )}

      <main className="main-content">
        <section className="chat-panel">
          <ResponseView
            messages={messages}
            isStreaming={isLoading}
            retrievalPhase={retrievalPhase}
            onSelectCitation={(c) => setActiveCitation(c)}
            onRetryMessage={(q, k) => handleRetry(q, k)}
          />
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
