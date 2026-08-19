/**
 * Domain model types and contracts for Corporate Document Assistant frontend.
 * Synchronized with backend Pydantic models.
 */

export interface Citation {
  file_name: string;
  page_number: number;
  chunk_id: string;
  excerpt: string;
  relevance_score: number;
}

export interface FinOpsMetadata {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  estimated_cost_usd: number;
  execution_time_seconds: number;
  is_cached: boolean;
}

export interface ChatRequest {
  query: string;
  conversation_id: string;
  top_k?: number;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  confidence_score: number;
  grounded: boolean;
  latency_ms: number;
  finops: FinOpsMetadata;
}

export interface RetrievalResult {
  chunk_id: string;
  text: string;
  file_name: string;
  page_number: number;
  relevance_score: number;
  retrieval_method: string;
}

export interface DebugRetrievalResponse {
  query: string;
  dense_hits: RetrievalResult[];
  sparse_hits: RetrievalResult[];
  rrf_fused: RetrievalResult[];
  final_reranked: RetrievalResult[];
}

export interface SSEMetaDataPayload {
  conversation_id: string;
  confidence_score: number;
  grounded: boolean;
  citations: Citation[];
}

export interface SSETokenPayload {
  delta: string;
}

export interface SSEDonePayload {
  status: string;
  finish_reason: string;
}

export interface SSEErrorPayload {
  error: string;
  code: string;
}

export type SSEEvent =
  | { type: "metadata"; payload: SSEMetaDataPayload }
  | { type: "token"; payload: SSETokenPayload }
  | { type: "done"; payload: SSEDonePayload }
  | { type: "error"; payload: SSEErrorPayload };

export type ConfidenceTier = "high" | "medium" | "low";

export type RetrievalPhase =
  | "idle"
  | "retrieving"
  | "reranking"
  | "generating"
  | "complete"
  | "error";

export interface ErrorInfo {
  message: string;
  code?: string;
  retryable?: boolean;
  timestamp?: string;
  query?: string;
  topK?: number;
}

export interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  content: string;
  citations?: Citation[];
  confidenceScore?: number;
  grounded?: boolean;
  timestamp: string;
  finops?: FinOpsMetadata;
  isStreaming?: boolean;
  error?: ErrorInfo;
  retrievalPhase?: RetrievalPhase;
}

export interface QueryState {
  isSubmitting: boolean;
  currentQuery: string;
  selectedTopK: number;
  activeCitation: Citation | null;
  errorMessage: string | null;
  lastFailedQuery?: string;
  lastFailedTopK?: number;
  retrievalPhase?: RetrievalPhase;
}
