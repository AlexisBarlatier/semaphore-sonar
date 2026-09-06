# -*- coding: utf-8 -*-
"""Import one-shot (E2) : convertit les pages HTML d'analyse existantes en
entrées brutes dans analyses/analyses.json (nouveau schéma « entrées »).

Règles :
- ne stocke QUE des entrées (faits, marché, hypothèses, qualitatif) ;
- aucun résultat n'est importé (pas de note/verdict/rendement/revient) ;
- ce qui n'est pas extractible reste absent → `champs_manquants` (le listing
  affichera « — » tant que la fiche n'est pas complétée, décision Alexis) ;
- provenance marquée `legacy.source = "html-import"` (métadonnée, pas résultat) ;
- idempotent : relançable, il régénère analyses.json en entier depuis les pages.

Usage :
  python3 scripts/analyse_app/import_legacy.py [--project /chemin/semaphore-sonar]
"""

import html
import json
import os
import re
import sys
from datetime import datetime, timezone

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)
from analyse_app.schema import champs_manquants, validate_record  # noqa: E402

PROJECT_DIR = None
for arg in sys.argv[1:]:
    if not arg.startswith("--"):
        PROJECT_DIR = os.path.abspath(arg)
        break
if PROJECT_DIR is None:
    for c in [os.getcwd(), os.path.expanduser("~/Documents/Semaphore-sonar"),
              os.path.expanduser("~/semaphore-sonar")]:
        if os.path.isdir(os.path.join(c, "analyses")):
            PROJECT_DIR = c
            break
if PROJECT_DIR is None:
    sys.exit("Erreur : dossier analyses/ introuvable")
ANALYSES_DIR = os.path.join(PROJECT_DIR, "analyses")
JSON_OUT = os.path.join(ANALYSES_DIR, "analyses.json")

PRIX_LABELS = ["Prix d'achat", "Prix de vente", "Prix FAI affiché",
               "Prix total TTC", "Prix négocié"]

# Corrections documentées pour les pages sans signal exploitable (voir
# l'étude de formats du 06/09/2026)
OVERRIDES = {
    "2026-07-04-extension-80-90-brignoles-350m2": {"type_bien": "immeuble"},
    "2026-06-01-extension-80-90-brignoles-83170": {"type_bien": "immeuble"},
    "2026-05-28-boulevard-blancarde-marseille-13004": {"type_bien": "immeuble"},
    "2026-05-28-les-aygalades-marseille-13015": {"type_bien": "appartement"},
    "2026-05-28-euromediterranee-marseille-13015": {"type_bien": "immeuble"},
    "2026-07-29-la-seyne-63-gambetta-immeuble-7-lots": {
        "ville": "La Seyne-sur-Mer", "code_postal": "83500"},
}

TYPE_PARKING = {"parking", "garage", "box", "stationnement", "sous-sol",
                "souterrain", "place"}
TYPE_LOCAL = {"local", "boutique", "bureau", "commercial", "entrepôt",
              "entrepot"}


def clean(s):
    if not s:
        return s
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = s.replace("\u00a0", " ").replace("\u202f", " ")
    return re.sub(r"\s+", " ", s).strip()


def first_num(s):
    if not s:
        return None
    m = re.search(r"-?\d+(?:[.,]\d+)?", clean(s).replace("\u202f", " "))
    return float(m.group(0).replace(",", ".")) if m else None


def first_amount(s, min_v=100.0):
    """Premier montant plausible d'une cellule (ignore listes et petits
    nombres : « ~2 600 € (11 × 875 € ≈ 9 600 €) » → 2 600)."""
    if not s or s in ("—", "-"):
        return None
    t = clean(s).replace(" ", "").replace("\u00a0", "")
    for m in re.finditer(r"(\d+(?:[.,]\d+)?)", t):
        v = float(m.group(1).replace(",", "."))
        if v >= min_v:
            return v
    return None


def money_min_max(s):
    if not s or s in ("—", "-", ""):
        return None, None
    t = re.sub(r"\(.*?\)", "", clean(s))
    t = t.replace("\u00a0", " ").replace("\u202f", " ")
    mult = 1000.0 if re.search(r"[kK]\s*€", t) else 1.0
    t = re.sub(r"[kK]\s*€", "", t)
    nums = []
    for part in re.split(r"[–—à-]", t):
        part = part.strip().replace(" ", "")
        m = re.search(r"(\d+(?:[.,]\d+)?)", part)
        if m:
            nums.append(float(m.group(1).replace(",", ".")) * mult)
    if not nums:
        return None, None
    return min(nums), max(nums)


def fiche_rows(content):
    rows = {}
    for k, v in re.findall(r'<tr><th>([^<]+)</th><td>(.*?)</td></tr>',
                           content, re.DOTALL):
        rows[clean(k)] = clean(v)
    return rows


def cards_of(content):
    return {html.unescape(l).strip(): html.unescape(v).strip()
            for l, v in re.findall(
                r'<span class="card-label">([^<]+)</span>\s*'
                r'<span class="card-value">([^<]*)</span>', content)}


def attrs_of(content):
    out = []
    for m in re.finditer(
            r'<span class="attr-label">(.*?)</span>\s*'
            r'<span class="attr-score"><strong>(\d+)/10</strong>.*?'
            r'<p class="attr-detail">(.*?)</p>', content, re.DOTALL):
        label = clean(m.group(1))
        code = label.lower()
        for fr, to in [("tension stationnement", "tension_stationnement"),
                       ("densité résidentielle", "densite_residentielle"),
                       ("accessibilité", "accessibilite"),
                       ("sécurité", "securite_acces"),
                       ("protection", "protection"),
                       ("demande locative", "demande_locative"),
                       ("transports", "transports"),
                       ("commerces", "commerces"),
                       ("écoles", "ecoles"),
                       ("visibilité", "visibilite_flux"),
                       ("bassin d'emploi", "bassin_emploi"),
                       ("concurrence", "concurrence"),
                       ("dynamisme", "dynamisme"),
                       ("réglementaire", "reglementaire")]:
            if fr in label.lower():
                code = to
                break
        out.append({"dimension": code, "score": int(m.group(2)),
                    "justification": clean(m.group(3))})
    return out


def risques_of(content):
    out = []
    cells = re.findall(
        r"<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*"
        r'<td><span class="severity severity-(\d)">\d/5</span></td>',
        content, re.DOTALL)
    for facteur, detail, sev in cells:
        out.append({"facteur": clean(facteur), "detail": clean(detail),
                    "severite": int(sev)})
    return out


def detect_type(titre, fiche_type, badge, slug, card_labels):
    t = f" {clean(titre or '').lower()} "
    f = f" {clean(fiche_type or '').lower()} "
    b = f" {clean(badge or '').lower()} "
    s = f" {slug.lower().replace('-', ' ')} "
    labels = " " + " ".join(card_labels).lower() + " "

    if re.match(r"\s*(local|boutique|bureau|entrepôt)", f):
        return "local-pro"
    if re.search(r"(?<!sou)terrain|\blotir\b|lotissement", t + b + s):
        return "terrain"
    if (re.search(r"\bparking\b|\bparkings\b|garage|box|stationnement|"
                  r"place[s]?\s+de\s+(parking|stationnement)", t + b + f + s)
            and not re.match(r"\s*(local|boutique)", f)):
        return "parking"
    if "promotion" in b or "lotissement" in b:
        return "promotion"
    if re.search(r"\bremise\b|\bgrange\b|\bdépôt\b|\bdepot\b", t + s):
        return "remise"
    if "villa" in t or re.search(r"\bmaison\b", t + f):
        return "maison"
    if (re.search(r"\bimmeuble\b|logement", t + b + f + s)
            or re.search(r"\b\d+\s*lots?\b|\b\d+\s*appartements\b",
                         t + f + s)):
        return "immeuble"
    if any(x in t + b + f for x in TYPE_LOCAL):
        return "local-pro"
    if re.search(r"\bstudios?\b|\bappartement\b|coloc|\b[tT]\d\b",
                 t + b + f + s):
        return "appartement"
    return "autre"


def detect_branche(type_bien, badge):
    b = clean(badge or "").lower()
    if type_bien == "parking":
        return "parking"
    if type_bien in ("local-pro",):
        return "professionnel"
    if "promotion" in b or "lotissement" in b or type_bien == "terrain":
        return "promotion"
    if "marchand de biens" in b or "mdb" in b:
        return "mdb"
    return "residentiel"


def detect_operation(branche, badge):
    b = clean(badge or "").lower()
    if "marchand de biens" in b or "mdb" in b:
        return "mdb"
    if "promotion" in b or "lotissement" in b:
        return "promotion"
    if branche == "promotion":
        return "promotion"
    return "locatif"


def detect_ville(adresse, titre, slug):
    ad = " ".join(x for x in [adresse, titre] if x)
    m = re.search(r"\((\d{5})\)", ad)
    cp = m.group(1) if m else None
    if cp is None:
        m = re.search(r"(?<![\d-])(\d{5})(?![\d])", ad)
        cp = m.group(1) if m else None
    segs = re.split(r"[,…;—–]", ad)
    for seg in reversed(segs):
        seg = re.sub(r"\(.*?\)", " ", seg).strip(" ()\t")
        if not seg:
            continue
        mc = re.search(r"(?<![\d])(\d{5})(?![\d])", seg)
        side = seg[:mc.start()] if mc else seg
        words = []
        for tok in side.replace(",", " ").split():
            tok = tok.strip(" '\"-–—,…()")
            if not tok or re.search(r"\d", tok):
                continue
            if "€" in tok or "%" in tok or "." in tok:
                continue
            if tok[0].isupper():
                words.append(tok)
        if mc:
            after = seg[mc.end():].strip(" )")
            if not words and after:
                words = [w for w in after.split() if w and w[0].isupper()
                         and not re.search(r"\d", w)]
        if words:
            return " ".join(words), cp
    return None, cp


def parse_one(folder):
    path = os.path.join(ANALYSES_DIR, folder, "index.html")
    if not os.path.isfile(path):
        return None
    content = open(path, encoding="utf-8").read()
    cards = cards_of(content)
    fiche = fiche_rows(content)
    slug = folder
    date_analyse = folder[:10] if re.match(r"\d{4}-\d{2}-\d{2}", folder) else None

    tm = re.search(r"<title>Analyse\s*[—–-]\s*(.+?)</title>", content, re.DOTALL)
    titre = clean(tm.group(1)) if tm else folder

    rm = re.search(r'<p class="report-address">(.*?)</p>', content, re.DOTALL)
    adresse_texte = clean(rm.group(1)) if rm else None

    sm = re.search(r'<div class="report-source-link">(.*?)</div>', content,
                   re.DOTALL)
    if sm:
        hm = re.search(r'href="([^"]+)"', sm.group(1))
        url = hm.group(1) if hm else None
    else:
        um = re.search(r"https?://[^\s\"'<>)]+", content)
        url = um.group(0) if um else None

    bm = re.search(r'<span class="strategy-badge">(.*?)</span>', content)
    badge = clean(bm.group(1)) if bm else None

    fiche_type = fiche.get("Type") or fiche.get("Type de bien")
    type_bien = detect_type(titre, fiche_type, badge, slug, cards.keys())
    ville, cp = detect_ville(adresse_texte, titre, slug)
    if slug in OVERRIDES:
        if "type_bien" in OVERRIDES[slug]:
            type_bien = OVERRIDES[slug]["type_bien"]
        if "ville" in OVERRIDES[slug]:
            ville = OVERRIDES[slug]["ville"]
        if "code_postal" in OVERRIDES[slug]:
            cp = OVERRIDES[slug]["code_postal"]

    branche = detect_branche(type_bien, badge)
    operation = detect_operation(branche, badge)

    # ---- Prix : carte canonique -------------------------------------------
    prix_label = None
    for lbl in PRIX_LABELS:
        if lbl in cards and cards[lbl] not in ("—", ""):
            prix_label = lbl
            break
    prix_texte = cards.get(prix_label) if prix_label else None
    pmin, pmax = money_min_max(prix_texte)
    offre = bool(prix_texte and "(offre" in prix_texte)
    annonce = {
        "plateforme": None,
        "url": url,
        "prix_affiche_euros": None,
        "prix_retenu_euros": None,
        "prix_statut": "affiche",
    }
    if pmin:
        if offre:
            annonce["prix_retenu_euros"] = pmin
            annonce["prix_statut"] = "offre"
        else:
            annonce["prix_affiche_euros"] = pmin
            if pmax and pmax != pmin:
                annonce["prix_affiche_max_euros"] = pmax

    # ---- Fiche : frais, charges, loyers ------------------------------------
    frais = None
    for key, val in fiche.items():
        if "frais de notaire" in key.lower():
            lo, _hi = money_min_max(val)
            if lo:
                frais = first_amount(val) or lo
            break

    loyer_mensuel = None
    loyer_note = None
    for key, val in fiche.items():
        if key == "Loyer cible" or "loyer" in key.lower() and "€/mois" in val:
            # première occurrence seulement ; fourchette « 60-70 €/mois »
            # → borne basse (conservatrice). « 80 €/mois/place » prime sur les
            # ancres citées ensuite (« constatés 78-95 €/mois »).
            m = re.search(r"(\d+(?:[.,]\d+)?)(?:\s*[-–—]\s*"
                          r"(\d+(?:[.,]\d+)?))?\s*€\s*/\s*mois", val)
            if m:
                a = float(m.group(1).replace(",", "."))
                b = m.group(2)
                loyer_mensuel = min(a, float(b.replace(",", "."))) if b else a
                loyer_note = val
            break
    if loyer_mensuel is None:
        # carte « Revenus bruts » : "880 €/mois (11 × 80 €)"
        rv = cards.get("Revenus bruts") or ""
        m = re.search(r"(\d+(?:[.,]\d+)?)\s*€\s*/\s*mois", clean(rv))
        if m:
            loyer_mensuel = float(m.group(1).replace(",", "."))
            loyer_note = "reconstitué depuis Revenus bruts"

    def fiche_montant(*fragments, min_v=20.0):
        """Premier montant plausible d'une ligne de fiche (fragments dans le
        libellé). « Exonérée… » → 0.0 (signalé comme exonération)."""
        for key, val in fiche.items():
            kl = key.lower()
            if any(frag in kl for frag in fragments):
                if "exonér" in val.lower():
                    return 0.0
                m = first_amount(val, min_v=min_v)
                if m is not None:
                    return m
        return None

    tf = fiche_montant("taxe foncière", "taxe fonciere")
    # « Lots de copropriété » ne doit pas être confondu avec les charges :
    # fragments volontairement limités aux libellés de charges
    copro = fiche_montant("charges copro", "charges de copropriété",
                          "charges de copropriete", "charges annuelles copro")

    tf_comment = None
    for key in fiche:
        if "taxe foncière" in key.lower() or "taxe fonciere" in key.lower():
            tf_comment = fiche[key]
    copro_comment = None
    for key in fiche:
        if "charges copro" in key.lower():
            copro_comment = fiche[key]
    # Lots pour les parkings — calculé AVANT la totalisation des charges
    # copro « par place » : la quantité en dépend (pitfall 34b — ordre).
    lots = None
    if type_bien == "parking":
        m = re.search(r"(\d+)\s*(?:places|parkings|lots)", titre.lower())
        if m:
            lots = {"count": int(m.group(1)), "nature": None,
                    "lots_distincts": None}
    if not lots and cards.get("Lots"):
        lo, _ = money_min_max(cards["Lots"])
        if lo:
            lots = {"count": int(lo), "nature": None, "lots_distincts": None}

    neuf = bool(re.search(r"vefa|neuve|neuf", f"{titre} {fiche_type or ''}".lower()))
    sous_type = None
    if type_bien == "parking":
        ft = f"{titre} {fiche_type or ''}".lower()
        if any(x in ft for x in ("sous-sol", "souterrain", "sous terrain")):
            sous_type = "sous-sol"
        elif any(x in ft for x in ("extérieur", "exterieur", "surface")):
            sous_type = "exterieur"
        elif "box" in ft or "garage" in ft:
            sous_type = "box"

    # charges exprimées « par place » : totaliser quand le nombre de lots est
    # connu (sinon valeur unitaire non totalisable → None, à compléter)
    if copro and copro_comment and ("/place" in copro_comment
                                    or "par place" in copro_comment):
        qty = (lots or {}).get("count") if lots else None
        copro = copro * qty if qty else None

    # Valeur marché depuis les cartes (marché retenu — input sourcé)
    valeur = {}
    for key in ("Valeur marché", "Valeur revente", "Valeur marché (MA rue)",
                "Valeur marché (DVF)"):
        if key in cards:
            lo, hi = money_min_max(cards[key])
            if lo:
                valeur = {
                    "basse_euros": lo,
                    "haute_euros": hi if hi and hi != lo else None,
                    "retenue_euros": None,
                    "source": f"carte « {key} » (import)",
                    "confiance": "faible",
                }
                break
    if valeur and valeur["haute_euros"]:
        valeur["retenue_euros"] = None   # milieu calculé par le moteur
    # stratégie retenue : nom + code
    strat_nom = None
    sm2 = re.search(r"Stratégie retenue\s*:\s*<strong>(.*?)</strong>",
                    content, re.DOTALL)
    if sm2:
        strat_nom = clean(sm2.group(1))
    code = "ld-nue"
    if branche == "parking":
        code = "parking-ld"
    elif branche == "professionnel":
        code = "pro-bail"
    elif operation == "mdb":
        code = "mdb"
    elif "coloc" in f"{titre} {strat_nom or ''}".lower():
        code = "colocation"
    strat = {"nom": strat_nom, "code": code, "lots": None}

    attrs = attrs_of(content)
    risques = risques_of(content)

    hypotheses = {"vacance_base_pct": None, "vacance_best_pct": None,
                  "vacance_worst_pct": None, "charges": {},
                  "frais_acquisition_euros": frais}
    if tf is not None:
        hypotheses["charges"]["taxe_fonciere_annuelle_euros"] = tf
        if tf_comment:
            hypotheses["charges"]["taxe_fonciere_commentaire"] = tf_comment
    if copro is not None and "charges annuelles" not in [k.lower() for k in fiche]:
        hypotheses["charges"]["charges_copro_annuelles_euros"] = copro
        if copro_comment:
            hypotheses["charges"]["charges_copro_commentaire"] = copro_comment
    if not hypotheses["charges"] and branche in ("residentiel", "parking",
                                                 "professionnel"):
        pass  # copro inconnue → champs_manquants (affichage « — »)
    hypotheses.pop("charges_ignores_tf", None)

    loyers = None
    if loyer_mensuel is not None:
        # loyer exprimé « par place » : la quantité vient des lots connus
        qty = 1
        if loyer_note and ("/place" in loyer_note or "par place" in loyer_note):
            qty = (lots or {}).get("count") or 1
        loyers = [{"lot": "ensemble (import)", "quantite": qty,
                   "loyer_mensuel_euros": loyer_mensuel,
                   "occupe": None, "note": loyer_note}]

    surface_texte = cards.get("Surface")
    rec = {
        "slug": slug,
        "date_analyse": date_analyse,
        "date_maj": None,
        "titre": titre,
        "bien": {
            "type_bien": type_bien,
            "sous_type": sous_type,
            "type_detail": fiche_type or badge,
            "neuf": neuf if neuf else None,
            "adresse": {"texte": adresse_texte, "ville": ville,
                        "code_postal": cp},
            "surfaces": {"texte": surface_texte},
            "lots": lots,
            "copro": {"charges_annuelles_euros": copro,
                      "charges_source": copro_comment},
            "travaux": {"montant_euros": None, "nature": None},
        },
        "annonce": annonce,
        "marche": {
            "valeur": valeur if valeur else None,
            "loyers": loyers,
            "notes": None,
        },
        "hypotheses": hypotheses,
        "analyse": {
            "branche": branche,
            "type_operation": operation,
            "strategie_retenue": strat,
            "strategies_explorees": [],
            "attractivite": attrs,
            "risques": risques,
        },
        "legacy": {"source": "html-import", "importe_le":
                   datetime.now(timezone.utc).date().isoformat()},
        "champs_manquants": [],
    }
    rec["champs_manquants"] = champs_manquants(rec)
    return rec


def main():
    from analyse_app.completions import apply as apply_completions
    records = []
    for folder in sorted(os.listdir(ANALYSES_DIR), reverse=True):
        if os.path.isdir(os.path.join(ANALYSES_DIR, folder)):
            rec = parse_one(folder)
            if rec:
                apply_completions(rec)
                rec["champs_manquants"] = champs_manquants(rec)
                records.append(rec)
    records.sort(key=lambda r: r["slug"], reverse=True)

    # rapport
    from collections import Counter
    cm = Counter()
    for r in records:
        for m in r["champs_manquants"]:
            cm[m] += 1
    types = Counter(r["bien"]["type_bien"] for r in records)
    branches = Counter(r["analyse"]["branche"] for r in records)
    print(f"{len(records)} fiches importées")
    print("types:", dict(types))
    print("branches:", dict(branches))
    print("champs manquants (top):", dict(cm.most_common(10)))
    calc = sum(1 for r in records if not r["champs_manquants"])
    print(f"fiches sans champ manquant : {calc}/{len(records)}")

    payload = {
        "meta": {
            "schema": "analyses-v2-entrees",
            "generated_at": datetime.now(timezone.utc).isoformat(
                timespec="seconds"),
            "source": "import_legacy.py",
            "count": len(records),
        },
        "analyses": records,
    }
    with open(JSON_OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print(f"✓ {JSON_OUT}")


if __name__ == "__main__":
    main()
