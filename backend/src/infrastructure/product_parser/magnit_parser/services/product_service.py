import logging
import time
from typing import List, Any, Dict

from ...http import PoliteHttpClient
from ..parsers import ProductDetailsParser
from ..schemas import CategoryProduct

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductService:
    """Сервис для работы с товарами"""

    def __init__(self, http_client: PoliteHttpClient, parser: ProductDetailsParser):
        self.http = http_client
        self.parser = parser

    def fetch_product_details(self, product: CategoryProduct) -> Dict[str, Any]:
        content = self.http.get(product.url)

        if not content:
            return {}

        details = self.parser.parse(content)
        details.update({
            'title': product.title,
            'url': product.url,
            'success': (details.get('weight') or
                        details.get('characteristics') or
                        details.get('nutrition_facts'))
        })

        return details

    def fetch_multiple_details(self, products: List[CategoryProduct]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []

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
