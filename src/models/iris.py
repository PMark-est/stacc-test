from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from .base import Base

class Iris(Base):
    __tablename__ = "iris"

    id: Mapped[int] = mapped_column(primary_key=True)
    species_id: Mapped[int] = mapped_column(ForeignKey("species.id"))
    sepal_length: Mapped[int] = mapped_column()  # Add mapped_column()
    sepal_width: Mapped[int] = mapped_column()   # Add mapped_column()
    petal_length: Mapped[int] = mapped_column()  # Add mapped_column()
    petal_width: Mapped[int] = mapped_column()   # Add mapped_column()

    # Relationship
    species: Mapped["Species"] = relationship(
        "Species", back_populates="irises")