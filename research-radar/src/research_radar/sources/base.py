from __future__ import annotations

import json
import time
from typing import Iterable, Iterator, List, Sequence, TypeVar
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET


USER_AGENT = "ResearchRadar/0.1 (https://zii-yye.github.io/; contact: ziyewang0324@gmail.com)"
T = TypeVar("T")


def _retry_delay(attempt: int, error: Exception) -> float:
    if isinstance(error, HTTPError):
        retry_after = error.headers.get("Retry-After")
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                pass
        if error.code == 429:
            return min(5.0 * attempt, 20.0)
        if 500 <= error.code < 600:
            return min(2.0 * attempt, 10.0)
    return min(2.0 * attempt, 10.0)


def _is_retryable(error: Exception) -> bool:
    if isinstance(error, HTTPError):
        return error.code == 429 or 500 <= error.code < 600
    return isinstance(error, URLError)


def fetch_bytes(url: str, timeout: int = 30, max_retries: int = 3) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            with urlopen(request, timeout=timeout) as response:
                return response.read()
        except (HTTPError, URLError) as error:
            last_error = error
            if attempt >= max_retries or not _is_retryable(error):
                raise
            time.sleep(_retry_delay(attempt, error))
    if last_error is not None:
        raise last_error
    raise RuntimeError(f"Failed to fetch URL: {url}")


def fetch_json(url: str, timeout: int = 30) -> dict:
    return json.loads(fetch_bytes(url, timeout=timeout).decode("utf-8"))


def fetch_xml(url: str, timeout: int = 30) -> ET.Element:
    return ET.fromstring(fetch_bytes(url, timeout=timeout))


def chunked(values: Sequence[T], size: int) -> Iterator[List[T]]:
    for index in range(0, len(values), size):
        yield list(values[index : index + size])
