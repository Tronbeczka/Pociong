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

## Wersja 201 – z bliska drogi bez zlewania się w plamę

- `jz/patch201.py` – mnożnik szerokości dróg zależny od zbliżenia (`rwF`): do 1,2 px/m 2,4, na postoju ok. 1,55, z bliska 1,05
- `pwt/look5.py` – zrzut całego ekranu w punkcie przy zadanej skali (px/m), np. `look5.py tag "51.1085,17.0478,250,4.5,50"`
- `pwt/t_v201.py` – jak t_v200 dla wersji 201

## Wersja 202 – płynne przesuwanie i zbliżanie

- `jz/patch202.py` – poziomy szerokości dróg (8, co ok. 12 %) zmieniane po zatrzymaniu zbliżania; budowanie od wersji 199:
  `patch200.py` (moduł `jz/jz.js`) → `patch201.py` → `patch202.py`
- `jz/jz.js` – linie pasów w tle (porcje ~6 ms), fragmentami po ok. 300 m, tylko w widoku; w trakcie gestu bez nowej geometrii
- `pwt/t_perfmove.py` – przesuwanie palcem i zbliżanie na procesorze spowolnionym CDP (`RATE=4`): liczba i czas malowań, przeliczenia, rozdzielczość
- `pwt/t_zoomjz.py` – gest dwoma palcami: bez przeliczeń w trakcie, po geście właściwa szerokość i gotowe linie
- `pwt/jzbench2.py` – czas sieci / geometrii / linii (min i mediana z 9 prób)

## Wersja 203 – bez cieni budynków, stała szerokość dróg w czasie jazdy

- `jz/patch203.py` – 2 poziomy szerokości dróg (1,6 do 3,4 px/m, 1,15 powyżej), `BLD_SH=false` (bez cieni budynków i budowli)
- `pwt/t_autozoom.py` – jazda 0–62–0 km/h: kamera zmienia zbliżenie, a szerokość dróg i jezdnie z pasami zostają bez zmian; bez cieni budynków
- `pwt/t_v203.py` – jak t_v202 dla wersji 203


## Wersja 204 – powrót do dróg z wersji 198

Na prośbę „Cofnij do wersji sprzed nakładek na drogi”: plik to wersja 198 (d6f0e67) z numerem wersji i wyłączonymi cieniami budynków (jak w 203).
Moduł jezdni z pasami (199–203) i poziomy szerokości dróg zostają w historii (`jz/`, testy t_jz, t_v199–t_v203, t_zoomjz, t_autozoom) do ewentualnego powrotu.

- `jz/patch204.py` – `python3 patch204.py wersja198.html wynik.html`
- `pwt/t_v204b.py` – `python3 t_v204b.py wersja198.html wersja204.html`: płótno mapy piksel w piksel jak w 198 (3 miejsca), brak modułu jezdni z pasami, szerokość dróg ×2,4, cienie budynków w 198 są, w 204 brak
- `pwt/t_v204.py` – sprawdzenia t_nolane dla wersji 204
