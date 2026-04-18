"""Accès à Légifrance.

Deux voies, du plus fiable au plus robuste :

1. **API officielle PISTE** (recommandée) — gratuite mais nécessite une
   inscription sur https://piste.gouv.fr pour obtenir un `client_id`
   et un `client_secret`. Variables d'environnement attendues :
   - ``LEGIFRANCE_CLIENT_ID``
   - ``LEGIFRANCE_CLIENT_SECRET``

2. **Scraping HTTP simple** — tenté si aucune credential PISTE n'est
   disponible. Légifrance bloque la plupart des user-agents
   non-navigateurs ; la fonction renvoie une liste vide dans ce cas.

Pour la veille immobilière, sans PISTE le système bascule sur les autres
sources juridiques (Doctrine.fr, actu-juridique.fr, etc.).
"""

from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timedelta
from typing import Optional

import requests

from ._common import HEADERS, TIMEOUT, get

logger = logging.getLogger(__name__)

PISTE_TOKEN_URL = "https://oauth.piste.gouv.fr/api/oauth/token"
PISTE_API_BASE = "https://api.piste.gouv.fr/dila/legifrance/lf-engine-app"

# Requêtes larges pour chaque fond Légifrance
BROAD_QUERIES = [
    "immobilier",
    "urbanisme",
    "logement",
    "bail commercial",
    "bail d'habitation",
    "copropriété",
    "succession",
    "fiscalité foncière",
]


def _piste_token() -> Optional[str]:
    client_id = os.environ.get("LEGIFRANCE_CLIENT_ID")
    client_secret = os.environ.get("LEGIFRANCE_CLIENT_SECRET")
    if not client_id or not client_secret:
        return None
    try:
        r = requests.post(
            PISTE_TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": "openid",
            },
            timeout=TIMEOUT,
        )
        if r.status_code != 200:
            logger.warning("PISTE token HTTP %s : %s", r.status_code, r.text[:200])
            return None
        return r.json().get("access_token")
    except requests.RequestException as exc:
        logger.warning("PISTE token échec : %s", exc)
        return None


def _piste_search(token: str, fond: str, query: str) -> list[dict]:
    """Recherche via l'API PISTE Légifrance (fond = JORF / JURI / CNIL...)."""
    start = datetime.utcnow() - timedelta(days=7)
    body = {
        "recherche": {
            "champs": [
                {
                    "typeChamp": "ALL",
                    "criteres": [
                        {
                            "typeRecherche": "EXACTE",
                            "valeur": query,
                            "operateur": "ET",
                        }
                    ],
                    "operateur": "ET",
                }
            ],
            "filtres": [
                {
                    "facette": "DATE_SIGNATURE",
                    "dates": {
                        "start": start.strftime("%Y-%m-%d"),
                        "end": datetime.utcnow().strftime("%Y-%m-%d"),
                    },
                }
            ],
            "pageNumber": 1,
            "pageSize": 10,
            "operateur": "ET",
            "sort": "SIGNATURE_DATE_DESC",
            "typePagination": "DEFAUT",
        },
        "fond": fond,
    }
    try:
        r = requests.post(
            f"{PISTE_API_BASE}/search",
            json=body,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
            timeout=TIMEOUT,
        )
        if r.status_code != 200:
            logger.warning(
                "PISTE search HTTP %s (%s/%s) : %s",
                r.status_code, fond, query, r.text[:200],
            )
            return []
        data = r.json()
    except requests.RequestException as exc:
        logger.warning("PISTE search échec : %s", exc)
        return []

    results = data.get("results") or []
    out: list[dict] = []
    for row in results:
        title_bits = row.get("titles") or []
        title = " — ".join(t.get("title", "") for t in title_bits if t.get("title"))
        if not title:
            title = row.get("title") or row.get("id") or ""
        url = ""
        # Construction URL publique à partir de l'id
        cid = row.get("id") or ""
        if cid:
            if fond == "JORF":
                url = f"https://www.legifrance.gouv.fr/jorf/id/{cid}"
            elif fond == "JURI":
                url = f"https://www.legifrance.gouv.fr/juri/id/{cid}"
            elif fond == "CNIL":
                url = f"https://www.legifrance.gouv.fr/cnil/id/{cid}"
            else:
                url = f"https://www.legifrance.gouv.fr/search/{fond.lower()}?query={cid}"
        date = row.get("date") or row.get("datePublication") or ""
        summary = row.get("text") or row.get("summary") or ""
        if not title or not url:
            continue
        out.append(
            {
                "source": f"Légifrance — {fond}",
                "title": title,
                "url": url,
                "summary": summary[:400],
                "date": date,
            }
        )
    return out


def _fetch_via_piste(fond: str) -> list[dict]:
    token = _piste_token()
    if not token:
        return []
    items: list[dict] = []
    seen: set[str] = set()
    for q in BROAD_QUERIES:
        time.sleep(0.3)  # politesse
        for it in _piste_search(token, fond, q):
            if it["url"] in seen:
                continue
            seen.add(it["url"])
            items.append(it)
    logger.info("Légifrance (PISTE/%s) : %s items", fond, len(items))
    return items


def _fetch_via_scrape(fond: str, label: str) -> list[dict]:
    """Tentative en dernier recours ; Légifrance bloque souvent -> [] .

    Utile pour le développement local ; en production, passez par PISTE.
    """
    logger.info(
        "Pas de credential PISTE — fallback scraping Légifrance (%s). "
        "Il est normal que cela renvoie 0 résultat si Légifrance bloque.",
        fond,
    )
    return []


def fetch_jorf() -> list[dict]:
    piste = _fetch_via_piste("JORF")
    if piste:
        return piste
    return _fetch_via_scrape("JORF", "Légifrance — JORF")


def fetch_jurisprudence() -> list[dict]:
    piste = _fetch_via_piste("JURI")
    if piste:
        return piste
    return _fetch_via_scrape("JURI", "Légifrance — Jurisprudence")


def fetch_cnil() -> list[dict]:
    piste = _fetch_via_piste("CNIL")
    if piste:
        return piste
    return _fetch_via_scrape("CNIL", "Légifrance — CNIL")
