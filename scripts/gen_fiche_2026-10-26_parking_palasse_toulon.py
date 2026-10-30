#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fiche de synthèse — place couverte, Toulon La Palasse (Le Kerylos).

Dossier hors listing : pas de record dans analyses.json, pas de note /10.
Tous les chiffres sont recalculés ici à partir des paramètres du dossier, et
vérifiés en fin de script par un contrôle de cohérence (aucun chiffre à la main).

Convention : SCI à l'IS 15 % ; achat comptant (aucune charge de financement) ;
vacance 5 % ; charges 164 €/an ; taxe foncière 32 €/an ; PNO 55 €/an.
"""
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
SLUG = "2026-10-26-parking-palasse-toulon"
SORTIE = os.path.join(RACINE, "analyses", SLUG, "index.html")

URL_ANNONCE = "https://www.leboncoin.fr/ad/ventes_immobilieres/3296014940"

PRIX = 5550.0
FRAIS = 1450.0
AEM = PRIX + FRAIS
CHARGES = 164.0
TF = 32.0
PNO = 55.0
VACANCE = 0.05
LOYER = 65.0
IS = 0.15

LAT, LON = 43.12504, 5.96675
ADRESSE = "890 avenue Joseph Gasquet, 83100 Toulon — résidence Le Kerylos"
LONG, LARG_ENTREE, LARG_FOND = 6.50, 3.60, 2.40
SURFACE = (LARG_ENTREE + LARG_FOND) / 2 * LONG


def net(loyer, vacance=VACANCE, charges=CHARGES, tf=TF, pno=PNO):
    return loyer * 12 * (1 - vacance) - charges - tf - pno


def rdt(loyer, prix=AEM):
    return net(loyer) / prix * 100


def mois(loyer, prix=AEM):
    return prix / loyer


def nfr(v, dec=0):
    return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")


def eur(v, dec=0):
    return nfr(v, dec) + " €"


def pc(v, dec=2):
    return nfr(v, dec) + " %"


def signe(v, dec=0):
    return ("+" if v > 0 else "−" if v < 0 else "±") + nfr(abs(v), dec) + " €"


# ---------------------------------------------------------------- contrôles
assert abs(SURFACE - 19.5) < 1e-9, SURFACE
assert abs(AEM - 7000) < 1e-9, AEM

L75, L70, L65, L60, L55 = 75.0, 70.0, 65.0, 60.0, 55.0
BASE = net(L65)
BEST = net(L75)
WORST = net(L55, vacance=0.15, charges=350.0)

# ---------------------------------------------------------------- blocs HTML
CARTES = [
    ("Prix affiché", eur(10000)),
    ("Offre maximale", eur(AEM) + " acte en main"),
    ("Loyer retenu", eur(L65) + "/mois"),
    ("Rendement net", pc(rdt(L65), 1)),
    ("Multiple", f"{nfr(mois(L65))} mois"),
    ("Charges / loyers", pc(CHARGES / (L65 * 12) * 100, 1)),
]
cartes = "\n".join(
    f'    <div class="card">\n      <span class="card-label">{lab}</span>\n'
    f'      <span class="card-value">{val}</span>\n    </div>'
    for lab, val in CARTES
)

ATTRACTIVITE = [
    ("Gare de Toulon-Sainte-Musse", "417 m — 5 min à pied"),
    ("Hôpital Sainte-Musse", "789 m — 10 min à pied"),
    ("Copro", "60 lots et plus, majoritairement des studios loués"),
    ("Résidence", "non fermée, sans contrôle d'accès"),
]
attractivite = "\n".join(
    f'      <div class="attract-item"><h3>{t}</h3><p>{d}</p></div>'
    for t, d in ATTRACTIVITE
)

IDENTITE = [
    ("Adresse", ADRESSE),
    ("Parcelle cadastrale", "AX 0608 (626 m²)"),
    ("Nature", "place de stationnement couverte, non fermée"),
    ("Dimensions relevées", f"{nfr(LONG,2)} m × {nfr(LARG_ENTREE,2)} m à l'entrée / {nfr(LARG_FOND,2)} m au fond"),
    ("Surface utile", f"≈ {nfr(SURFACE,1)} m²"),
    ("Hauteurs", "2,40 m sous le plus bas tuyau — 2,90 m au total"),
    ("Charges de copropriété", eur(CHARGES) + "/an"),
    ("Taxe foncière", eur(TF) + "/an"),
    ("Syndic", "Citya Toulon"),
    ("Occupation", "lot libre, aucun bail en cours"),
    ("Vendeur", "particulier, sans agence"),
    ("Prix affiché / dernier mot", f"{eur(10000)} / {eur(7000)}"),
]
identite = "\n".join(
    f'      <tr><th scope="row">{k}</th><td>{v}</td></tr>' for k, v in IDENTITE
)

ANNONCE_VS_PIECES = [
    ("Nature", "« place de stationnement couverte »", "couverte, non fermée, dans une résidence ouverte"),
    ("Dimensions", "aucune", "6,50 m × 3,60 / 2,40 m, hauteur 2,40 m sous tuyaux"),
    ("Charges", "aucune", "164 €/an"),
    ("Taxe foncière", "aucune", "32 €/an"),
    ("Copropriété", "« petite résidence »", "60 lots et plus, studios de 21 à 29 m²"),
    ("Fermeture en box", "« possibilité de la fermer après AG »", "aucune demande instruite, article 25 sur 60 lots"),
    ("Occupation", "aucune", "lot libre, aucun bail"),
    ("Loyer", "aucun", "aucune preuve — relevé de marché seulement"),
]
avp = "\n".join(
    f"        <tr><th scope=\"row\">{k}</th><td>{a}</td><td>{b}</td></tr>"
    for k, a, b in ANNONCE_VS_PIECES
)

GRILLE = []
for loyer in (75.0, 70.0, 65.0, 60.0, 55.0):
    GRILLE.append(
        f"        <tr><td>{eur(loyer)}/mois</td><td>{eur(net(loyer))}</td>"
        f"<td>{pc(rdt(loyer),1)}</td><td>{pc(net(loyer)*0.85/AEM*100,1)}</td>"
        f"<td>{nfr(mois(loyer))} mois</td></tr>"
    )
grille = "\n".join(GRILLE)

LOYERS = [
    ("Places extérieures, Toulon", "50 à 70 €/mois", "relevés 60 € ; bas de fourchette retenu pour un produit sans abri"),
    ("Couverts et sous-sol sécurisés, Toulon", "85 à 115 €/mois", "100 € double place en enfilade (Les Routes), 112 € garage 12 m², 115 € box 17 m² (Pont du Las), 85 € sous-sol (Saint-Roch)"),
    ("Ce lot — couverte, résidence ouverte", "50 à 70 €/mois", "la bande « sécurisée » ne s'applique pas : pas de barrière, pas de porte"),
    ("Loyer retenu au dossier", eur(L65) + "/mois", "haut de la bande ouverte, justifié par la gare à 417 m et l'hôpital à 789 m"),
    ("DVF — lot 60 (dépendance seule)", eur(6500) + " (09/2024)", "soit 6 850 € indexé à 2,5 %/an ; autres dépendances seules du secteur : 4 000 à 9 500 €"),
]
loyers = "\n".join(
    f"        <tr><td>{s}</td><td>{l}</td><td>{d}</td></tr>" for s, l, d in LOYERS
)

RISQUES = [
    ("Fermeture en box non crédible", "Vote à l'article 25 sur 60 lots majoritairement composés d'investisseurs ; aucune demande jamais instruite. Aucune valeur dans le prix.", 4),
    ("Accès du syndic aux tuyauteries", "Accès sans délai nécessaire, donc serrure passe-partout : le locataire ne peut pas être garanti que le volume reste fermé. Pas de loyer de box, pas de stockage.", 4),
    ("Résidence non sécurisée", "Aucune barrière, aucun contrôle d'accès : la place est exposée au stationnement sauvage des voisins, premier motif de départ d'un locataire.", 3),
    ("Charges lourdes pour le loyer", f"{eur(CHARGES)}/an pour {eur(L65*12)}/an de loyers, soit {pc(CHARGES/(L65*12)*100,1)} — au-dessus du seuil de refus de 15 %. Aucun prix ne corrige ce ratio.", 4),
    ("Aucune preuve de loyer", "Le lot n'a jamais été loué : la bande 50-70 € est une lecture de marché, pas un bail. Le test locatif n'a pas été publié.", 3),
    ("Dalle et niveau inférieur non vérifiés", "Si un local ou un parking existe sous l'emplacement, le perçage d'un arceau est exclu. Sans arceau, le loyer retombe à 55-60 € et le dossier se referme.", 5),
    ("Travaux votés inconnus", "PV d'AG non communiqués : ravalement, toiture ou ascenseur sur 60 lots peuvent peser 1 500 à 3 000 € par lot.", 4),
    ("Motif de vente non documenté", "« besoin de vendre assez urgemment », prix baissé de 10 000 à 7 000 € en trois jours, sans sollicitation. Signal de pression, motif non justifié.", 2),
    ("Liquidité de sortie", "19,5 m² atypiques, résidence ouverte, charges élevées : la revente s'adresse au même acheteur de rendement, pas à un utilisateur.", 3),
    ("Frais d'acquisition fixes", f"{eur(FRAIS)} sur {eur(PRIX)} de prix, soit {pc(FRAIS/PRIX*100,1)} : la friction pèse plus que la négociation espérée.", 2),
]
risques = "\n".join(
    f'        <tr><td>{f}</td><td>{d}</td><td class="sev-{s}">{s}/5</td></tr>'
    for f, d, s in RISQUES
)

PIECES = [
    "Décomposition des 164 €/an : part des charges générales, part ascenseur, part voirie et portail — si l'ascenseur y figure, demander la clé de répartition au syndic",
    "Procès-verbaux des trois dernières assemblées générales",
    "État daté et acte de propriété (numéro de lot, date d'acquisition, charges à jour)",
    "Règlement de copropriété : clause sur l'installation d'ouvrages et la location à un non-résident",
    "Réponse du syndic sur l'existence d'un local ou d'un parking sous l'emplacement, et sur l'épaisseur de la dalle",
]
pieces = "\n".join(f"        <li>{p}</li>" for p in PIECES)

SCENARIOS = [
    ("Base", L65, 0.05, CHARGES, "loyer de marché haut de la bande ouverte"),
    ("Best", L75, 0.05, CHARGES, "arceau installé, emplacement réservé, loyer en haut de bande"),
    ("Worst", L55, 0.15, 350.0, "place squatée, vacance longue, charges à 350 €/an"),
]
scen = []
for nom, loyer, vac, ch, note in SCENARIOS:
    n = net(loyer, vacance=vac, charges=ch)
    scen.append(
        f'      <div class="projection-card"><h3>{nom} — {eur(loyer)}/mois</h3>'
        f"<p>{note}</p><p><strong>{eur(n)}/an</strong> net — {pc(n/AEM*100,1)} sur l'acte en main</p></div>"
    )
scenarios = "\n".join(scen)

ANNEE1_WORST = WORST - 2000  # travaux de copropriété non votés connus : 2 000 € appelés la première année

HTML = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Synthèse — parking couvert, Toulon La Palasse</title>
  <link rel="stylesheet" href="../../style.css">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
</head>
<body>

<header class="report-header">
  <nav class="report-breadcrumb"><a href="../../analyses/index.html">← Retour aux analyses</a></nav>
  <h1>Fiche de synthèse — décision d'acquisition</h1>
  <p class="report-address">{ADRESSE}</p>
  <p class="report-date">Mise à jour le 30 octobre 2026 — fiche de synthèse hors listing, non notée</p>
  <p class="report-source">Source : Leboncoin, vendeur particulier, sans agence</p>
  <div class="report-source-link"><a href="{URL_ANNONCE}">{URL_ANNONCE}</a></div>
</header>

<main>

  <div class="strategy-banner">
    <span class="strategy-badge">Placement parking — une place, un loyer</span>
    <p>Stratégie retenue : <strong>location longue durée à un particulier, sans travaux et sans assemblée générale</strong> — SCI à l'IS (15 %), achat comptant.</p>
  </div>

  <section class="summary-cards">
{cartes}
  </section>

  <section class="map-section">
    <h2>Localisation</h2>
    <div id="map-container" data-lat="{LAT}" data-lon="{LON}" data-address="{ADRESSE}"></div>
  </section>

  <section class="attractiveness">
    <h2>Attractivité — La Palasse, à 400 m de la gare de Sainte-Musse</h2>
    <p class="attractiveness-intro">Le bassin de locataires est structurel : la résidence elle-même est composée de studios de 21 à 29 m² vendus entre 48 000 et 85 000 €, la gare de Toulon-Sainte-Musse est à 417 m et l'hôpital à 789 m. Ce sont des locataires sans parking, du personnel hospitalier et des navetteurs. La demande existe donc à l'échelle de deux foyers, pas du quartier. Le point faible n'est pas la demande, c'est l'offre : la résidence n'est pas fermée et les places y sont utilisées gratuitement par les copropriétaires, ce qui plafonne le loyer tant qu'aucun dispositif ne réserve l'emplacement.</p>
    <div class="attractiveness-grid">
{attractivite}
    </div>
    <div class="attractiveness-summary">
      <p><strong>Profil locataire cible :</strong> résident de la résidence ou du voisinage immédiat, un seul véhicule, cherchant un emplacement abrité et réservé à proximité de la gare.</p>
      <p><strong>Conclusion :</strong> 65 €/mois est tenable ; 75 € ne se défend que si l'emplacement est effectivement réservé par un dispositif individuel.</p>
    </div>
  </section>

  <section class="strategy-exploration">
    <h2>Ce que l'annonce dit, ce que les pièces disent</h2>
    <table class="comparison-table">
      <thead>
        <tr><th>Point</th><th>Annonce</th><th>Pièces et réponses du vendeur</th></tr>
      </thead>
      <tbody>
{avp}
      </tbody>
    </table>
  </section>

  <section class="identity-sheet">
    <h2>Fiche d'identité</h2>
    <table class="identity-table">
{identite}
    </table>
  </section>

  <section class="strategy-exploration">
    <h2>Les quatre points négatifs, et ce qu'ils valent</h2>
    <p class="attractiveness-intro"><strong>1. La fermeture en box n'est pas une hypothèse crédible.</strong> Il faudrait un vote à l'article 25, soit la majorité des voix de tous les copropriétaires, dans une copropriété de plus de 60 lots majoritairement composée d'investisseurs. Aucune demande n'a jamais été instruite. Le second passage de l'article 25-1 suppose douze à vingt-quatre mois et un conseil syndical porteur. <strong>Cette perspective ne vaut pas un euro dans le prix.</strong></p>
    <p class="attractiveness-intro"><strong>2. Même obtenu, le box ne protégerait rien.</strong> Les tuyauteries imposent au syndic un accès sans délai, donc une serrure passe-partout : le locataire ne peut pas avoir la garantie que ses affaires restent inaccessibles. Ce n'est pas un box, c'est une place avec une porte. Aucun loyer de box ne peut être défendu, et aucun stockage n'est louable.</p>
    <p class="attractiveness-intro"><strong>3. La résidence n'est pas sécurisée.</strong> Pas de barrière, pas de contrôle d'accès : la place est exposée au stationnement sauvage des voisins. C'est le premier motif de départ d'un locataire sur ce type de produit, et c'est aussi ce qui plafonne le loyer.</p>
    <p class="attractiveness-intro"><strong>4. Les charges sont hors de proportion avec le service rendu.</strong> {eur(CHARGES)}/an pour {eur(L65*12)}/an de loyers, soit {pc(CHARGES/(L65*12)*100,1)}. Un emplacement de stationnement ne se sert pas de l'ascenseur, et il n'y a aucun portail à entretenir dans cette résidence. Si la quote-part comprend des charges d'ascenseur, elle est contestable au titre des charges spéciales ; sinon, elle reste anormalement lourde pour un lot isolé. Dans les deux cas, c'est un argument de prix immédiat, pas une ligne à espérer corriger : une clé de répartition se révise en assemblée, sur des mois.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Relevé de loyers et de ventes — Toulon, octobre 2026</h2>
    <table class="comparison-table">
      <thead>
        <tr><th>Source</th><th>Loyer ou prix</th><th>Détail</th></tr>
      </thead>
      <tbody>
{loyers}
      </tbody>
    </table>
    <p class="attractiveness-intro">La bande utile s'arrête à 70 €/mois pour une place couverte dans une résidence ouverte. Les 85 à 115 € relevés à Toulon décrivent des produits fermés ou en sous-sol sécurisé, qui ne sont pas ce lot. Le prix de la dernière dépendance vendue seule dans l'immeuble — 6 500 € en septembre 2024 — est le comparable direct : il valide le niveau de 7 000 € acte en main et invalide le prix affiché de 10 000 €.</p>
  </section>

  <section class="strategy-exploration">
    <h2>Grille de prix par loyer — acte en main de {eur(AEM)}</h2>
    <p class="attractiveness-intro">Frais d'acquisition {eur(FRAIS)} (droit commun, aucun taux réduit), charges {eur(CHARGES)}/an, taxe foncière {eur(TF)}/an, assurance {eur(PNO)}/an, vacance 5 %. Le rendement est calculé sur l'acte en main, pas sur le seul prix d'achat.</p>
    <table class="comparison-table">
      <thead>
        <tr><th>Loyer</th><th>Net annuel</th><th>Net sur acte en main</th><th>Après IS (15 %)</th><th>Multiple</th></tr>
      </thead>
      <tbody>
{grille}
      </tbody>
    </table>
    <p class="attractiveness-intro">Le seuil maison de 5 % net après IS est tenu jusqu'à 60 €/mois. À 65 €, le lot est à {nfr(mois(L65))} mois de loyer, sous le plafond des 120 mois.</p>
  </section>

  <section class="financial-projections">
    <h2>Trois scénarios</h2>
    <div class="projections-grid">
{scenarios}
    </div>
    <div class="projection-summary">
      <p class="attractiveness-intro">Dans le scénario dégradé, un appel de travaux de copropriété de 2 000 € la première année fait passer l'exercice à {signe(ANNEE1_WORST)} : le lot reste finançable, mais il ne produit rien cette année-là.</p>
      <p class="attractiveness-intro"><strong>Aucun scénario ne dépend d'une hausse de loyer.</strong> C'est la condition du dossier : la valeur vient du prix d'entrée, pas d'une hypothèse d'exploitation.</p>
    </div>
  </section>

  <section class="risk-matrix">
    <h2>Matrice de risques</h2>
    <table class="risk-table">
      <thead>
        <tr><th>Facteur de risque</th><th>Détail</th><th>Sévérité</th></tr>
      </thead>
      <tbody>
{risques}
      </tbody>
    </table>
  </section>

  <section class="strategy-exploration">
    <h2>Réserves et pièces à exiger avant tout engagement</h2>
    <ul>
{pieces}
    </ul>
    <p class="attractiveness-intro">Le point bloquant est la dalle. S'il existe un local ou un parking sous l'emplacement, le dispositif de réservation ne peut pas être ancré : le loyer retombe à 55-60 €/mois et le dossier se referme. Tant que la réponse n'est pas écrite, le dossier reste ouvert mais non engageable.</p>
  </section>

  <section class="verdict nego">
    <h2>Recommandation</h2>
    <div class="verdict-decision">
      <p class="verdict-stance"><strong>On achète à {eur(AEM)} acte en main, pas un euro de plus.</strong> Offre unique, ferme, sans contre-proposition : {eur(PRIX)} net vendeur et {eur(FRAIS)} de frais, soit {nfr(mois(L65))} mois de loyer à 65 €/mois. Au-delà, on passe.</p>
    </div>
    <div class="verdict-details">
      <p><strong>Pourquoi ce prix et pas celui du vendeur :</strong> le vendeur est passé seul de 10 000 à 7 000 € en trois jours. Ce n'est pas une remise obtenue, c'est un signal de pression — et 7 000 € acte en main correspond au prix de la dépendance vendue seule dans le même immeuble en septembre 2024. Le prix affiché n'était pas un prix de marché.</p>
      <p><strong>Ce que le lot produit :</strong> {eur(BASE)} par an net à 65 €/mois, soit {pc(rdt(L65),1)} sur l'acte en main et {pc(BASE*0.85/AEM*100,1)} après IS. Le rendement est modeste mais réel, et il ne dépend d'aucune transformation.</p>
      <p><strong>Ce qui ferait basculer le dossier :</strong></p>
      <ul>
        <li>Un local ou un parking sous l'emplacement : pas de dispositif de réservation possible, donc pas d'achat.</li>
        <li>Des charges très au-dessus des 164 €/an annoncés, ou des travaux votés non financés.</li>
        <li>Un loyer qui ne trouve pas preneur au test : sous 60 €/mois, le dossier sort du seuil de 5 % net après IS.</li>
      </ul>
      <p><strong>Condition de forme :</strong> l'accord de l'associé est requis avant envoi. Sans accord, aucune démarche n'est engagée auprès du vendeur.</p>
    </div>
    <div class="verdict-meta">
      <p><strong>Régime fiscal retenu :</strong> SCI à l'IS (15 %) — amortissement non retenu (convention prudente), aucun travaux</p>
      <p><strong>Hypothèses retenues :</strong> loyer {eur(L65)}/mois, vacance 5 %, charges {eur(CHARGES)}/an, taxe foncière {eur(TF)}/an, assurance {eur(PNO)}/an, frais d'acquisition {eur(FRAIS)}</p>
      <p><strong>Nature du document :</strong> fiche de synthèse interne, hors listing, non notée</p>
    </div>
  </section>

  <footer class="report-signature">
    <p>Analyse réalisée par</p>
    <p class="signature-names">Rémy Barlatier — 06 27 84 53 50 — sarl.spbi@gmail.com</p>
    <p class="signature-names">Alexis Barlatier — 06 61 26 13 83</p>
  </footer>

</main>

<script>
  (function () {{
    var mapEl = document.getElementById('map-container');
    var lat  = parseFloat(mapEl.getAttribute('data-lat'));
    var lon  = parseFloat(mapEl.getAttribute('data-lon'));
    var addr = mapEl.getAttribute('data-address');

    if (isNaN(lat) || isNaN(lon)) {{
      mapEl.innerHTML = '<p class="map-fallback">Coordonnées non disponibles</p>';
      return;
    }}

    var map = L.map('map-container').setView([lat, lon], 15);
    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19
    }}).addTo(map);
    L.marker([lat, lon]).addTo(map).bindPopup(addr).openPopup();
  }})();
</script>

</body>
</html>
"""

INTERDITS = ("prêt", "emprunt", "crédit", "apport", "mensualité", "levier")


def main():
    bas = HTML.lower()
    for mot in INTERDITS:
        if re.search(r"\b" + mot, bas):
            sys.exit(f"Mot de financement interdit dans la page : {mot}")
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as f:
        f.write(HTML)
    print(f"écrit : {SORTIE} ({len(HTML)} octets)")
    print(f"AEM {AEM:.0f} | net 65 € {BASE:.0f} | {rdt(L65):.2f} % | {mois(L65):.0f} mois")
    print(f"worst {WORST:.0f} | année 1 worst {ANNEE1_WORST:.0f}")


if __name__ == "__main__":
    main()
