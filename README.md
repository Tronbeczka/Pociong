# Testy aplikacji (gałąź pomocnicza)

Środowisko testowe odbudowane w wersji 192: przeglądarka (Playwright) z lokalnymi danymi –
kafelki OpenFreeMap okolic Wrocławia (gałąź `test-data`), zamiennik Overpass i OSRM liczony
na wyciągu OSM (gałąź `testdata`, `pwt/osmload.py` → `osm.pkl`), przejazdy z repozytorium.

- `pwt/h.py` – wspólne narzędzia (launch, goto, fix, cam, settle, plan, roadpos)
- `pwt/t_*.py` – testy funkcjonalne (`APP=plik.html python3 t_core.py`)
- `pwt/vis.py` + `pwt/vcmp.py` – zrzuty porównawcze dwóch wersji i obraz różnic
- `lint/lintcmp.sh stara.html nowa.html` – nowe błędy ESLint (no-undef itd.)
