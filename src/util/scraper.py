import re
from typing import Self

import aiohttp
from aiohttp import ClientResponse, ClientSession
from bs4 import BeautifulSoup
from pydantic import HttpUrl

from ..schemas.recipies import DirectionCreate, IngredientCreate, RecipeCreate
from ..util.enums import DietType, MealType


class RecipeScraper:
    def __init__(self, url: HttpUrl):
        self.url = url
        self._session: ClientSession | None = None
        self._response: ClientResponse | None = None

    async def __aenter__(self) -> Self:
        # This could probably be done in the scrape function, using the normal context manager for both the session and the response
        self._session = aiohttp.ClientSession()
        self._response = await self._session.get(self.url)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None
        if self._response is not None:
            await self._response.release()
            self._response = None
        pass

    async def scrape(self) -> RecipeCreate:
        # TODO: Add support for other websites
        if self.url.host != "www.chefkoch.de":
            raise RuntimeError("This scraper only works for chefkoch.de")
        if self._response is None:
            raise RuntimeError("Please use the context manager to create the scraper")
        if self._response.status != 200:
            raise RuntimeError("Could not scrape the page")
        soup = BeautifulSoup(await self._response.text())

        title = soup.find("h1").text.strip()
        description = soup.find("p", class_="recipe-text").text.strip()

        ingredients = []
        for ingredient in soup.find("table", class_="ingredients").find_all("tr"):
            quantity_and_unit = ingredient.find("td", class_="td-left").text.strip()
            name = ingredient.find("td", class_="td-right").text.strip()
            quantity_search = re.search(r"^\d*\s*", quantity_and_unit)
            print(quantity_search)
            if quantity_search is None:
                quantity = ""
            else:
                quantity = quantity_search.group(0)
            unit = quantity_and_unit[len(quantity) :].strip()
            ingredients.append(
                IngredientCreate(
                    name=name,
                    quantity=int(quantity.strip()) if quantity.strip() else 1,
                    unit=unit,
                )
            )

        directions = []
        for direction in (
            soup.find("h2", text="Zubereitung")
            .parent.find("div", class_="ds-box")
            .text.split("\n")
        ):
            directions.append(DirectionCreate(description=direction.strip()))

        return RecipeCreate(
            name=title,
            description=description,
            dietType=DietType.vegan,
            mealType=MealType.dinner,
            tags=[],
            ingredients=ingredients,
            directions=directions,
        )
