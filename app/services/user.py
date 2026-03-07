"""Service métier pour les utilisateurs."""

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


class UserService:
    """Encapsule la logique métier liée aux utilisateurs.

    Args:
        db: Session SQLAlchemy active.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: UserCreate) -> User:
        """Crée un utilisateur en base.

        Args:
            data: Données validées par le schéma Pydantic.

        Returns:
            L'instance User créée.
        """
        user = User(username=data.username, email=data.email)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> User | None:
        """Récupère un utilisateur par ID.

        Args:
            user_id: Identifiant de l'utilisateur.

        Returns:
            L'utilisateur ou None.
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        """Récupère un utilisateur par email.

        Args:
            email: Adresse email.

        Returns:
            L'utilisateur ou None.
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Liste les utilisateurs avec pagination.

        Args:
            skip: Offset.
            limit: Nombre max de résultats.

        Returns:
            Liste d'utilisateurs.
        """
        return self.db.query(User).offset(skip).limit(limit).all()

    def delete(self, user_id: int) -> bool:
        """Supprime un utilisateur.

        Args:
            user_id: Identifiant de l'utilisateur.

        Returns:
            True si supprimé, False si non trouvé.
        """
        user = self.get_by_id(user_id)
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True
