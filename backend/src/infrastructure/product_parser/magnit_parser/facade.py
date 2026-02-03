from functools import cached_property
import logging
from typing import List, Optional, Dict, Any

from .schemas import CategoryProduct, CatalogCategory
from .parsers import CatalogParser, CategoryParser, ProductDetailsParser

from .services import CatalogService, CategoryService, ProductService
from ..http import PoliteHttpClient


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# синтаксические соглашения(по советам дипсика):
# Одно подчеркивание в начале = "Это внутренний атрибут, не используйте его напрямую извне класса"
# Два подчеркивания в начале = Name Mangling (искажение имен) - Python изменяет имя, чтобы затруднить доступ извне
# Пример: self.__secret = "hidden"  # Станет _MyClass__secret
# Одно подчеркивание в конце = Используется, чтобы избежать конфликта с ключевыми словами
# Двойное подчеркивание в начале и в конце = Специальные методы Python (magic methods)


class MagnitParser:
    def __init__(self):
        self.http = PoliteHttpClient()
        self.product_parser = ProductDetailsParser()
        self.catalog_parser = CatalogParser()
        self.category_parser = CategoryParser()

        self.category_service = CategoryService(self.http, self.category_parser)
        self.product_service = ProductService(self.http, self.product_parser)
        self.catalog_service = CatalogService(self.http, self.catalog_parser)

        self.products: List[CatalogCategory] = []

    @cached_property
    def catalog_categories(self) -> List[CatalogCategory]:
        return self.catalog_service.fetch_categories()

    def category_products(self, categories: Optional[List[CatalogCategory]] = None) -> List[CategoryProduct]:
        categories_to_parse = categories if categories else self.catalog_categories
        self.products = self.category_service.fetch_multiple_products(categories_to_parse)
        return self.products

    def parse_products(self, products: Optional[List[CategoryProduct]] = None) -> List[Dict[str, Any]]:
        products_to_parse = products if products else self.category_products()
        return self.product_service.fetch_multiple_details(products_to_parse)

    def clear_cache(self):
        self.http.clear_cache()
