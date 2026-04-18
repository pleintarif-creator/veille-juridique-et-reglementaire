from .doctrine import fetch_doctrine_actus
from .legifrance import fetch_cnil, fetch_jorf, fetch_jurisprudence
from .rss import (
    fetch_actu_juridique,
    fetch_francetv_immo,
    fetch_legavox,
    fetch_village_justice,
)

__all__ = [
    "fetch_actu_juridique",
    "fetch_cnil",
    "fetch_doctrine_actus",
    "fetch_francetv_immo",
    "fetch_jorf",
    "fetch_jurisprudence",
    "fetch_legavox",
    "fetch_village_justice",
]
