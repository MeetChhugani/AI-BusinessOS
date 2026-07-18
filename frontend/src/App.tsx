import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ForgotPasswordPage } from './pages/ForgotPasswordPage';
import { ResetPasswordPage } from './pages/ResetPasswordPage';
import { DashboardPage } from './pages/DashboardPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { DashboardLayout } from './layouts/DashboardLayout';
import { Loader2 } from 'lucide-react';

// HCM Module pages
import { HCMDashboard } from './pages/hcm/Dashboards';
import { EmployeeDirectory } from './pages/hcm/EmployeeDirectory';
import { EmployeeProfile } from './pages/hcm/EmployeeProfile';
import { OrgChartPage } from './pages/hcm/OrgChartPage';
import { OnboardingPipeline } from './pages/hcm/OnboardingPipeline';
import { CSVImportPage } from './pages/hcm/CSVImportPage';
import { LeavesPage } from './pages/hcm/LeavesPage';

// Inventory Module pages
import { WarehouseDashboard } from './pages/inventory/WarehouseDashboard';
import { InventoryDirectory } from './pages/inventory/InventoryDirectory';
import { ProductCatalog } from './pages/inventory/ProductCatalog';
import { PurchaseOrdersPage } from './pages/inventory/PurchaseOrdersPage';
import { StockTransfersPage } from './pages/inventory/StockTransfersPage';
import { AuditsPage } from './pages/inventory/AuditsPage';

// CRM Module pages
import { CRMDashboard } from './pages/crm/CRMDashboard';
import { CustomerDirectory } from './pages/crm/CustomerDirectory';
import { LeadsPipeline } from './pages/crm/LeadsPipeline';
import { OpportunitiesKanban } from './pages/crm/OpportunitiesKanban';
import { QuotationsOrdersPage } from './pages/crm/QuotationsOrdersPage';
import { TasksCalendarPage } from './pages/crm/TasksCalendarPage';

// Finance Module pages
import { FinanceDashboard } from './pages/finance/FinanceDashboard';
import { ChartOfAccounts } from './pages/finance/ChartOfAccounts';
import { JournalEntries } from './pages/finance/JournalEntries';
import { InvoicesBillsPage } from './pages/finance/InvoicesBillsPage';
import { BankReconciliation } from './pages/finance/BankReconciliation';
import { ExpenseClaimsPage } from './pages/finance/ExpenseClaimsPage';
import { FixedAssetsPage } from './pages/finance/FixedAssetsPage';
import { BudgetsPage } from './pages/finance/BudgetsPage';
import { FinancialReportsPage } from './pages/finance/FinancialReportsPage';

// Platform Module pages
import { PlatformDashboard } from './pages/platform/PlatformDashboard';
import { NotificationCenter } from './pages/platform/NotificationCenter';
import { WorkflowBuilder } from './pages/platform/WorkflowBuilder';
import { AuditCenter } from './pages/platform/AuditCenter';
import { SearchCenter } from './pages/platform/SearchCenter';
import { FileManager } from './pages/platform/FileManager';
import { SystemSettings } from './pages/platform/SystemSettings';
import { FeatureFlags } from './pages/platform/FeatureFlags';

// Analytics Module pages
import { ExecutiveDashboard } from './pages/analytics/ExecutiveDashboard';
import { HRAnalyticsDashboard } from './pages/analytics/HRAnalyticsDashboard';
import { CRMAnalyticsDashboard } from './pages/analytics/CRMAnalyticsDashboard';
import { InventoryAnalyticsDashboard } from './pages/analytics/InventoryAnalyticsDashboard';
import { FinanceAnalyticsDashboard } from './pages/analytics/FinanceAnalyticsDashboard';
import { KPIManager } from './pages/analytics/KPIManager';
import { ForecastDashboard } from './pages/analytics/ForecastDashboard';

// Protected Route wrapper component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex flex-col justify-center items-center">
        {/* Glowing loader */}
        <div className="absolute w-[200px] h-[200px] bg-blue-500/10 rounded-full blur-[50px] pointer-events-none" />
        <div className="relative flex flex-col items-center space-y-4">
          <Loader2 size={36} className="animate-spin text-blue-500" />
          <span className="text-xs font-bold text-muted-foreground uppercase tracking-widest animate-pulse">
            Connecting session...
          </span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Public Route wrapper that redirects authenticated users to the dashboard
const PublicOnlyRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex flex-col justify-center items-center">
        <Loader2 size={36} className="animate-spin text-blue-500" />
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public landing */}
            <Route path="/" element={<LandingPage />} />

            {/* Auth screens */}
            <Route
              path="/login"
              element={
                <PublicOnlyRoute>
                  <LoginPage />
                </PublicOnlyRoute>
              }
            />
            <Route
              path="/register"
              element={
                <PublicOnlyRoute>
                  <RegisterPage />
                </PublicOnlyRoute>
              }
            />
            <Route
              path="/forgot-password"
              element={
                <PublicOnlyRoute>
                  <ForgotPasswordPage />
                </PublicOnlyRoute>
              }
            />
            <Route
              path="/reset-password"
              element={
                <PublicOnlyRoute>
                  <ResetPasswordPage />
                </PublicOnlyRoute>
              }
            />

            {/* Core Workspace Dashboard - Protected */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <DashboardPage />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />

            {/* HCM Module Routes */}
            <Route
              path="/dashboard/hcm"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <HCMDashboard />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/hcm/directory"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <EmployeeDirectory />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/hcm/profile/:id"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <EmployeeProfile />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/hcm/org"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <OrgChartPage />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/hcm/pipeline"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <OnboardingPipeline />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/hcm/import"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <CSVImportPage />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/hcm/leaves"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <LeavesPage />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />

            {/* Inventory Module Routes */}
            <Route
              path="/dashboard/inventory"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <WarehouseDashboard />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/inventory/directory"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <InventoryDirectory />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/inventory/catalog"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <ProductCatalog />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/inventory/po"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <PurchaseOrdersPage />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/inventory/transfers"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <StockTransfersPage />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/inventory/audits"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <AuditsPage />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />

            {/* CRM Module Routes */}
            <Route
              path="/dashboard/crm"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <CRMDashboard />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/crm/directory"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <CustomerDirectory />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/crm/leads"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <LeadsPipeline />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/crm/opportunities"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <OpportunitiesKanban />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/crm/quotations"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <QuotationsOrdersPage />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/crm/tasks"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <TasksCalendarPage />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />

            {/* Finance Module Routes */}
            <Route
              path="/dashboard/finance"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <FinanceDashboard />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/finance/accounts"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <ChartOfAccounts />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/finance/journal"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <JournalEntries />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/finance/invoices"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <InvoicesBillsPage />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/finance/reconciliation"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <BankReconciliation />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/finance/expenses"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <ExpenseClaimsPage />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/finance/assets"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <FixedAssetsPage />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/finance/budgets"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <BudgetsPage />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/finance/reports"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <FinancialReportsPage />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />

            {/* Platform Module Routes */}
            <Route
              path="/dashboard/platform"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <PlatformDashboard />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/platform/notifications"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <NotificationCenter />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/platform/workflows"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <WorkflowBuilder />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/platform/audit"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <AuditCenter />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/platform/search"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <SearchCenter />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/platform/files"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <FileManager />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/platform/settings"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <SystemSettings />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/platform/features"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <FeatureFlags />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />

            {/* Analytics Module Routes */}
            <Route
              path="/dashboard/analytics"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <ExecutiveDashboard />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/analytics/hr"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <HRAnalyticsDashboard />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/analytics/crm"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <CRMAnalyticsDashboard />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/analytics/inventory"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <InventoryAnalyticsDashboard />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/analytics/finance"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <FinanceAnalyticsDashboard />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/analytics/kpis"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <KPIManager />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard/analytics/forecasts"
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <ForecastDashboard />
                  </DashboardLayout>
                </ProtectedRoute>
              }
            />

            {/* 404 Fallback page */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
