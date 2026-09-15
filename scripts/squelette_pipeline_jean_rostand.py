#!/usr/bin/env python
"""Crée le squelette pipeline 02c-Jean-Rostand-11pkgs-La-Seyne dans le Drive Sémaphore Patrimoine.

Usage: python squelette_pipeline_jean_rostand.py
Convention: dossiers sans espaces ni accents, fichier 00-FICHE-<nom>.md à la racine.
"""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

TOKEN = '/home/alexis-barlatier/.hermes/profiles/semaphore-sonar/google_token.json'
PIPELINE = '15Zs4NuBmtO8ed5PTP2NhHTMIWdh-OBs6'  # 02-Pipeline-opportunites

NOM_DOSSIER = '02c-Jean-Rostand-11pkgs-La-Seyne'
SOUS_DOSSIERS = ['Actes-et-compromis', 'Financement', 'Baux-et-locataires',
                 'Copropriete', 'Fiscalite-locale', 'Assurance']

FICHE_MD = """# 00-FICHE — 02c Jean Rostand, 11 parkings (La Seyne-sur-Mer)

## Identification
- Programme neuf (VEFA) « Jean Rostand » — promoteur : Constructa Promotion (commercialisation 1964.immo, Isabelle Alain Scala)
- Quartier Saint-Jean, bd Jean Rostand / av. Jean Vilar, La Seyne-sur-Mer (83500) — QPV Berthe (vérifié carte CGET)
- 11 lots de parking standard en sous-sol (12 m²/place, ~132 m² au total) — lots 9 et 20-29 de la grille Constructa, sous-sol R-1
- Livraison : 2e trimestre 2027
- Statut 10/09/2026 : offre d'achat à 6 000 €/place, soit 66 000 € net vendeur (prix catalogue 8 000 €/place) + frais d'acquisition 1 980 € → prix de revient 67 980 € (6 180 €/place)
- Usage retenu : location longue durée — fourchette de loyers envisagée 54 à 65 €/mois/place (retenu 60 €/m)

## Financement
- Demande : 59 400 € (90 % du prix net vendeur) sur 15 ans à 3,70 % → mensualité 447,33 €/mois (assurance 0,34 % incluse)
- Apport : 8 580 € (fonds propres de la SCI) = 12,6 % du prix de revient
- Garanties : hypothèque de premier rang sur les 11 places, **prise à l'acte notarié d'acquisition** (pas de report à la livraison — le banquier ne l'accepterait pas). Nantissement des parts sociales et caution des gérants : **non proposés d'office** (cela ferme la négociation parallèle avec une autre banque), accordables seulement si la banque les demande
- Intérêts intercalaires (~500 à 1 650 €) servis par la trésorerie de la SCI, sans compte courant d'associé
- Encours présenté au banquier : parc Verrerie seul (70 002 €) — le prêt in fine La Garde entre associés est exclu
- À COMPLETER : retour banque (offre de prêt), taux et durée retenus

## Revenus / charges (hypothèses retenues 09-10/2026)
- Loyers : 11 × 60 €/mois (retenu) = 7 920 €/an pleine occupation
- Charges copro : 180 €/an/place (1 980 €/an) — À CONFIRMER (budget prévisionnel écrit) ; TF exonérée 2 ans puis ~500 €/an
- Amortissement SCI IS : 2 039 €/an (90 % du prix de revient sur 30 ans)
- Capacité après IS (15 %) : 432 €/mois à 60 €/m ; 478 €/mois à 65 € ; 377 €/mois à 54 €
- Point mort : EBE ≥ 0 dès 3/11 places ; autofinancement trésorerie ~62 €/m ; vision banque dès 8/11

## Marqueurs de reconnaissance
- Promoteur : Constructa Promotion (VEFA)
- Quartier Saint-Jean, La Seyne-sur-Mer — résidence « Jean Rostand »
- 11 lots parking sous-sol, livraison T2 2027
- Commercialisation annexes : Isabelle Alain Scala — ialainscala@1964.immo (1964.immo) ; grille prix stock + plans parking R-1/R-2 reçus 08/09/2026 (catalogue parking simple 8 000 € TTC = 6 667 € HT, TVA 20 %)

## À COMPLETER
- Numéros de lots définitifs, syndic de la résidence, référence contrat VEFA
- Date d'acceptation de l'offre / compromis
- Montants réels : TF, charges copro (budget prévisionnel), frais de notaire définitifs
- Acceptation écrite par le promoteur : un acte unique pour les 11 lots (sinon ~9 600 € de frais)
"""


def main():
    creds = Credentials.from_authorized_user_info(json.load(open(TOKEN)))
    drv = build('drive', 'v3', credentials=creds)

    # Vérifier que le dossier n'existe pas déjà
    existing = drv.files().list(
        q=f"'{PIPELINE}' in parents and name='{NOM_DOSSIER}' and trashed=false",
        fields='files(id,name)').execute().get('files', [])
    if existing:
        print('EXISTE DEJA:', existing[0]['id'])
        return

    folder = drv.files().create(body={
        'name': NOM_DOSSIER, 'mimeType': 'application/vnd.google-apps.folder',
        'parents': [PIPELINE]}, fields='id,name').execute()
    fid = folder['id']
    print('Dossier cree:', folder['name'], fid)

    for sub in SOUS_DOSSIERS:
        s = drv.files().create(body={
            'name': sub, 'mimeType': 'application/vnd.google-apps.folder',
            'parents': [fid]}, fields='id,name').execute()
        print(' -', s['name'], s['id'])

    media = MediaIoBaseUpload(io.BytesIO(FICHE_MD.encode('utf-8')),
                              mimetype='text/markdown')
    f = drv.files().create(body={
        'name': f'00-FICHE-{NOM_DOSSIER}.md', 'parents': [fid]},
        media_body=media, fields='id,name').execute()
    print('Fiche creee:', f['name'], f['id'])


if __name__ == '__main__':
    main()
