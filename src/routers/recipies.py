from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src.scraper.scraper import RecipeScraper

from ..database import SessionLocal
from ..models import recipies as models
from ..schemas.recipies import Recipe, RecipeCreate

router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=Recipe)
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)) -> models.Recipe:
    db_recipe: models.Recipe = models.Recipe(
        name=recipe.name, description=recipe.description
    )
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


@router.post("/from_url", response_model=Recipe)
async def create_recipe_from_url(
    url: str, db: Session = Depends(get_db)
) -> models.Recipe:
    async with RecipeScraper(url) as scraper:
        recipe = scraper.scrape()
    return create_recipe(recipe, db)


@router.get("/", response_model=list[Recipe])
def get_recipes(
    search: str | None = None,
    tags: list[str] | None = None,
    db: Session = Depends(get_db),
) -> list[models.Recipe]:
    # TODO: implement search / Tags
    return db.query(models.Recipe).all()


@router.get("/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)) -> models.Recipe:
    try:
        return db.query(models.Recipe).filter(models.Recipe.id == recipe_id).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Recipe not found")


@router.patch("/{recipe_id}", response_model=Recipe)
def patch_recipe(
    recipe_id: int, recipe: RecipeCreate, db: Session = Depends(get_db)
) -> models.Recipe:
    db_recipe = get_recipe(recipe_id)
    db_recipe.name = recipe.name
    db_recipe.description = recipe.description
    # add deep relationships
    db_recipe.ingredients = [
        models.Ingredient(**ingredient.dict()) for ingredient in recipe.ingredients
    ]
    db_recipe.directions = [
        models.Direction(**direction.dict()) for direction in recipe.directions
    ]
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@router.delete("/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)) -> None:
    db.query(models.Recipe).filter(models.Recipe.id == recipe_id).delete()
