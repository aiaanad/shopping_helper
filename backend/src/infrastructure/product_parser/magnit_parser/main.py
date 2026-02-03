from pprint import pprint

from . import MagnitParser


def main():
    parser = MagnitParser()
    parser.http.clear_cache()

    # Только первые 3 категории
    categories = parser.catalog_categories[:3]
    pprint(categories)
    # Только 2 страницы на категорию
    products = parser.category_service.fetch_multiple_products(
        categories,
        max_pages=5
    )

    # Только первые 10 товаров
    details = parser.product_service.fetch_multiple_details(products)

    return details


if __name__ == '__main__':
    pprint(main())
