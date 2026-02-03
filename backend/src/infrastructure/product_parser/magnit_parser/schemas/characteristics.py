from typing import Annotated

from pydantic import BaseModel, Field


class Characteristics(BaseModel):
    product_type: Annotated[str, Field(description='Тип продукта')]
    weight: Annotated[float, Field(gt=0, description='Вес продукта в граммах')]
    _is_by_weight: Annotated[bool, Field(repr=False, description='Продается ли продукт на развес')]
