from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import recipies as models
from ..schemas.recipies import Recipe

router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=Recipe)
async def create_recipe(recipe: Recipe, db: Session = Depends(get_db)) -> models.Recipe:
    db_recipe = models.Recipe(name=recipe.name, description=recipe.description)
    # add deep relationships
    db_recipe.ingredients = [
        models.Ingredient(**ingredient.dict()) for ingredient in recipe.ingredients
    ]
    db_recipe.directions = [
        models.Direction(**direction.dict()) for direction in recipe.directions
    ]
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@router.get("/", response_model=list[Recipe])
async def get_recipes(db: Session = Depends(get_db)) -> list[models.Recipe]:
    return db.query(models.Recipe).all()


@router.get("/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: int, db: Session = Depends(get_db)) -> models.Recipe:
    return db.query(models.Recipe).filter(models.Recipe.id == recipe_id).one()
