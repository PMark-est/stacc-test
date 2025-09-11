from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from typing import List, Optional, Dict
from .base import Base


class Species(Base):
    """Species model."""
    __tablename__ = "species"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    irises: Mapped[List["Iris"]] = relationship(
        "Iris", back_populates="species")

    def to_dict(self) -> Dict[str, str]:
        return {"id": self.id, "name": self.name}
