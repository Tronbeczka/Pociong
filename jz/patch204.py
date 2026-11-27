# Wersja 204: powrót do dróg z wersji 198 (bez jezdni z pasami z wersji 199–203); cienie budynków nadal wyłączone (jak w 203)
import sys
src,dst=sys.argv[1],sys.argv[2]   # src: wersja 198 (git d6f0e67), dst: wynik
s=open(src).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:80]);s=s.replace(a,b)
rep("""    for(let n=Math.max(start,lst.length-260);n<lst.length;n++){
      if(fogOn&&lst[n].y<fe)continue;   // w pasie mgły cieni nie rysujemy""","""    if(BLD_SH)for(let n=Math.max(start,lst.length-260);n<lst.length;n++){   // Wersja 203: cienie budynków wyłączone (na prośbę – ciemne plamy na jezdni wyglądały jak budynki nachodzące na drogę)
      if(fogOn&&lst[n].y<fe)continue;   // w pasie mgły cieni nie rysujemy""")
rep("""function bld3Draw(){""","""const BLD_SH=false;   // Wersja 203: bez cieni budynków i budowli (cienie drzew zostają); Wersja 204: zostaje tak po powrocie do dróg z wersji 198
function bld3Draw(){""")
rep('<span id="ver">wersja 198<','<span id="ver">wersja 204<')
open(dst,'w').write(s);print('zapisano',dst,len(s))
