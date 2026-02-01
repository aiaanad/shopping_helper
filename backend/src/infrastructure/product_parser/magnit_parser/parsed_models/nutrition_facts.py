from typing import Optional

from pydantic import BaseModel, Field


class NutritionFacts(BaseModel):
    kilocalories: Optional[float] = Field(gt=0, le=1000, description="Килокалории на 100 грамм продукта")
    proteins: Optional[float] = Field(gt=0, le=100, description="Белки на 100 грамм продукта")
    fats: Optional[float] = Field(gt=0, le=100, description="Жиры на 100 грамм продукта")
    carbohydrates: Optional[float] = Field(gt=0, le=100, description="Углеводы на 100 грамм продукта")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            float: lambda v: round(v, 2)
        }

