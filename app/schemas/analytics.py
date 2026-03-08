"""Schémas Pydantic pour les endpoints analytics."""

from decimal import Decimal

from pydantic import BaseModel


# ── Department Costs ──────────────────────────────────────────────────────────

class DepartmentCostItem(BaseModel):
    """Coûts agrégés pour un département."""

    department: str
    total_cost: Decimal
    tools_count: int
    total_users: int
    average_cost_per_tool: Decimal
    cost_percentage: float


class DepartmentSummary(BaseModel):
    """Résumé global des coûts départements."""

    total_company_cost: Decimal
    departments_count: int
    most_expensive_department: str | None


class DepartmentCostsResponse(BaseModel):
    """Réponse GET /analytics/department-costs."""

    data: list[DepartmentCostItem]
    summary: DepartmentSummary


# ── Expensive Tools ───────────────────────────────────────────────────────────

class ExpensiveToolItem(BaseModel):
    """Outil coûteux avec rating d'efficacité."""

    id: int
    name: str
    monthly_cost: Decimal
    active_users_count: int
    cost_per_user: Decimal | None
    department: str
    vendor: str | None
    efficiency_rating: str


class ExpensiveAnalysis(BaseModel):
    """Analyse globale du top outils coûteux."""

    total_tools_analyzed: int
    avg_cost_per_user_company: Decimal
    potential_savings_identified: Decimal


class ExpensiveToolsResponse(BaseModel):
    """Réponse GET /analytics/expensive-tools."""

    data: list[ExpensiveToolItem]
    analysis: ExpensiveAnalysis


# ── Tools by Category ─────────────────────────────────────────────────────────

class CategoryCostItem(BaseModel):
    """Coûts agrégés pour une catégorie d'outils."""

    category_name: str
    tools_count: int
    total_cost: Decimal
    total_users: int
    percentage_of_budget: float
    average_cost_per_user: Decimal | None


class CategoryInsights(BaseModel):
    """Insights métier sur les catégories."""

    most_expensive_category: str | None
    most_efficient_category: str | None


class ToolsByCategoryResponse(BaseModel):
    """Réponse GET /analytics/tools-by-category."""

    data: list[CategoryCostItem]
    insights: CategoryInsights


# ── Low Usage Tools ───────────────────────────────────────────────────────────

class LowUsageToolItem(BaseModel):
    """Outil sous-utilisé avec niveau d'alerte et recommandation."""

    id: int
    name: str
    monthly_cost: Decimal
    active_users_count: int
    cost_per_user: Decimal | None
    department: str
    vendor: str | None
    warning_level: str
    potential_action: str


class SavingsAnalysis(BaseModel):
    """Analyse des économies potentielles sur outils sous-utilisés."""

    total_underutilized_tools: int
    potential_monthly_savings: Decimal
    potential_annual_savings: Decimal


class LowUsageToolsResponse(BaseModel):
    """Réponse GET /analytics/low-usage-tools."""

    data: list[LowUsageToolItem]
    savings_analysis: SavingsAnalysis


# ── Vendor Summary ────────────────────────────────────────────────────────────

class VendorSummaryItem(BaseModel):
    """Agrégation par fournisseur d'outils."""

    vendor: str
    tools_count: int
    total_monthly_cost: Decimal
    total_users: int
    departments: str
    average_cost_per_user: Decimal
    vendor_efficiency: str


class VendorInsights(BaseModel):
    """Insights comparatifs entre fournisseurs."""

    most_expensive_vendor: str | None
    most_efficient_vendor: str | None
    single_tool_vendors: int


class VendorSummaryResponse(BaseModel):
    """Réponse GET /analytics/vendor-summary."""

    data: list[VendorSummaryItem]
    vendor_insights: VendorInsights
