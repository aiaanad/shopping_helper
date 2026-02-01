from typing import Optional

from pydantic import BaseModel, Field, computed_field


class CatalogProduct(BaseModel):
    title: str = Field(..., description="Заголовок продукта в каталоге",
                       min_length=10,
                       max_length=200)
    href: str = Field(..., description="Полный URL продукта",
                      min_length=10,
                      max_length=200)

    @computed_field
    @property
    def url(self) -> str:
        return f'https://magnit.ru{self.href}'
