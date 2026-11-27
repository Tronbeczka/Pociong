# Wersja 206: linie pasów na jezdni – od nowa, tylko linie na drogach z mapy (moduł /tmp/ll/ll.js)
import sys
src,dst=sys.argv[1],sys.argv[2]
s=open(src).read();LLJS=open('/tmp/ll/ll.js').read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:90]);s=s.replace(a,b)
# 1) drogi z kafelków: klasa rysowania (łącznik autostrady węższy) i kierunek jednokierunkowej
rep("""        if(ra&&ra.length>=4){ra.k=cls;ra.o=owT?1:0;if(clK)ra.cl=clK;""","""        if(ra&&ra.length>=4){ra.k=cls;ra.o=owT?1:0;ra.kw=cw;ra.od=owT?((pr.oneway==-1||pr.oneway==='-1')?-1:1):0;if(clK)ra.cl=clK;""")
# 2) moduł linii pasów + przełącznik w ustawieniach
rep("""{const e=$('laneCb');if(e){e.checked=laneOn;e.onchange=()=>{laneOn=e.checked;LSput('laneOn',laneOn);vd=null;laneVer++;if(route)route.lp=null;if(laneOn)lnTick()}}}""",
LLJS+"""{const e=$('laneCb');if(e){e.checked=llOn;e.onchange=()=>{llOn=e.checked;LSput('llOn',llOn);LL.scanKey='';vd=null;if(llOn)lnTick()}}}   // Wersja 206: przełącznik linii pasów na jezdni (stary moduł pasów zostaje wyłączony)""")
rep("""  <label style="display:none!important"><input type="checkbox" id="laneCb"> Pasy ruchu na drogach i na trasie (dane z OpenStreetMap)</label>""",
"""  <label><input type="checkbox" id="laneCb"> Linie pasów na jezdni (dane z OpenStreetMap)</label>""")
# 3) rysowanie: linie na drogach na ziemi – po jezdniach wszystkich klas, przed mostami; na mostach – po mostach
rep("""    const BO={pal,s,rwz,cwz,night,dm,rlw};""","""    try{llWant(D,cam);llDraw(c,D,s,pal,night,dm,0,cam)}catch(e){c.setLineDash([]);c.lineCap='round';lnFail(e)}   // Wersja 206: linie pasów na jezdni (drogi na ziemi)
    const BO={pal,s,rwz,cwz,night,dm,rlw};""")
rep("""    if(D.BR&&D.BR.length)try{drawBridges(c,D.BR,BO,'over');drawBridges(c,D.BR,BO,'rail')}catch(e){c.setLineDash([]);c.lineCap='round';errNote('mosty',e)}   // wiadukty nad torami zasłaniają tory; tory na mostach – ponad drogami""",
"""    if(D.BR&&D.BR.length)try{drawBridges(c,D.BR,BO,'over');drawBridges(c,D.BR,BO,'rail')}catch(e){c.setLineDash([]);c.lineCap='round';errNote('mosty',e)}   // wiadukty nad torami zasłaniają tory; tory na mostach – ponad drogami
    try{llDraw(c,D,s,pal,night,dm,1,cam)}catch(e){c.setLineDash([]);c.lineCap='round';lnFail(e)}   // Wersja 206: linie pasów na mostach i wiaduktach""")
# 4) dane o pasach: przy włączonych liniach – wokół auta (jak dawniej), nie tylko wzdłuż trasy
rep("""  const pan=!laneOn&&lnPanel;   // Wersja 205: tylko panel strzałek u góry ekranu – dane wzdłuż trasy, i tylko w czasie nawigacji""",
"""  const pan=!laneOn&&!llOn&&lnPanel;   // Wersja 205: tylko panel strzałek u góry ekranu – dane wzdłuż trasy, i tylko w czasie nawigacji; Wersja 206: linie pasów na jezdni – dane wokół auta""")
rep("""  if(!(laneOn||(pan&&route&&route.len>0&&route.steps&&route.steps.length>2))||!vec||!vecData||window.preview||demo)return;""",
"""  if(!(laneOn||llOn||(pan&&route&&route.len>0&&route.steps&&route.steps.length>2))||!vec||!vecData||window.preview||demo)return;""")
rep("""  if(add){laneVer++;if(laneOn)vd=null}   // Wersja 205: same dane dla panelu strzałek nie zmieniają mapy – bez przemalowania""","""  if(add){laneVer++;if(laneOn||llOn)vd=null}   // Wersja 205: same dane dla panelu strzałek nie zmieniają mapy – bez przemalowania; Wersja 206: przy liniach pasów przemalowanie uruchamia ich liczenie""")
rep('<span id="ver">wersja 205<','<span id="ver">wersja 206<')
open(dst,'w').write(s);print('zapisano',dst)
