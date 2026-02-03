import json
import random
import time
from typing import Protocol, Optional, Dict, Any

import requests

from .session_config import session


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
            # logger.error(f"HTTP error: {e}")
            return None

    def clear_cache(self, content: Optional[str] = None):
        self._cache.clear()


class PoliteHttpClient(RequestHttpClient):
    def get(self, url: str, params=None):
        # Случайная пауза между 1 и 3 секундами
        time.sleep(random.uniform(1.0, 3.0))
        return super().get(url, params)
