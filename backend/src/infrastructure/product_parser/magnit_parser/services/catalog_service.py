from typing import List

from ..parsers import CatalogParser
from ..schemas import CatalogCategory
from ...http import PoliteHttpClient


class CatalogService:
    def __init__(self, http_client: PoliteHttpClient, parser: CatalogParser):
        self.http = http_client
        self.parser = parser
        self.base_url = "https://magnit.ru/catalog"

    def fetch_categories(self, shop_code: int = 784507,
                         shop_type: int = 1) -> List[CatalogCategory]:
        params = {
            'shopType': shop_type,
            'shopCode': shop_code,
        }
        content = self.http.get(self.base_url, params)
        return self.parser.parse(content)
