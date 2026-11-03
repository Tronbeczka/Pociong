#!/usr/bin/env python3
"""Baza przejazdów kolejowo-drogowych dla aplikacji (Polska, z OpenStreetMap).

Użycie: przejazdy_pl.py poland.osm.pbf poland.poly katalog_wyjściowy

To samo, o co aplikacja pyta serwery Overpass, ale policzone raz dla całego kraju:
 1) węzły oznaczone railway=level_crossing,
 2) węzły wspólne toru (rail / narrow_gauge / preserved, bez service, poza mostem i tunelem)
    i drogi (bez chodników, ścieżek itp., poza mostem i tunelem) – przejazdy, których nikt nie opisał.
Wynik: komórki 0,5° × 0,5° (plik cLA_LO.json, LA=floor(lat·2), LO=floor(lon·2)) z listą
[id, lat, lon, tagi], plus meta.json. "f":1 = komórka w całości w granicach wyciągu (pełne dane).
"""
import json, math, os, sys, datetime
import osmium

RAIL = {'rail', 'narrow_gauge', 'preserved'}
HW_SKIP = {'footway', 'path', 'cycleway', 'steps', 'pedestrian', 'bridleway', 'construction', 'proposed', 'corridor', 'elevator'}
KEEP = ('railway', 'crossing', 'crossing:barrier', 'crossing:light', 'crossing:bell', 'crossing:activation', 'crossing:supervision', 'crossing:on_demand', 'supervised', 'tracks')


def read_poly(path):
    rings, cur, name = [], None, None
    with open(path, encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip()]
    for l in lines[1:]:
        if cur is None:
            if l == 'END':
                break
            cur = {'hole': l.startswith('!'), 'pts': []}
        elif l == 'END':
            rings.append(cur); cur = None
        else:
            x, y = l.split()[:2]
            cur['pts'].append((float(x), float(y)))
    return rings


def inside(rings, lon, lat):
    def pip(pts):
        c = False; j = len(pts) - 1
        for i in range(len(pts)):
            xi, yi = pts[i]; xj, yj = pts[j]
            if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
                c = not c
            j = i
        return c
    ins = any(pip(r['pts']) for r in rings if not r['hole'])
    return ins and not any(pip(r['pts']) for r in rings if r['hole'])


def main(pbf, poly, out):
    rings = read_poly(poly)
    # 1) węzły torów
    rail = set()
    for w in osmium.FileProcessor(pbf, osmium.osm.WAY).with_filter(osmium.filter.KeyFilter('railway')):
        t = w.tags
        if t.get('railway') in RAIL and 'service' not in t and 'bridge' not in t and 'tunnel' not in t:
            rail.update(n.ref for n in w.nodes)
    print('węzły torów:', len(rail), flush=True)
    # 2) węzły wspólne toru i drogi
    cand = set()
    for w in osmium.FileProcessor(pbf, osmium.osm.WAY).with_filter(osmium.filter.KeyFilter('highway')):
        t = w.tags
        if t.get('highway') in HW_SKIP or 'bridge' in t or 'tunnel' in t:
            continue
        for n in w.nodes:
            if n.ref in rail:
                cand.add(n.ref)
    print('węzły tor + droga:', len(cand), flush=True)
    del rail
    # 3) współrzędne i tagi
    found = {}
    kst, vst = {}, {}
    def add(n):
        if not n.location.valid():
            return
        tg = {k: n.tags[k] for k in KEEP if k in n.tags}
        if n.tags.get('railway') == 'level_crossing':
            for t in n.tags:
                kst[t.k] = kst.get(t.k, 0) + 1
                if t.k.startswith('crossing') or 'categ' in t.k or t.k.startswith('railway:'):
                    kv = t.k + '=' + t.v[:30]
                    vst[kv] = vst.get(kv, 0) + 1
        found[n.id] = [n.id, round(n.location.lat, 6), round(n.location.lon, 6), tg]
    for n in osmium.FileProcessor(pbf, osmium.osm.NODE).with_filter(osmium.filter.TagFilter(('railway', 'level_crossing'))):
        add(n)
    ntag = len(found)
    if cand:
        for n in osmium.FileProcessor(pbf, osmium.osm.NODE).with_filter(osmium.filter.IdFilter(cand)):
            if n.id not in found:
                add(n)
    print('przejazdy: oznaczone', ntag, 'razem', len(found), flush=True)
    if len(found) < int(os.environ.get('MINX', '5000')):
        sys.exit('za mało przejazdów (%d) – nie nadpisuję bazy' % len(found))
    # 4) komórki
    cells = {}
    for e in found.values():
        cells.setdefault((math.floor(e[1] * 2), math.floor(e[2] * 2)), []).append(e)
    lats = [p[1] for r in rings for p in r['pts']]; lons = [p[0] for r in rings for p in r['pts']]
    la0, la1 = math.floor(min(lats) * 2), math.floor(max(lats) * 2)
    lo0, lo1 = math.floor(min(lons) * 2), math.floor(max(lons) * 2)
    day = datetime.date.today().isoformat()
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.startswith('c') and f.endswith('.json'):
            os.remove(os.path.join(out, f))
    nfile = nfull = 0
    for la in range(la0, la1 + 1):
        for lo in range(lo0, lo1 + 1):
            # komórka w całości w granicach wyciągu? (siatka 9×9 punktów)
            pts = [inside(rings, (lo + i / 8) / 2, (la + j / 8) / 2) for i in range(9) for j in range(9)]
            if not any(pts) and (la, lo) not in cells:
                continue
            full = all(pts)
            el = sorted(cells.get((la, lo), []))
            with open(os.path.join(out, 'c%d_%d.json' % (la, lo)), 'w', encoding='utf-8') as f:
                json.dump({'t': day, 'f': 1 if full else 0, 'e': [[e[0], e[1], e[2], e[3] or 0] for e in el]}, f, ensure_ascii=False, separators=(',', ':'))
            nfile += 1; nfull += full
    with open(os.path.join(out, 'meta.json'), 'w', encoding='utf-8') as f:
        json.dump({'t': day, 'n': len(found), 'oznaczone': ntag, 'komorki': nfile, 'pelne': nfull, 'zrodlo': 'OpenStreetMap (ODbL), wyciąg Geofabrik',
                   'klucze': dict(sorted(kst.items(), key=lambda a: -a[1])[:40]),
                   'wartosci': dict(sorted(vst.items(), key=lambda a: -a[1])[:60])}, f, ensure_ascii=False, indent=0)
    print('komórki:', nfile, 'pełne:', nfull, flush=True)


if __name__ == '__main__':
    main(*sys.argv[1:4])
