from typing import Annotated

from pydantic import Field, computed_field, HttpUrl, AfterValidator, BaseModel, ConfigDict

from .base import BaseSchema


def validate_url(url: str) -> str:
    HttpUrl(url)
    return url


class CategoryProduct(BaseSchema):
    title: Annotated[str, Field(..., description="Заголовок продукта в каталоге",
                                min_length=2,
                                max_length=200)]
    href: Annotated[str, Field(..., description="Полный URL продукта",
                               min_length=10,
                               max_length=200)]

    @computed_field(alias='catalog-url')
    @property
    def url(self) -> Annotated[str, AfterValidator(validate_url)]:
        return f'https://magnit.ru{self.href}'

