#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Carte des rendements locatifs bruts par commune (13 + 83) — regenere
analyses/rendements-communes.html depuis les sources brutes.

Sources :
  - loyers  : ANIL / DHUP, « Carte des loyers » 2025, indicateur appartement (pred-app-mef-dhup.csv)
  - prix    : DVF 2025, mutations reelles, departements 13 et 83 (geo-dvf)
  - centres : geo.api.gouv.fr (distances a vol d'oiseau)

Regle : les lots multiples d'une meme mutation sont agreges (surface sommee, valeur
comptee une fois). On ne garde que les appartements avec >= 10 ventes et >= 500 EUR/m2.
Le taux de loyer est marque « mesure » (observations locales) ou « estime » (maillage
ANIL, quand la commune n'a pas assez d'annonces) — c'est la colonne qui dit si le
rendement affiche repose sur un loyer constate ou sur une extrapolation.
"""
import csv
import gzip
import json
import math
import statistics as st
import unicodedata
from collections import defaultdict

LOYERS = '/tmp/loyers_app.csv'
DVF = {'83': '/tmp/dvf83_2025.csv.gz', '13': '/tmp/dvf13_2025.csv.gz'}
CENTRES = {'83': '/tmp/centres_83.json', '13': '/tmp/centres_13.json'}
SORTIE = '/home/alexis-barlatier/Documents/Semaphore-sonar/analyses/rendements-communes.html'

ANCRES = {'Marseille': (43.2964, 5.3698), 'Cuers': (43.2372, 6.0708)}

# secteur de recherche actuel : dossiers en cours + communes instruites
SECTEUR = ['PIERREFEU-DU-VAR', 'CUERS', 'SOLLIES-PONT', 'SOLLIES-TOUCAS', 'SOLLIES-VILLE',
           'LA GARDE', 'LA CRAU', 'LA FARLEDE', 'OLLIOULES', 'SIX-FOURS-LES-PLAGES',
           'SANARY-SUR-MER', 'CARQUEIRANNE', 'HYERES', 'LA LONDE-LES-MAURES', 'BORMES-LES-MIMOSAS',
           'TOULON', 'LA SEYNE-SUR-MER', 'LA VALETTE-DU-VAR', 'PUGET-VILLE', 'CARNOULES',
           'PIGNANS', 'GONFARON', 'LE LUC', 'LE CANNET-DES-MAURES', 'VIDAUBAN', 'FLASSANS-SUR-ISSOLE',
           'BRIGNOLES', 'BELGENTIER', 'NEOULES', 'ROCBARON', 'MEOUNES-LES-MONTRIEUX',
           'FORCALQUEIRET', 'CARCES', 'COTIGNAC', 'LE VAL', 'SIGNES', 'DRAGUIGNAN']


def norm(s):
    """Majuscules sans accents ni apostrophes typographiques, pour comparer des noms."""
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode()
    return s.upper().replace('’', "'").strip()


def haversine(a, b):
    (la1, lo1), (la2, lo2) = a, b
    p = math.pi / 180
    x = 0.5 - math.cos((la2 - la1) * p) / 2 + math.cos(la1 * p) * math.cos(la2 * p) * (1 - math.cos((lo2 - lo1) * p)) / 2
    return 2 * 6371 * math.asin(math.sqrt(x))


def charge_loyers(path):
    out = {}
    with open(path, encoding='utf-8', errors='replace') as f:
        for row in csv.DictReader(f, delimiter=';'):
            cc = (row.get('INSEE_C') or '').strip()
            if not cc:
                continue
            try:
                loyer = float((row.get('loypredm2') or '').replace(',', '.'))
            except ValueError:
                continue
            out[cc] = {
                'loyer': round(loyer, 2),
                'bas': (row.get('lwr.IPm2') or '').replace(',', '.'),
                'haut': (row.get('upr.IPm2') or '').replace(',', '.'),
                'type': (row.get('TYPPRED') or '').strip(),
                'obs': int(float((row.get('nbobs_com') or '0').replace(',', '.'))),
                'nom': (row.get('LIBGEO') or '').strip(),
                'dep': (row.get('DEP') or '').strip(),
            }
    return out


def charge_dvf(paths):
    """{code_commune: {'nom':…, 'mediane':…, 'n':…}} — appartements, mutation agregee."""
    muts = defaultdict(dict)
    noms = {}
    for dep, path in paths.items():
        with gzip.open(path, 'rt', encoding='utf-8', errors='replace') as f:
            for row in csv.DictReader(f):
                if row.get('type_local') != 'Appartement':
                    continue
                cc = row['code_commune']
                noms[cc] = row.get('nom_commune') or cc
                mid = row['id_mutation']
                m = muts[cc].setdefault(mid, {'vf': None, 'surf': 0.0})
                if m['vf'] is None:
                    try:
                        m['vf'] = float(row['valeur_fonciere'])
                    except (TypeError, ValueError):
                        m['vf'] = 0.0
                try:
                    m['surf'] += float(row['surface_reelle_bati'] or 0)
                except ValueError:
                    pass
    out = {}
    for cc, d in muts.items():
        v = [x['vf'] / x['surf'] for x in d.values() if x['surf'] > 10 and x['vf'] > 10000]
        if len(v) < 10:
            continue
        med = st.median(v)
        if med < 500:
            continue
        out[cc] = {'nom': noms[cc], 'mediane': round(med), 'n': len(v)}
    return out


def centres(paths):
    out = {}
    for dep, path in paths.items():
        for c in json.load(open(path, encoding='utf-8')):
            co = (c.get('centre') or {}).get('coordinates')
            if co:
                out[c['code']] = {'nom': c['nom'], 'lat': co[1], 'lon': co[0]}
    return out


def bande(rdt):
    if rdt >= 8:
        return 'vert', '#166534', '#dcfce7'
    if rdt >= 5:
        return 'orange', '#b45309', '#fef3c7'
    return 'rouge', '#991b1b', '#fee2e2'


def main():
    loyers = charge_loyers(LOYERS)
    prix = charge_dvf(DVF)
    cen = centres(CENTRES)
    print(f"  loyers ANIL : {len(loyers)} communes")
    print(f"  DVF appts >= 10 ventes : {len(prix)} communes")

    rows = []
    for cc, p in prix.items():
        lo = loyers.get(cc)
        if not lo or cc not in cen:
            continue
        if lo['dep'] not in ('13', '83'):
            continue
        rdt = lo['loyer'] * 12 / p['mediane'] * 100
        dist = min(haversine((cen[cc]['lat'], cen[cc]['lon']), a) for a in ANCRES.values())
        rows.append({
            'insee': cc, 'nom': p['nom'].upper(), 'dep': lo['dep'],
            'prix': p['mediane'], 'loyer': lo['loyer'], 'rdt': rdt, 'n': p['n'],
            'dist': round(dist), 'type_loyer': lo['type'], 'obs': lo['obs'],
            'lat': cen[cc]['lat'], 'lon': cen[cc]['lon'],
        })
    rows.sort(key=lambda r: -r['rdt'])
    mesures = [r for r in rows if r['type_loyer'] != 'maille']
    estimes = [r for r in rows if r['type_loyer'] == 'maille']
    print(f"  lignes retenues : {len(rows)}  (loyer mesure : {len(mesures)} / estime : {len(estimes)})")

    # ------------------------------------------------------------------ tableau
    lignes = []
    for i, r in enumerate(rows, 1):
        cls, coul, fond = bande(r['rdt'])
        flag = '' if r['type_loyer'] != 'maille' else ' <span style="color:#9a3412;font-size:0.7rem;">est.</span>'
        lignes.append(
            f'<tr><td>{i}</td><td>{r["nom"]} ({r["dep"]}){flag}</td>'
            f'<td>{r["prix"]:,} €</td>'.replace(',', ' ') +
            f'<td>{r["loyer"]:.1f} €</td>'
            f'<td><strong style="color:{coul}">{r["rdt"]:.1f} %</strong></td>'
            f'<td>{r["dist"]} km</td><td>{r["n"]}</td><td>{r["obs"]}</td></tr>')

    # ------------------------------------------------------- marqueurs de carte
    mc = []
    for r in rows:
        _, coul, fond = bande(r['rdt'])
        # echappement obligatoire : plusieurs communes portent une apostrophe
        # (BERRE-L'ETANG, PLAN-D'AUPS...) qui casse le litteral JS et tue tout le script
        nom_js = r['nom'].replace('\\', '\\\\').replace("'", "\\'")
        prix_txt = f"{r['prix']:,}".replace(',', ' ')
        mc.append(
            f"L.circleMarker([{r['lat']:.4f},{r['lon']:.4f}],{{radius:6,color:'{coul}',"
            f"fillColor:'{fond}',fillOpacity:0.9,weight:1.5}}).addTo(map)"
            f".bindPopup('<b>{nom_js}</b><br>{r['rdt']:.1f} % brut, {prix_txt} €/m², "
            f"{r['loyer']:.1f} €/m², {r['n']} ventes');")
    marqueurs = "\n".join(mc)

    # ---------------------------------------------------- bloc secteur de recherche
    sect = [r for r in rows if norm(r['nom']) in {norm(x) for x in SECTEUR}]
    sect.sort(key=lambda r: -r['rdt'])
    srows = []
    for r in sect:
        flag = 'mesuré' if r['type_loyer'] != 'maille' else 'estimé'
        srows.append(f'<tr><td>{r["nom"]}</td><td>{r["prix"]:,} €</td>'.replace(',', ' ') +
                     f'<td>{r["loyer"]:.1f} €</td><td><strong>{r["rdt"]:.1f} %</strong></td>'
                     f'<td>{r["dist"]} km</td><td>{flag}</td><td>{r["n"]}</td></tr>')
    secteur_html = "\n".join(srows)

    # -------------------------------------------------------------- assemblage
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Sémaphore Sonar — Rendements par commune</title>
<link rel="stylesheet" href="../style.css">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  .yield-table {{ width:100%; border-collapse:collapse; font-size:0.85rem; }}
  .yield-table th {{ background:var(--color-accent-light); color:var(--color-accent); padding:0.5rem 0.6rem; text-align:left; font-size:0.75rem; text-transform:uppercase; }}
  .yield-table td {{ padding:0.4rem 0.5rem; border-bottom:1px solid var(--color-border); }}
  .yield-table tr:hover {{ background:#f8f7f6; }}
  #yield-map {{ height:400px; border:1px solid var(--color-border); border-radius:var(--radius); margin:1.5rem 0; }}
  .source-note {{ font-size:0.75rem; color:var(--color-text-muted); margin-top:2rem; }}
  .encadre {{ border-left:3px solid var(--color-accent); background:#f8f7f6; padding:0.9rem 1.1rem; margin:1.5rem 0; font-size:0.9rem; }}
  @media(max-width:768px){{ main{{overflow-x:auto;}} .yield-table{{min-width:760px;}} }}
</style>
</head>
<body>
<header class="listing-hero">
  <h1>Sémaphore Sonar</h1>
  <p class="hero-subtitle">Rendement locatif brut par commune — Bouches-du-Rhône (13) &amp; Var (83)</p>
</header>
<main>
  <p style="color:var(--color-text-muted);margin-bottom:1rem;font-size:0.9rem;">
    Rendement brut = (loyer médian/m² × 12) / prix d'achat médian/m².
    <br>Loyers : ANIL/DHUP 2025, indicateur appartement (charges comprises). Prix : DVF 2025, mutations réelles, appartements uniquement, minimum 10 ventes.
    <br>Distance : à vol d'oiseau jusqu'à Marseille ou Cuers (le plus proche).
    <br><strong>Colonne « est. »</strong> : le loyer de la commune n'est pas mesuré mais extrapolé par l'ANIL depuis les communes voisines (maillage). Le rendement affiché n'y repose sur aucun loyer constaté localement.
  </p>

  <div id="yield-map"></div>

  <div class="encadre">
    <strong>Ce que ça dit pour nos recherches.</strong> Notre doctrine est 5 % net d'IS après charges,
    vacance et fiscalité, ce qui correspond empiriquement à environ 8 % brut sur le prix de revient.
    Sur les {len(rows)} communes retenues, {len([r for r in rows if r['rdt'] >= 8])} dépassent 8 % brut,
    {len([r for r in rows if 6 <= r['rdt'] < 8])} se situent entre 6 et 8 %, et les autres sont hors jeu
    au prix de marché. Le classement ci-dessous sert de filtre avant visite : au-dessus de 8 %, on instruit ;
    entre 6 et 8 %, il faut que le prix d'achat décroche d'au moins 20 % ; en dessous, on passe.
  </div>

  <h2>Secteur de recherche</h2>
  <table class="yield-table">
    <thead><tr><th>Commune</th><th>Prix/m²</th><th>Loyer/m²</th><th>Rendement brut</th><th>Distance</th><th>Loyer</th><th>Ventes</th></tr></thead>
    <tbody>
{secteur_html}
    </tbody>
  </table>

  <h2>Classement complet</h2>
  <table class="yield-table">
    <thead><tr><th>#</th><th>Commune</th><th>Prix/m²</th><th>Loyer/m²</th><th>Rendement brut</th><th>Distance</th><th>Ventes</th><th>Obs. loyer</th></tr></thead>
    <tbody>
{chr(10).join(lignes)}
    </tbody>
  </table>

  <p class="source-note">
    Sources : estimations ANIL/DHUP 2025 à partir des données Groupe SeLoger et leboncoin (loyers) —
    DVF 2025, Ministère de l'Économie, mutations réelles (prix). {len(rows)} communes retenues sur 272
    (appartements, minimum 10 ventes, prix/m² ≥ 500 €). Distance à vol d'oiseau (Haversine).
    Fiche établie le 22 septembre 2026 ; version précédente du 28 mai 2026.
  </p>
</main>

<script>
var map = L.map('yield-map').setView([43.4, 5.6], 9);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{attribution:'&copy; OSM',maxZoom:14}}).addTo(map);
L.marker([43.2964,5.3698]).addTo(map).bindPopup('<b>Marseille</b>');
L.marker([43.2372,6.0708]).addTo(map).bindPopup('<b>Cuers</b>');
L.circle([43.2964,5.3698], {{radius:25000,color:'#1e40af',fillColor:'#dbeafe',fillOpacity:0.15,weight:1}}).addTo(map);
L.circle([43.2372,6.0708], {{radius:25000,color:'#166534',fillColor:'#dcfce7',fillOpacity:0.15,weight:1}}).addTo(map);
{marqueurs}
</script>
</body>
</html>
"""
    with open(SORTIE, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  ecrit : {SORTIE} ({len(html):,} octets)")
    print(f"  secteur : {len(sect)} communes")
    print("\n  --- top 12 ---")
    for r in rows[:12]:
        print(f"   {r['nom']:<26} {r['prix']:>6,} €/m²  {r['loyer']:>5.1f} €  {r['rdt']:>5.1f} %  "
              f"{'mesure' if r['type_loyer']!='maille' else 'estime':<7} {r['n']:>4} ventes".replace(',', ' '))
    print("\n  --- secteur de recherche (tri rendement) ---")
    for r in sect:
        print(f"   {r['nom']:<26} {r['prix']:>6,} €/m²  {r['loyer']:>5.1f} €  {r['rdt']:>5.1f} %  "
              f"{'mesure' if r['type_loyer']!='maille' else 'estime':<7} {r['n']:>4} ventes".replace(',', ' '))


if __name__ == '__main__':
    main()
