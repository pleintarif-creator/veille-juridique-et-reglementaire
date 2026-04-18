"""Scraping de la section actualités publiques de Doctrine.fr.

Doctrine.fr propose une section d'actualités / blog juridique en accès
libre. On y récupère les articles récents, filtrés ensuite par mots-clés.
"""

from __future__ import annotations

import logging
from typing import Iterable

from ._common import clean, get, soup

logger = logging.getLogger(__name__)

CANDIDATE_URLS = [
    "https://www.doctrine.fr/blog",
    "https://www.doctrine.fr/actualites",
    "https://www.doctrine.fr/",
]

SOURCE_LABEL = "Doctrine.fr"


def _parse(html: str) -> list[dict]:
    s = soup(html)
    items: list[dict] = []
    seen: set[str] = set()

    # Stratégie robuste : on prend tous les liens qui pointent vers une
    # page d'article / actualité et dont le libellé ressemble à un titre.
    for a in s.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/"):
            href = "https://www.doctrine.fr" + href
        if "doctrine.fr" not in href:
            continue
        # on filtre les liens manifestement non-articles
        if any(
            seg in href
            for seg in (
                "/login",
                "/signup",
                "/connexion",
                "/inscription",
                "#",
                "/tarifs",
                "/produits",
                "/contact",
                "/api",
            )
        ):
            continue
        if href in seen:
            continue

        title = clean(a.get_text())
        # heuristique : titre plausible si suffisamment long
        if len(title) < 25 or len(title) > 300:
            continue
        # on exclut les éléments de navigation évidents
        low = title.lower()
        if low in {"en savoir plus", "voir plus", "lire la suite", "accueil"}:
            continue

        seen.add(href)
        items.append(
            {
                "source": SOURCE_LABEL,
                "title": title,
                "url": href,
                "summary": "",
                "date": "",
            }
        )
    return items


def fetch_doctrine_actus() -> list[dict]:
    all_items: list[dict] = []
    seen_urls: set[str] = set()
    for url in CANDIDATE_URLS:
        r = get(url)
        if r is None:
            continue
        for it in _parse(r.text):
            if it["url"] in seen_urls:
                continue
            seen_urls.add(it["url"])
            all_items.append(it)
    logger.info("Doctrine.fr : %s items bruts récupérés", len(all_items))
    return all_items
