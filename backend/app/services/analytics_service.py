import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.custom_exceptions import ValidationException, EntityNotFoundException
from app.logging.config import logger

from app.models.analytics.dashboard import Dashboard, DashboardWidget
from app.models.analytics.metrics import BusinessMetric, MetricSnapshot
from app.models.analytics.kpis import KPIDefinition, KPIValue
from app.models.analytics.forecast import ForecastModel, ForecastResult
from app.models.analytics.reports import ReportDefinition

# Importing Transactional models from other domains to compute metrics dynamically
from app.models.hcm import Employee, Attendance
from app.models.inventory import Product, InventoryTransaction
from app.models.crm import Lead, Opportunity
from app.models.finance import CustomerInvoice, VendorBill, GeneralLedgerAccount

class MetricsEngine:
    @staticmethod
    async def calculate_metric(db: AsyncSession, metric_code: str) -> float:
        # Resolves metrics dynamically without duplicating calculations
        if metric_code == "REVENUE":
            # Sum of all active invoices
            q = select(func.sum(CustomerInvoice.total_amount)).where(CustomerInvoice.deleted_at.is_(None))
            res = await db.execute(q)
            return float(res.scalar() or 0.0)

        elif metric_code == "GROSS_PROFIT":
            # Sales Invoices minus COGS (approximated here by VendorBills)
            rev_q = select(func.sum(CustomerInvoice.total_amount)).where(CustomerInvoice.deleted_at.is_(None))
            exp_q = select(func.sum(VendorBill.total_amount)).where(VendorBill.deleted_at.is_(None))
            rev_res = await db.execute(rev_q)
            exp_res = await db.execute(exp_q)
            return float((rev_res.scalar() or 0.0) - (exp_res.scalar() or 0.0))

        elif metric_code == "INVENTORY_VALUE":
            # Sum of inventory items values (quantity * standard cost)
            q = select(func.sum(Product.quantity * Product.standard_cost)).where(Product.deleted_at.is_(None))
            res = await db.execute(q)
            return float(res.scalar() or 0.0)

        elif metric_code == "LEAD_CONVERSION_RATE":
            # Converted leads (having opportunity) / total leads
            tot_q = select(func.count(Lead.id))
            conv_q = select(func.count(Lead.id)).where(Lead.status == "CONVERTED")
            tot_res = await db.execute(tot_q)
            conv_res = await db.execute(conv_q)
            tot = tot_res.scalar() or 0
            return float((conv_res.scalar() or 0) / tot * 100.0) if tot > 0 else 0.0

        elif metric_code == "EMPLOYEE_HEADCOUNT":
            # Active headcount counts
            q = select(func.count(Employee.id)).where(Employee.deleted_at.is_(None))
            res = await db.execute(q)
            return float(res.scalar() or 0.0)

        return 0.0

class KPIEngine:
    @staticmethod
    async def evaluate_kpi(db: AsyncSession, kpi_code: str) -> KPIValue:
        q = select(KPIDefinition).where(KPIDefinition.metric_code == kpi_code)
        res = await db.execute(q)
        kpi = res.scalars().first()
        if not kpi:
            raise EntityNotFoundException("KPI definition not found")

        curr_val = await MetricsEngine.calculate_metric(db, kpi_code)
        
        # Traffic Light status indicators checks
        indicator = "GREEN"
        if curr_val < kpi.threshold_red:
            indicator = "RED"
        elif curr_val < kpi.threshold_yellow:
            indicator = "YELLOW"

        val = KPIValue(
            kpi_id=kpi.id,
            current_value=curr_val,
            status_indicator=indicator
        )
        db.add(val)
        await db.commit()
        return val

class ForecastEngine:
    @staticmethod
    async def generate_baseline_forecast(
        db: AsyncSession,
        metric_code: str,
        steps: int = 6
    ) -> List[Dict[str, Any]]:
        # Statistical projection using linear regression baseline
        # In mock databases, we simulate statistical datasets points
        historical_values = [120000.0, 145000.0, 160000.0, 185000.0, 210000.0]
        # Pure python least-squares linear fit
        n = len(historical_values)
        x_list = list(range(n))
        y_list = historical_values
        mean_x = sum(x_list) / n
        mean_y = sum(y_list) / n
        num = sum((x_list[i] - mean_x) * (y_list[i] - mean_y) for i in range(n))
        den = sum((x_list[i] - mean_x) ** 2 for i in range(n))
        slope = num / den if den != 0 else 0.0
        intercept = mean_y - slope * mean_x

        results = []
        start_date = datetime.utcnow()
        for idx in range(1, steps + 1):
            future_step = len(historical_values) + idx
            val = slope * future_step + intercept
            results.append({
                "date": (start_date + timedelta(days=idx*30)).strftime("%Y-%m-%d"),
                "value": float(val),
                "lower": float(val * 0.9),
                "upper": float(val * 1.1)
            })
        return results

class InsightsEngine:
    @staticmethod
    async def generate_deterministic_insights(db: AsyncSession) -> List[Dict[str, Any]]:
        # Determinisitic scanning for spikes, alerts, or budget leaks
        insights = []
        
        # 1. Lead Conversion scan
        lead_conv = await MetricsEngine.calculate_metric(db, "LEAD_CONVERSION_RATE")
        if lead_conv < 25.0:
            insights.append({
                "category": "CRM",
                "severity": "WARNING",
                "message": f"Lead Conversion rate is currently low at {lead_conv:.1f}%. Recommended sales review.",
                "action_url": "/dashboard/crm"
            })

        # 2. Headcount growth
        headcount = await MetricsEngine.calculate_metric(db, "EMPLOYEE_HEADCOUNT")
        if headcount > 0:
            insights.append({
                "category": "HCM",
                "severity": "INFO",
                "message": f"Active organization headcount stands at {int(headcount)} employees.",
                "action_url": "/dashboard/hcm"
            })

        return insights

class AnalyticsQueryEngine:
    @staticmethod
    async def execute_query(
        db: AsyncSession,
        metric_code: str,
        dimensions: List[str],
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Resolves queries and formats payload outputs for frontend Recharts graphs
        val = await MetricsEngine.calculate_metric(db, metric_code)
        return {
            "metric": metric_code,
            "value": val,
            "dimensions": dimensions,
            "filters": filters,
            "timestamp": datetime.utcnow().isoformat()
        }
