from pydantic import BaseModel


class Ingredient(BaseModel):
    id: int | None = None
    name: str
    description: str = ""
    quantity: int
    unit: str

    class Config:
        orm_mode = True


class Direction(BaseModel):
    id: int | None = None
    description: str
    time: int

    class Config:
        orm_mode = True


class Recipe(BaseModel):
    id: int | None = None
    name: str
    description: str
    ingredients: list[Ingredient]
    directions: list[Direction]

    class Config:
        orm_mode = True
