export interface GeneralLedgerAccount {
  id: string;
  code: string;
  name: string;
  account_type: 'ASSET' | 'LIABILITY' | 'EQUITY' | 'REVENUE' | 'EXPENSE';
  parent_id?: string;
  opening_balance: number;
  current_balance: number;
  status: 'ACTIVE' | 'INACTIVE';
}

export interface JournalEntryLine {
  id: string;
  account_id: string;
  debit: number;
  credit: number;
  cost_center_id?: string;
  department_id?: string;
  project_id?: string;
  region?: string;
}

export interface JournalEntry {
  id: string;
  entry_number: string;
  entry_date: string;
  description: string;
  status: 'DRAFT' | 'POSTED' | 'VOIDED';
  source_document?: string;
  lines: JournalEntryLine[];
}

export interface InvoiceItem {
  id: string;
  product_id: string;
  quantity: number;
  unit_price: number;
  total_cost: number;
}

export interface CustomerInvoice {
  id: string;
  invoice_number: string;
  customer_id: string;
  sales_order_id?: string;
  issue_date: string;
  due_date: string;
  payment_terms: string;
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  total_amount: number;
  outstanding_balance: number;
  status: 'DRAFT' | 'PENDING_APPROVAL' | 'APPROVED' | 'ISSUED' | 'PARTIALLY_PAID' | 'PAID' | 'CANCELLED';
  items?: InvoiceItem[];
}

export interface VendorBillItem {
  id: string;
  product_id: string;
  quantity: number;
  unit_price: number;
  total_cost: number;
}

export interface VendorBill {
  id: string;
  bill_number: string;
  supplier_id: string;
  purchase_order_id?: string;
  bill_date: string;
  due_date: string;
  subtotal: number;
  tax_amount: number;
  total_amount: number;
  outstanding_balance: number;
  status: 'DRAFT' | 'APPROVED' | 'PARTIALLY_PAID' | 'PAID' | 'CANCELLED';
  items?: VendorBillItem[];
}

export interface PaymentAllocation {
  id: string;
  payment_id: string;
  invoice_id?: string;
  vendor_bill_id?: string;
  allocated_amount: number;
}

export interface Payment {
  id: string;
  payment_number: string;
  payment_type: 'CUSTOMER_INFLOW' | 'VENDOR_OUTFLOW' | 'REFUND';
  payment_date: string;
  amount: number;
  payment_method: string;
  reference_number?: string;
  status: string;
  allocations: PaymentAllocation[];
}

export interface ExpenseCategory {
  id: string;
  name: string;
  code: string;
  default_account_id?: string;
}

export interface ExpenseClaim {
  id: string;
  claim_number: string;
  employee_id: string;
  expense_category_id: string;
  amount: number;
  claim_date: string;
  description: string;
  receipt_image_url?: string;
  status: 'DRAFT' | 'SUBMITTED' | 'APPROVED' | 'REIMBURSED' | 'REJECTED';
}

export interface Asset {
  id: string;
  asset_number: string;
  name: string;
  category: string;
  purchase_date: string;
  purchase_value: number;
  residual_value: number;
  useful_life_months: number;
  status: 'ACTIVE' | 'DISPOSED' | 'FULLY_DEPRECIATED';
}

export interface BudgetLine {
  id: string;
  account_id: string;
  allocated_amount: number;
  actual_amount: number;
}

export interface Budget {
  id: string;
  name: string;
  cost_center_id: string;
  start_date: string;
  end_date: string;
  status: string;
  lines: BudgetLine[];
}

export interface BankAccount {
  id: string;
  account_number: string;
  bank_name: string;
  account_type: string;
  gl_account_id: string;
  status: string;
}

export interface BankTransaction {
  id: string;
  bank_account_id: string;
  transaction_date: string;
  description: string;
  debit: number;
  credit: number;
  reference_number?: string;
  reconciliation_status: 'MATCHED' | 'PARTIALLY_MATCHED' | 'UNMATCHED' | 'IGNORED';
}
