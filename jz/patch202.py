# Wersja 202: szerokość dróg przy zbliżeniu – poziomy (co ok. 12 %), zmieniane dopiero po zatrzymaniu zbliżania; jezdnie z pasami nie przeliczają się w trakcie ruchu
src='/tmp/app/v201.html';dst='/tmp/app/v202.html'
s=open(src).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:80]);s=s.replace(a,b)
rep("""// Szerokość w pikselach i tak rośnie przy zbliżaniu (mnożnik maleje wolniej, niż rośnie skala).
const rwF=s=>s<=1.2?2.4:Math.max(1.05,2.4-Math.log(s/1.2));""",
"""// Szerokość w pikselach i tak rośnie przy zbliżaniu (mnożnik maleje wolniej, niż rośnie skala).
// Wersja 202: mnożnik ma 8 poziomów (co ok. 12 %) i zmienia się dopiero wtedy, gdy zbliżanie się zatrzyma (palce zdjęte, kamera doszła do docelowej skali).
// W wersji 201 zmieniał się płynnie razem ze skalą: każde przemalowanie w trakcie zbliżania miało inną szerokość dróg niż powiększany obraz (drogi „telepały się”),
// a jezdnie z pasami liczyły się od nowa kilkadziesiąt razy na jeden gest – malowanie trwało po ~100 ms, więc aplikacja obniżała rozdzielczość mapy (wszystko się zlewało).
const RWL=[0,1,2,3,4,5,6,7].map(k=>2.4/Math.pow(1.12,k));
let rwLv=-1,rwRest=0,rwZt=0,rwSt=0,rwMov=false;   // rwLv: bieżący poziom (−1: jeszcze nieustalony); rwZt: kiedy ostatnio zmieniła się docelowa skala; rwMov: trwa zbliżanie/oddalanie albo palec na mapie
const rwLvFor=s=>{if(s<=1.2)return 0;const f=Math.max(1.05,2.4-Math.log(s/1.2));return Math.max(0,Math.min(7,Math.round(Math.log(2.4/f)/Math.log(1.12))))};
const rwF=s=>s<=.6?2.4:RWL[Math.max(0,rwLv)];""")
rep("""  if(!vctx||$('vmap').width!==Math.round(S*vq))sizeV();
  if(!vctx)return;
  const sh=vShift(S,scaleCur,cam);""","""  if(!vctx||$('vmap').width!==Math.round(S*vq))sizeV();
  if(!vctx)return;
  {const kd=rwLvFor(scaleCur);if(scaleTgt!==rwSt){rwSt=scaleTgt;rwZt=now}   // poziom szerokości dróg: zmiana tylko w spoczynku (Wersja 202)
   const rest=Math.abs(scaleCur/scaleTgt-1)<.01&&now-rwZt>300&&!(window.__ptrs&&window.__ptrs()>0)&&!panGlide;rwMov=!rest;
   if(rwLv<0)rwLv=kd;
   else if(kd!==rwLv){if(!rest)rwRest=0;else if(!rwRest)rwRest=now;else if(now-rwRest>250){rwLv=kd;rwRest=0;vd=null}}
   else rwRest=0;
   if(rest&&typeof JZN!=='undefined'&&JZN&&JZN.stale){JZN.stale=false;vd=null}}   // jezdnie z pasami: po zatrzymaniu geometria dla właściwej skali
  const sh=vShift(S,scaleCur,cam);""")
rep('<span id="ver">wersja 201<','<span id="ver">wersja 202<')
open(dst,'w').write(s);print('zapisano',dst,len(s))
