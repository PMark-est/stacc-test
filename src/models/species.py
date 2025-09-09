from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from typing import List
from .base import Base


class Species(Base):  # <-- Inherit from Base
    __tablename__ = "species"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    # Relationship
    irises: Mapped[List["Iris"]] = relationship(
        "Iris", back_populates="species")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }
