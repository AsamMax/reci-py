"""
keep in sync with frontend
"""
from enum import StrEnum


class DietType(StrEnum):
    vegan = "vegan"
    vegetarian = "vegetarian"
    fish = "fish"
    seafood = "seafood"
    poultry = "poultry"
    beef = "beef"
    pork = "pork"
    other = "other"


class MealType(StrEnum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"
    dessert = "dessert"
    drink = "drink"
    other = "other"


class RecipeTags(StrEnum):
    quick = "quick"
    easy = "easy"
    healthy = "healthy"
    cheap = "cheap"
    spicy = "spicy"
    sweet = "sweet"
    salty = "salty"
    savory = "savory"
    satisfying = "satisfying"
    filling = "filling"
    light = "light"
    heavy = "heavy"
