"""Orchestrateur principal : récupère, filtre, compose et envoie."""

from __future__ import annotations

import logging
import os
import sys

import config
import email_sender
import newsletter
import state
from sources import _common
from sources import (
    fetch_actu_juridique,
    fetch_cnil,
    fetch_doctrine_actus,
    fetch_francetv_immo,
    fetch_jorf,
    fetch_jurisprudence,
    fetch_legavox,
    fetch_village_justice,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("veille")


SOURCE_FETCHERS = {
    "legifrance_jorf": fetch_jorf,
    "legifrance_juri": fetch_jurisprudence,
    "legifrance_cnil": fetch_cnil,
    "doctrine_actus": fetch_doctrine_actus,
    "actu_juridique": fetch_actu_juridique,
    "village_justice": fetch_village_justice,
    "legavox": fetch_legavox,
    "francetv_immo": fetch_francetv_immo,
}


def collect_raw() -> list[dict]:
    all_items: list[dict] = []
    for key, enabled in config.SOURCES.items():
        if not enabled:
            continue
        fetcher = SOURCE_FETCHERS.get(key)
        if not fetcher:
            logger.warning("Source inconnue ignorée : %s", key)
            continue
        try:
            items = fetcher()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Erreur lors de la récupération %s : %s", key, exc)
            items = []
        all_items.extend(items)
    logger.info("Total items bruts toutes sources : %s", len(all_items))
    return all_items


def filter_relevant(items: list[dict]) -> list[dict]:
    kept: list[dict] = []
    for it in items:
        # On ne matche pas l'URL : trop de faux positifs (mots dans le slug).
        text = " ".join([it.get("title", ""), it.get("summary", "")])
        hits = _common.matches_keywords(text, config.KEYWORDS)
        if not hits:
            continue
        it["matched_keywords"] = hits
        kept.append(it)
    logger.info("Items pertinents (mots-clés métier) : %s", len(kept))

    # cap par source pour éviter des emails géants
    capped: list[dict] = []
    counts: dict[str, int] = {}
    for it in kept:
        s = it.get("source", "")
        counts[s] = counts.get(s, 0) + 1
        if counts[s] <= config.MAX_ITEMS_PER_SOURCE:
            capped.append(it)
    return capped


def main() -> int:
    dry_run = os.environ.get("DRY_RUN") == "1"

    raw = collect_raw()
    relevant = filter_relevant(raw)
    fresh = state.filter_new(relevant)

    logger.info("Items nouveaux (non déjà envoyés) : %s", len(fresh))

    if not fresh:
        logger.info("Aucune nouveauté -> aucun email envoyé.")
        return 0

    subject = newsletter.build_subject(fresh)
    html_body = newsletter.build_html(fresh)
    text_body = newsletter.build_text(fresh)

    if dry_run:
        out = "newsletter_preview.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html_body)
        logger.info("DRY_RUN : prévisualisation écrite dans %s", out)
        print(text_body)
        return 0

    try:
        email_sender.send(subject, html_body, text_body)
    except email_sender.EmailConfigError as exc:
        logger.error("Configuration email invalide : %s", exc)
        return 2
    except Exception as exc:  # noqa: BLE001
        logger.exception("Échec de l'envoi : %s", exc)
        return 3

    # on ne marque "vu" qu'après envoi réussi
    state.commit(fresh)
    logger.info("État mis à jour avec %s nouvelles signatures.", len(fresh))
    return 0


if __name__ == "__main__":
    sys.exit(main())
