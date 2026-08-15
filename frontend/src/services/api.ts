/**
 * API client service for Corporate Document Assistant backend endpoints.
 * Handles SSE streaming chat requests and retrieval diagnostics.
 */

import {
  ChatRequest,
  Citation,
  DebugRetrievalResponse,
  SSEMetaDataPayload,
} from "../types";

export class ApiClientError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(message: string, status = 500, code = "API_ERROR") {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.code = code;
  }
}

export interface StreamCallbacks {
  onMetadata?: (meta: SSEMetaDataPayload) => void;
  onToken?: (token: string) => void;
  onDone?: (status: string) => void;
  onError?: (error: Error) => void;
}

const API_BASE = "/api/v1";

export async function streamChat(
  request: ChatRequest,
  callbacks: StreamCallbacks
): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify(request),
    });
  } catch (err) {
    const error = new ApiClientError(
      err instanceof Error ? err.message : "Network error connecting to API",
      0,
      "NETWORK_ERROR"
    );
    callbacks.onError?.(error);
    throw error;
  }

  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    try {
      const errJson = await response.json();
      if (errJson && errJson.detail) {
        errorDetail = errJson.detail;
      }
    } catch {
      // Use fallback error message
    }
    const error = new ApiClientError(errorDetail, response.status, "HTTP_ERROR");
    callbacks.onError?.(error);
    throw error;
  }

  const reader = response.body?.getReader();
  if (!reader) {
    const error = new ApiClientError("No readable stream in response body", 500);
    callbacks.onError?.(error);
    throw error;
  }

  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const blocks = buffer.split("\n\n");
      buffer = blocks.pop() || "";

      for (const block of blocks) {
        const lines = block.split("\n");
        let eventType = "message";
        let dataStr = "";

        for (const line of lines) {
          if (line.startsWith("event:")) {
            eventType = line.slice(6).trim();
          } else if (line.startsWith("data:")) {
            dataStr = line.slice(5).trim();
          }
        }

        if (!dataStr) continue;

        try {
          const parsed = JSON.parse(dataStr);
          if (eventType === "metadata" && callbacks.onMetadata) {
            callbacks.onMetadata(parsed as SSEMetaDataPayload);
          } else if (eventType === "token" && callbacks.onToken) {
            callbacks.onToken(parsed.delta || "");
          } else if (eventType === "done" && callbacks.onDone) {
            callbacks.onDone(parsed.status || "completed");
          } else if (eventType === "error") {
            const err = new ApiClientError(
              parsed.error || "Server stream error",
              500,
              parsed.code || "STREAM_ERROR"
            );
            callbacks.onError?.(err);
          }
        } catch {
          // Fallback if data is raw string
          if (eventType === "token" && callbacks.onToken) {
            callbacks.onToken(dataStr);
          }
        }
      }
    }
  } catch (err) {
    const streamErr = new ApiClientError(
      err instanceof Error ? err.message : "Error reading SSE stream",
      500,
      "STREAM_READ_ERROR"
    );
    callbacks.onError?.(streamErr);
    throw streamErr;
  }
}

export async function getDebugRetrieval(
  query: string,
  topK = 5
): Promise<DebugRetrievalResponse> {
  const url = `${API_BASE}/debug/retrieval?query=${encodeURIComponent(
    query
  )}&top_k=${topK}`;
  const response = await fetch(url, {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new ApiClientError(
      `Debug retrieval failed: ${response.statusText}`,
      response.status
    );
  }

  return (await response.json()) as DebugRetrievalResponse;
}
