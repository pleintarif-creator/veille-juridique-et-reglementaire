"""Gestion de l'état pour éviter les doublons dans la newsletter."""

import hashlib
import json
from pathlib import Path
from typing import Iterable

STATE_FILE = Path(__file__).parent / "state.json"
MAX_HISTORY = 5000  # on conserve les 5000 dernières signatures


def _load() -> dict:
    if not STATE_FILE.exists():
        return {"seen": []}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"seen": []}


def _save(data: dict) -> None:
    STATE_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def signature(item: dict) -> str:
    """Signature stable d'un item (url si dispo, sinon titre)."""
    key = item.get("url") or item.get("title", "")
    return hashlib.sha256(key.strip().lower().encode("utf-8")).hexdigest()[:16]


def filter_new(items: Iterable[dict]) -> list[dict]:
    data = _load()
    seen = set(data.get("seen", []))
    fresh = []
    for item in items:
        sig = signature(item)
        if sig in seen:
            continue
        item["_sig"] = sig
        fresh.append(item)
    return fresh


def commit(items: Iterable[dict]) -> None:
    data = _load()
    seen = list(data.get("seen", []))
    for item in items:
        sig = item.get("_sig") or signature(item)
        if sig not in seen:
            seen.append(sig)
    # on garde les N dernières
    if len(seen) > MAX_HISTORY:
        seen = seen[-MAX_HISTORY:]
    _save({"seen": seen})
