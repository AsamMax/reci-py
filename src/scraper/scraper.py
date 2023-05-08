from typing import Self

from ..schemas.recipies import RecipeCreate


class RecipeScraper:
    def __init__(self, url):
        self.url = url

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        pass

    def scrape(self) -> RecipeCreate:
        raise NotImplementedError()
