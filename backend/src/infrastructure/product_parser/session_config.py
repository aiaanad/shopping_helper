from typing import Dict

import requests
from requests.exceptions import RequestException


class Session:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.9',
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def headers_update(self, headers: Dict[str, str] | None) -> None:
        try:
            self.session.headers.update(headers)
        except RequestException as e:
            raise ValueError from e

    def get_session(self):
        return self.session


# Синглтон
session = Session().get_session()
