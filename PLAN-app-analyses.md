# Plan — App « analyses pilotées par la base » (Sémaphore Sonar)

Version : 1 — 06/09/2026 — à valider par Alexis avant construction

## 1. Constat et décision

Aujourd'hui, le pipeline est à l'envers de la cible :

- chaque analyse est une page HTML écrite par l'agent (LLM) ;
- la base `analyses.json` actuelle est *rétro-extraite* des pages HTML par un script de scraping ;
- le listing `analyses/index.html` est régénéré par un script qui lit… les pages HTML.

Cible validée avec Alexis :

- **la base de données est la source de vérité**, remplie par l'agent au moment de l'analyse ;
- **le code produit les pages** (listing maintenant, fiches d'analyse à terme) ;
- **aucun résultat de calcul n'est stocké** (note, verdict, rendements…) : le code les calcule au build ;
- l'agent n'écrit plus jamais le HTML du listing (économie d'énergie cognitive, format maintenu par le code) ;
- les fiches d'analyse individuelles restent écrites par l'agent (LLM) pour l'instant, mais le schéma est conçu en superset pour qu'un générateur les produise plus tard.

## 2. Principes d'architecture

1. `analyses/analyses.json` = seule source de vérité (versionnée, diffable, publiée sur GitHub Pages).
2. La base ne stocke que des **entrées** : faits constatés, données marché sourcées, hypothèses, jugements qualitatifs chiffrés. Jamais de résultats dérivés.
3. Tout résultat (prix de revient, rendements, ratio coût/valeur, note /10, verdict, classes CSS) est **calculé par un moteur de code déterministe** au moment du build.
4. Mêmes données → même HTML (build idempotent, testable).
5. Les règles de calcul vivent dans le code + sa documentation, pas dans la tête de l'agent.
6. Confidentialité : `analyses.json` est public (repo GitHub Pages). Le schéma ne contient jamais de financement (règle #41 du skill) ; le suivi interne (offre acceptée, achat, prêt) reste hors repo.

## 3. Frontière données stockées / données calculées

### Stocké dans la base (inputs)

| Groupe | Champs (extrait) |
|---|---|
| Identité | slug, date d'analyse, titre, adresse (rue, quartier, ville, CP), type de bien |
| Bien | type détaillé, surfaces (Carrez, utile, terrain, totale), lots/pièces, DPE/GES, copro (charges annuelles réelles si connues, nb lots), travaux (nature, montant estimé ou devis, statut), particularités bloquantes |
| Annonce | plateforme, URL, prix affiché, honoraires/FMN, prix de référence retenu, vendeur, contact |
| Marché | prix/m² et valeur marché (fourchette basse/haute, sources croisées DVF + MeilleursAgents, écart > 15 % documenté, indice de confiance), loyers constatés par lot (occupé/vacant), valeur locative m²/an pour le pro, taux de capitalisation |
| Hypothèses | taxe foncière (réelle ou estimée), charges copro, PNO, entretien, provision rénovation (2,5 %), taux de vacance par scénario (Base/Best/Worst) et leur justification, taux de charges refacturables (pro) |
| Analyse (jugement) | stratégie retenue + stratégies explorées, scores d'attractivité 6 dimensions (1-10 + justification d'une phrase), type d'opération (locatif / MDB / promotion), liste de risques (label, sévérité 1-5, commentaire), liquidité |
| Spécifique MDB/promo | prix de revente estimé, enveloppe travaux, durée de portage, frais de portage, marge promoteur, SdP, prix terrain max |
| Héritage (transitoire) | `heritage` : note/verdict/rendement affichés historiquement par les pages de l'ère LLM — uniquement pour la migration des 50 fiches, purgé dès que le moteur peut calculer (voir §6) |

### Calculé par le code (jamais stocké)

- prix de revient : prix retenu + frais d'acquisition réels (barème notaire par type/branche — neuf/ancien, parking à l'unité vs lots multiples) + travaux + frais divers
- revenus bruts annualisés (somme des loyers × taux d'occupation)
- résultat fiscal IS (15 %, amortissements par branche — parking sous-sol bâti amortissable, extérieur non)
- rendements (brut, net IS sur valeur après travaux, double affichage revient/marché)
- ratio coût/valeur et verdict associé
- note /10 selon la formule officielle du skill :
  - Rendement net (ou ROI pour MDB) : 40 % → `min(10, rdt × 1.5)`
  - Ratio coût/valeur : 30 % → `max(0, 10 − (ratio − 0.7) × 15)`
  - Adéquation quartier : 20 % → moyenne pondérée des 6 scores selon la matrice de pondération de la stratégie
  - Risque : 10 % → `10 − moyenne des sévérités`
- verdict : ≥ 6,5 « À acheter » ; 4,0–6,4 « À négocier » ; < 4,0 « À fuir »
- colonnes et classes CSS du listing (note-high/mid/low…)

Conséquence pour l'agent : le « jugement » n'est plus un chiffre magique final, mais la saisie structurée des entrées qualitatives (scores 1-10, sévérités 1-5, hypothèses justifiées). La note en découle mécaniquement.

## 4. Schéma cible (analyses.json)

```
{
  "meta": { "schema_version": 1, "generated_at": … },
  "analyses": [
    {
      "slug", "date_analyse",
      "statut_public": "analyse" | "en-cours" | "cloturee",   // info publiable uniquement
      "bien": { … },                    // §3 groupe Bien
      "annonce": { … },
      "marche": { … },
      "hypotheses": { … },
      "analyse": {
        "branche": "residentiel" | "professionnel" | "parking" | "promotion" | "mdb",
        "strategie_retenue": { "nom", "code", "lots", "adéquation_score" },
        "attractivite": [ { "dimension", "score", "justification" } ×6 ],
        "risques": [ { "label", "severite", "commentaire" } ],
        "type_operation": "locatif" | "mdb" | "promotion" | "mixte"
      },
      "mdb": { … } | "promotion": { … },   // selon branche
      "heritage": { "note", "verdict", "rendement" } | null,  // transitoire
      "champs_manquants": [ … ]             // auto-rempli par validate
    }
  ]
}
```

Pas de stockage : prix de revient, rendements, ratio, note, verdict, IS, CF. Sur les inputs marché : toujours `source` + `date` + `confiance` (règles pitfall 39/44 du skill).

## 5. L'app (code dans le repo)

Petit package Python stdlib (zéro dépendance — suppression d'openpyxl/xlsx) :

```
scripts/analyse_app/
  schema.py          # définition + validation JSON (champs obligatoires par branche)
  engine.py          # moteur : revient, EBE, IS, rendements, ratio (règles fiscalité du skill)
  scoring.py         # note /10 + verdict (formule §3, calibrée)
  build_listing.py   # analyses/analyses.json → analyses/index.html (mêmes classes CSS)
  build_fiche.py     # [plus tard] analyses.json → page d'analyse complète
  import_legacy.py   # one-shot : 50 pages HTML → entrées brutes + heritage
  cli.py             # validate / compute --slug / build-listing / import-legacy
  tests/             # fixtures locatif + parking + MDB + promo
```

Commandes :
- `cli.py validate` — schéma + cohérence minimale (CP↔ville, prix>0, scores 1-10…)
- `cli.py compute --slug X` — affiche les composantes de la note (utile pendant l'analyse et pour calibrer)
- `cli.py build-listing` — régénère `analyses/index.html` (artefact, jamais édité à la main)
- `cli.py import-legacy` — une fois, puis archivé

## 6. Migration des 50 analyses existantes

1. `import_legacy.py` lit les 50 pages et ne stocke que les **inputs** qu'elles contiennent réellement (adresse, prix, surfaces, TF/charges quand présentes dans la fiche, loyers). Champs non extractibles → `champs_manquants` (on les complète petit à petit, dossier par dossier, sans urgence — validé).
2. **Aucun résultat historique stocké** (décision Alexis 06/09) : pas de section `heritage`. Tant que les inputs d'une fiche ne permettent pas le calcul, le listing affiche « — » dans les colonnes dérivées (note, verdict). Les fiches sont re-saisies au fil de l'eau (quand on retouche un dossier ou par lots), et la colonne se remplit automatiquement au build suivant.
3. Conséquence assumée : au moment de la bascule E3, la colonne Note du listing passera en « — » pour les fiches legacy non encore re-saisies. C'est le prix de la propreté : la base ne contient que du vrai, et le listing ne montre que ce que le code sait calculer.
4. Objectif de calibration : sur les fiches aux inputs complets, la note calculée doit retomber sur la note publiée à ±0,2 (les pages actuelles ont été produites avec cette formule — vérifiable). Les écarts résiduels sont documentés.

## 7. Workflow agent après bascule (nouvelle Phase 4-5)

1. Analyse de l'annonce inchangée (extraction, marché, PLU…) ;
2. Saisie structurée de la fiche dans `analyses.json` (via `cli.py`, validation OK) ;
3. Génération de la page d'analyse HTML par l'agent (LLM, pour l'instant) — les chiffres affichés viennent de `compute --slug`, donc fiche et base sont cohérentes par construction ;
4. `cli.py build-listing` → listing à jour, sans intervention humaine sur le HTML ;
5. Contrôles automatiques (schéma + cohérence fiche↔base sur les champs partagés) → commit → push.

L'agent ne touche plus jamais `analyses/index.html` ni le format du listing. Aucune énergie cognitive sur la page : elle devient un artefact jetable du build.

## 8. Étapes de construction

| Étape | Livrable | Critère de sortie |
|---|---|---|
| E1 | Schéma + validation + moteur de calcul + scoring | `compute` reproduit les notes publiées à ±0,2 sur les fiches aux inputs complets |
| E2 | `import_legacy` → analyses.json initial (50 fiches : inputs + heritage) | 50 entrées valides, listing régénérable à l'identique |
| E3 | `build_listing.py` + bascule | `analyses/index.html` régénéré depuis la base = listing actuel (diff nul), puis l'ancien scraping (`build_analyses_db.py`) est retiré |
| E4 | Skill v3 (workflow, conventions, pitfall 34b réécrit, déploiement) | l'agent suit le nouveau pipeline sans ambiguïté |
| E5 | [Plus tard — décision séparée] `build_fiche.py` | une fiche d'analyse générée par code depuis la base |

## 9. Risques et points de vigilance

- **Sensibilité** : `analyses.json` sera public. Aucun champ financement/statut d'offre interne dans le schéma. Le statut « on a acheté/offert » reste hors repo (Drive) si vous le souhaitez.
- **Jugement qualitatif** : le code ne peut pas scorer un quartier ni la sévérité d'un risque. C'est la saisie structurée de l'agent. Fiche sans scores → note non calculable → affichage « — » ou heritage, jamais de note inventée.
- **Changement de règle** (ex. : barème notaire, formule de note) = modification du code + re-build de tout le listing, pas de retouche page par page (pitfall 22 du skill : régénération intégrale).
- **Pages historiques** : figées telles quelles ; la base ne les réécrit pas.
- **xlsx** : abandonné (validé) ; le script `build_analyses_db.py` actuel devient obsolète à E3 (sa logique d'extraction est réutilisée par `import_legacy`).

## 10. Décisions actées (06/09/2026)

1. **Pas de `heritage`** : aucune note/verdict historique stockée ; colonnes « — » tant que le calcul ne passe pas (re-saisie au fil de l'eau).
2. **Emplacement** : `analyses/analyses.json`, publié sur le site (choix laissé à l'agent — la base est « pour la page »).
3. **Suivi interne** (offre faite, achat, financement) : sur le Drive Sémaphore, hors repo. Le repo et `analyses.json` restent 100 % publiables, sans champ de statut d'acquisition.
4. **Pas d'export xlsx** ; openpyxl retiré du pipeline.

## 11. Interface d'édition (question ouverte — décision différée)

Question Alexis : plutôt qu'un build statique lancé par l'agent, une petite app web où il pourrait modifier certaines valeurs directement ?

Réponse honnête : le moteur de calcul et le générateur de pages restent **identiques** dans les deux mondes. La vraie différence, c'est la couche d'édition :

| Option | Effort | Serveur à maintenir | Usage mobile | Zéro dépendance LLM |
|---|---|---|---|---|
| A. Statique actuel (agent remplit la base) | aucun supplément | non | non (passe par le chat) | oui |
| B. Google Sheets comme interface de saisie | faible (+1 script de lecture) | non | oui (app Sheets) | oui |
| C. App web hébergée (FastAPI + SQLite + auth + auto-deploy GitHub) | élevé (+60-70 % de surface : auth, API, UI, serveur, token de déploiement) | oui (à vie) | oui | oui |

Analyse : pour deux utilisateurs qui vivent déjà sur Drive + GitHub, l'option C est une usine à gaz (serveur à sécuriser et maintenir pour un gain marginal) ; l'option B donne une « interface » connue, mobile et partagée avec Rémy, sans serveur. Le compromis recommandé : construire A maintenant (E1-E4), et si l'envie d'éditer soi-même apparaît, brancher B (le schéma de saisie du Sheet = les inputs du §3, les calculs restent dans le moteur Python). C ne se justifie que si un jour le besoin dépasse ce que Sheets sait faire.
