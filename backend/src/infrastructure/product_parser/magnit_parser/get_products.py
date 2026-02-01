from collections import defaultdict
from functools import cached_property
import json
import logging
from pprint import pprint
import time
from typing import List, Annotated, Optional, Dict, Any
from typing import Protocol

import requests
# протокол - аналог интерфейса

from bs4 import BeautifulSoup
from pydantic import ValidationError

from .parsed_models import CatalogProduct
from ..session_config import session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# синтаксические соглашения(по советам дипсика):
# Одно подчеркивание в начале = "Это внутренний атрибут, не используйте его напрямую извне класса"
# Два подчеркивания в начале = Name Mangling (искажение имен) - Python изменяет имя, чтобы затруднить доступ извне
# Пример: self.__secret = "hidden"  # Станет _MyClass__secret
# Одно подчеркивание в конце = Используется, чтобы избежать конфликта с ключевыми словами
# Двойное подчеркивание в начале и в конце = Специальные методы Python (magic methods)

class HttpClient(Protocol):
    def get(self, url: str, params: Optional[Dict] = None) -> Optional[str]: ...

    def clear_cache(self, content: str) -> Any: ...


class RequestHttpClient(HttpClient):
    """
    Http клиент на основе requests, библиотеки для работы с HTTP-запросами в Python.
    Она обеспечивает интерфейс для выполнения операций с REST API, загрузки данных с веб-страниц,
    а также отправки файлов и авторизации.
    """

    def __init__(self):
        self.session = session
        self._cache: Dict[str, str] = {}

    def get(self, url: str, params: Optional[Dict] = None) -> Optional[str]:
        cache_key = f'{url}_{json.dumps(params, sort_keys=True) if params else ''}'
        # Параметр sort_keys задаёт, будут ли ключи в результирующем JSON отсортированы в алфавитном порядке.
        # Сериализация питон словаря в json объект
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            response = self.session.get(url=url, params=params, timeout=(5, 10))
            response.raise_for_status()
            content = response.text
            self._cache[cache_key] = content
            return content
        except requests.RequestException as e:
            logger.error(f"HTTP error: {e}")
            return None

    def clear_cache(self, content: str) -> Any:
        self._cache.clear()


class PageParser(Protocol):
    def parse(self, content: str) -> Any: ...


class CatalogParser(PageParser):
    def __init__(self):
        self.selector = 'a.pl-hover-base'

    def parse(self, content: str) -> List[CatalogProduct]:
        if not content:
            return []

        soup = BeautifulSoup(content, 'lxml')

        products = []
        for product in soup.select(self.selector):
            href = product.get('href', '').strip()
            title = product.get('title', '').strip()
            if href and title:
                products.append(CatalogProduct(title=title, href=href))

        return products

    def selector_update(self, selector: str = None):
        if selector:
            self.selector = selector


class ProductDetailsParser(PageParser):
    def __init__(self):
        self._selectors = {
            'details': 'div.unit-product-details__details-container',
            'characteristics_item': '.product-details-parameters-list__item',
            'characteristics_name': 'span[data-test-id*="item-name"]',
            'characteristics_value': 'span[data-test-id*="item-value"]',
            'nutrition': 'section.product-details-nutrition-facts div[data-test-id="v-product-details-nutrition-fact-value"]',
        }

    def parse(self, content: str) -> Dict[str, Any]:
        if not content:
            return {}

        soup = BeautifulSoup(content, 'lxml')
        details = soup.select_one(self._selectors['details'])

        if not details:
            return {}

        return {
            'characteristics': self._extract_characteristics(details),
            'nutrition_facts': self._extract_nutrition(details),
        }

    def _extract_characteristics(self, soup: BeautifulSoup) -> Dict[str, str]:
        characteristics = {}
        items = soup.select(self._selectors['characteristics_item'])

        for item in items:
            name = item.select_one(self._selectors['characteristics_name'])
            value = item.select_one(self._selectors['characteristics_value'])

            if name and value:
                name_text = name.get_text(strip=True)
                value_text = value.get_text(strip=True)
                if name_text and value_text:
                    characteristics[name_text] = value_text

        return characteristics

    def _extract_nutrition(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        values = soup.select(self._selectors['nutrition'])

        if len(values) < 4:
            return None

        facts = {
            'kilocalories': values[0].get_text(strip=True),
            'proteins': values[1].get_text(strip=True) if len(values) > 1 else "",
            'fats': values[2].get_text(strip=True) if len(values) > 2 else "",
            'carbohydrates': values[3].get_text(strip=True) if len(values) > 3 else "",
        }

        return facts if any(facts.values()) else None


class CatalogService:
    def __init__(self, http_client: RequestHttpClient, parser: CatalogParser):
        self.http = http_client
        self.parser = parser
        self.base_url = "https://magnit.ru/catalog"

    def fetch_all_products(self, shop_code: int = 784507,
                           shop_type: int = 1,
                           max_pages: int = 10) -> List[CatalogProduct]:
        all_products = []
        page = 0

        while page < max_pages:
            params = {'shopCode': shop_code, 'shopType': shop_type, 'page': page}
            content = self.http.get(url=self.base_url, params=params)

            if not content:
                break

            page_products = self.parser.parse(content)

            if not page_products:
                break

            all_products.extend(page_products)
            page += 1
            time.sleep(0.1)

        return all_products


class ProductService:
    """Сервис для работы с товарами"""

    def __init__(self, http_client: RequestHttpClient, parser: ProductDetailsParser):
        self.http = http_client
        self.parser = parser

    def fetch_product_details(self, product: CatalogProduct) -> Dict[str, Any]:
        content = self.http.get(product.url)

        if not content:
            return {}

        details = self.parser.parse(content)
        details.update({
            'title': product.title,
            'url': product.url,
            'success': bool(details.get('weight') or
                            details.get('characteristics') or
                            details.get('nutrition_facts'))
        })

        return details

    def fetch_multiple_products(self, products: List[CatalogProduct]) -> List[Dict[str, Any]]:
        results = []

        for i, product in enumerate(products, 1):
            logger.info(f"Processing product {i}/{len(products)}")

            try:
                result = self.fetch_product_details(product)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {product.title}: {e}")
                results.append({
                    'title': product.title,
                    'url': product.url,
                    'error': str(e),
                    'success': False
                })

            time.sleep(0.1)

        return results


# Фасад.
class MagnitParser:
    def __init__(self):
        self.http = RequestHttpClient()
        self.product_parser = ProductDetailsParser()
        self.catalog_parser = CatalogParser()

        self.product_service = ProductService(self.http, self.product_parser)
        self.catalog_service = CatalogService(self.http, self.catalog_parser)

    @cached_property
    def catalog_products(self) -> List[CatalogProduct]:
        return self.catalog_service.fetch_all_products()

    def parse_products(self, products: Optional[List[CatalogProduct]]) -> List[Dict[str, Any]]:
        products_to_parse = products or self.catalog_products
        return self.product_service.fetch_multiple_products(products_to_parse)

    def clear_cache(self):
        self.http.clear_cache()


def main():
    # Создаем клиент
    client = MagnitParser()

    # Получаем товары из каталога
    products = client.catalog_products  # Первые 3 товара
    # Парсим их
    results = client.parse_products(products)
    for result in results:
        print(f"\n{result['title']}")
        print(f"Success: {result['success']}")
        if result['success']:
            if result.get('characteristics'):
                print(f"Characteristics: {len(result['characteristics'])}")


if __name__ == '__main__':
    main()
