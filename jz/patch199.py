# Wersja 199: jezdnie z pasami od nowa – etap 1: obrys jezdni i linie pasów (nowy moduł jz*, stary wyłączony od wersji 198)
src='/tmp/app/v198.html';dst='/tmp/app/v199.html'
s=open(src).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:100]);s=s.replace(a,b)
JZ=open('/tmp/jz/jz.js').read()
# moduł – przed planem pasa dla trasy (po danych o pasach)
rep("""// ---- plan pasa dla trasy ----""",JZ+"""
// ---- plan pasa dla trasy ----""")
# dane o pasach wczytujemy dla nowego modułu (stary moduł nadal wyłączony)
rep("""  if(!laneOn||!vec||!vecData||window.preview||demo)return;   // dopiero gdy mapa jest już wczytana (nie spowalniamy jej startu)""",
"""  if(!(laneOn||jzOn)||!vec||!vecData||window.preview||demo)return;   // dopiero gdy mapa jest już wczytana (nie spowalniamy jej startu); Wersja 199: także dla nowych jezdni z pasami""")
# malowanie mapy: haki nowego modułu w tych samych miejscach co stary
rep("""let LV=[],LG=null;try{LV=lnVis(D,s,ox,oy,S);LG=LV.length?lnGroups(LV,s):null}catch(e){LV=[];LG=null;lnFail(e)}   // drogi z kilkoma pasami (dane OSM)""",
"""let LV=[],LG=null;try{LV=lnVis(D,s,ox,oy,S);LG=LV.length?lnGroups(LV,s):null}catch(e){LV=[];LG=null;lnFail(e)}   // drogi z kilkoma pasami (dane OSM)
    let JF=null;try{JF=jzFrame(D,s,ox,oy,S)}catch(e){JF=null;lnFail(e)}   // Wersja 199: jezdnie z pasami (nowy moduł)""")
rep("""      if(LG&&night)try{lnStroke(c,LG,gl,cwz+18,s,g=>g.kc<=3)}catch(e){c.lineCap='round';lnFail(e)}""",
"""      if(LG&&night)try{lnStroke(c,LG,gl,cwz+18,s,g=>g.kc<=3)}catch(e){c.lineCap='round';lnFail(e)}
      if(JF&&night)try{jzHalo(c,JF,gl,cwz+18,s,kc=>kc<=3)}catch(e){c.lineCap='round';lnFail(e)}""")
rep("""      if(LG&&s>=1.2)try{lnStroke(c,LG,wk,cwz+9,s,g=>g.kc===0||g.kc>=3)}catch(e){c.lineCap='round';lnFail(e)}""",
"""      if(LG&&s>=1.2)try{lnStroke(c,LG,wk,cwz+9,s,g=>g.kc===0||g.kc>=3)}catch(e){c.lineCap='round';lnFail(e)}
      if(JF&&s>=1.2)try{jzHalo(c,JF,wk,cwz+9,s,kc=>kc===0||kc>=3)}catch(e){c.lineCap='round';lnFail(e)}""")
rep("""      if(LG)try{lnStroke(c,LG,shw,cwz+2,s)}catch(e){c.lineCap='round';lnFail(e)}""",
"""      if(LG)try{lnStroke(c,LG,shw,cwz+2,s)}catch(e){c.lineCap='round';lnFail(e)}
      if(JF)try{jzHalo(c,JF,shw,cwz+2,s)}catch(e){c.lineCap='round';lnFail(e)}""")
rep("""    if(LG)try{lnStroke(c,LG,g=>g.kc===1?pal.csMw:g.kc===2?pal.csPr:g.kc===3?pal.csSc:pal.casing,cwz+(dm?1.2:0),s)}catch(e){c.lineCap='round';lnFail(e)}   // obrysy dróg z pasami: pod wypełnieniem ulic bocznych (ich wloty zostają otwarte)""",
"""    if(LG)try{lnStroke(c,LG,g=>g.kc===1?pal.csMw:g.kc===2?pal.csPr:g.kc===3?pal.csSc:pal.casing,cwz+(dm?1.2:0),s)}catch(e){c.lineCap='round';lnFail(e)}   // obrysy dróg z pasami: pod wypełnieniem ulic bocznych (ich wloty zostają otwarte)
    if(JF)try{jzCasing(c,JF,pal,cwz,dm,s,0)}catch(e){c.lineCap='round';lnFail(e)}   // Wersja 199: obrys jezdni z pasami (na ziemi) – też pod wypełnieniem ulic bocznych""")
rep("""    if(D.BR&&D.BR.length)try{drawBridges(c,D.BR,BO,'road')}catch(e){c.setLineDash([]);c.lineCap='round';errNote('mosty',e)}   // mosty i wiadukty (nad drogami niższego poziomu)
    const tramDraw=()=>{if(P.tram&&s>=.3){c.lineCap='round';c.lineJoin='round';c.setLineDash([]);c.strokeStyle=night?'#6f7a96':'#9aa0aa';c.lineWidth=Math.max(1.6,rlw*.4)/s;c.stroke(P.tram)}};
    let tramDone=false;   // Wersja 194: na drogach z pasami tory rysujemy po asfalcie, a przed liniami pasów (linie i strzałki nad szynami)
    if(LG)try{lnBody(c,LG,LV,pal,s,dm,night,lite||ecoOn,()=>{tramDraw();tramDone=true})}catch(e){c.setLineDash([]);c.lineCap='round';lnFail(e)}   // wypełnienie, linie pasów, strzałki""",
"""    const tramDraw=()=>{if(P.tram&&s>=.3){c.lineCap='round';c.lineJoin='round';c.setLineDash([]);c.strokeStyle=night?'#6f7a96':'#9aa0aa';c.lineWidth=Math.max(1.6,rlw*.4)/s;c.stroke(P.tram)}};
    let tramDone=false;   // Wersja 194: na drogach z pasami tory rysujemy po asfalcie, a przed liniami pasów (linie i strzałki nad szynami)
    if(JF)try{jzBody(c,JF,pal,s,dm,night,()=>{tramDraw();tramDone=true},0,cwz)}catch(e){c.setLineDash([]);c.lineCap='round';lnFail(e)}   // Wersja 199: jezdnie z pasami na ziemi – wypełnienie, tory, linie; przed mostami (most zasłania drogę pod sobą)
    if(D.BR&&D.BR.length)try{drawBridges(c,D.BR,BO,'road')}catch(e){c.setLineDash([]);c.lineCap='round';errNote('mosty',e)}   // mosty i wiadukty (nad drogami niższego poziomu)
    if(LG)try{lnBody(c,LG,LV,pal,s,dm,night,lite||ecoOn,()=>{tramDraw();tramDone=true})}catch(e){c.setLineDash([]);c.lineCap='round';lnFail(e)}   // wypełnienie, linie pasów, strzałki
    if(JF)try{jzBody(c,JF,pal,s,dm,night,null,1,cwz)}catch(e){c.setLineDash([]);c.lineCap='round';lnFail(e)}   // Wersja 199: jezdnie z pasami na mostach i wiaduktach""")
rep('<span id="ver">wersja 198<','<span id="ver">wersja 199<')
open(dst,'w').write(s);print('zapisano',dst,len(s))
