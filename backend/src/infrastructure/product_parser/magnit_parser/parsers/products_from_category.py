import logging
from typing import List
from pprint import pprint

from bs4 import BeautifulSoup

from .base import PageParser
from ..schemas.category_product import CategoryProduct


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CategoryParser(PageParser):
    def __init__(self):
        self.selector = 'a.pl-hover-base[data-test-id*="v-app-link"]'

    def parse(self, content: str) -> List[CategoryProduct]:
        if not content:
            logger.warning("Пустой контент передан в парсер")
            return []

        logger.debug(f"Длина контента: {len(content)} символов")

        soup = BeautifulSoup(content, 'lxml')
        if not soup:
            logger.warning("При преобразовании вернулся пустой суп")
            return []

        # Проверка, что это действительно HTML страница с товарами
        if "товар" not in content.lower() and len(content) < 1000:
            logger.warning(f"Контент слишком короткий или не содержит товаров: {len(content)} символов")
            logger.debug(f"Первые 500 символов: {content[:500]}")
            return []

        selected = soup.select(self.selector)
        logger.info(f"Найдено элементов по селектору: {len(selected)}")

        if not selected:
            # Дополнительная диагностика
            all_links = soup.find_all('a')
            logger.warning(f"Всего ссылок на странице: {len(all_links)}")

            # Проверьте другие возможные селекторы
            test_selectors = [
                'a[href*="/promo-product/"]',
                'article a',
                '[data-test-id]',
                '.pl-hover-base'
            ]

            for test_selector in test_selectors:
                test_results = soup.select(test_selector)
                if test_results:
                    logger.info(f"По селектору '{test_selector}' найдено: {len(test_results)}")
                    break

        products: List[CategoryProduct] = []
        for product in selected:
            href = product.get('href', '').strip()
            title = product.get('title', '').strip()

            if href and title:
                products.append(CategoryProduct(title=title, href=href))
                logger.debug(f"Добавлен продукт: {title[:50]}...")

        logger.info(f"Итоговое количество продуктов: {len(products)}")
        return products