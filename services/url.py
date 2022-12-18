from typing import Any
from urllib.parse import urlencode


def set_query_params(url: str, **query_params: Any) -> str:
    if not query_params:
        return url

    return url + "?" + urlencode(query_params)
