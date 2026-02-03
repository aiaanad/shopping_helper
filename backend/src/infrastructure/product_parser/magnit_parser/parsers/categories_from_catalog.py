from typing import Optional, List

from bs4 import BeautifulSoup

from .base import PageParser
from ..schemas.catalog_category import CatalogCategory


class CatalogParser(PageParser):
    def __init__(self):
        self.selector = (
                'div.pl-list-item.pl-list-item_primary.pl-list-item_hoverable.pl-list-item_icon_m.header-catalog-item'
                + ' div.pl-list-item-content'
                + ' div.pl-list-item-content-left'
                + ' div.pl-list-item__title'
                + ' a.header-catalog-item__subitem')

    def update_selector(self, selector: Optional[str]):
        if selector:
            self.selector = selector

    def parse(self, content: str) -> List[CatalogCategory]:
        if not content:
            return []

        soup = BeautifulSoup(content, 'lxml')

        categories: List[CatalogCategory] = []
        selected = soup.select(self.selector)
        if not selected:
            # logger.debug("DEBUG: Categories not found in catalog with current selector")
            return []
        for category in selected:
            href = category.get('href', '').strip()
            title = category.text.strip()
            if href and title:
                categories.append(CatalogCategory(title=title, href=href))

        return categories
