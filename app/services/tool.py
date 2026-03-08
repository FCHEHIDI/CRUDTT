"""Service métier pour les outils SaaS."""

import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.category import Category
from app.models.tool import Tool
from app.schemas.tool import ToolCreate, ToolUpdate, ToolRead, ToolDetail, ToolListResponse

logger = logging.getLogger(__name__)

class ToolService:
    """Encapsule la logique métier liée aux outils SaaS.
    
    Args:
        db: Session SQLAlchemy active.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

# Lecture

    def get_all(
        self,
        department: str | None = None,
        status: str | None = None,
        category: str | None = None,
        min_cost: float | None = None,
        max_cost: float | None = None,
        sort_by: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 100,
    ) -> ToolListResponse:
        """Liste les outils avec filtres, tri et pagination.

        Args:
            department: Filtre sur owner_department.
            status: Filtre sur status.
            category: Filtre sur le nom de la catégorie.
            min_cost: Coût mensuel minimum.
            max_cost: Coût mensuel maximum.
            sort_by: Champ de tri (name | monthly_cost | created_at).
            order: Sens du tri (asc | desc).
            page: Numéro de page (1-based).
            limit: Nombre d'éléments par page.

        Returns:
            ToolListResponse avec data, total, filtered et filters_applied.
        """
        total = self.db.query(func.count(Tool.id)).scalar()

        query = self.db.query(Tool).options(joinedload(Tool.category))

        filters_applied: dict = {}
        if department:
            query = query.filter(Tool.owner_department == department)
            filters_applied["department"] = department
        if status:
            query = query.filter(Tool.status == status)
            filters_applied["status"] = status
        if category:
            query = query.join(Category).filter(Category.name == category)
            filters_applied["category"] = category
        if min_cost is not None:
            query = query.filter(Tool.monthly_cost >= min_cost)
            filters_applied["min_cost"] = min_cost
        if max_cost is not None:
            query = query.filter(Tool.monthly_cost <= max_cost)
            filters_applied["max_cost"] = max_cost

        filtered = query.count()

        # Tri
        sort_col = {"monthly_cost": Tool.monthly_cost, "created_at": Tool.created_at}.get(
            sort_by, Tool.name
        )
        query = query.order_by(sort_col.desc() if order == "desc" else sort_col.asc())

        # Pagination
        tools = query.offset((page - 1) * limit).limit(limit).all()

        return ToolListResponse(
            data=[self._to_read(t) for t in tools],
            total=total,
            filtered=filtered,
            filters_applied=filters_applied,
        )

    def get_by_id(self, tool_id: int) -> ToolDetail | None:
        """Récupère un outil par son ID.

        Args:
            tool_id: Identifiant de l'outil.

        Returns:
            ToolDetail de l'outil, None si inexistant.
        """
        tool = self.db.query(Tool).options(joinedload(Tool.category)).filter(Tool.id == tool_id).first()
        if not tool:
            return None
        return self._to_detail(tool)
    
    
    def get_by_name(self, name: str) -> Tool | None:
        """Récupère un outil par son nom.

        Args:
            name: Nom de l'outil.

        Returns:
            Tool trouvé, None si inexistant.
        """
        return self.db.query(Tool).filter(Tool.name == name).first()
    
    
    def category_exists(self, category_id: int) -> bool:
        """Vérifie l'existence d'une catégorie par son ID.

        Args:
            category_id: Identifiant de la catégorie.

        Returns:
            True si la catégorie existe, False sinon.
        """
        return self.db.query(Category).filter(Category.id == category_id).first() is not None

# Ecriture

    def create(self, data: ToolCreate) -> ToolDetail:
        """Crée un nouvel outil SaaS.
        
        Args:
            data: Données de création validées par Pydantic.
            
        Returns:
            ToolDetail de l'outil créé.
        """

        tool = Tool(
            name=data.name,
            description=data.description,
            vendor=data.vendor,
            website_url=data.website_url,
            category_id=data.category_id,
            monthly_cost=data.monthly_cost,
            owner_department=data.owner_department.value,
            status="active",
            active_users_count=0,
        )
        self.db.add(tool)
        self.db.commit()
        self.db.refresh(tool)
        return self.get_by_id(tool.id)
    
    
    def update(self, tool_id: int, data: ToolUpdate) -> ToolDetail | None:
        """ Met à jour partiellement un outil.
        
        Args:
            tool_id: Identifiant de l'outil à mettre à jour.
            data: Champs à modifier (None = conservé).
            
            Returns:
                ToolDetail mis à jour, None si inexistant.
                """
        tool = self.db.query(Tool).filter(Tool.id == tool_id).first()
        if not tool:
            return None
        
        for field, value in data.model_dump(exclude_none=True).items():
            # Convertir les enums en valeur string
            setattr(tool, field, value.value if hasattr(value, "value") else value)

        tool.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(tool)
        return self.get_by_id(tool.id) # il ne reconnait pas la méthode get_by_id, il faut la créer avant de l'appeler, sinon ça fait une erreur d'attribut.


# Helpers privés

    def _to_read(self, tool: Tool) -> ToolRead:
        """Convertit un Tool en ToolRead.
        
        Args:
            tool: Instance ORM.
            
        Returns:
            ToolRead sérialisable.
        """
        return ToolRead(
            id=tool.id,
            name=tool.name,
            description=tool.description,
            vendor=tool.vendor,
            category=tool.category.name if tool.category else "",
            monthly_cost=tool.monthly_cost,
            owner_department=tool.owner_department,
            status=tool.status,
            website_url=tool.website_url,
            active_users_count=tool.active_users_count,
            created_at=tool.created_at
        )
    
    
    def _to_detail(self, tool: Tool) -> ToolDetail:
        """Convertit une instance Tool en ToolDetail avec métriques.

        Args:
            tool: Instance ORM avec category chargée.

        Returns:
            ToolDetail complet.
        """
        from app.models.tool import Tool  # import local pour éviter circularité

        # Métriques usage_logs sur les 30 derniers jours
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        try:
            from app.models.usage_log import UsageLog
            rows = (
                self.db.query(
                    func.count(UsageLog.id).label("sessions"),
                    func.coalesce(func.avg(UsageLog.usage_minutes), 0).label("avg_min"),
                )
                .filter(
                    UsageLog.tool_id == tool.id,
                    UsageLog.session_date >= thirty_days_ago.date(),
                )
                .first()
            )
            total_sessions = rows.sessions if rows else 0
            avg_minutes = float(rows.avg_min) if rows else 0.0
        except Exception:
            logger.warning("usage_logs unavailable for tool %d", tool.id)
            total_sessions = 0
            avg_minutes = 0.0

        total_cost = Decimal(str(tool.monthly_cost)) * tool.active_users_count

        return ToolDetail(
            id=tool.id,
            name=tool.name,
            description=tool.description,
            vendor=tool.vendor,
            category=tool.category.name if tool.category else "",
            monthly_cost=tool.monthly_cost,
            owner_department=tool.owner_department,
            status=tool.status,
            website_url=tool.website_url,
            active_users_count=tool.active_users_count,
            created_at=tool.created_at,
            updated_at=tool.updated_at,
            total_monthly_cost=total_cost,
            usage_metrics={
                "last_30_days": {
                    "total_sessions": total_sessions,
                    "avg_session_minutes": round(avg_minutes, 1),
                    }
                    },
                    )