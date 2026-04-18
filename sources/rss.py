"""Sources de veille juridique basées sur des flux RSS.

Chacun renvoie une liste d'items au format commun :
    {source, title, url, summary, date}
"""

from __future__ import annotations

import logging
from typing import Optional

from bs4 import BeautifulSoup

from ._common import clean, get

logger = logging.getLogger(__name__)


def _parse_rss(xml: str, source_label: str) -> list[dict]:
    # On utilise le parseur XML (lxml) : indispensable pour que <link>
    # soit bien interprété en texte et non comme le tag HTML auto-fermé.
    try:
        s = BeautifulSoup(xml, "xml")
    except Exception:  # noqa: BLE001
        s = BeautifulSoup(xml, "html.parser")

    items: list[dict] = []

    # RSS 2.0 (<item>) ou Atom (<entry>)
    entries = s.find_all("item") or s.find_all("entry")

    for item in entries:
        title_n = item.find("title")
        desc_n = item.find("description") or item.find("summary") or item.find("content")
        date_n = (
            item.find("pubDate")
            or item.find("pubdate")
            or item.find("published")
            or item.find("updated")
            or item.find("date")
        )

        title = clean(title_n.get_text()) if title_n else ""

        # Extraction robuste de l'URL : d'abord <link> texte (RSS),
        # sinon <link href="..."/> (Atom), sinon <guid>.
        link = ""
        for link_n in item.find_all("link"):
            txt = clean(link_n.get_text()) if link_n.string else ""
            if txt:
                link = txt
                break
            href = link_n.get("href")
            if href:
                link = href.strip()
                break
        if not link:
            guid_n = item.find("guid")
            if guid_n:
                g = clean(guid_n.get_text())
                if g.startswith("http"):
                    link = g

        summary = clean(desc_n.get_text()) if desc_n else ""
        # Si le résumé contient du HTML, on le dénude proprement.
        if summary and "<" in summary:
            summary = clean(BeautifulSoup(summary, "html.parser").get_text(" "))
        date = clean(date_n.get_text()) if date_n else ""

        if not title or not link:
            continue
        items.append(
            {
                "source": source_label,
                "title": title,
                "url": link,
                "summary": summary[:400],
                "date": date,
            }
        )
    return items


def _fetch_rss(url: str, source_label: str) -> list[dict]:
    r = get(url)
    if r is None:
        return []
    items = _parse_rss(r.text, source_label)
    logger.info("%s : %s items", source_label, len(items))
    return items


def fetch_actu_juridique() -> list[dict]:
    return _fetch_rss("https://www.actu-juridique.fr/feed/", "Actu-juridique.fr")


def fetch_village_justice() -> list[dict]:
    # SPIP backend
    return _fetch_rss(
        "https://www.village-justice.com/articles/spip.php?page=backend",
        "Village de la Justice",
    )


def fetch_francetv_immo() -> list[dict]:
    return _fetch_rss(
        "https://www.francetvinfo.fr/economie/immobilier.rss",
        "France Info — Immobilier",
    )


def fetch_legavox() -> list[dict]:
    return _fetch_rss("https://www.legavox.fr/rss.xml", "Legavox")
