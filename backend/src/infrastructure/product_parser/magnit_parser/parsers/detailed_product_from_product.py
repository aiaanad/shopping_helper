from enum import Enum
from typing import Optional, Dict, Any

from bs4 import BeautifulSoup

from .base import PageParser


class Selectors(Enum):
    details = 'div.unit-product-details__details-container'
    characteristics_item = '.product-details-parameters-list__item'
    characteristics_name = 'span[data-test-id*="item-name"]'
    characteristics_value = 'span[data-test-id*="item-value"]'
    nutrition = 'section.product-details-nutrition-facts div[data-test-id="v-product-details-nutrition-fact-value"]'
    bulk_food_weight = 'span.pl-text.product-details-price__weight[data-test-id="v-text"][data-test-id="v-product-detail-weight"]'


class ProductDetailsParser(PageParser):
    def __init__(self):
        self._selectors = Selectors

    def parse(self, content: str) -> Dict[str, Any]:
        if not content:
            return {}

        soup = BeautifulSoup(content, 'lxml')
        details = soup.select_one(self._selectors.details.value)

        if not details:
            return {}

        return {
            'characteristics': self._extract_characteristics(details),
            'nutrition_facts': self._extract_nutrition(details),
            'is_food_by_weight': self._extract_weight_for_check_food_is_bulk(details),
        }

    def _extract_characteristics(self, soup: BeautifulSoup) -> Dict[str, str]:
        characteristics = {}
        items = soup.select(self._selectors.characteristics_item.value)

        for item in items:
            name = item.select_one(self._selectors.characteristics_name.value)
            value = item.select_one(self._selectors.characteristics_value.value)

            if name and value:
                name_text = name.get_text(strip=True)
                value_text = value.get_text(strip=True)
                if name_text and value_text:
                    characteristics[name_text] = value_text

        return characteristics

    def _extract_weight_for_check_food_is_bulk(self, soup: BeautifulSoup) -> bool:
        weight = soup.select(self._selectors.bulk_food_weight.value)
        if not weight:
            return False
        return True

    def _extract_nutrition(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        values = soup.select(self._selectors.nutrition.value)

        if len(values) < 4:
            return None

        facts = {
            'kilocalories': values[0].get_text(strip=True),
            'proteins': values[1].get_text(strip=True) if len(values) > 1 else "",
            'fats': values[2].get_text(strip=True) if len(values) > 2 else "",
            'carbohydrates': values[3].get_text(strip=True) if len(values) > 3 else "",
        }

        return facts if any(facts.values()) else None
