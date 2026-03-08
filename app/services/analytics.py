"""Service analytique — calculs métier agrégés sur les outils SaaS actifs."""

import logging
from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.tool import Tool

logger = logging.getLogger(__name__)

_ACTIVE = "active"
_D2 = Decimal("0.01")


def _d2(value: float | Decimal) -> Decimal:
    """Arrondit une valeur à 2 décimales (ROUND_HALF_UP).

    Args:
        value: Valeur numérique à arrondir.

    Returns:
        Decimal arrondi à 2 décimales.
    """
    return Decimal(str(value)).quantize(_D2, rounding=ROUND_HALF_UP)


def _pct(part: float, total: float) -> float:
    """Calcule un pourcentage arrondi à 1 décimale.

    Args:
        part: Valeur partielle.
        total: Valeur totale.

    Returns:
        Pourcentage (0.0 si total est nul).
    """
    return round(part / total * 100, 1) if total else 0.0


class AnalyticsService:
    """Encapsule la logique métier des cinq endpoints analytics.

    Tous les calculs portent exclusivement sur les outils avec status='active'.

    Args:
        db: Session SQLAlchemy active.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Helpers privés ────────────────────────────────────────────────────────

    def _cpu(self, monthly_cost: Decimal, users: int) -> Decimal | None:
        """Coût par utilisateur. Retourne None si 0 utilisateurs (division par zéro).

        Args:
            monthly_cost: Coût mensuel de l'outil.
            users: Nombre d'utilisateurs actifs.

        Returns:
            Decimal arrondi à 2 décimales ou None.
        """
        if users <= 0:
            return None
        return _d2(float(monthly_cost) / users)

    def _efficiency_rating(self, cpu: Decimal | None, avg: Decimal) -> str:
        """Rating d'efficacité basé sur cost_per_user vs moyenne entreprise.

        Args:
            cpu: Coût par utilisateur de l'outil (None = 0 users).
            avg: Moyenne pondérée entreprise (coût / users).

        Returns:
            "excellent" | "good" | "average" | "low"
        """
        if cpu is None or avg == 0:
            return "low"
        ratio = float(cpu) / float(avg)
        if ratio < 0.5:
            return "excellent"
        if ratio < 0.8:
            return "good"
        if ratio <= 1.2:
            return "average"
        return "low"

    def _vendor_efficiency(self, avg_cpu: Decimal) -> str:
        """Rating d'efficacité fournisseur basé sur average_cost_per_user.

        Args:
            avg_cpu: Coût moyen par utilisateur du vendor.

        Returns:
            "excellent" | "good" | "average" | "poor"
        """
        v = float(avg_cpu)
        if v < 5:
            return "excellent"
        if v < 15:
            return "good"
        if v < 25:
            return "average"
        return "poor"

    def _warning_level(self, tool: Tool) -> str:
        """Niveau d'alerte pour un outil sous-utilisé.

        Args:
            tool: Instance ORM Tool.

        Returns:
            "high" | "medium" | "low"
        """
        if tool.active_users_count == 0:
            return "high"
        cpu = float(tool.monthly_cost) / tool.active_users_count
        if cpu < 20:
            return "low"
        if cpu <= 50:
            return "medium"
        return "high"

    # ── Endpoints ─────────────────────────────────────────────────────────────

    def department_costs(self, sort_by: str = "total_cost", order: str = "desc") -> dict:
        """Répartition des coûts outils actifs par département.

        Args:
            sort_by: "total_cost" ou "department".
            order: "asc" ou "desc".

        Returns:
            Dictionnaire compatible DepartmentCostsResponse.
        """
        rows = (
            self.db.query(
                Tool.owner_department,
                func.sum(Tool.monthly_cost).label("total_cost"),
                func.count(Tool.id).label("tools_count"),
                func.sum(Tool.active_users_count).label("total_users"),
            )
            .filter(Tool.status == _ACTIVE)
            .group_by(Tool.owner_department)
            .all()
        )

        total_company_cost = _d2(sum(float(r.total_cost) for r in rows))

        data = []
        for r in rows:
            tc = _d2(r.total_cost)
            avg = _d2(float(tc) / r.tools_count) if r.tools_count else Decimal("0.00")
            data.append({
                "department": r.owner_department,
                "total_cost": tc,
                "tools_count": r.tools_count,
                "total_users": r.total_users or 0,
                "average_cost_per_tool": avg,
                "cost_percentage": _pct(float(tc), float(total_company_cost)),
            })

        reverse = order.lower() == "desc"
        if sort_by == "department":
            data.sort(key=lambda x: x["department"], reverse=reverse)
        else:
            data.sort(key=lambda x: x["total_cost"], reverse=reverse)

        most_expensive = None
        if rows:
            best = sorted(rows, key=lambda r: (-float(r.total_cost), r.owner_department))[0]
            most_expensive = best.owner_department

        return {
            "data": data,
            "summary": {
                "total_company_cost": total_company_cost,
                "departments_count": len(data),
                "most_expensive_department": most_expensive,
            },
        }

    def expensive_tools(self, limit: int = 10, min_cost: float | None = None) -> dict:
        """Top outils actifs les plus coûteux avec rating d'efficacité.

        avg_cost_per_user_company = somme(monthly_cost) / somme(active_users_count)
        calculé sur les outils actifs ayant AU MOINS 1 utilisateur.

        Args:
            limit: Nombre maximum d'outils retournés (1–100).
            min_cost: Filtre coût mensuel minimum (optionnel).

        Returns:
            Dictionnaire compatible ExpensiveToolsResponse.
        """
        all_active = self.db.query(Tool).filter(Tool.status == _ACTIVE).all()
        tools_with_users = [t for t in all_active if t.active_users_count > 0]
        total_cost_sum = sum(float(t.monthly_cost) for t in tools_with_users)
        total_users_sum = sum(t.active_users_count for t in tools_with_users)
        avg_cpu = (
            _d2(total_cost_sum / total_users_sum) if total_users_sum > 0 else Decimal("0.00")
        )

        query = self.db.query(Tool).filter(Tool.status == _ACTIVE)
        if min_cost is not None:
            query = query.filter(Tool.monthly_cost >= Decimal(str(min_cost)))
        tools = query.order_by(Tool.monthly_cost.desc()).limit(limit).all()

        data = []
        for t in tools:
            cpu = self._cpu(t.monthly_cost, t.active_users_count)
            data.append({
                "id": t.id,
                "name": t.name,
                "monthly_cost": t.monthly_cost,
                "active_users_count": t.active_users_count,
                "cost_per_user": cpu,
                "department": t.owner_department,
                "vendor": t.vendor,
                "efficiency_rating": self._efficiency_rating(cpu, avg_cpu),
            })

        potential_savings = _d2(
            sum(float(item["monthly_cost"]) for item in data if item["efficiency_rating"] == "low")
        )

        return {
            "data": data,
            "analysis": {
                "total_tools_analyzed": len(data),
                "avg_cost_per_user_company": avg_cpu,
                "potential_savings_identified": potential_savings,
            },
        }

    def tools_by_category(self) -> dict:
        """Répartition des outils actifs et de leurs coûts par catégorie.

        Returns:
            Dictionnaire compatible ToolsByCategoryResponse.
        """
        rows = (
            self.db.query(
                Category.name.label("category_name"),
                func.count(Tool.id).label("tools_count"),
                func.sum(Tool.monthly_cost).label("total_cost"),
                func.sum(Tool.active_users_count).label("total_users"),
            )
            .join(Tool, Tool.category_id == Category.id)
            .filter(Tool.status == _ACTIVE)
            .group_by(Category.id, Category.name)
            .all()
        )

        total_company_cost = sum(float(r.total_cost) for r in rows)

        data = []
        for r in rows:
            tc = _d2(r.total_cost)
            total_users = r.total_users or 0
            avg_cpu = _d2(float(tc) / total_users) if total_users > 0 else None
            data.append({
                "category_name": r.category_name,
                "tools_count": r.tools_count,
                "total_cost": tc,
                "total_users": total_users,
                "percentage_of_budget": _pct(float(tc), total_company_cost),
                "average_cost_per_user": avg_cpu,
            })

        most_expensive = None
        most_efficient = None
        if data:
            most_expensive = sorted(
                data, key=lambda x: (-float(x["total_cost"]), x["category_name"])
            )[0]["category_name"]

            eligible = [d for d in data if d["average_cost_per_user"] is not None]
            if eligible:
                most_efficient = sorted(
                    eligible,
                    key=lambda x: (float(x["average_cost_per_user"]), x["category_name"]),
                )[0]["category_name"]

        return {
            "data": data,
            "insights": {
                "most_expensive_category": most_expensive,
                "most_efficient_category": most_efficient,
            },
        }

    def low_usage_tools(self, max_users: int = 5) -> dict:
        """Outils actifs sous-utilisés (active_users_count <= max_users).

        warning_level : "high" si cost_per_user > 50€ ou 0 users,
                        "medium" si 20–50€, "low" si < 20€.
        potential_monthly_savings = somme des monthly_cost des outils "high" + "medium".

        Args:
            max_users: Seuil d'utilisateurs actifs (défaut 5, min 0).

        Returns:
            Dictionnaire compatible LowUsageToolsResponse.
        """
        _ACTIONS: dict[str, str] = {
            "high": "Consider canceling or downgrading",
            "medium": "Review usage and consider optimization",
            "low": "Monitor usage trends",
        }

        tools = (
            self.db.query(Tool)
            .filter(Tool.status == _ACTIVE, Tool.active_users_count <= max_users)
            .order_by(Tool.monthly_cost.desc())
            .all()
        )

        data = []
        for t in tools:
            level = self._warning_level(t)
            data.append({
                "id": t.id,
                "name": t.name,
                "monthly_cost": t.monthly_cost,
                "active_users_count": t.active_users_count,
                "cost_per_user": self._cpu(t.monthly_cost, t.active_users_count),
                "department": t.owner_department,
                "vendor": t.vendor,
                "warning_level": level,
                "potential_action": _ACTIONS[level],
            })

        monthly_savings = _d2(
            sum(
                float(item["monthly_cost"])
                for item in data
                if item["warning_level"] in ("high", "medium")
            )
        )

        return {
            "data": data,
            "savings_analysis": {
                "total_underutilized_tools": len(data),
                "potential_monthly_savings": monthly_savings,
                "potential_annual_savings": _d2(float(monthly_savings) * 12),
            },
        }

    def vendor_summary(self) -> dict:
        """Analyse des fournisseurs d'outils actifs.

        Les départements sont concaténés par ordre alphabétique, sans doublons.
        single_tool_vendors = nombre de vendors avec exactement 1 outil actif.

        Returns:
            Dictionnaire compatible VendorSummaryResponse.
        """
        rows = (
            self.db.query(
                Tool.vendor,
                func.count(Tool.id).label("tools_count"),
                func.sum(Tool.monthly_cost).label("total_monthly_cost"),
                func.sum(Tool.active_users_count).label("total_users"),
            )
            .filter(Tool.status == _ACTIVE, Tool.vendor.isnot(None))
            .group_by(Tool.vendor)
            .all()
        )

        # Récupération des départements uniques par vendor (compatible SQLite/PG)
        dept_rows = (
            self.db.query(Tool.vendor, Tool.owner_department)
            .filter(Tool.status == _ACTIVE, Tool.vendor.isnot(None))
            .distinct()
            .all()
        )
        vendor_depts: dict[str, set[str]] = defaultdict(set)
        for r in dept_rows:
            vendor_depts[r.vendor].add(r.owner_department)

        data = []
        for r in rows:
            total_users = r.total_users or 0
            avg_cpu = (
                _d2(float(r.total_monthly_cost) / total_users)
                if total_users > 0
                else Decimal("0.00")
            )
            data.append({
                "vendor": r.vendor,
                "tools_count": r.tools_count,
                "total_monthly_cost": _d2(r.total_monthly_cost),
                "total_users": total_users,
                "departments": ",".join(sorted(vendor_depts[r.vendor])),
                "average_cost_per_user": avg_cpu,
                "vendor_efficiency": self._vendor_efficiency(avg_cpu),
            })

        most_expensive_vendor = None
        most_efficient_vendor = None
        if data:
            most_expensive_vendor = sorted(
                data, key=lambda x: -float(x["total_monthly_cost"])
            )[0]["vendor"]

            eligible = [d for d in data if d["total_users"] > 0]
            if eligible:
                most_efficient_vendor = sorted(
                    eligible,
                    key=lambda x: (float(x["average_cost_per_user"]), x["vendor"]),
                )[0]["vendor"]

        single_tool_vendors = sum(1 for r in rows if r.tools_count == 1)

        return {
            "data": data,
            "vendor_insights": {
                "most_expensive_vendor": most_expensive_vendor,
                "most_efficient_vendor": most_efficient_vendor,
                "single_tool_vendors": single_tool_vendors,
            },
        }
