from . import CategoryProduct, NutritionFacts


class ParsedProduct(CategoryProduct):
    pass


class FoodProduct(ParsedProduct):
    """Еда фиксированного веса"""
    pass


class BulkFoodProduct(ParsedProduct, NutritionFacts):
    """Еда на развес"""
    pass


class NonFoodProduct(ParsedProduct):
    """Не съедобные товары"""
    pass
