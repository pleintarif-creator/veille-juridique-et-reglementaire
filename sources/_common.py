"""Utilitaires communs aux différents scrapers."""

import logging
import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/webp,*/*;q=0.8"
    ),
}

TIMEOUT = 25


def get(url: str, params: Optional[dict] = None, retries: int = 3) -> Optional[requests.Response]:
    """GET avec headers navigateur et petit retry."""
    last_exc = None
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
            if r.status_code == 200:
                return r
            logger.warning("%s -> HTTP %s (tentative %s)", url, r.status_code, attempt + 1)
        except requests.RequestException as exc:  # noqa: PERF203
            last_exc = exc
            logger.warning("%s -> %s (tentative %s)", url, exc, attempt + 1)
        time.sleep(1.5 * (attempt + 1))
    if last_exc:
        logger.error("Echec définitif %s : %s", url, last_exc)
    return None


def soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def clean(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


_KW_CACHE: dict[tuple[str, ...], list[tuple[str, "re.Pattern"]]] = {}


def _compile_keywords(keywords: list[str]):
    key = tuple(keywords)
    cached = _KW_CACHE.get(key)
    if cached is not None:
        return cached
    compiled = []
    for kw in keywords:
        # on échappe la ponctuation et on borne par (?<!\w) / (?!\w) :
        # cela gère aussi les mots-clés multi-mots et les apostrophes.
        pattern = re.compile(
            r"(?<!\w)" + re.escape(kw) + r"(?!\w)",
            flags=re.IGNORECASE,
        )
        compiled.append((kw, pattern))
    _KW_CACHE[key] = compiled
    return compiled


def matches_keywords(text: str, keywords: list[str]) -> list[str]:
    """Retourne les mots-clés trouvés (mot entier, insensible à la casse)."""
    if not text:
        return []
    hits: list[str] = []
    for kw, pattern in _compile_keywords(keywords):
        if pattern.search(text):
            hits.append(kw)
    return hits
