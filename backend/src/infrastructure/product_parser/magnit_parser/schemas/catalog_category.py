from typing import Annotated

from pydantic import Field, computed_field, HttpUrl, AfterValidator, BaseModel, ConfigDict

from .base import BaseSchema


def validate_url(url: str) -> str:
    HttpUrl(url)
    return url


class CatalogCategory(BaseSchema):
    title: Annotated[str, Field(description="Заголовок продукта в каталоге",
                                min_length=3,
                                max_length=200, alias='catalog-title')]
    href: Annotated[str, Field(description="Полный URL продукта",
                               min_length=10,
                               max_length=400, alias='catalog-href', repr=False)]

    @computed_field(alias='catalog-url')
    @property
    def url(self) -> Annotated[str, AfterValidator(validate_url)]:
        return f'https://magnit.ru{self.href}'
