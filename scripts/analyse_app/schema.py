# -*- coding: utf-8 -*-
"""Schéma de données des analyses (entrées uniquement).

Validation : `validate_record(record)` retourne la liste des problèmes.
Une fiche est « calculable » quand le moteur dispose de tout ce qu'il lui
faut (sinon le listing affiche « — », décision Alexis 06/09).

Vocabulaire des branches (arbres de décision du skill analyse-annonce-immo) :
- residentiel : appartement / maison / immeuble de rapport
- professionnel : local commercial, bureaux, entrepôt (bail 3-6-9)
- parking : place, box, garage, bloc de lots
- promotion : construction-vente / lotissement (voir references promotion)
- mdb : achat-rénovation-revente (marchand de biens)
"""

BRANCHES = ("residentiel", "professionnel", "parking", "promotion", "mdb")

TYPE_BIEN = (
    "appartement", "maison", "immeuble", "local-pro", "parking", "remise",
    "terrain", "promotion", "autre",
)

# Types d'opération affichés (fiche d'identité / listing)
TYPE_OPERATION = ("locatif", "mdb", "promotion", "mixte")

# Codes de stratégies reconnues par la grille de pondération de l'attractivité
STRATEGIE_CODES = (
    "ld-nue",        # location longue durée, nue (ou meublée classique)
    "ld-meuble",     # location meublée longue durée
    "colocation",    # colocation meublée
    "airbnb",        # location courte durée
    "mdb",           # achat-rénovation-revente
    "promotion",     # construction / division
    "parking-ld",    # location longue durée parking (bloc ou place isolée)
    "pro-bail",      # bail commercial 3-6-9
)

# Dimensions d'attractivité (selon branche — codes stables)
DIMENSIONS_RESIDENTIEL = (
    "transports", "commerces", "ecoles", "securite", "demande_locative",
    "dynamisme",
)
DIMENSIONS_PARKING = (
    "tension_stationnement", "densite_residentielle", "accessibilite",
    "securite_acces", "protection", "demande_locative",
)
DIMENSIONS_PRO = (
    "accessibilite", "visibilite_flux", "bassin_emploi",
    "concurrence", "dynamisme", "reglementaire",
)
DIMENSIONS = {
    "residentiel": DIMENSIONS_RESIDENTIEL,
    "professionnel": DIMENSIONS_PRO,
    "parking": DIMENSIONS_PARKING,
    # promotion / mdb : attractivité du secteur = dimensions résidentielles
    "promotion": DIMENSIONS_RESIDENTIEL,
    "mdb": DIMENSIONS_RESIDENTIEL,
}

AMORTISSABLE_PAR_TYPE = {
    "parking": None,      # décidé par sous-type (sous-sol bâti = oui)
    "immeuble": True,     # quote-part bâti ~90 % par défaut
    "appartement": True,
    "maison": True,
    "local-pro": True,
    "remise": True,
    "terrain": False,
    "autre": True,
}


class RecordError(Exception):
    pass


def _num(record, *path, default=None):
    cur = record
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return default
        cur = cur[p]
    return cur


def champs_manquants(record):
    """Liste des entrées manquantes qui empêchent (ou limitent) le calcul.
    Utilisé par validate, par l'import legacy et par l'agent pendant la saisie."""
    missing = []

    if not record.get("titre"):
        missing.append("titre")
    if not record.get("date_analyse"):
        missing.append("date_analyse")

    bien = record.get("bien") or {}
    if not bien.get("type_bien"):
        missing.append("bien.type_bien")
    ville = _num(bien, "adresse", "ville")
    cp = _num(bien, "adresse", "code_postal")
    if not ville:
        missing.append("bien.adresse.ville")
    if not cp:
        missing.append("bien.adresse.code_postal")

    annonce = record.get("annonce") or {}
    prix_affiche = annonce.get("prix_affiche_euros")
    prix_retenu = annonce.get("prix_retenu_euros")
    if not (prix_affiche or prix_retenu):
        missing.append("annonce.prix")

    marche = record.get("marche") or {}
    valeur = marche.get("valeur") or {}
    if not (valeur.get("retenue_euros") or valeur.get("basse_euros")):
        missing.append("marche.valeur")

    analyse = record.get("analyse") or {}
    branche = analyse.get("branche")
    locatif = branche in ("residentiel", "professionnel", "parking")
    if locatif and not marche.get("loyers"):
        missing.append("marche.loyers")
    hypotheses = record.get("hypotheses") or {}

    # Hypothèses locatives uniquement requises pour les branches locatives
    locatif = branche in ("residentiel", "professionnel", "parking")
    if locatif and hypotheses.get("vacance_base_pct") is None:
        missing.append("hypotheses.vacance_base_pct")
    if locatif:
        charges = hypotheses.get("charges") or {}
        if charges.get("taxe_fonciere_annuelle_euros") is None \
                and not hypotheses.get("charges_ignores_tf"):
            missing.append("hypotheses.charges.taxe_fonciere")
        if charges.get("charges_copro_annuelles_euros") is None \
                and hypotheses.get("charges_ignores_copro") is None:
            missing.append("hypotheses.charges.copro")

    if branche not in BRANCHES:
        missing.append("analyse.branche")
    if analyse.get("type_operation") not in TYPE_OPERATION:
        missing.append("analyse.type_operation")
    if not analyse.get("strategie_retenue", {}).get("code"):
        missing.append("analyse.strategie_retenue.code")

    # Le calcul de la note exige en plus le qualitatif (sinon note = None)
    if len(analyse.get("attractivite") or []) < 6:
        missing.append("analyse.attractivite")
    if not analyse.get("risques"):
        missing.append("analyse.risques")

    # Spécifique branches
    if analyse.get("branche") == "parking":
        if bien.get("sous_type") is None:  # ex: "sous-sol", "exterieur", "box"
            missing.append("bien.sous_type")
    if analyse.get("branche") == "mdb":
        if not marche.get("revente", {}).get("prix_euros"):
            missing.append("marche.revente")
        if bien.get("travaux", {}).get("montant_euros") is None:
            missing.append("bien.travaux.montant")
    if analyse.get("branche") == "promotion":
        if not (marche.get("sdP") or marche.get("sdP") == 0):
            missing.append("marche.sdP")

    return missing


def validate_record(record):
    """Retourne la liste des erreurs STRUCTURELLES (schéma + cohérence).
    Vide = fiche bien formée. Les entrées manquantes ne sont pas des erreurs
    de schéma : elles sont listées par `champs_manquants` (affichage « — »)."""
    errors = []
    if not isinstance(record, dict):
        return ["enregistrement non objet"]

    bien = record.get("bien") or {}
    if bien.get("type_bien") and bien["type_bien"] not in TYPE_BIEN:
        errors.append(f"type_bien inconnu : {bien['type_bien']}")
    analyse = record.get("analyse") or {}
    if analyse.get("branche") and analyse["branche"] not in BRANCHES:
        errors.append(f"branche inconnue : {analyse['branche']}")
    strat = analyse.get("strategie_retenue", {})
    if strat.get("code") and strat["code"] not in STRATEGIE_CODES:
        errors.append(f"code stratégie inconnu : {strat['code']}")

    # Cohérence prix
    annonce = record.get("annonce") or {}
    pa = annonce.get("prix_affiche_euros")
    pr = annonce.get("prix_retenu_euros")
    for label, v in (("prix affiché", pa), ("prix retenu", pr)):
        if v is not None and v <= 0:
            errors.append(f"{label} doit être > 0")
    if pr and pa and pr > pa:
        # possible (négociation à la hausse ? non) — signaler
        errors.append("prix retenu > prix affiché : vérifier")

    # Scores 0-10 (la grille parking score « Protection » à 0 pour les places
    # extérieures — 0 est une valeur légitime)
    for dim in analyse.get("attractivite") or []:
        s = dim.get("score")
        if s is not None and not (0 <= s <= 10):
            errors.append(f"score attractivité hors 0-10 : {dim}")
    for r in analyse.get("risques") or []:
        sev = r.get("severite")
        if sev is not None and not (1 <= sev <= 5):
            errors.append(f"sévérité hors 1-5 : {r}")
    return errors


def is_valid(record):
    return not validate_record(record)
