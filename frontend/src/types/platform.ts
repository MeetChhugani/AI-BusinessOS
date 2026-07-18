export interface NotificationLog {
  id: string;
  user_id: string;
  title: string;
  message: string;
  channel: 'IN_APP' | 'EMAIL' | 'SMS' | 'WHATSAPP' | 'PUSH';
  priority: 'LOW' | 'NORMAL' | 'HIGH' | 'URGENT';
  delivery_status: 'PENDING' | 'SENT' | 'FAILED';
  read_status: boolean;
  created_at: string;
}

export interface WorkflowTrigger {
  id: string;
  trigger_type: string;
  event_name: string;
  parameters?: Record<string, any>;
}

export interface WorkflowCondition {
  id: string;
  operator: string;
  expression: Record<string, any>;
}

export interface WorkflowAction {
  id: string;
  action_type: string;
  parameters: Record<string, any>;
  sequence_order: number;
}

export interface WorkflowDefinition {
  id: string;
  name: string;
  code: string;
  version: number;
  description?: string;
  status: string;
  created_at: string;
}

export interface AuditEvent {
  id: string;
  entity_name: string;
  entity_id: string;
  operation: string;
  old_value?: string;
  new_value?: string;
  source: 'API' | 'SCHEDULER' | 'WORKFLOW' | 'AI' | 'MANUAL';
  user_id?: string;
  request_id?: string;
  ip_address?: string;
  browser?: string;
  created_at: string;
}

export interface FileMetadata {
  id: string;
  name: string;
  folder_id?: string;
  mime_type: string;
  file_size_bytes: number;
  storage_path: string;
  sha256_checksum: string;
  created_at: string;
}

export interface ScheduledJob {
  id: string;
  name: string;
  code: string;
  cron_expression: string;
  status: 'ACTIVE' | 'INACTIVE';
  last_run_at?: string;
  next_run_at?: string;
}

export interface SystemSetting {
  id: string;
  key: string;
  value: string;
  category: string;
  description?: string;
}

export interface FeatureFlag {
  id: string;
  name: string;
  enabled: boolean;
  description?: string;
}

export interface HealthMetric {
  id: string;
  api_latency_ms: number;
  db_latency_ms: number;
  redis_connected: boolean;
  disk_usage_percent: number;
  memory_usage_percent: number;
  scheduler_queue_depth: number;
  email_queue_depth: number;
  workflow_queue_depth: number;
  created_at: string;
}

export interface SearchIndex {
  id: string;
  entity_type: string;
  entity_id: string;
  title: string;
  description?: string;
  metadata_json?: Record<string, any>;
}
