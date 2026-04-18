"""Construction du contenu HTML et texte de la newsletter."""

from __future__ import annotations

import html
from datetime import datetime
from collections import defaultdict


STYLE = """
<style>
  body { font-family: Georgia, 'Times New Roman', serif; color: #1a1a1a; background:#f7f5f0; margin:0; padding:0; }
  .wrap { max-width: 720px; margin: 0 auto; padding: 24px; background:#fff; }
  h1 { color:#0b2b4a; border-bottom: 3px solid #c9a24b; padding-bottom: 8px; margin-top:0; font-size: 24px;}
  h2 { color:#0b2b4a; margin-top: 28px; font-size: 18px; border-left: 4px solid #c9a24b; padding-left: 10px;}
  .item { margin: 14px 0 18px; padding-bottom: 14px; border-bottom: 1px dashed #ddd; }
  .item:last-child { border-bottom: none; }
  .title { font-weight: bold; color:#0b2b4a; text-decoration: none; font-size: 15px; }
  .title:hover { text-decoration: underline; }
  .meta { color:#666; font-size: 12px; margin-top: 4px; font-family: Arial, sans-serif; }
  .kw { display:inline-block; background:#fdf3dc; color:#7a5a12; padding:1px 6px; border-radius:3px; margin-right:4px; font-size:11px; font-family: Arial, sans-serif;}
  .summary { color:#333; font-size: 14px; margin-top: 6px; }
  .footer { color:#888; font-size:11px; margin-top: 36px; text-align:center; font-family: Arial, sans-serif;}
  .intro { color:#444; font-size: 14px; }
</style>
"""


def _group_by_source(items: list[dict]) -> dict[str, list[dict]]:
    g: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        g[it.get("source", "Autre")].append(it)
    return g


def build_subject(items: list[dict]) -> str:
    date_str = datetime.now().strftime("%d/%m/%Y")
    n = len(items)
    plur = "s" if n > 1 else ""
    return f"[Veille juridique immobilier] {date_str} — {n} nouveauté{plur}"


def build_html(items: list[dict]) -> str:
    date_str = datetime.now().strftime("%A %d %B %Y")
    groups = _group_by_source(items)

    parts: list[str] = []
    parts.append("<!doctype html><html lang='fr'><head><meta charset='utf-8'>")
    parts.append(f"<title>Veille juridique — {date_str}</title>{STYLE}</head><body>")
    parts.append("<div class='wrap'>")
    parts.append("<h1>Veille juridique & réglementaire</h1>")
    parts.append(
        "<p class='intro'>Sélection quotidienne des publications concernant "
        "l'immobilier, la fiscalité immobilière, l'urbanisme, les successions "
        "immobilières et le logement social.</p>"
    )
    parts.append(f"<p class='meta'>Date : {html.escape(date_str)} — {len(items)} élément(s)</p>")

    for source, its in groups.items():
        parts.append(f"<h2>{html.escape(source)} <span class='meta'>({len(its)})</span></h2>")
        for it in its:
            title = html.escape(it.get("title", "(sans titre)"))
            url = html.escape(it.get("url", "#"))
            summary = html.escape(it.get("summary", ""))
            date = html.escape(it.get("date", ""))
            kws = it.get("matched_keywords") or []
            kw_html = " ".join(f"<span class='kw'>{html.escape(k)}</span>" for k in kws[:5])

            parts.append("<div class='item'>")
            parts.append(f"<a class='title' href='{url}'>{title}</a>")
            if summary:
                parts.append(f"<div class='summary'>{summary}</div>")
            meta_bits = []
            if date:
                meta_bits.append(date)
            if kw_html:
                meta_bits.append(kw_html)
            if meta_bits:
                parts.append("<div class='meta'>" + " · ".join(meta_bits) + "</div>")
            parts.append("</div>")

    parts.append(
        "<div class='footer'>Veille générée automatiquement — "
        "sources : Légifrance, Doctrine.fr, Actu-juridique.fr, "
        "Village de la Justice, France Info Immobilier.<br>"
        "Pour modifier les mots-clés ou les sources, éditez <code>config.py</code>.</div>"
    )
    parts.append("</div></body></html>")
    return "".join(parts)


def build_text(items: list[dict]) -> str:
    """Version texte brute pour les clients mail qui n'affichent pas l'HTML."""
    date_str = datetime.now().strftime("%d/%m/%Y")
    lines = [f"Veille juridique & réglementaire — {date_str}", "=" * 60, ""]
    groups = _group_by_source(items)
    for source, its in groups.items():
        lines.append(f"\n### {source} ({len(its)})")
        lines.append("-" * 60)
        for it in its:
            lines.append(f"• {it.get('title','(sans titre)')}")
            if it.get("date"):
                lines.append(f"  {it['date']}")
            if it.get("summary"):
                lines.append(f"  {it['summary'][:280]}")
            lines.append(f"  {it.get('url','')}")
            lines.append("")
    lines.append("")
    lines.append(
        "-- Veille générée automatiquement (Légifrance, Doctrine.fr, "
        "Actu-juridique.fr, Village de la Justice, France Info Immobilier)."
    )
    return "\n".join(lines)
