# Veille juridique & réglementaire — immobilier

Logiciel qui réalise chaque jour une veille juridique et réglementaire
ciblée sur l'**immobilier**, la **fiscalité immobilière**, l'**urbanisme**,
les **successions immobilières** et le **logement social**.

Sources interrogées quotidiennement :

| Source                  | Contenu                                                      |
|-------------------------|--------------------------------------------------------------|
| **Légifrance** (PISTE)  | JORF (Journal Officiel), jurisprudence, délibérations CNIL   |
| **Doctrine.fr**         | Commentaires, BOFiP, jurisprudence thématique                |
| **Actu-juridique.fr**   | Actualités juridiques (LGDJ)                                 |
| **Village de la Justice** | Articles d'avocats et praticiens                           |
| **France Info Immobilier** | Actualité immobilière grand public                         |

Les résultats sont filtrés par mots-clés métier (modifiables dans
`config.py`), dédupliqués (on ne renvoie jamais la même publication deux
fois), puis mis en forme dans une newsletter HTML envoyée par email.

**S'il n'y a aucune nouveauté, aucun email n'est envoyé.**

---

## Comment ça tourne chaque jour

Le workflow GitHub Actions `.github/workflows/daily.yml` se déclenche tous
les jours à **07h00 UTC** (≈ 9h heure de Paris en été, 8h en hiver).
Il peut aussi être lancé manuellement depuis l'onglet **Actions** de GitHub
(bouton **Run workflow**).

---

## Installation (3 étapes, une seule fois)

### 1. Créer le dépôt sur GitHub

Allez sur https://github.com/new et créez un dépôt vide nommé
`veille-juridique-et-reglementaire` (ou le nom que vous voulez).
Ne cochez rien (pas de README, pas de licence). Notez l'URL du dépôt.

### 2. Pousser le code

Dans le Terminal, collez (en remplaçant `VOTRE_UTILISATEUR` par votre nom GitHub) :

```bash
cd "/Users/mathieugarotta/Desktop/Claude Code/veille-juridique"
git remote add origin https://github.com/VOTRE_UTILISATEUR/veille-juridique-et-reglementaire.git
git branch -M main
git push -u origin main
```

Si GitHub vous demande un mot de passe, utilisez un **personal access token**
(https://github.com/settings/tokens, cocher `repo`).

### 3. Ajouter les identifiants email (GitHub Secrets)

Sur votre dépôt GitHub :
**Settings → Secrets and variables → Actions → New repository secret**.

Ajoutez **six secrets** :

| Nom              | Valeur exemple (Gmail)                       |
|------------------|----------------------------------------------|
| `SMTP_HOST`      | `smtp.gmail.com`                             |
| `SMTP_PORT`      | `587`                                        |
| `SMTP_USER`      | `votre.adresse@gmail.com`                    |
| `SMTP_PASSWORD`  | *un mot de passe d'application Gmail*        |
| `EMAIL_FROM`     | `Veille juridique <votre.adresse@gmail.com>` |
| `EMAIL_TO`       | `destinataire1@ex.fr,destinataire2@ex.fr`    |

#### Comment obtenir un mot de passe d'application Gmail (5 min)

1. Activer la validation en deux étapes :
   https://myaccount.google.com/security
2. Créer un mot de passe d'application :
   https://myaccount.google.com/apppasswords
3. Copier le mot de passe à 16 caractères dans `SMTP_PASSWORD`.

> Avec un autre fournisseur (Outlook, OVH, Infomaniak…) : mettez
> simplement leur `SMTP_HOST` / `SMTP_PORT` (465 pour SSL, 587 pour STARTTLS)
> et les identifiants correspondants.

### 4. Lancer un premier test

Onglet **Actions → Veille juridique quotidienne → Run workflow**.
Si la veille détecte des nouveautés, vous recevez un email dans la minute ;
sinon, rien n'est envoyé (comportement voulu).

---

## Activer Légifrance (optionnel mais recommandé)

Légifrance bloque les accès anonymes. Pour activer les sources JORF et
jurisprudence Légifrance, il faut passer par l'API officielle **PISTE**
(gratuite) :

1. S'inscrire sur https://piste.gouv.fr (bouton *Inscription*, 2 min).
2. Créer une application et s'abonner à l'API **Légifrance**.
3. Récupérer le `client_id` et le `client_secret`.
4. Ajouter deux secrets GitHub supplémentaires :
   - `LEGIFRANCE_CLIENT_ID`
   - `LEGIFRANCE_CLIENT_SECRET`

Sans ces secrets, les sources Légifrance renvoient simplement une liste
vide et les autres sources (Doctrine.fr, Actu-juridique.fr…) prennent
le relais — la veille continue de fonctionner.

---

## Personnaliser

Tout se passe dans [`config.py`](config.py) :

- `KEYWORDS` : liste des mots-clés métier. Ajoutez / retirez librement.
  Le filtrage se fait en **mot entier**, insensible à la casse.
- `SOURCES` : activer ou désactiver chaque source (`True` / `False`).
- `MAX_ITEMS_PER_SOURCE` : limite d'articles par source dans une newsletter.

Pour changer l'heure d'envoi, modifiez la ligne `cron:` dans
`.github/workflows/daily.yml`. Syntaxe cron classique, en UTC.

---

## Tester en local

```bash
cd "/Users/mathieugarotta/Desktop/Claude Code/veille-juridique"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Test "à blanc" : n'envoie pas d'email, écrit newsletter_preview.html
DRY_RUN=1 python main.py
open newsletter_preview.html
```

---

## Architecture

```
veille-juridique/
├── main.py              Orchestrateur (collecte → filtre → envoi)
├── config.py            Mots-clés et sources
├── newsletter.py        Génère HTML + texte brut
├── email_sender.py      Envoi SMTP
├── state.py             Déduplication entre exécutions
├── state.json           État persistant (signatures déjà envoyées)
├── sources/
│   ├── legifrance.py    Légifrance via API PISTE (JORF, JURI, CNIL)
│   ├── doctrine.py      Doctrine.fr (pages publiques)
│   └── rss.py           Flux RSS (actu-juridique, village-justice…)
└── .github/workflows/
    └── daily.yml        Cron quotidien GitHub Actions
```

---

## Notes légales

Ce logiciel ne fait que lire des **contenus publics librement accessibles**
(Légifrance relève du domaine public, les flux RSS sont mis à disposition
par les éditeurs) et compose un récapitulatif privé à destination de son
propriétaire. Il n'effectue pas de rediffusion publique.

Les liens renvoient aux sources originales : les consulter reste nécessaire
pour toute analyse juridique sérieuse.
