export interface BusinessMetric {
  id: string;
  name: string;
  code: string;
  formula: string;
  dependencies_json: Record<string, any>;
  cache_refresh_rate: 'DAILY' | 'HOURLY' | 'REALTIME';
  description?: string;
}

export interface KPIDefinition {
  id: string;
  name: string;
  metric_code: string;
  target_value: number;
  threshold_yellow: number;
  threshold_red: number;
  status: string;
}

export interface KPIValue {
  id: string;
  kpi_id: string;
  current_value: number;
  status_indicator: 'GREEN' | 'YELLOW' | 'RED';
  created_at: string;
}

export interface DeterministicInsight {
  category: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  message: string;
  action_url?: string;
}

export interface ForecastResult {
  date: string;
  value: number;
  lower: number;
  upper: number;
}

export interface Dashboard {
  id: string;
  name: string;
  code: string;
  allowed_roles: string;
  description?: string;
}
