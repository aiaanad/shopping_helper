import logging
import time
from typing import List

from ...http import PoliteHttpClient
from ..parsers import CategoryParser
from ..schemas import CatalogCategory, CategoryProduct


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CategoryService:
    def __init__(self, http_client: PoliteHttpClient, parser: CategoryParser):
        self.http = http_client
        self.parser = parser
        self._processed_pages = set()  # Для отслеживания уже обработанных страниц

    def fetch_category_products(self, category: CatalogCategory,
                                shop_code: int = 784507,
                                shop_type: int = 1,
                                max_pages: int = 5) -> List[CategoryProduct]:
        """
        Получает товары из категории с пагинацией
        """
        all_products: List[CategoryProduct] = []
        page = 0  # Начинаем с 0

        logger.info(f"=== Начало парсинга категории: {category.title} ===")

        while page < max_pages:
            # Создаем уникальный ключ для страницы
            page_key = f"{category.url}_page{page}"

            if page_key in self._processed_pages:
                logger.warning(f"Страница {page} уже обрабатывалась, пропускаем")
                page += 1
                continue

            params = {
                'shopCode': shop_code,
                'shopType': shop_type,
                'page': page
            }

            logger.info(f"  Запрос страницы {page}...")
            logger.debug(f"    URL: {category.url}")
            logger.debug(f"    Параметры: {params}")

            # ВАЖНО: Добавим временную метку для избежания кэша
            timestamp = int(time.time())
            params_with_timestamp = {**params, '_t': timestamp}

            content = self.http.get(url=category.url, params=params_with_timestamp)

            if not content:
                logger.warning(f"    Пустой ответ, останавливаемся")
                break

            logger.debug(f"    Получено {len(content)} символов")

            # Сохраняем для отладки (первую и последнюю страницу)
            if page == 0 or page == max_pages - 1:
                with open(f'debug_page_{category.title}_page{page}.html', 'w', encoding='utf-8') as f:
                    f.write(content[:5000] + "\n\n..." if len(content) > 5000 else content)

            page_products = self.parser.parse(content)

            if not page_products:
                logger.info(f"    Парсер не нашел товаров на странице {page}")

                # Проверяем, не капча ли это
                if "captcha" in content.lower() or "cloudflare" in content.lower():
                    logger.error(f"    ОБНАРУЖЕНА КАПЧА ИЛИ CLOUDFLARE!")
                    break

                # Если первая страница пустая - что-то не так
                if page == 0:
                    logger.error(f"    ПЕРВАЯ СТРАНИЦА ПУСТАЯ! Проверьте селектор.")
                    break
                else:
                    logger.info(f"    Вероятно, это последняя страница, останавливаемся")
                    break

            logger.info(f"    На странице {page} найдено: {len(page_products)} товаров")

            # Логируем несколько товаров для примера
            for i, prod in enumerate(page_products[:3]):  # Первые 3 товара
                logger.debug(f"      Товар {i + 1}: {prod.title[:50]}...")

            all_products.extend(page_products)
            self._processed_pages.add(page_key)  # Помечаем как обработанную

            page += 1

            # Пауза между запросами
            time.sleep(0.3)

        logger.info(f"=== Категория '{category.title}': итого {len(all_products)} товаров ===\n")
        return all_products

    def fetch_multiple_products(self, categories: List[CatalogCategory],
                                shop_code: int = 784507,
                                shop_type: int = 1,
                                max_pages: int = 5) -> List[CategoryProduct]:
        """
        Парсит товары из нескольких категорий
        """
        results = []

        # Очищаем кэш HTTP-клиента перед началом
        logger.info("Очищаем кэш HTTP-клиента...")
        self.http.clear_cache()

        # Очищаем отслеживание страниц
        self._processed_pages.clear()

        for i, category in enumerate(categories, 1):
            logger.info(f"\n{'=' * 50}")
            logger.info(f"Обработка категории {i}/{len(categories)}")
            logger.info(f"Категория: {category.title}")
            logger.info(f"URL: {category.url}")
            logger.info(f"{'=' * 50}")

            try:
                products: List[CategoryProduct] = self.fetch_category_products(
                    category,
                    shop_code=shop_code,
                    shop_type=shop_type,
                    max_pages=max_pages
                )
                results.extend(products)
                logger.info(f"✓ Категория '{category.title}' обработана: {len(products)} товаров")

            except Exception as e:
                logger.error(f"✗ Ошибка обработки '{category.title}': {e}", exc_info=True)

            # Увеличиваем паузу между категориями
            time.sleep(1.0)  # 1 секунда между категориями

        logger.info(f"\n{'=' * 50}")
        logger.info(f"ВСЕГО СОБРАНО ТОВАРОВ: {len(results)}")
        logger.info(f"{'=' * 50}")

        return results

    def clear_processed_pages(self):
        """Очищает список обработанных страниц"""
        self._processed_pages.clear()