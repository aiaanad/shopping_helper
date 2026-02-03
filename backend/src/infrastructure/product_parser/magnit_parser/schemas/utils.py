import re
from decimal import Decimal, InvalidOperation
from typing import Optional
from functools import lru_cache


class TextUtils:
    """Утилиты для работы с текстом"""

    @staticmethod
    def clean_text(text: Optional[str]) -> Optional[str]:
        """Очистка текста от лишних пробелов и символов"""
        if not text:
            return None
        return ' '.join(text.split()).strip()

    @staticmethod
    @lru_cache(maxsize=100)
    def extract_number(text: str) -> Optional[Decimal]:
        """Извлекает число из текста"""
        if not text:
            return None

        # Ищем числа с точкой или запятой как разделителем
        match = re.search(r'(\d+[.,]?\d*)', text.replace(' ', ''))
        if match:
            try:
                # Заменяем запятую на точку для Decimal
                number_str = match.group(1).replace(',', '.')
                return Decimal(number_str)
            except (InvalidOperation, ValueError):
                return None
        return None

    @staticmethod
    def normalize_weight(weight_text: str) -> Optional[Decimal]:
        """Нормализует вес в кг"""
        if not weight_text:
            return None

        weight_text = weight_text.lower().strip()
        number = TextUtils.extract_number(weight_text)

        if number is None:
            return None

        # Конвертируем в кг
        if 'г' in weight_text or 'грамм' in weight_text:
            return number / Decimal('1000')
        elif 'кг' in weight_text or 'килограмм' in weight_text:
            return number
        elif 'мг' in weight_text or 'миллиграмм' in weight_text:
            return number / Decimal('1000000')
        elif 'л' in weight_text and 'г' not in weight_text:  # Литр
            return number  # Для жидкостей считаем 1л = 1кг (грубо)
        else:
            # По умолчанию считаем граммами
            return number / Decimal('1000')


class PriceUtils:
    """Утилиты для работы с ценами"""

    @staticmethod
    def extract_price(price_text: str) -> Optional[Decimal]:
        """Извлекает цену из текста"""
        if not price_text:
            return None

        # Удаляем символы валюты и пробелы
        cleaned = re.sub(r'[^\d.,]', '', price_text.strip())
        number = TextUtils.extract_number(cleaned)
        return number

    @staticmethod
    def calculate_price_per_kg(price: Decimal, weight_kg: Decimal) -> Optional[Decimal]:
        """Рассчитывает цену за кг"""
        if not price or not weight_kg or weight_kg == 0:
            return None
        return price / weight_kg