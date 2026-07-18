export interface Customer {
  id: string;
  name: string;
  customer_type: 'COMPANY' | 'INDIVIDUAL';
  gst_number?: string;
  industry?: string;
  segment: 'ENTERPRISE' | 'SME' | 'VIP' | 'DISTRIBUTOR' | 'GOVERNMENT';
  credit_limit: number;
  payment_terms: string;
  territory_id?: string;
  status: 'ACTIVE' | 'INACTIVE';
  created_at: string;
  contacts?: CustomerContact[];
}

export interface CustomerContact {
  id: string;
  customer_id: string;
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  job_title?: string;
  is_primary: boolean;
}

export interface CustomerAddress {
  id: string;
  customer_id: string;
  address_type: 'BILLING' | 'SHIPPING';
  address_line1: string;
  address_line2?: string;
  city: string;
  state: string;
  country: string;
  zip_code: string;
}

export interface CustomerNote {
  id: string;
  customer_id: string;
  note: string;
  created_by_id: string;
  created_at: string;
}

export interface CustomerActivityLog {
  id: string;
  customer_id: string;
  activity_type: 'CALL' | 'EMAIL' | 'MEETING' | 'OPPORTUNITY_CHANGED';
  description: string;
  created_by_id: string;
  created_at: string;
}

export interface Lead {
  id: string;
  first_name: string;
  last_name: string;
  company_name?: string;
  email?: string;
  phone?: string;
  source: 'WEBSITE' | 'REFERRAL' | 'CAMPAIGN' | 'MANUAL';
  status: 'NEW' | 'CONTACTED' | 'QUALIFIED' | 'UNQUALIFIED' | 'CONVERTED';
  score: number;
  assigned_to_id?: string;
  converted_customer_id?: string;
  created_at: string;
}

export interface LeadActivity {
  id: string;
  lead_id: string;
  activity_type: 'CALL' | 'EMAIL' | 'MEETING' | 'NOTE';
  details: string;
  created_by_id: string;
  created_at: string;
}

export interface OpportunityProduct {
  id: string;
  opportunity_id: string;
  product_id: string;
  quantity: number;
  unit_price: number;
  is_upsell: boolean;
}

export interface Opportunity {
  id: string;
  name: string;
  customer_id: string;
  stage: 'PROSPECTING' | 'QUALIFICATION' | 'PROPOSAL' | 'NEGOTIATION' | 'WON' | 'LOST';
  probability: number;
  expected_revenue: number;
  close_date: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  competitors?: string;
  assigned_to_id?: string;
  lost_reason?: string;
  created_at: string;
  products?: OpportunityProduct[];
}

export interface PricingRule {
  id: string;
  name: string;
  customer_segment: string;
  product_id?: string;
  discount_percentage: number;
  start_date: string;
  end_date: string;
  priority: number;
  status: 'ACTIVE' | 'INACTIVE';
}

export interface SalesTerritory {
  id: string;
  name: string;
  region: string;
  assigned_salesperson_id?: string;
}

export interface QuotationItem {
  id: string;
  quotation_id: string;
  product_id: string;
  quantity: number;
  unit_price: number;
  tax_rate: number;
  total_cost: number;
}

export interface Quotation {
  id: string;
  quotation_number: string;
  opportunity_id?: string;
  customer_id: string;
  status: 'DRAFT' | 'SUBMITTED' | 'APPROVED' | 'REJECTED' | 'ACCEPTED' | 'CONVERTED';
  version: number;
  valid_until: string;
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  total_amount: number;
  created_at: string;
  items?: QuotationItem[];
}

export interface SalesOrderItem {
  id: string;
  sales_order_id: string;
  product_id: string;
  variant_id?: string;
  quantity: number;
  unit_price: number;
  tax_rate: number;
  total_cost: number;
}

export interface SalesOrder {
  id: string;
  order_number: string;
  customer_id: string;
  quotation_id?: string;
  status: 'DRAFT' | 'PENDING_APPROVAL' | 'APPROVED' | 'SHIPPED' | 'COMPLETED' | 'CANCELLED';
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  total_amount: number;
  created_by_id: string;
  salesperson_id?: string;
  shipping_status: 'PENDING' | 'SHIPPED' | 'DELIVERED';
  created_at: string;
}

export interface CustomerDocument {
  id: string;
  customer_id: string;
  file_name: string;
  file_path: string;
  file_size: number;
  uploaded_by_id: string;
}

export interface CRMTask {
  id: string;
  title: string;
  description?: string;
  due_date: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED';
  assigned_to_id?: string;
  customer_id?: string;
  lead_id?: string;
  created_at: string;
}

export interface CRMMeeting {
  id: string;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  location?: string;
  assigned_to_id?: string;
  customer_id?: string;
  lead_id?: string;
}
