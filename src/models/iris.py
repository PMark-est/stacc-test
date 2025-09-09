from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from .base import Base


class Iris(Base):
    __tablename__ = "iris"

    id: Mapped[int] = mapped_column(primary_key=True)
    species_id: Mapped[int] = mapped_column(ForeignKey("species.id"))
    sepal_length: Mapped[float] = mapped_column()
    sepal_width: Mapped[float] = mapped_column()
    petal_length: Mapped[float] = mapped_column()
    petal_width: Mapped[float] = mapped_column()\

    sepal_area: Mapped[float] = mapped_column()
    petal_area: Mapped[float] = mapped_column()
    sepal_to_petal_area_ratio: Mapped[float] = mapped_column()
    sepal_to_petal_length_ratio: Mapped[float] = mapped_column()
    sepal_to_petal_width_ratio: Mapped[float] = mapped_column()

    # Relationship
    species: Mapped["Species"] = relationship(
        "Species", back_populates="irises")
