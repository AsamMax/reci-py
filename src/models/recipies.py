import datetime

from sqlalchemy import ForeignKey, PickleType
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.util.enums import DietType, MealType, RecipeTags

from ..util.database import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str | None]
    quantity: Mapped[int]
    unit: Mapped[str | None]

    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipies.id"))


class Direction(Base):
    __tablename__ = "directions"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str]
    time: Mapped[int]

    recipe: Mapped["Recipe"] = relationship(back_populates="directions")
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipies.id"))


class Recipe(Base):
    __tablename__ = "recipies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    last_modified: Mapped[datetime.datetime]
    dietType: Mapped[DietType]
    mealType: Mapped[MealType]
    tags: Mapped[list[RecipeTags]] = mapped_column(PickleType())
    # load eagerly
    ingredients: Mapped[list[Ingredient]] = relationship(
        back_populates="recipe", lazy="joined"
    )
    directions: Mapped[list[Direction]] = relationship(
        back_populates="recipe", lazy="joined"
    )
