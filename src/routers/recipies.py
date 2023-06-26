from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from ..models import recipies as models
from ..schemas.recipies import Recipe, RecipeCreate
from ..schemas.users import User
from ..scraper.scraper import RecipeScraper
from ..util.auth import get_current_user
from ..util.database import get_db

router = APIRouter()


@router.post("/", response_model=Recipe)
def create_recipe(
    recipe: RecipeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> models.Recipe:
    db_recipe = models.Recipe(
        name=recipe.name,
        description=recipe.description,
        dietType=recipe.dietType,
        mealType=recipe.mealType,
        tags=recipe.tags,
        last_modified=datetime.now(),
        owner=user.username,
    )
    # add deep relationships
    db_recipe.ingredients = [
        models.Ingredient(**ingredient.dict())
        for ingredient in recipe.ingredients
        if ingredient.name
    ]
    db_recipe.directions = [
        models.Direction(**direction.dict())
        for direction in recipe.directions
        if direction.description
    ]
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@router.post("/from_url", response_model=Recipe)
async def create_recipe_from_url(
    url: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> models.Recipe:
    async with RecipeScraper(url) as scraper:
        recipe = scraper.scrape()
    return create_recipe(recipe, db)


class RecipeOrdering(str, Enum):
    newest = "newest"
    oldest = "oldest"
    random = "random"
    alphabetical = "alphabetical"


@router.get("/", response_model=list[Recipe])
def get_recipes(
    search: str | None = None,
    tags: str | None = None,
    order: RecipeOrdering = RecipeOrdering.newest,
    limit: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[models.Recipe]:
    q = db.query(models.Recipe)

    # filter by user
    q.filter(models.Recipe.owner == user.username)

    # TODO: include more fields in search
    q.filter(models.Recipe.name.like(f"%{search}%"))
    # TODO: filter by Tags

    if order == RecipeOrdering.newest:
        q = q.order_by(models.Recipe.last_modified.desc())
    elif order == RecipeOrdering.oldest:
        q = q.order_by(models.Recipe.last_modified.asc())
    elif order == RecipeOrdering.random:
        q = q.order_by(func.random())
    elif order == RecipeOrdering.alphabetical:
        q = q.order_by(models.Recipe.name.asc())

    if limit:
        q = q.limit(limit)

    return q.all()


@router.get("/{recipe_id}", response_model=Recipe)
def get_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> models.Recipe:
    try:
        return db.query(models.Recipe).filter(models.Recipe.id == recipe_id).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Recipe not found")


@router.patch("/{recipe_id}", response_model=Recipe)
def patch_recipe(
    recipe_id: int,
    recipe: RecipeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> models.Recipe:
    db_recipe = get_recipe(recipe_id, db, user)

    # delete deep relationships
    db.query(models.Ingredient).filter(
        models.Ingredient.recipe_id == recipe_id
    ).delete()
    db.query(models.Direction).filter(models.Direction.recipe_id == recipe_id).delete()

    # update shallow relationships
    db_recipe.last_modified = datetime.now()
    db_recipe.name = recipe.name
    db_recipe.description = recipe.description

    # add deep relationships
    db_recipe.ingredients = [
        models.Ingredient(**ingredient.dict())
        for ingredient in recipe.ingredients
        if ingredient.name
    ]
    db_recipe.directions = [
        models.Direction(**direction.dict())
        for direction in recipe.directions
        if direction.description
    ]
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@router.delete("/{recipe_id}")
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    db.query(models.Recipe).filter(models.Recipe.id == recipe_id).delete()
