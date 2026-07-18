export interface LLMProvider {
  id: string;
  name: string;
  code: string;
  api_endpoint?: string;
  status: string;
}

export interface ModelConfiguration {
  id: string;
  provider_id: string;
  model_name: string;
  temperature: number;
  max_tokens: number;
  is_default: boolean;
}

export interface AISession {
  id: string;
  user_id: string;
  status: string;
}

export interface AIConversation {
  id: string;
  session_id: string;
  title: string;
  current_goal?: string;
  completed_tasks?: Record<string, any>;
  pending_tasks?: Record<string, any>;
  active_entities?: Record<string, any>;
}

export interface AIMessage {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  confidence_score?: 'HIGH' | 'MEDIUM' | 'LOW';
  created_at: string;
}

export interface AgentDefinition {
  id: string;
  name: string;
  code: string;
  capabilities: string;
  priority: number;
  version: number;
}

export interface AgentExecution {
  id: string;
  agent_id: string;
  tool_used?: string;
  duration_ms: number;
  inputs_payload?: Record<string, any>;
  outputs_payload?: Record<string, any>;
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  error_message?: string;
  created_at: string;
}

export interface ToolDefinition {
  id: string;
  name: string;
  description: string;
  input_schema: Record<string, any>;
  required_permissions: string;
  timeout_seconds: number;
}
