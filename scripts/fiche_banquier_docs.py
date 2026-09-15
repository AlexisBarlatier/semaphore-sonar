#!/usr/bin/env python
"""Générateur de fiches banquier Google Docs pour SCI Sémaphore Patrimoine.

Maquette « design 2026-09-09 » (calquée sur le rendu cible « dossier (2) ») :
  - En-tête 2 colonnes, filet sombre ; titre serif ; intro grise.
  - 5 cartes KPI (label gris / valeur noire / légende grise), filets fins.
  - Tableau d'exploitation (hypothèse prudente 52 € vs cible 60 €) : loyers
    noirs, charges et annuité rouge brique, RNE noir gras, trésorerie rouge
    ou vert gras selon le signe.
  - Jauge bicolore du point mort (rose pâle -> vert pâle, curseur noir).
  - Tableau d'impact sur la structure (4 colonnes, variation du patrimoine
    net en vert).
  - Garanties vs Risques en deux colonnes (intitulé gras + corps gris).
  - Frise calendrier : ligne grise, jalons bordeaux.

Palette extraite du rendu : encre #17181b, gris #5e6268, vert #2e6350,
rouge brique #a0392b, bordeaux #7a2b33, filets #c9c6be/#e3e1db, fonds de
jauge #e7cdc9 (rose) et #cfded6 (vert pâle).

Deux modes :
  --generer jr  : copie la maquette MAÎTRE (gérée à la main dans Google Docs),
                  remplace les {{PLACEHOLDERS}}, corbeille les versions
                  antérieures du même motif, exporte le PDF + copie locale.
  --init-modele  : GARDE-FOU — reconstruit la maquette depuis ce script.
                  Réservé à un `--init-modele --force` explicite : la maquette
                  maître est éditée à la main dans Docs et un rebuild écrase
                  ces retouches (incident du 10/09/2026). Ne l'utiliser que
                  pour repartir de zéro, jamais pour « rafraîchir ».

La maquette maître porte 65 placeholders (pas de bloc point mort depuis
l'édition Alexis du 09/09/2026 : le point mort est rappelé dans la légende
de la ligne « Trésorerie dégagée »).

Exécution : /home/alexis-barlatier/.hermes/hermes-agent/venv/bin/python
"""
import json
import re
import sys
import io

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

TOKEN = '/home/alexis-barlatier/.hermes/profiles/semaphore-sonar/google_token.json'
DOSSIER_BANQUE = '1A7WclBZTezWVgYkGyHwQ30eO9hOkA-zl'        # 03-Banque-et-financement
DOSSIER_FINANCEMENT_JR = '1b8pb9a1iobXPIkbvz-ZIr68jEDFXnehl'  # 02c/Financement
NOM_MODELE = '00-MODELE-Fiche-banquier-demande-financement'

# ---------- Palette « design 2026-09-09 » ----------
INK = '#17181b'       # texte principal
GRIS = '#5e6268'      # texte secondaire
VERT = '#2e6350'      # valeurs positives
ROUGE = '#a0392b'     # valeurs négatives (rouge brique)
BORDEAUX = '#7a2b33'  # date, jalons calendrier
LINE_F = '#c9c6be'    # filets marqués (cadres KPI, en-têtes)
LINE_T = '#e3e1db'    # filets fins internes
ROSE_PALE = '#e7cdc9' # jauge : zone déficitaire
VERT_PALE = '#cfded6' # jauge : zone autofinancée
SERIF = 'Georgia'


def rgb(h):
    h = h.lstrip('#')
    return {'red': int(h[0:2], 16)/255, 'green': int(h[2:4], 16)/255, 'blue': int(h[4:6], 16)/255}


def border(hexcol, w_pt):
    return {'color': {'color': {'rgbColor': rgb(hexcol)}},
            'width': {'magnitude': w_pt, 'unit': 'PT'}, 'dashStyle': 'SOLID'}


def NO_BORDER():
    return {'color': {'color': {'rgbColor': rgb(INK)}},
            'width': {'magnitude': 0, 'unit': 'PT'}, 'dashStyle': 'SOLID'}


# ---------- Contenu maquette (grilles des tables) ----------
HEADER_ROW = ['SCI Sémaphore Patrimoine\nGérants : Alexis Barlatier & Rémy Barlatier',
              'La Seyne-sur-Mer (83500)\n{{DATE_DOC}}']

# Table 1 : cartes KPI — chaque cellule : label (dur), valeur, légende
KPI_GRID = [['Capital demandé\n{{K_CAPITAL}}\n{{K_CAPITAL_D}}',
             'Durée et taux\n{{K_DUREE}}\n{{K_DUREE_D}}',
             'Mensualité\n{{K_MENSUALITE}}\n{{K_MENSUALITE_D}}',
             'Apport\n{{K_APPORT}}\n{{K_APPORT_D}}',
             'Coût de revient\n{{K_COUT}}\n{{K_COUT_D}}']]

# Table 2 : titre de section 1 (gauche) + sous-titre (droite)
SECTION1_ROW = ['{{TITRE_EXPLO}}', '{{SUB_EXPLO}}']

# Table 3 : exploitation — en-têtes sur 2 lignes, 5 lignes de données
EXPLO_GRID = [
    ['', '{{X_H1_PRUD}}\n{{X_H2_PRUD}}', '{{X_H1_CIBLE}}\n{{X_H2_CIBLE}}'],
    ['Loyers encaissés', '{{X_LOY_PRUD}}', '{{X_LOY_CIBLE}}'],
    ['Charges de copropriété et taxe foncière', '{{X_CHA_PRUD}}', '{{X_CHA_CIBLE}}'],
    ['Revenu net d’exploitation', '{{X_RNE_PRUD}}', '{{X_RNE_CIBLE}}'],
    ['Annuité de crédit, assurance incluse', '{{X_ANN_PRUD}}', '{{X_ANN_CIBLE}}'],
    ['Trésorerie dégagée par le bloc', '{{X_TRESO_PRUD}}\n{{X_TRESO_D_PRUD}}',
     '{{X_TRESO_CIBLE}}\n{{X_TRESO_D_CIBLE}}'],
]

# Table 4 : jauge du point mort — r0 barre bicolore, r1 bornes 54/65
PM_BAR_ROW = [['\u00a0', '\u00a0'], ['54 €', '65 €']]

# Table 5 : titre de section 2 + sous-titre
SECTION2_ROW = ['{{TITRE_BILAN}}', '{{SUB_BILAN}}']

# Table 6 : impact structure — Indicateur / Aujourd'hui / Après / Variation
STRUCT_GRID = [
    ['Indicateur', 'Aujourd’hui', 'Après l’opération', 'Variation'],
    ['Patrimoine brut, valeur vénale estimée', '{{S_BRUT_AV}}', '{{S_BRUT_AP}}', '{{S_BRUT_VAR}}'],
    ['Encours de crédit', '{{S_ENC_AV}}', '{{S_ENC_AP}}', '{{S_ENC_VAR}}'],
    ['Patrimoine net', '{{S_NET_AV}}', '{{S_NET_AP}}', '{{S_NET_VAR}}'],
    ['Trésorerie mensuelle dégagée par le parc', '{{S_CF_AV}}', '{{S_CF_AP}}', '{{S_CF_VAR}}'],
]

# Table 7 : garanties / risques — intitulé + ' — ' + corps
GAR_GRID = [
    ['Garanties proposées', 'Risques identifiés et parades'],
    ['{{G_L1_H}} — {{G_L1_D}}', '{{R_L1_H}} — {{R_L1_D}}'],
    ['{{G_L2_H}} — {{G_L2_D}}', '{{R_L2_H}} — {{R_L2_D}}'],
    ['{{G_L3_H}} — {{G_L3_D}}', '{{R_L3_H}} — {{R_L3_D}}'],
]

# Table 8 : calendrier — ● / mois / texte
CAL_ROW = [['\u25cf\n{{C1_MOIS}}\n{{C1_TXT}}', '\u25cf\n{{C2_MOIS}}\n{{C2_TXT}}',
            '\u25cf\n{{C3_MOIS}}\n{{C3_TXT}}', '\u25cf\n{{C4_MOIS}}\n{{C4_TXT}}']]

# Largeurs de colonnes par table (index de construction), total ~515 pt
COLW = {
    0: [335.0, 180.0],        # header
    1: [103.0] * 5,           # KPI
    2: [360.0, 155.0],        # titre de section 1
    3: [205.0, 155.0, 155.0], # exploitation
    4: [77.0, 438.0],         # jauge point mort — curseur à 15 % (55,70 € sur 54-65)
    5: [360.0, 155.0],        # titre de section 2
    6: [185.0, 110.0, 110.0, 110.0],  # structure
    7: [285.0, 230.0],        # garanties / risques
    8: [128.75] * 4,          # calendrier
}


def docs_req(docs, doc_id, requests, label=''):
    docs.documents().batchUpdate(documentId=doc_id,
        body={'requests': requests}).execute()
    print(f'  [batch {label}] {len(requests)} requests OK')


def get_body_end(docs, doc_id):
    d = docs.documents().get(documentId=doc_id).execute()
    return d['body']['content'][-1].get('endIndex', 0)


def find_last_table(d):
    content = d['body']['content']
    for el in reversed(content):
        if 'table' in el:
            return el['table']
    return None


def fill_cell_text(docs, doc_id, tbl, grid):
    """Insère le texte multi-paragraphe de chaque cellule."""
    reqs = []
    for r, row in enumerate(tbl['tableRows']):
        for c, cell in enumerate(row['tableCells']):
            content = grid[r][c]
            if not content:
                continue
            p = cell['content'][0]['paragraph']
            elems = p.get('elements') or []
            start = elems[0].get('startIndex', p.get('startIndex', 0)) \
                if elems else p.get('startIndex', cell.get('startIndex', 0))
            reqs.append({'insertText': {'text': content,
                                        'location': {'segmentId': '', 'index': start}}})
    if reqs:
        docs_req(docs, doc_id, list(reversed(reqs)), 'fill table')


def mk_modele():
    creds = Credentials.from_authorized_user_info(json.load(open(TOKEN)))
    docs = build('docs', 'v1', credentials=creds)
    drv = build('drive', 'v3', credentials=creds)

    q = drv.files().list(q=f"name='{NOM_MODELE}' and trashed=false",
                         fields='files(id)').execute().get('files', [])
    for f in q:
        drv.files().update(fileId=f['id'], body={'trashed': True}).execute()
        print('Ancienne maquette corbeillée:', f['id'])

    doc = docs.documents().create(body={'title': NOM_MODELE}).execute()
    doc_id = doc['documentId']
    print('Doc créé:', doc_id)

    docs_req(docs, doc_id, [{'updateDocumentStyle': {
        'documentStyle': {
            'pageSize': {'width': {'magnitude': 595.3, 'unit': 'PT'},
                         'height': {'magnitude': 841.9, 'unit': 'PT'}},
            'marginTop': {'magnitude': 18, 'unit': 'PT'},
            'marginBottom': {'magnitude': 16, 'unit': 'PT'},
            'marginLeft': {'magnitude': 40, 'unit': 'PT'},
            'marginRight': {'magnitude': 40, 'unit': 'PT'}},
        'fields': 'pageSize,marginTop,marginBottom,marginLeft,marginRight'}}], 'docstyle')

    # --- construction séquentielle : tables et textes ---
    # Ligne de texte racine puis table ; on repère chaque table à l'insertion.
    tables_order = []  # libellés des tables insérées, dans l'ordre

    def insert_text(txt):
        docs_req(docs, doc_id, [{'insertText': {
            'text': txt + '\n', 'endOfSegmentLocation': {'segmentId': ''}}}], 'text')

    def insert_table(rows, cols, grid):
        # paragraphe d'air avant la table (sinon deux tables se collent)
        insert_text(' ')
        end = get_body_end(docs, doc_id) - 1
        docs_req(docs, doc_id, [{'insertTable': {
            'rows': rows, 'columns': cols,
            'location': {'segmentId': '', 'index': end}}}], f'table{rows}x{cols}')
        d = docs.documents().get(documentId=doc_id).execute()
        tbl = find_last_table(d)
        fill_cell_text(docs, doc_id, tbl, grid)
        return tbl

    # 0 header
    insert_table(1, 2, [HEADER_ROW])
    tables_order.append('header')
    # 1 titre + intro
    insert_text('{{TITRE_H1}}')
    insert_text('{{INTRO}}')
    # 2 KPI
    insert_table(1, 5, KPI_GRID)
    tables_order.append('kpi')
    # 3 section 1 + tableau exploitation
    insert_table(1, 2, [SECTION1_ROW])
    tables_order.append('section1')
    insert_table(6, 3, EXPLO_GRID)
    tables_order.append('explo')
    # 4 point mort : titre, jauge, légende, note
    insert_text('{{PM_TITRE}}')
    insert_table(2, 2, PM_BAR_ROW)
    tables_order.append('pmbar')
    insert_text('{{PM_LEG}}')
    insert_text('{{PM_NOTE_H}} {{PM_NOTE_D}}')
    # 5 section 2 + tableau structure
    insert_table(1, 2, [SECTION2_ROW])
    tables_order.append('section2')
    insert_table(5, 4, STRUCT_GRID)
    tables_order.append('struct')
    # 6 garanties / risques
    insert_table(4, 2, GAR_GRID)
    tables_order.append('gar')
    # 7 calendrier
    insert_table(1, 4, CAL_ROW)
    tables_order.append('cal')

    # purge des paragraphes racine vides parasites
    d = docs.documents().get(documentId=doc_id).execute()
    content = d['body']['content']
    purge = []
    for i, el in enumerate(content):
        if 'paragraph' not in el:
            continue
        s_, e_ = el.get('startIndex', 0), el.get('endIndex', 0)
        is_void = (e_ - s_ <= 1)
        if not is_void or i == len(content) - 1:
            continue
        prev_is_table = i > 0 and 'table' in content[i - 1]
        next_is_table = i < len(content) - 1 and 'table' in content[i + 1]
        if i == 0 or (prev_is_table and not next_is_table):
            purge.append({'deleteContentRange': {
                'range': {'segmentId': '', 'startIndex': s_, 'endIndex': e_}}})
    if purge:
        docs_req(docs, doc_id, purge, 'purge vides')

    # ============ STYLING ============
    d = docs.documents().get(documentId=doc_id).execute()
    reqs = []

    def style_text(s, e, bold=None, size=None, color=None, italic=None,
                   family=None):
        ts = {}
        if bold is not None: ts['bold'] = bold
        if size: ts['fontSize'] = {'magnitude': size, 'unit': 'PT'}
        if color: ts['foregroundColor'] = {'color': {'rgbColor': rgb(color)}}
        if italic is not None: ts['italic'] = italic
        if family:
            ts['weightedFontFamily'] = {'fontFamily': family, 'weight': 700 if bold else 400}
        if ts and e > s:
            reqs.append({'updateTextStyle': {
                'range': {'segmentId': '', 'startIndex': s, 'endIndex': e},
                'textStyle': ts, 'fields': ','.join(ts.keys())}})

    def style_par(s, e, align=None, before=None, after=None, line=None, shading=None):
        ps = {}
        if align: ps['alignment'] = align
        if before is not None: ps['spaceAbove'] = {'magnitude': before, 'unit': 'PT'}
        if after is not None: ps['spaceBelow'] = {'magnitude': after, 'unit': 'PT'}
        if line: ps['lineSpacing'] = line
        if shading:
            ps['shading'] = {'backgroundColor': {'color': {'rgbColor': rgb(shading)}}}
        fields = [k for k in ('alignment', 'spaceAbove', 'spaceBelow', 'lineSpacing',
                              'shading') if k in ps]
        if fields and e > s:
            reqs.append({'updateParagraphStyle': {
                'range': {'segmentId': '', 'startIndex': s, 'endIndex': e},
                'paragraphStyle': ps, 'fields': ','.join(fields)}})

    def cell_style(tbl_start, row, col, borders=None, bg=None, pad=None):
        def loc():
            return {'tableRange': {'rowSpan': 1, 'columnSpan': 1,
                                   'tableCellLocation': {
                                       'tableStartLocation': {'segmentId': '', 'index': tbl_start},
                                       'rowIndex': row, 'columnIndex': col}}}
        visibles, nulles = {}, {}
        if borders:
            for side, b in zip(('borderTop', 'borderBottom', 'borderLeft', 'borderRight'),
                               borders):
                w = (b.get('width') or {}).get('magnitude', 0)
                (visibles if w > 0 else nulles)[side] = b
        if bg:
            visibles['backgroundColor'] = {'color': {'rgbColor': rgb(bg)}}
        if pad is not None:
            visibles['paddingTop'] = visibles['paddingBottom'] = {'magnitude': pad, 'unit': 'PT'}
        if visibles:
            reqs.append({'updateTableCellStyle': {
                'tableCellStyle': visibles,
                'fields': ','.join(visibles.keys()),
                **loc()}})
        if nulles:
            reqs.append({'updateTableCellStyle': {
                'tableCellStyle': nulles,
                'fields': ','.join(nulles.keys()),
                **loc()}})

    # --- textes racine ---
    content = d['body']['content']
    for el in content:
        if 'paragraph' not in el:
            continue
        p = el['paragraph']
        s, e = el.get('startIndex', 0), el.get('endIndex', 0)
        txt = ''.join(run.get('textRun', {}).get('content', '')
                      for run in p.get('elements', []))
        ptxt = txt.rstrip('\n').replace('\t', '')
        if ptxt == '':
            continue
        if ptxt == '{{TITRE_H1}}':
            style_text(s, e, size=16, color=INK, family=SERIF)
            style_par(s, e, before=10, after=3, line=108)
        elif ptxt == '{{INTRO}}':
            style_text(s, e, size=8, color=GRIS)
            style_par(s, e, after=6, line=115)
        elif ptxt == '{{PM_TITRE}}':
            style_text(s, e, bold=True, size=9.5, color=INK)
            style_par(s, e, before=8, after=4)
        elif ptxt == '{{PM_LEG}}':
            style_text(s, e, size=7.2, color=GRIS)
            style_par(s, e, before=3, after=8, line=108)
        elif ptxt.startswith('{{PM_NOTE_H}}'):
            # premier segment en gras, corps en gris
            m = re.match(r'\{\{[A-Z0-9_]+\}\}', ptxt)
            if m:
                h_len = len(m.group(0))
                style_text(s, s + h_len, bold=True, size=7.6, color=INK)
                style_text(s + h_len + 1, e, size=7.6, color=GRIS)
            style_par(s, e, after=2, line=110)
        else:
            style_text(s, e, size=7.6, color=GRIS)
            style_par(s, e, after=2, line=110)

    # --- tables, identifiées par ordre ---
    content = d['body']['content']
    ti = -1
    for el in content:
        if 'table' not in el:
            continue
        tbl = el['table']
        ti += 1
        role = tables_order[ti]
        nrows = len(tbl['tableRows'])
        ncols = len(tbl['tableRows'][0]['tableCells'])
        tbl_start = el.get('startIndex', 0)

        def paras_of(cell):
            out = []
            for p in cell['content']:
                if 'paragraph' not in p:
                    continue
                ps, pe = p.get('startIndex', 0), p.get('endIndex', 0)
                tcell = ''.join(run.get('textRun', {}).get('content', '')
                                for run in p['paragraph'].get('elements', []))
                out.append((ps, pe, tcell.rstrip('\n')))
            return out

        if role == 'header':
            # nom SCI serif / gérants gris à gauche ; ville / date bordeaux à droite
            for c, cell in enumerate(tbl['tableRows'][0]['tableCells']):
                ps = paras_of(cell)
                for idx, (a, b, tcell) in enumerate(ps):
                    if c == 0:
                        if idx == 0:
                            style_text(a, b, size=12.5, color=INK, family=SERIF)
                            style_par(a, b, align='START', after=1)
                        else:
                            style_text(a, b, size=7.5, color=GRIS)
                            style_par(a, b, align='START')
                    else:
                        if tcell.startswith('La Seyne'):
                            style_text(a, b, size=7.5, color=GRIS)
                            style_par(a, b, align='END', after=1)
                        elif tcell.startswith('{{DATE_DOC}}'):
                            style_text(a, b, bold=True, size=7.5, color=BORDEAUX)
                            style_par(a, b, align='END')
                cell_style(tbl_start, 0, c,
                           borders=(NO_BORDER(), border(INK, 1.0),
                                    NO_BORDER(), NO_BORDER()), pad=1)
        elif role == 'kpi':
            for c, cell in enumerate(tbl['tableRows'][0]['tableCells']):
                ps = paras_of(cell)
                for idx, (a, b, tcell) in enumerate(ps):
                    style_par(a, b, align='CENTER', line=100)
                    if idx == 0:
                        style_text(a, b, size=6.6, color=GRIS)
                    elif idx == 1:
                        style_text(a, b, bold=True, size=13, color=INK)
                    else:
                        style_text(a, b, size=6.2, color=GRIS)
                # filets verticaux fins entre cartes, lignes haute/basse continues
                # (bordure de cellule : top, bottom, left, right)
                cell_style(tbl_start, 0, c,
                           borders=(border(LINE_F, 0.75),      # top
                                    border(LINE_F, 0.75),      # bottom
                                    border(LINE_T, 0.5) if c > 0 else NO_BORDER(),
                                    border(LINE_T, 0.5) if c < ncols - 1 else NO_BORDER()),
                           pad=3)
        elif role == 'section1' or role == 'section2':
            for c, cell in enumerate(tbl['tableRows'][0]['tableCells']):
                ps = paras_of(cell)
                for a, b, tcell in ps:
                    if c == 0:
                        style_text(a, b, bold=True, size=10.5, color=INK, family=SERIF)
                        style_par(a, b, align='START', before=6, after=1)
                    else:
                        style_text(a, b, size=7.2, color=GRIS)
                        style_par(a, b, align='END', before=6, after=1)
                cell_style(tbl_start, 0, c, borders=(NO_BORDER(),)*4, pad=0)
        elif role == 'explo':
            for r in range(nrows):
                for c in range(ncols):
                    cell = tbl['tableRows'][r]['tableCells'][c]
                    ps = paras_of(cell)
                    if r == 0:
                        # en-têtes de colonnes : titre gris, valeur noire grasse
                        for idx, (a, b, tcell) in enumerate(ps):
                            style_par(a, b, align='CENTER', line=100)
                            if tcell == '':
                                continue
                            if idx == 0:
                                style_text(a, b, size=6.4, color=GRIS)
                            else:
                                style_text(a, b, bold=True, size=8.5, color=INK)
                        cell_style(tbl_start, r, c,
                                   borders=(NO_BORDER(), border(LINE_F, 0.75),
                                            NO_BORDER(), NO_BORDER()), pad=2)
                        continue
                    # lignes de données
                    for a, b, tcell in ps:
                        if tcell == '':
                            continue
                        if c == 0:
                            style_text(a, b, size=7.4, color=GRIS)
                            style_par(a, b, align='START', line=100)
                        else:
                            # couleur sémantique selon la ligne
                            if r == 1:
                                col, bold = INK, False
                            elif r == 2 or r == 4:
                                col, bold = ROUGE, False
                            elif r == 3:
                                col, bold = INK, True
                            else:  # trésorerie
                                col = VERT if 'CIBLE' in tcell else ROUGE
                                bold = True
                            # la 2e ligne (mention soit -x €) reste grise
                            is_detail = tcell.startswith('{{X_TRESO_D_')
                            if is_detail:
                                col, bold = GRIS, False
                            style_text(a, b, bold=bold, size=7.8, color=col)
                            style_par(a, b, align='CENTER', line=100)
                    if r == 5:
                        cell_style(tbl_start, r, c, pad=1)
                    else:
                        # filet fin entre lignes ; trait sombre avant la trésorerie
                        bd = border(LINE_T, 0.5) if r < 4 else border(INK, 1.2)
                        cell_style(tbl_start, r, c,
                                   borders=(NO_BORDER(), bd, NO_BORDER(), NO_BORDER()), pad=1)
        elif role == 'pmbar':
            # hauteur minimale de la rangée-barre (jauge visible ~10 pt)
            reqs.append({'updateTableRowStyle': {
                'tableStartLocation': {'segmentId': '', 'index': tbl_start},
                'rowIndices': [0],
                'tableRowStyle': {
                    'minRowHeight': {'magnitude': 10, 'unit': 'PT'}},
                'fields': 'minRowHeight'}})
            for r in range(nrows):
                for c in range(ncols):
                    cell = tbl['tableRows'][r]['tableCells'][c]
                    ps = paras_of(cell)
                    for a, b, tcell in ps:
                        if r == 0:
                            style_text(a, b, size=7, color=INK)
                            style_par(a, b, line=60)
                            bg = ROSE_PALE if c == 0 else VERT_PALE
                            # curseur noir = bordure épaisse à la jonction des deux
                            # cellules : portée par la droite de la zone rose ET la
                            # gauche de la zone verte (sinon Docs l'annule)
                            borders = [NO_BORDER(), NO_BORDER(), NO_BORDER(), NO_BORDER()]
                            if c == 0:
                                borders[3] = border(INK, 1.6)
                            else:
                                borders[2] = border(INK, 1.6)
                            cell_style(tbl_start, r, c, borders=borders, bg=bg, pad=0)
                        else:
                            style_text(a, b, size=6.2, color=GRIS)
                            style_par(a, b, align='START' if c == 0 else 'END',
                                      before=2, line=100)
                            cell_style(tbl_start, r, c, borders=(NO_BORDER(),)*4, pad=0)
        elif role == 'struct':
            for r in range(nrows):
                for c in range(ncols):
                    cell = tbl['tableRows'][r]['tableCells'][c]
                    ps = paras_of(cell)
                    for a, b, tcell in ps:
                        if r == 0:
                            col = VERT if tcell == 'Variation' else GRIS
                            style_text(a, b, bold=True, size=7, color=col)
                            style_par(a, b, align='START' if c == 0 else 'CENTER')
                        elif c == 0:
                            bold = (r == 3)
                            style_text(a, b, bold=bold, size=7.4, color=INK if r == 3 else GRIS)
                            style_par(a, b, align='START', line=100)
                        elif c == 3:
                            if tcell.startswith('{{S_CF_VAR'):
                                style_text(a, b, size=7.2, color=GRIS)
                            elif r == 3:
                                style_text(a, b, bold=True, size=7.6, color=VERT)
                            else:
                                style_text(a, b, bold=True, size=7.6, color=INK)
                            style_par(a, b, align='CENTER', line=100)
                        else:
                            bold = (r == 3)
                            style_text(a, b, bold=bold, size=7.6, color=INK)
                            style_par(a, b, align='CENTER', line=100)
                    if r == 0:
                        cell_style(tbl_start, r, c,
                                   borders=(NO_BORDER(), border(LINE_F, 0.75),
                                            NO_BORDER(), NO_BORDER()), pad=2)
                    elif r == 4:
                        cell_style(tbl_start, r, c,
                                   borders=(NO_BORDER(), border(LINE_F, 0.75),
                                            NO_BORDER(), NO_BORDER()), pad=1)
                    else:
                        cell_style(tbl_start, r, c,
                                   borders=(NO_BORDER(), border(LINE_T, 0.5),
                                            NO_BORDER(), NO_BORDER()), pad=1)
        elif role == 'gar':
            for r in range(nrows):
                for c in range(ncols):
                    cell = tbl['tableRows'][r]['tableCells'][c]
                    ps = paras_of(cell)
                    for a, b, tcell in ps:
                        if r == 0:
                            style_text(a, b, size=11, color=INK, family=SERIF)
                            style_par(a, b, align='START', after=2, before=8)
                        else:
                            # intitulé gras puis ' — ' puis corps gris
                            m1 = re.search(r'\{\{[A-Z0-9_]+\}\}', tcell)
                            if not m1:
                                continue
                            rest = tcell[m1.end():]
                            m2 = re.search(r'\{\{[A-Z0-9_]+\}\}', rest)
                            if not m2:
                                continue
                            h_end = a + m1.end()
                            d_start = a + m1.end() + m2.start()
                            style_text(a, h_end, bold=True, size=7.4, color=INK)
                            style_text(d_start, b, size=7.3, color=GRIS)
                            style_par(a, b, align='START', after=4, line=110)
                    if r == 0:
                        cell_style(tbl_start, r, c,
                                   borders=(NO_BORDER(), border(LINE_F, 0.75),
                                            NO_BORDER(), NO_BORDER()), pad=1)
                    else:
                        cell_style(tbl_start, r, c, borders=(NO_BORDER(),)*4, pad=1)
        elif role == 'cal':
            for c, cell in enumerate(tbl['tableRows'][0]['tableCells']):
                ps = paras_of(cell)
                for idx, (a, b, tcell) in enumerate(ps):
                    if idx == 0:
                        style_text(a, b, size=7, color=BORDEAUX)
                        style_par(a, b, align='CENTER', after=0)
                    elif tcell.startswith('{{C') and '_MOIS' in tcell:
                        style_text(a, b, bold=True, size=8.4, color=BORDEAUX)
                        style_par(a, b, align='CENTER', after=1)
                    else:
                        style_text(a, b, size=6.8, color=GRIS)
                        style_par(a, b, align='CENTER', line=105)
                cell_style(tbl_start, 0, c,
                           borders=(border(LINE_F, 0.75), NO_BORDER(),
                                    NO_BORDER(), NO_BORDER()), pad=3)

    docs_req(docs, doc_id, reqs, 'styling final')

    # aplatir les paragraphes racine vides résiduels
    d = docs.documents().get(documentId=doc_id).execute()
    flat = []
    for el in d['body']['content']:
        if 'paragraph' not in el:
            continue
        s_, e_ = el.get('startIndex', 0), el.get('endIndex', 0)
        if e_ - s_ <= 1:
            flat.append({'updateTextStyle': {
                'range': {'segmentId': '', 'startIndex': s_, 'endIndex': e_},
                'textStyle': {'fontSize': {'magnitude': 2, 'unit': 'PT'}},
                'fields': 'fontSize'}})
    if flat:
        docs_req(docs, doc_id, flat, 'aplatir vides')

    # largeurs de colonnes (par ordre d'apparition des tables)
    d = docs.documents().get(documentId=doc_id).execute()
    width_reqs = []
    ti = -1
    for el in d['body']['content']:
        if 'table' not in el:
            continue
        ti += 1
        spec = COLW.get(ti)
        if not spec:
            continue
        for ci, w in enumerate(spec):
            width_reqs.append({'updateTableColumnProperties': {
                'tableStartLocation': {'segmentId': '', 'index': el.get('startIndex', 0)},
                'columnIndices': [ci],
                'tableColumnProperties': {
                    'widthType': 'FIXED_WIDTH',
                    'width': {'magnitude': w, 'unit': 'PT'}},
                'fields': 'width,widthType'}})
    if width_reqs:
        docs_req(docs, doc_id, width_reqs, 'colwidths')

    root = drv.files().get(fileId='root', fields='id').execute()['id']
    drv.files().update(fileId=doc_id, addParents=DOSSIER_BANQUE,
                       removeParents=root, fields='id,parents').execute()
    print('Maquette OK:', doc_id,
          'https://docs.google.com/document/d/' + doc_id)
    return doc_id


# ---------- Données Jean Rostand (MAJ 2026-09-10 : offre 6 k€/place, loyers 54-65, QPV) ----------
DATA_JR = {
    '{{DATE_DOC}}': '10 septembre 2026',
    '{{TITRE_H1}}': 'Demande de financement de 59 400 € pour l’acquisition de 11 places de parking neuves à 6 000 € l’unité, que le programme commercialise à 8 000 €',
    '{{INTRO}}': 'Résidence « Jean Rostand », quartier Saint-Jean (QPV Berthe), La Seyne-sur-Mer (83500) — VEFA Constructa Promotion, livraison au 2e trimestre 2027. L’opération s’équilibre sur ses loyers et ajoute 23 100 € de fonds propres à la SCI à la livraison.',
    '{{K_CAPITAL}}': '59 400 €',
    '{{K_CAPITAL_D}}': '90 % du prix d’acquisition',
    '{{K_DUREE}}': '15 ans',
    '{{K_DUREE_D}}': '3,70 % fixe',
    '{{K_MENSUALITE}}': '447 €',
    '{{K_MENSUALITE_D}}': 'assurance 0,34 % incluse',
    '{{K_APPORT}}': '8 580 €',
    '{{K_APPORT_D}}': 'fonds propres de la SCI',
    '{{K_COUT}}': '67 980 €',
    '{{K_COUT_D}}': '6 180 € par place, frais inclus',
    '{{TITRE_EXPLO}}': 'Ce que l’opération produit chaque année',
    '{{SUB_EXPLO}}': '11 places louées, en année pleine',
    '{{X_H1_PRUD}}': 'Hypothèse basse',
    '{{X_H2_PRUD}}': '54 €/mois/place',
    '{{X_H1_CIBLE}}': 'Hypothèse haute',
    '{{X_H2_CIBLE}}': '65 €/mois/place',
    '{{X_LOY_PRUD}}': '7 128 €',
    '{{X_LOY_CIBLE}}': '8 580 €',
    '{{X_CHA_PRUD}}': '− 1 980 €',
    '{{X_CHA_CIBLE}}': '− 1 980 €',
    '{{X_RNE_PRUD}}': '5 148 €',
    '{{X_RNE_CIBLE}}': '6 600 €',
    '{{X_ANN_PRUD}}': '− 5 368 €',
    '{{X_ANN_CIBLE}}': '− 5 368 €',
    '{{X_TRESO_PRUD}}': '− 216 €',
    '{{X_TRESO_D_PRUD}}': 'soit − 18 €/mois — point mort 55,70 €',
    '{{X_TRESO_CIBLE}}': '+ 1 236 €',
    '{{X_TRESO_D_CIBLE}}': 'soit + 103 €/mois',
    '{{TITRE_BILAN}}': 'Effet sur le bilan de la SCI',
    '{{SUB_BILAN}}': '15 places louées aujourd’hui, 26 après l’opération',
    '{{S_BRUT_AV}}': '144 000 €',
    '{{S_BRUT_AP}}': '226 500 €',
    '{{S_BRUT_VAR}}': '+ 82 500 €',
    '{{S_ENC_AV}}': '70 000 €',
    '{{S_ENC_AP}}': '129 400 €',
    '{{S_ENC_VAR}}': '+ 59 400 €',
    '{{S_NET_AV}}': '74 000 €',
    '{{S_NET_AP}}': '97 100 €',
    '{{S_NET_VAR}}': '+ 23 100 €',
    '{{S_CF_AV}}': '~ 700 €',
    '{{S_CF_AP}}': '680 à 800 €',
    '{{S_CF_VAR}}': 'selon loyer',
    '{{G_L1_H}}': 'Hypothèque de premier rang sur les 11 places de parking',
    '{{G_L1_D}}': 'prise à l’acte notarié d’acquisition, sans attendre la livraison : l’immobilier est affecté en garantie.',
    '{{G_L2_H}}': 'Couverture de 1,3 à 1,5× le capital prêté',
    '{{G_L2_D}}': 'bloc estimé entre 77 000 et 88 000 € pour 59 400 € empruntés.',
    '{{G_L3_H}}': 'Actif fractionnable',
    '{{G_L3_D}}': '11 lots distincts, cessibles à l’unité sans affecter l’exploitation du reste.',
    '{{R_L1_H}}': 'Vacance',
    '{{R_L1_D}}': 'au loyer bas de la fourchette (54 €), le bloc couvre 96 % de son annuité sur ses seuls loyers ; une place vide coûte 54 €/mois, absorbée par le surplus du parc.',
    '{{R_L2_H}}': 'Places invendues du programme',
    '{{R_L2_D}}': 'le promoteur commercialise encore à 8 000 € l’unité. Notre décote de 25 % est acquise à l’achat.',
    '{{R_L3_H}}': 'Intérêts intercalaires',
    '{{R_L3_D}}': 'payés par la trésorerie de la SCI pendant le chantier (environ 500 à 1 650 €), sans appel aux fonds propres des associés ni engagement en compte courant d’associé.',
    '{{C1_MOIS}}': 'Septembre 2026',
    '{{C1_TXT}}': 'Offre d’achat à 6 000 €/place',
    '{{C2_MOIS}}': 'Octobre 2026',
    '{{C2_TXT}}': 'Compromis sous condition de prêt',
    '{{C3_MOIS}}': 'T1 2027',
    '{{C3_TXT}}': 'Acte notarié, hypothèque sur les lots',
    '{{C4_MOIS}}': 'T2-T3 2027',
    '{{C4_TXT}}': 'Livraison, mise en location, première mensualité',
}


def generer(nom_projet, data, nom_fichier, dossier_dest, pdf_local=None):
    creds = Credentials.from_authorized_user_info(json.load(open(TOKEN)))
    docs = build('docs', 'v1', credentials=creds)
    drv = build('drive', 'v3', credentials=creds)

    q = drv.files().list(q=f"name='{NOM_MODELE}' and trashed=false",
                         fields='files(id,name)').execute().get('files', [])
    if not q:
        raise SystemExit('Maquette introuvable — lancer --init-modele d’abord.')
    modele_id = q[0]['id']
    print('Maquette:', modele_id)

    old = drv.files().list(q=f"name='{nom_fichier}' and '{dossier_dest}' in parents and trashed=false",
                           fields='files(id)').execute().get('files', [])
    old += drv.files().list(q=f"name='{nom_fichier}.pdf' and '{dossier_dest}' in parents and trashed=false",
                            fields='files(id)').execute().get('files', [])
    for f in old:
        drv.files().update(fileId=f['id'], body={'trashed': True}).execute()
    if old:
        print(f'  {len(old)} ancienne(s) version(s) corbeillée(s)')
    cp = drv.files().copy(fileId=modele_id, body={'name': nom_fichier,
                                                  'parents': [dossier_dest]},
                          fields='id,name,webViewLink').execute()
    fiche_id = cp['id']
    print('Copie créée:', fiche_id, cp['webViewLink'])

    reqs = [{'replaceAllText': {'containsText': {'text': k, 'matchCase': True},
                                'replaceText': v}} for k, v in data.items()]
    docs.documents().batchUpdate(documentId=fiche_id, body={'requests': reqs}).execute()
    print(f'  {len(reqs)} placeholders remplacés')

    d = docs.documents().get(documentId=fiche_id).execute()
    def walk_text(elems):
        out = []
        for el in elems:
            if 'paragraph' in el:
                for run in el['paragraph'].get('elements', []):
                    out.append(run.get('textRun', {}).get('content', ''))
            elif 'table' in el:
                for row in el['table']['tableRows']:
                    for cell in row['tableCells']:
                        out.append(walk_text(cell.get('content', [])))
        return ''.join(out)
    texte = walk_text(d['body']['content'])
    residus = re.findall(r'\{\{[A-Z0-9_]+\}\}', texte)
    if residus:
        print('ATTENTION placeholders résiduels:', sorted(set(residus)))
    else:
        print('  Aucun placeholder résiduel.')

    pdf_name = nom_fichier + '.pdf'
    buf = io.BytesIO()
    dl = MediaIoBaseDownload(buf, drv.files().export_media(
        fileId=fiche_id, mimeType='application/pdf'))
    done = False
    while not done:
        _, done = dl.next_chunk()
    buf.seek(0)
    pdf_bytes = buf.read()
    drv.files().create(body={'name': pdf_name, 'parents': [dossier_dest]},
                       media_body=MediaIoBaseUpload(io.BytesIO(pdf_bytes),
                       mimetype='application/pdf'), fields='id,name').execute()
    print('PDF Drive:', pdf_name)
    if pdf_local:
        with open(pdf_local, 'wb') as f:
            f.write(pdf_bytes)
        print('PDF local:', pdf_local)
        n = len(re.findall(rb'/Type\s*/Page[^s]', pdf_bytes))
        print('Pages PDF (approx.):', max(n, 1))
    return fiche_id, cp['webViewLink']


def corbeiller(drv, dossier, motif):
    """Corbeille les fichiers du dossier dont le nom contient `motif`."""
    q = (f"name contains '{motif}' and '{dossier}' in parents and trashed=false")
    for f in drv.files().list(q=q, fields='files(id,name)').execute().get('files', []):
        drv.files().update(fileId=f['id'], body={'trashed': True}).execute()
        print('  ancienne version corbeillée :', f['name'], f['id'])


if __name__ == '__main__':
    if '--init-modele' in sys.argv:
        if '--force' not in sys.argv:
            raise SystemExit(
                "STOP — la maquette maître est éditée à la main dans Google Docs.\n"
                "Un rebuild depuis ce script écrase ces retouches (incident 10/09/2026).\n"
                "Pour générer une fiche : --generer jr\n"
                "Pour repartir de zéro malgré tout : --init-modele --force")
        mk_modele()
    elif '--generer' in sys.argv:
        i = sys.argv.index('--generer')
        projet = sys.argv[i + 1]
        if projet == 'jr':
            import json as _json
            _creds = Credentials.from_authorized_user_info(_json.load(open(TOKEN)))
            corbeiller(build('drive', 'v3', credentials=_creds),
                       DOSSIER_FINANCEMENT_JR, 'Fiche-banquier-11-parkings-Jean-Rostand')
            generer('jr', DATA_JR,
                    '2026-09-10_Fiche-banquier-11-parkings-Jean-Rostand',
                    DOSSIER_FINANCEMENT_JR,
                    pdf_local='/home/alexis-barlatier/Documents/Semaphore-sonar/analyses/2026-09-03-11-parkings-jean-rostand-la-seyne/documents/fiche-banquier-11-parkings-Jean-Rostand.pdf')
    else:
        print(__doc__)
