"""Configuration de la veille juridique.

Modifiez les mots-clés, les sources et les destinataires ici.
"""

# Mots-clés pour filtrer les publications (insensible à la casse).
# Un résultat est retenu s'il contient AU MOINS UN de ces mots-clés
# dans son titre, son résumé ou son URL.
KEYWORDS = [
    # Immobilier général
    "immobilier", "immobilière", "immeuble", "copropriété", "copropriete",
    "bail", "baux", "location", "loyer", "loyers", "locatif", "locative",
    "vente immobilière", "promesse de vente", "compromis", "VEFA",
    "construction", "permis de construire", "marchand de biens",
    "agent immobilier", "loi Hoguet", "ALUR", "ELAN", "Climat et résilience",

    # Fiscalité immobilière
    "plus-value immobilière", "plus-values immobilières",
    "revenus fonciers", "revenu foncier", "LMNP", "LMP",
    "déficit foncier", "IFI", "impôt sur la fortune immobilière",
    "droits de mutation", "DMTO", "TVA immobilière", "SCI",
    "Pinel", "Denormandie", "Malraux", "monuments historiques",
    "démembrement", "usufruit", "nue-propriété", "nue propriete",

    # Urbanisme
    "urbanisme", "PLU", "plan local d'urbanisme", "SCoT", "SCOT",
    "zonage", "ZAC", "lotissement", "déclaration préalable",
    "permis d'aménager", "changement de destination",
    "servitude", "droit de préemption", "DPU", "expropriation",
    "code de l'urbanisme",

    # Successions immobilières
    "succession", "successions", "héritage", "héritier", "héritiers",
    "donation", "donation-partage", "indivision", "licitation",
    "réserve héréditaire", "quotité disponible", "rapport successoral",
    "droits de succession",

    # Logement social
    "logement social", "HLM", "SRU", "loi SRU", "bailleur social",
    "PLS", "PLUS", "PLAI", "APL", "aide personnalisée au logement",
    "DALO", "droit au logement opposable", "CCAS",

    # Bail d'habitation / commercial / rural
    "bail d'habitation", "loi du 6 juillet 1989", "bail commercial",
    "renouvellement du bail", "indemnité d'éviction", "pas-de-porte",
    "bail rural", "fermage", "métayage",
    "bail réel solidaire", "BRS", "OFS",

    # Diagnostics / performance
    "DPE", "diagnostic de performance énergétique", "passoire thermique",
    "rénovation énergétique", "MaPrimeRénov",

    # Divers
    "notaire", "notariat", "publicité foncière",
    "hypothèque", "privilège de prêteur de deniers", "caution",
    "syndic", "assemblée générale copropriété",
]

# Sources à interroger (mettre à False pour désactiver).
# Les sources Légifrance nécessitent des identifiants PISTE pour
# fonctionner (cf. README → « Activer Légifrance ») ; sinon elles sont
# silencieusement ignorées et les autres sources prennent le relais.
SOURCES = {
    "legifrance_jorf": True,        # Journal Officiel (via PISTE)
    "legifrance_juri": True,        # Jurisprudence judiciaire (via PISTE)
    "legifrance_cnil": False,       # CNIL (via PISTE) — souvent hors-sujet
    "doctrine_actus": True,         # Doctrine.fr (accès libre)
    "actu_juridique": True,         # actu-juridique.fr (RSS)
    "village_justice": True,        # village-justice.com (RSS)
    "legavox": False,               # legavox.fr (flux indisponible)
    "francetv_immo": True,          # France Info rubrique immobilier (RSS)
}

# Nombre maximum d'éléments retenus par source (évite les newsletters trop longues).
MAX_ITEMS_PER_SOURCE = 12

# Paramètres de l'email et identifiants PISTE sont lus depuis les variables
# d'environnement (injectées par les GitHub Secrets). Ne mettez rien en dur ici.
#
#   SMTP_HOST               ex: smtp.gmail.com
#   SMTP_PORT               ex: 587
#   SMTP_USER               ex: votre.adresse@gmail.com
#   SMTP_PASSWORD           mot de passe d'application (pas votre mdp habituel)
#   EMAIL_FROM              expéditeur affiché
#   EMAIL_TO                destinataires séparés par des virgules
#   LEGIFRANCE_CLIENT_ID    (optionnel) client_id PISTE
#   LEGIFRANCE_CLIENT_SECRET (optionnel) client_secret PISTE
