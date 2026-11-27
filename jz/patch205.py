# Wersja 205: (1) przycisk „do auta” po wyszukaniu miejsca wraca do auta (ostatnia pozycja z GPS), a nie do oglądanego miejsca;
# (2) panel strzałek pasów u góry ekranu przed skrzyżowaniami ma dane jak w wersjach 138–203 (pobierane w tle wzdłuż trasy), bez oznaczeń na jezdni
import sys
src,dst=sys.argv[1],sys.argv[2]
s=open(src).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:90]);s=s.replace(a,b)

# --- (1) powrót z podglądu wyszukanego miejsca do auta ---
rep("""function recenter(){
  if(window.preview&&!window.browse&&route&&vec){fitFly();return}""","""function recenter(){
  if(window.browse&&!window.brwLive){brwHome(true);return}   // Wersja 205: podgląd wyszukanego miejsca – przycisk wraca do auta (ostatnia pozycja z GPS), a nie do oglądanego miejsca
  if(window.preview&&!window.browse&&route&&vec){fitFly();return}""")
rep("""$('brwBack').onclick=()=>{$('start').click()};""","""$('brwBack').onclick=()=>brwHome(false);
// Wersja 205: powrót z podglądu wyszukanego miejsca do auta – przycisk „do auta” (wyśrodkowanie), „Wróć do mojej pozycji (GPS)” i „Prowadź tutaj”.
// W podglądzie GPS jest wyłączony, a „auto” stoi w oglądanym miejscu (co 1,5 s także pozycja last): przycisk „do auta” wracał więc do wyszukanego
// miejsca, po „Wróć do mojej pozycji” auto stało w oglądanym miejscu, dopóki telefon nie podał nowej pozycji, a „Prowadź tutaj” liczyło trasę
// z wyszukanego miejsca do niego samego („start i cel są w tym samym miejscu”). Teraz mapa od razu wraca do ostatniej pozycji z GPS (sprzed wyszukania;
// po ponownym uruchomieniu aplikacji – zapamiętanej), auto jest szare, dopóki nie przyjdzie nowy odczyt (jak przy starcie), a trasa liczy się od auta.
function brwPos(){   // ostatnia prawdziwa pozycja z GPS albo zapamiętana w telefonie; null – nieznana
  if(gpsOk&&gpsOk.lat>-90&&gpsOk.lat<90&&gpsOk.lon>-180&&gpsOk.lon<180)return {lat:gpsOk.lat,lon:gpsOk.lon,h:gpsOk.h,t:gpsOk.t};
  try{const q=JSON.parse(localStorage.getItem('lastpos')||'null');if(q&&q.lat>-90&&q.lat<90&&q.lon>-180&&q.lon<180)return {lat:q.lat,lon:q.lon,h:null,t:q.t}}catch(e){}
  return null;
}
function brwRestore(lp){   // po wyjściu z podglądu: kamera i auto (szare do pierwszego odczytu) w ostatniej znanej pozycji; bez niej auto zostaje, a pozycja jest nieznana
  const c=lp||vecCam0(performance.now());
  if(c){fix=null;provCam={lat:c.lat,lon:c.lon};document.body.classList.add('nofix');hAnch=null}
  if(lp){
    last={lat:lp.lat,lon:lp.lon,t:lp.t||0};   // czas odczytu: świeży (do 30 s) służy od razu za start trasy, starszy – trasa czeka na odczyt z telefonu
    if(lp.h!=null&&!isNaN(lp.h)){lastH=lp.h;tgtRot=-lastH}
    if(!lastFetch||dist(lastFetch.lat,lastFetch.lon,lp.lat,lp.lon)>1500)loadCrossings(lp.lat,lp.lon);
  }else last=null;   // oglądane miejsce nie jest pozycją auta
  clearInterval(window.brwHT);let n=0;vecNext=0;   // mapa wokół auta doczytuje się, zanim przyjdzie odczyt GPS (potem robi to follow)
  const lv=()=>{if(fix||window.preview||++n>75){clearInterval(window.brwHT);return}const cp=vecCam(performance.now());
    if(cp&&vec&&(!vecData||dist(vecData.lat,vecData.lon,cp.lat,cp.lon)>600)&&Date.now()>vecNext)loadVec(cp.lat,cp.lon)};
  window.brwHT=setInterval(lv,800);lv();
}
function brwHome(quiet){
  const lp=brwPos();
  exitPreview(true);brwRestore(lp);
  startGps(quiet);
  updRecenter();
}""")
rep("""$('brwGo').onclick=()=>{
  const it=window.browseIt;if(!it)return;
  exitPreview();""","""$('brwGo').onclick=()=>{
  const it=window.browseIt;if(!it)return;
  const lp=brwPos();
  exitPreview();brwRestore(lp);   // Wersja 205: trasa od auta (ostatnia pozycja z GPS), a nie od wyszukanego miejsca""")
rep("""      if(!started){started=true;enterBrowse({lat:o.lat,lon:o.lon,title:ttl,label:ttl});$('brwFav').style.display='none';$('brwGo').style.display='none'}""",
"""      if(!started){started=true;enterBrowse({lat:o.lat,lon:o.lon,title:ttl,label:ttl});window.brwLive=true;$('brwFav').style.display='none';$('brwGo').style.display='none'}   // brwLive (Wersja 205): „auto” podglądu to śledzony kierowca – przycisk „do auta” wraca do niego""")
rep("""  window.preview=true;window.browse=true;document.body.classList.add('preview');
  const p={lat:it.lat,lon:it.lon,speed:0,heading:0};""","""  window.preview=true;window.browse=true;window.brwLive=false;document.body.classList.add('preview');
  const p={lat:it.lat,lon:it.lon,speed:0,heading:0};""")

# --- (2) dane o pasach dla panelu strzałek ---
rep("""// zostaje – pobiera strzałki z OpenStreetMap sam (fetchLanes), jak przed wersją 138.
var laneOn=false,leOn=false;""","""// zostaje – pobiera strzałki z OpenStreetMap sam (fetchLanes), jak przed wersją 138.
// Wersja 205: dla tego panelu dane o pasach znów pobierają się w tle (komórkami, wzdłuż trasy w czasie nawigacji – jak w wersjach 138–203),
// więc strzałki są od razu, także gdy pojedyncze zapytanie o jeden manewr się nie uda. Na jezdni nadal nic nie rysujemy (laneOn=false).
var lnPanel=true;
var laneOn=false,leOn=false;""")
rep("""  if(add){laneVer++;vd=null}""","""  if(add){laneVer++;if(laneOn)vd=null}   // Wersja 205: same dane dla panelu strzałek nie zmieniają mapy – bez przemalowania""")
rep("""  for(const [k,c] of lnCells)if(c.s===2){const x=((c.cx+.5)*LN_CELL.x-p.lon)*kx,y=((c.cy+.5)*LN_CELL.y-p.lat)*111195;if(Math.abs(x)>R||Math.abs(y)>R)lnCells.delete(k)}
  laneVer++;vd=null;""","""  for(const [k,c] of lnCells)if(c.s===2){const x=((c.cx+.5)*LN_CELL.x-p.lon)*kx,y=((c.cy+.5)*LN_CELL.y-p.lat)*111195;if(Math.abs(x)>R||Math.abs(y)>R)lnCells.delete(k)}
  laneVer++;if(laneOn)vd=null;""")
rep("""function lnTick(){
  if(!laneOn||!vec||!vecData||window.preview||demo)return;   // dopiero gdy mapa jest już wczytana (nie spowalniamy jej startu)
  const p=(vf&&vf.car)||last;if(!p)return;
  if(!xReady(p)&&performance.now()<20000)return;   // najpierw przejazdy kolejowe (ważniejsze); pasy dopiero po ich wczytaniu (najpóźniej po 20 s)
  lnPrune(p);
  const dy=1300/111195,dx=1300/(111195*Math.cos(rad(p.lat)));
  for(const [a,b] of [[0,0],[1,0],[-1,0],[0,1],[0,-1],[1,1],[-1,-1],[1,-1],[-1,1]])lnWant(p.lat+a*dy,p.lon+b*dx,Math.hypot(a,b));
  if(route&&route.len>0&&!window.browse){const a0=route.along||0;for(let d=700;d<=7000;d+=700){const q=routeAt(route,Math.min(route.len,a0+d));lnWant(q[0],q[1],1+d/700)}}
  if(lnQ.length)lnPump();
}""","""function lnTick(){
  const pan=!laneOn&&lnPanel;   // Wersja 205: tylko panel strzałek u góry ekranu – dane wzdłuż trasy, i tylko w czasie nawigacji
  if(!(laneOn||(pan&&route&&route.len>0&&route.steps&&route.steps.length>2))||!vec||!vecData||window.preview||demo)return;   // dopiero gdy mapa jest już wczytana (nie spowalniamy jej startu)
  const p=(vf&&vf.car)||last;if(!p)return;
  if(!xReady(p)&&performance.now()<20000)return;   // najpierw przejazdy kolejowe (ważniejsze); pasy dopiero po ich wczytaniu (najpóźniej po 20 s)
  lnPrune(p);
  const dy=1300/111195,dx=1300/(111195*Math.cos(rad(p.lat)));
  if(!pan)for(const [a,b] of [[0,0],[1,0],[-1,0],[0,1],[0,-1],[1,1],[-1,-1],[1,-1],[-1,1]])lnWant(p.lat+a*dy,p.lon+b*dx,Math.hypot(a,b));
  if(route&&route.len>0&&!window.browse){const a0=route.along||0;for(let d=pan?0:700;d<=7000;d+=700){const q=routeAt(route,Math.min(route.len,a0+d));lnWant(q[0],q[1],(pan?0:1)+d/700)}}
  if(lnQ.length)lnPump();
}""")
rep("""  if(!turn||d>450||d<8){lnRender(null);return}
  if(s.lanes===undefined&&!s.laneBusy){""","""  if(!turn||d>450||d<8){lnRender(null);return}
  if(!s.lanes&&!s.laneBusy&&LANEW.size&&s.lnV!==laneVer){s.lnV=laneVer;try{const L=lnLanesFromStore(route,s);if(L)s.lanes=L}catch(e){}}   // Wersja 205: strzałki z danych pobranych w tle – także gdy dotarły po nieudanym zapytaniu o ten manewr
  if(s.lanes===undefined&&!s.laneBusy){""")
rep("""function drawLaneArrow(){
  if(!(vec&&vf&&route&&nav&&nav.i>0&&!freeCam))return;""","""const LN_ROAD_ARROW=false;   // Wersja 205: strzałki pasów na jezdni przed manewrem wyłączone – na razie bez oznaczeń na ulicy (nieczytelne); strzałki są w panelu u góry ekranu
function drawLaneArrow(){
  if(!LN_ROAD_ARROW)return;
  if(!(vec&&vf&&route&&nav&&nav.i>0&&!freeCam))return;""")
rep('<span id="ver">wersja 204<','<span id="ver">wersja 205<')
open(dst,'w').write(s);print('zapisano',dst)
