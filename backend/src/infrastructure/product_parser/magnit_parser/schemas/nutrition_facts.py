from typing import Optional, Annotated

from pydantic import BaseModel, Field


class NutritionFacts(BaseModel):
    kilocalories: Annotated[Optional[float], Field(gt=0, le=1000,
                                                   description="Килокалории на 100 грамм продукта")]
    proteins: Annotated[Optional[float], Field(gt=0, le=100,
                                               description="Белки на 100 грамм продукта")]
    fats: Annotated[Optional[float], Field(gt=0, le=100,
                                           description="Жиры на 100 грамм продукта")]
    carbohydrates: Annotated[Optional[float], Field(gt=0, le=100,
                                                    description="Углеводы на 100 грамм продукта")]


