from typing import Sequence

from pydantic import BaseModel


class IngredientCreate(BaseModel):
    name: str
    description: str = ""
    quantity: int
    unit: str

    class Config:
        orm_mode = True


class Ingredient(IngredientCreate):
    id: int

    class Config:
        orm_mode = True


class DirectionCreate(BaseModel):
    description: str
    time: int

    class Config:
        orm_mode = True


class Direction(DirectionCreate):
    id: int

    class Config:
        orm_mode = True


class RecipeCreate(BaseModel):
    name: str
    description: str
    ingredients: Sequence[IngredientCreate]
    directions: Sequence[DirectionCreate]

    class Config:
        orm_mode = True


class Recipe(RecipeCreate):
    id: int
    ingredients: Sequence[Ingredient]
    directions: Sequence[Direction]

    class Config:
        orm_mode = True
