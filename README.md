# Testy aplikacji (gałąź pomocnicza)

Środowisko testowe odbudowane w wersji 192: przeglądarka (Playwright) z lokalnymi danymi –
kafelki OpenFreeMap okolic Wrocławia (gałąź `test-data`), zamiennik Overpass i OSRM liczony
na wyciągu OSM (gałąź `testdata`, `pwt/osmload.py` → `osm.pkl`), przejazdy z repozytorium.

- `pwt/h.py` – wspólne narzędzia (launch, goto, fix, cam, settle, plan, roadpos)
- `pwt/t_*.py` – testy funkcjonalne (`APP=plik.html python3 t_core.py`)
- `pwt/vis.py` + `pwt/vcmp.py` – zrzuty porównawcze dwóch wersji i obraz różnic
- `lint/lintcmp.sh stara.html nowa.html` – nowe błędy ESLint (no-undef itd.)

## Wersja 199 – nowy moduł jezdni z pasami (etap 1)

- `jz/jz.js` – moduł (wstawiany do aplikacji przez `jz/patch199.py` z wersji 198)
- `node jz/test.js [jz.js]` – testy modułu na danych syntetycznych (Curie, rozwidlenie, przedłużenie, skrzyżowanie, kreski, most)
- `pwt/t_jz.py` – 10 sprawdzeń w 16 miejscach Wrocławia: brzeg bez wcięć, łagodna zmiana szerokości, linie nie wchodzą na inne jezdnie,
  linie odnóg się nie krzyżują, rozwidlenia od brzegów, mosty w częściach, czas pierwszej i kolejnych klatek
- `pwt/t_v199.py` – stary moduł wyłączony, nowy rysuje; panel pasów w nawigacji bez zmian
- `pwt/t_zoomjz.py` – płynna zmiana skali: linie nie znikają, geometria liczona rzadko
- `pwt/jzbench.py`, `pwt/fkdbg2.py`, `pwt/dipdbg.py` – pomiar czasu i podgląd rozwidleń / przebiegu szerokości

## Wersja 200 – szerokość jezdni jak na mapie

- `jz/patch200.py` – podmiana modułu w wersji 199 (`jz/jz.js`: jezdnia = szerokość zwykłej drogi z mapy, pasy dzielą ją między siebie,
  jezdnie obok siebie dzielą wspólne miejsce według liczby pasów)
- `pwt/t_jz.py` – 11 sprawdzeń, nowe: „jezdnia nie szersza niż zwykła droga z mapy pod nią”
- `pwt/t_v200.py` – stary moduł wyłączony, nowy rysuje, panel pasów bez zmian
- `pwt/fkone2.py` – podgląd szerokości odnogi przy węźle rozwidlenia

