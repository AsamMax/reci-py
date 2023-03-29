import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Ingredient(BaseModel):
    name: str
    description: str
    quantity: int
    unit: str


class Direction(BaseModel):
    description: str
    time: int


class Recipe(BaseModel):
    name: str
    description: str
    ingredients: list[Ingredient]
    directions: list[Direction]


recipes = [
    Recipe(
        name="Pancakes",
        description="Delicious pancakes",
        ingredients=[
            Ingredient(name="Flour", description="Flour", quantity=1, unit="cup"),
            Ingredient(name="Eggs", description="Eggs", quantity=2, unit=""),
            Ingredient(name="Milk", description="Milk", quantity=1, unit="cup"),
            Ingredient(name="Butter", description="Butter", quantity=2, unit="tbsp"),
        ],
        directions=[
            Direction(description="Mix ingredients", time=5),
            Direction(description="Cook", time=10),
        ],
    ),
    Recipe(
        name="Pizza",
        description="Delicious pizza",
        ingredients=[
            Ingredient(name="Flour", description="Flour", quantity=1, unit="cup"),
            Ingredient(name="Eggs", description="Eggs", quantity=2, unit=""),
            Ingredient(name="Milk", description="Milk", quantity=1, unit="cup"),
            Ingredient(name="Butter", description="Butter", quantity=2, unit="tbsp"),
        ],
        directions=[
            Direction(description="Mix ingredients", time=5),
            Direction(description="Cook", time=10),
        ],
    ),
]


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/recipes")
async def create_recipe(recipe: Recipe):
    recipes.append(recipe)
    return recipe


@app.get("/recipes")
async def get_recipes():
    return recipes


@app.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: int):
    return recipes[recipe_id]


def dev():
    uvicorn.run("src.main:app", port=8000, reload=True)
