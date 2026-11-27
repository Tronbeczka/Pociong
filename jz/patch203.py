# Wersja 203: bez cieni budynków; szerokość dróg – tylko 2 poziomy (zmiana dopiero przy dużym ręcznym zbliżeniu), więc przy jeździe drogi nie „skaczą”
src='/tmp/app/v202.html';dst='/tmp/app/v203.html'
s=open(src).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:80]);s=s.replace(a,b)
rep("""const RWL=[0,1,2,3,4,5,6,7].map(k=>2.4/Math.pow(1.12,k));""","""// Wersja 203: tylko 2 poziomy – 1,6 do 3,4 px/m (cały zakres zbliżenia przy jeździe i na postoju: 0,85–2,8 px/m) i 1,15 przy dużym ręcznym zbliżeniu.
// Przy 8 poziomach każda zmiana prędkości (kamera oddala się przy 25 i 50 km/h) kończyła się skokiem szerokości dróg o 12–25 % („nadal trochę lata”).
// Poniżej ok. 1 px/m i tak rządzą najmniejsze szerokości w pikselach (VC.w).
const RWL=[1.6,1.15];""")
rep("""const rwLvFor=s=>{if(s<=1.2)return 0;const f=Math.max(1.05,2.4-Math.log(s/1.2));return Math.max(0,Math.min(7,Math.round(Math.log(2.4/f)/Math.log(1.12))))};
const rwF=s=>s<=.6?2.4:RWL[Math.max(0,rwLv)];""","""const rwLvFor=s=>rwLv===1?(s>=3.1?1:0):(s>=3.4?1:0);   // (z małym zapasem, żeby nie przełączać w tę i z powrotem przy granicy)
const rwF=s=>RWL[Math.max(0,rwLv)];""")
rep("""    for(let n=Math.max(start,lst.length-260);n<lst.length;n++){
      if(fogOn&&lst[n].y<fe)continue;   // w pasie mgły cieni nie rysujemy""","""    if(BLD_SH)for(let n=Math.max(start,lst.length-260);n<lst.length;n++){   // Wersja 203: cienie budynków wyłączone (na prośbę – ciemne plamy na jezdni wyglądały jak budynki nachodzące na drogę)
      if(fogOn&&lst[n].y<fe)continue;   // w pasie mgły cieni nie rysujemy""")
rep("""function bld3Draw(){""","""const BLD_SH=false;   // Wersja 203: bez cieni budynków i budowli (cienie drzew zostają)
function bld3Draw(){""")
rep('<span id="ver">wersja 202<','<span id="ver">wersja 203<')
open(dst,'w').write(s);print('zapisano',dst,len(s))
