#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
00-SYNTHESE-Parc — tableau de bord du parc Sémaphore Patrimoine (Google Sheets natif).
Cree/met à jour un spreadsheet a la racine de 01-Parc sur le Drive Sémaphore
(ID/lien stable si le fichier existe deja). Remplace l'ancienne version .xlsx
(decision Alexis 09/09/2026 : Google Sheet, pas Excel).

Sources : fiches 00-FICHE du Drive (01a/01b/02a-02d) + decisions de sessions.
Regle : jamais de valeur inventee — « À COMPLÉTER » tant que non confirme.
MAJ : editer les donnees ci-dessous puis relancer (venv hermes-agent, PEP 668).
"""
import json
import datetime

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build as gbuild
from googleapiclient.http import MediaIoBaseUpload

TOKEN = '/home/alexis-barlatier/.hermes/profiles/semaphore-sonar/google_token.json'
DOSSIER_PARC = '1QIx252z9jmei5iG_tPQ-aXgn9ATtDust'   # 01-Parc
NOM_FICHIER = '00-SYNTHESE-Parc'                     # sans extension : spreadsheet natif
MIME_SHEET = 'application/vnd.google-apps.spreadsheet'

MAJ = datetime.date.today().isoformat()

# ---------------------------------------------------------------- donnees
PARCS = [
    {
        'dossier': '01a-Valentine-La-Verrerie-13pkgs',
        'bien': 'La Verrerie — 148 traverse de la Martine, 13011 Marseille 11e (La Valentine)',
        'lots': '13 places couvertes (PKG INT) — lots 108-234, RDC et sous-sols bât. B1/B2 (6/10098e chacun)',
        'statut': 'PARC — exploité, loué en bloc',
        'acquisition': '2026-04-23',
        'vendeur': 'SCI La Martine (SIREN 503808495) — acte Me Gilson 23/04/2026',
        'prix': 85800,
        'marche': 130000,
        'credit': 'Crédit Mutuel Marseille Castellane — contrat n°10278 08980 00021441704',
        'encours': 71500,
        'taux_forme': '3,70 % fixe — 180 mois (assurance incluse), TEG 5,64 %',
        'echeance': 546.79,
        'fin_credit': '05/04/2041',
        'locataire': 'SCHINDLER — bail 18/10/2021 ; 4 623,32 € HT/trimestre (rév. 2025)',
        'loyer_an': 4623.32 * 4,
        'refacture': 'charges copro + PNO (598,91 €/an, facture 030426)',
        'charges_sci': 'TF : à compléter (copro refacturée)',
        'notes': 'Prix acte : 85 800 € TTC = 71 500 HT + TVA 20 % (14 300) = 6 600 €/place TTC. Frais prêt : dossier 500 € + garanties 4 658 € ; cautions solidaires A. et R. Barlatier. Acte classé dans Actes-et-compromis. Valeur marché : ≥10 k€/pl (est. Alexis 09/09/2026 — comparables 13011 places non boxées 7-12 k€, boxes 15-30 k€). ANCRAGE LOCATAIRE (Rémy 11/09/2026) : le preneur a investi près de 150 k€ dans ses bureaux et dans la pose de bornes électriques — coût de sortie élevé, amortissement long, risque de départ quasi nul à horizon de bail. Risque résiduel à surveiller : cession ou liquidation de la société, changement de stratégie, rachat.',
    },
    {
        'dossier': '01b-La-Garde-2-ext',
        'bien': 'Le Dionysos — 325 av. de la Paix, La Garde (83)',
        'lots': '2 places extérieures — lots 80-81 (P15-P16), quote-part 5/10000e',
        'statut': 'PARC — acquis, 2 places louées',
        'acquisition': 'à confirmer (vente Jenzi, dossier suivi 09/2026 ; RC/EDD 21/11/2024)',
        'vendeur': 'société JENZI (SIREN 729502526) — notaire Me Grobon / VIANOTA',
        'prix': 12000,
        'marche': 14000,
        'credit': 'prêt interne associés (in fine)',
        'encours': 11500,
        'taux_forme': '3 % in fine — refonte prévue amortissable 240 mois @ 2 %',
        'echeance': None,
        'fin_credit': 'n/a (in fine)',
        'locataire': '2 places louées ~61 €/m chacune (à confirmer)',
        'loyer_an': 61 * 2 * 12,
        'refacture': '—',
        'charges_sci': 'copro Le Dionysos + TF : à compléter (syndic à déterminer)',
        'notes': 'Prix ~6 k€/place, à confirmer. Intérêts in fine ~29 €/m. Valeur marché : ~7 k€/pl (est. Alexis 09/09/2026). Lot de diversification : ne compte jamais dans la capacité de portage (règle 09/2026).',
    },
]

PIPELINE = [
    {
        'dossier': '02c-Jean-Rostand-11pkgs-La-Seyne',
        'projet': 'Jean Rostand — La Seyne-sur-Mer (quartier Saint-Jean)',
        'nature': '11 parkings ss-sol neufs (12 m²) — VEFA Constructa Promotion, livraison T2 2027',
        'statut': 'NÉGOCIATION — offre 66 k€ acte en main validée en interne (08/09/2026)',
        'etape': 'Offre : 66 k€ acte en main (net vendeur 63,4 k€ + notaire ~2,6 k€) ; plafond 72,1 k€ ; repli 69-70 k€',
        'chiffres': 'Loyers marché QPV Berthe : 52-60 €/m/place (pas 78-95 € hors QPV). Crédit différé total jusqu\'à livraison.',
        'contact': 'Constructa Promotion — commercialisation Alain Scala Isabelle (1964.immo)',
        'action': 'Mettre à jour la fiche Drive 02c (encore à 77 k€) ; relancer le banquier sur la base 66 k€',
    },
    {
        'dossier': '02a-Parc-des-Arts-Marseille9',
        'projet': 'Parc des Arts — 343 bd Romain Rolland, Marseille 9e',
        'nature': 'Parkings à vendre (quantité et lots à préciser)',
        'statut': 'PROSPECTION — aucune offre',
        'etape': 'Offre reçue 27/07/2026 (Franck Fazi, Mon Garage en Ville) ; docs reçus : plan de masse, ERP, EDD synoptique',
        'chiffres': '—',
        'contact': 'Franck FAZI — franck@mongaragenville.fr',
        'action': 'Appliquer les plafonds acte en main pipeline avant toute offre',
    },
    {
        'dossier': '02d-Milos-La-Seyne',
        'projet': 'Milos — La Seyne-sur-Mer (83)',
        'nature': 'Annexes parking ss-sol, bât. A et B (R-1/R-2)',
        'statut': 'PROSPECTION — aucune offre',
        'etape': 'Mail « ANNEXES DISPONIBLES » reçu 08/09/2026 ; plans parking reçus',
        'chiffres': '—',
        'contact': 'Alain Scala Isabelle (1964.immo) — même commercialisateur que Rostand',
        'action': 'Compléter la fiche (adresse, promoteur, prix, livraison) avant analyse',
    },
    {
        'dossier': '02b-Sollies-Pont-2-appartements',
        'projet': 'Solliès-Pont — 2 T2 centre (83)',
        'nature': '2 appartements T2',
        'statut': 'NON ACHETÉ (état 09/2026)',
        'etape': 'Piste étudiée 06/2026 (visite Rémy 11/06/2026), sans suite d\'achat',
        'chiffres': 'Projection intégration : crédit 86-156 k€/20 ans (xlsx en Financement)',
        'contact': 'Camille Calegari — IAD France',
        'action': 'Aucune (dossier clos)',
    },
]

# ---------------------------------------------------------------- helpers
def c(r, g, b):
    return {'red': r / 255, 'green': g / 255, 'blue': b / 255}

NAVY = c(31, 56, 100)
BLANC = {'red': 1, 'green': 1, 'blue': 1}

def lignes_parc():
    header = ['Dossier Drive', 'Bien / résidence — ville', 'Lots', 'Statut',
              'Acquis le', 'Vendeur', "Prix d'achat (€)", 'Valeur marché estimée (€)',
              'Crédit (prêteur)', 'Encours (€)', 'Taux / forme', 'Échéance (€/m)',
              'Fin de crédit', 'Locataire / loyer facturé', 'Loyer annualisé (€)',
              'Refacturé au locataire', 'Charges SCI non refacturées',
              'Marge av. TF & IS (€/m)', 'À compléter / vigilance']
    rows = [header]
    for p in PARCS:
        if p['echeance']:
            marge = round((p['loyer_an'] - p['echeance'] * 12) / 12)
        else:
            marge = round(p['loyer_an'] / 12 - p['encours'] * 0.03 / 12)
        rows.append([p['dossier'], p['bien'], p['lots'], p['statut'],
                     p['acquisition'], p['vendeur'], p['prix'], p['marche'],
                     p['credit'], p['encours'], p['taux_forme'], p['echeance'],
                     p['fin_credit'], p['locataire'], p['loyer_an'],
                     p['refacture'], p['charges_sci'], marge, p['notes']])
    tot_loyer = sum(p['loyer_an'] for p in PARCS)
    tot_encours = sum(p['encours'] for p in PARCS if p['encours'])
    tot_marche = sum(p['marche'] for p in PARCS)
    consolide = [
        ['CONSOLIDÉ PARC (référence 09/2026)'],
        [f"Loyers annualisés : ~{tot_loyer:,.0f} €/an (Verrerie 18 493 € documenté + La Garde ~1 464 € à confirmer)"],
        [f"Encours crédits : ~{tot_encours:,.0f} € (CM 71,5 k€ + prêt interne in fine 11,5 k€)"],
        [f"Valeur vénale estimée (09/2026) : Verrerie ≥130 k€ (13 × 10 k€/pl mini) + La Garde ~14 k€ (2 × 7 k€) = ~{tot_marche:,} €"],
        [f"Patrimoine net estimé ≈ {tot_marche - tot_encours:,} € (valeur − encours) — estimations à affiner par un expert local avant usage banquier"],
        ['Surplus CF net du parc : ~700 €/m (référence analyse financement 03/09/2026, validée 09/2026 — à consolider sur les comptes)'],
    ]
    return rows, consolide

def lignes_pipeline():
    header = ['Dossier Drive', 'Projet / ville', 'Nature', 'Statut', 'Étape clé',
              'Chiffres connus', 'Contact', 'Prochaine action']
    rows = [header] + [[p['dossier'], p['projet'], p['nature'], p['statut'],
                        p['etape'], p['chiffres'], p['contact'], p['action']]
                       for p in PIPELINE]
    return rows

def lignes_legende():
    return [[
        f"Tableau de bord du parc Sémaphore Patrimoine — généré le {MAJ}.",
        'CONTENU : une ligne par bien (01a, 01b) avec acquisition, financement, revenus, charges et points ouverts ; un onglet Pipeline (02a-02d) pour les dossiers en cours ; le consolidé parc en bas de l\'onglet Parc.',
        'SOURCE : fiches 00-FICHE du Drive (dossier de chaque bien) + décisions actées en session. Ne pas corriger ici un chiffre documenté : corriger la fiche du bien puis régénérer.',
        'RÈGLE : aucune valeur inventée. Tout montant non confirmé sur acte/avis/relevé est marqué « à compléter » ou « ~ » (estimation).',
        'COLONNE « Valeur marché estimée » : valeur vénale estimée (est. Alexis 09/09/2026 + comparables d\'annonces) — plancher prudent, à affiner par un expert local avant usage banquier.',
        'MAJ : exécuter le script local « scripts/synthese_parc.py » (venv hermes-agent). Upsert sur le Drive : l\'ID/lien du fichier reste stable.',
        'STATUTS : PARC = bien détenu et exploité ; Pipeline : PROSPECTION (aucune offre) / NÉGOCIATION (offre en cours) / NON ACHETÉ (dossier clos).',
        'Le fichier vit à la racine de 01-Parc (Drive Sémaphore Patrimoine). Ne pas le déplacer.',
    ]]

def write_values(sheets, sid, titre, values):
    # RAW : garde les dates/textes tels quels (pas de conversion USER_ENTERED)
    sheets.spreadsheets().values().update(
        spreadsheetId=sid, range=f"'{titre}'!A1", body={'values': values},
        valueInputOption='RAW').execute()

# ---------------------------------------------------------------- principal
def main():
    creds = Credentials.from_authorized_user_info(json.load(open(TOKEN)))
    drv = gbuild('drive', 'v3', credentials=creds)
    sheets = gbuild('sheets', 'v4', credentials=creds)

    # upsert : chercher le spreadsheet existant dans 01-Parc
    q = f"name='{NOM_FICHIER}' and '{DOSSIER_PARC}' in parents and trashed=false and mimeType='{MIME_SHEET}'"
    old = drv.files().list(q=q, fields='files(id,webViewLink)').execute().get('files', [])
    if old:
        sid = old[0]['id']
        print('Spreadsheet existant:', sid, old[0].get('webViewLink'))
    else:
        f = drv.files().create(body={'name': NOM_FICHIER, 'mimeType': MIME_SHEET,
                                     'parents': [DOSSIER_PARC]},
                               fields='id,webViewLink').execute()
        sid = f['id']
        print('Créé:', sid, f.get('webViewLink'))

    # structure des feuilles : renommer la 1re en « Parc », ajouter Pipeline/Légende
    meta = sheets.spreadsheets().get(spreadsheetId=sid).execute()
    ids = {s['properties']['title']: s['properties']['sheetId'] for s in meta['sheets']}
    reqs = []
    if 'Parc' not in ids:
        # renommer la feuille par défaut
        defaut = [s['properties']['sheetId'] for s in meta['sheets']][0]
        reqs.append({'updateSheetProperties': {'properties': {'sheetId': defaut,
                                                              'title': 'Parc'},
                                               'fields': 'title'}})
        ids['Parc'] = defaut
    for titre in ('Pipeline', 'Légende'):
        if titre not in ids:
            r = sheets.spreadsheets().batchUpdate(
                spreadsheetId=sid, body={'requests': [
                    {'addSheet': {'properties': {'title': titre}}}]}).execute()
            ids[titre] = r['replies'][0]['addSheet']['properties']['sheetId']
    if reqs:
        sheets.spreadsheets().batchUpdate(spreadsheetId=sid, body={'requests': reqs}).execute()

    # valeurs
    rows_p, consolide = lignes_parc()
    write_values(sheets, sid, 'Parc', rows_p + [[]] + consolide)
    write_values(sheets, sid, 'Pipeline', lignes_pipeline())
    write_values(sheets, sid, 'Légende', lignes_legende())

    # formatage
    n_b = len(PARCS)
    reqs = [
        # ---- Parc : freeze, filtre
        {'updateSheetProperties': {'properties': {'sheetId': ids['Parc'],
                                                  'gridProperties': {'frozenRowCount': 1}},
                                   'fields': 'gridProperties.frozenRowCount'}},
        {'setBasicFilter': {'filter': {'range': {'sheetId': ids['Parc'],
                                                 'startRowIndex': 0, 'endRowIndex': n_b + 1,
                                                 'startColumnIndex': 0, 'endColumnIndex': 19}}}},
        # header navy
        {'repeatCell': {'range': {'sheetId': ids['Parc'], 'startRowIndex': 0, 'endRowIndex': 1,
                                  'startColumnIndex': 0, 'endColumnIndex': 19},
                        'cell': {'userEnteredFormat': {
                            'backgroundColor': NAVY,
                            'textFormat': {'bold': True, 'foregroundColor': BLANC, 'fontSize': 10},
                            'wrapStrategy': 'WRAP', 'verticalAlignment': 'MIDDLE'}},
                        'fields': 'userEnteredFormat.backgroundColor,userEnteredFormat.textFormat,userEnteredFormat.wrapStrategy,userEnteredFormat.verticalAlignment'}},
        # données wrap top
        {'repeatCell': {'range': {'sheetId': ids['Parc'], 'startRowIndex': 1, 'endRowIndex': n_b + 1,
                                  'startColumnIndex': 0, 'endColumnIndex': 19},
                        'cell': {'userEnteredFormat': {'wrapStrategy': 'WRAP',
                                                       'verticalAlignment': 'TOP'}},
                        'fields': 'userEnteredFormat.wrapStrategy,userEnteredFormat.verticalAlignment'}},
        # formats numeriques : prix + marche (G,H), encours (J), echeance (L), loyer (O), marge (R)
        {'repeatCell': {'range': {'sheetId': ids['Parc'], 'startRowIndex': 1, 'endRowIndex': n_b + 1,
                                  'startColumnIndex': 6, 'endColumnIndex': 8},
                        'cell': {'userEnteredFormat': {'numberFormat': {'type': 'NUMBER', 'pattern': '#,##0'}}},
                        'fields': 'userEnteredFormat.numberFormat'}},
        {'repeatCell': {'range': {'sheetId': ids['Parc'], 'startRowIndex': 1, 'endRowIndex': n_b + 1,
                                  'startColumnIndex': 9, 'endColumnIndex': 10},
                        'cell': {'userEnteredFormat': {'numberFormat': {'type': 'NUMBER', 'pattern': '#,##0'}}},
                        'fields': 'userEnteredFormat.numberFormat'}},
        {'repeatCell': {'range': {'sheetId': ids['Parc'], 'startRowIndex': 1, 'endRowIndex': n_b + 1,
                                  'startColumnIndex': 11, 'endColumnIndex': 12},
                        'cell': {'userEnteredFormat': {'numberFormat': {'type': 'NUMBER', 'pattern': '0.00'}}},
                        'fields': 'userEnteredFormat.numberFormat'}},
        {'repeatCell': {'range': {'sheetId': ids['Parc'], 'startRowIndex': 1, 'endRowIndex': n_b + 1,
                                  'startColumnIndex': 14, 'endColumnIndex': 15},
                        'cell': {'userEnteredFormat': {'numberFormat': {'type': 'NUMBER', 'pattern': '#,##0'}}},
                        'fields': 'userEnteredFormat.numberFormat'}},
        {'repeatCell': {'range': {'sheetId': ids['Parc'], 'startRowIndex': 1, 'endRowIndex': n_b + 1,
                                  'startColumnIndex': 17, 'endColumnIndex': 18},
                        'cell': {'userEnteredFormat': {'numberFormat': {'type': 'NUMBER', 'pattern': '#,##0'}}},
                        'fields': 'userEnteredFormat.numberFormat'}},
        # ligne consolidé en gras
        {'repeatCell': {'range': {'sheetId': ids['Parc'], 'startRowIndex': n_b + 2,
                                  'endRowIndex': n_b + 3, 'startColumnIndex': 0, 'endColumnIndex': 1},
                        'cell': {'userEnteredFormat': {'textFormat': {'bold': True}}},
                        'fields': 'userEnteredFormat.textFormat'}},
        # ---- Pipeline : freeze, filtre, header, wrap
        {'updateSheetProperties': {'properties': {'sheetId': ids['Pipeline'],
                                                  'gridProperties': {'frozenRowCount': 1}},
                                   'fields': 'gridProperties.frozenRowCount'}},
        {'setBasicFilter': {'filter': {'range': {'sheetId': ids['Pipeline'],
                                                 'startRowIndex': 0, 'endRowIndex': 1 + len(PIPELINE),
                                                 'startColumnIndex': 0, 'endColumnIndex': 8}}}},
        {'repeatCell': {'range': {'sheetId': ids['Pipeline'], 'startRowIndex': 0, 'endRowIndex': 1,
                                  'startColumnIndex': 0, 'endColumnIndex': 8},
                        'cell': {'userEnteredFormat': {
                            'backgroundColor': NAVY,
                            'textFormat': {'bold': True, 'foregroundColor': BLANC, 'fontSize': 10},
                            'wrapStrategy': 'WRAP', 'verticalAlignment': 'MIDDLE'}},
                        'fields': 'userEnteredFormat.backgroundColor,userEnteredFormat.textFormat,userEnteredFormat.wrapStrategy,userEnteredFormat.verticalAlignment'}},
        {'repeatCell': {'range': {'sheetId': ids['Pipeline'], 'startRowIndex': 1,
                                  'endRowIndex': 1 + len(PIPELINE),
                                  'startColumnIndex': 0, 'endColumnIndex': 8},
                        'cell': {'userEnteredFormat': {'wrapStrategy': 'WRAP',
                                                       'verticalAlignment': 'TOP'}},
                        'fields': 'userEnteredFormat.wrapStrategy,userEnteredFormat.verticalAlignment'}},
        # ---- Légende : wrap
        {'repeatCell': {'range': {'sheetId': ids['Légende'], 'startRowIndex': 0,
                                  'endRowIndex': 8, 'startColumnIndex': 0, 'endColumnIndex': 1},
                        'cell': {'userEnteredFormat': {'wrapStrategy': 'WRAP',
                                                       'verticalAlignment': 'TOP'}},
                        'fields': 'userEnteredFormat.wrapStrategy,userEnteredFormat.verticalAlignment'}},
    ]
    # largeurs (chars -> px ~ x7)
    def col_req(sheet_id, start, end, largeurs_px):
        out = []
        for i, w in enumerate(largeurs_px):
            out.append({'updateDimensionProperties': {
                'range': {'sheetId': sheet_id, 'dimension': 'COLUMNS',
                          'startIndex': start + i, 'endIndex': start + i + 1},
                'properties': {'pixelSize': w}, 'fields': 'pixelSize'}})
        return out
    reqs += col_req(ids['Parc'], 0, 19, [int(w * 7) for w in
                   [30, 34, 34, 22, 20, 26, 12, 14, 20, 12, 24, 11, 12, 30, 14, 24, 24, 12, 42]])
    reqs += col_req(ids['Pipeline'], 0, 8, [int(w * 7) for w in [32, 30, 30, 26, 44, 40, 28, 40]])
    reqs += col_req(ids['Légende'], 0, 1, [900])
    sheets.spreadsheets().batchUpdate(spreadsheetId=sid, body={'requests': reqs}).execute()

    meta = drv.files().get(fileId=sid, fields='id,name,mimeType,webViewLink').execute()
    print('OK:', meta['name'], '|', meta['webViewLink'])

if __name__ == '__main__':
    main()
