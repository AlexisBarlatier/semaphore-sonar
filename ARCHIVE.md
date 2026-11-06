# Archivé le 06/11/2026

Depuis le 06/11/2026, les opérations immobilières du groupe Sémaphore vivent dans l'application Sémaphore (dépôt `semaphore-sonar-app`). Sonar y accède par ses outils MCP « semaphore » (skill `semaphore-sonar-app`). Ce dépôt n'est plus la source des dossiers.

## Archivé, à ne plus modifier

| Ancien support | Repris dans l'application |
|---|---|
| `analyses/analyses.json` (fiches d'analyse) | dossier chiffré de chaque opération (note et verdict calculés par l'application) |
| `documents/suivi/affaires-a-suivre.json` (registre des affaires à suivre) | opérations en veille avec leur date de revue, prix plafond, échéances, historique au fil |
| `analyses/*/etat-dossier.md` | point de situation et fil de chaque opération |
| fiches `00-FICHE-*.md` du Drive | fil et documents de l'opération (bandeau « Fiche archivée » en tête de chaque fiche ; celle du parc de La Verrerie reste vivante) |
| pages `analyses/*/index.html` | figées en PDF dans le Drive (`02-Pipeline-opportunites/00-Archives-pages-analyse`) et déclarées comme documents de leur opération |

`analyses.json` et le registre sont en lecture seule sur le disque.

## Site public

GitHub Pages ne sert plus que l'accueil et la page de confidentialité, exigées par l'écran de consentement Google de Sonar (branche `pages`). Les analyses ne sont plus publiées.

**Ce dépôt est public** : n'y poussez plus aucune donnée de dossier (prix, négociation, pièce).

## Ce qui reste vivant ici

- les scripts outils : Gmail, Drive, contacts, veille ;
- les pages transverses : marchés locaux, enchères, trésorerie du parc ;
- les pièces encore sur le disque (`analyses/*/documents/`, `inbox_pj/`), qui migrent vers le Drive au fil de l'eau, déclarées dans l'application.
