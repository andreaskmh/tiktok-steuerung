#!/usr/bin/env python3
"""Alle Exporte (exporte/<konto>.xlsx) → bestellungen.json (eine Zeile pro Bestellposition).
  python3 werkzeuge/analyse/baue.py"""
import sys, json, glob, os, datetime as D
HIER = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HIER)
import xl

import re
f = lambda s: round(float(re.sub(r'[\s.\u00a0\u202f€]', '', s).replace(',', '.')), 2) if s and s.strip() not in ('/', '-', '') else 0.0
def d(s):
    return D.datetime.strptime(s, '%d/%m/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M') if s and s != '/' else None
STATUS = {'Bezahlt': 'ausgezahlt', 'Ausstehend': 'offen', 'Ungeeignet': 'nicht berechtigt'}

rows = []; quellen = []
for p in sorted(glob.glob(os.path.join(HIER, 'exporte', '*.xlsx'))):
    konto = os.path.basename(p)[:-5]
    z = list(xl.lesen(p).values())[0]; k = z[0]
    for r in (dict(zip(k, r)) for r in z[1:]):
        vor = sum(f(r.get(c)) for c in ('Vorauss. Standardprovision', 'Vorauss. Provision bei Shop-Anzeigen',
                                         'Vorauss. Bonus', 'Vorauss. Bonus für Affiliate-Partner*innen'))
        b = d(r['Bestelldatum']); a = d(r['Abrechnungsdatum der Provision'])
        rows.append({'konto': konto, 'bestell_id': r['Bestell-ID'], 'produkt': r['Produktname'], 'produkt_id': r['Produkt-ID'],
                     'video_id': r['Inhalts-ID'], 'status': STATUS.get(r['Abrechnungsstatus der Bestellung'], r['Abrechnungsstatus der Bestellung']),
                     'bestellt': b[:10], 'bestellt_zeit': b, 'ausgezahlt_am': a[:10] if a else None,
                     'umsatz': f(r['GMV']), 'provision_vorauss': round(vor, 2),
                     'provision_tats': f(r['Endgültig verdienter Gesamtbetrag']),
                     'erstattet': int(f(r['Rückerstattete Artikel'])), 'satz': r.get('Standard') or ''})
    quellen.append({'konto': konto, 'datei_stand': D.datetime.fromtimestamp(os.path.getmtime(p)).strftime('%Y-%m-%d %H:%M'),
                    'zeilen': len(z) - 1})
json.dump({'rows': rows, 'quellen': quellen}, open(os.path.join(HIER, 'bestellungen.json'), 'w'), ensure_ascii=False)
print(len(rows), 'Zeilen', [(q['konto'], q['zeilen']) for q in quellen])
