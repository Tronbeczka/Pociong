# Wersja 204: powrót do dróg z wersji 198 (bez jezdni z pasami z wersji 199–203) – te same sprawdzenia co t_nolane; cienie budynków sprawdza t_v204b
import asyncio,sys,os,math,json
sys.path.insert(0,'/tmp/pwt')
import h as H
from h import *
t=T()
ROUTE=[(51.107264,17.0437886),(51.1072801,17.0435088),(51.1073375,17.043157),(51.1074863,17.0422453),(51.1075481,17.0418875),(51.1076284,17.041417),
       (51.107711,17.0408232),(51.107767,17.0404812),(51.1077998,17.0403036),(51.1078734,17.0396134),(51.1079149,17.0392189)]   # Oławska na zachód, do placu Dominikańskiego
async def main():
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=51.1116,lon=17.0593)
        await goto(pg,51.1116,17.0593,hd=297,speed=0,zoom=2.4,tilt=50,wait=2000)
        await pg.evaluate("(()=>{window.__lnb=0;const f=lnBody;window.lnBody=function(){window.__lnb++;return f.apply(this,arguments)};return 0})()")
        for k in range(6):   # kilka klatek z ruchem mapy
            await fix(pg,51.1116+k*2e-5,17.0593-k*4e-5,297,5);await pg.wait_for_timeout(1200)
        r=await pg.evaluate("""(()=>{const D=vecData,s=scaleCur,kx=111195*Math.cos(rad(D.lat)),c=vecCam(performance.now());
          const lab=id=>{const e=document.getElementById(id);return e?getComputedStyle(e.closest('label')).display:'brak'};
          return {laneOn,leOn,lanew:LANEW.size,vis:lnVis(D,s,(c.lon-D.lon)*kx,(c.lat-D.lat)*111195,600).length,lnb:window.__lnb,lnErr:window.__lnErr||null,
            labLane:lab('laneCb'),labLe:lab('leCb'),ver:(document.getElementById('ver')||{}).textContent,free:freeLanePos(),rs:D.RS?D.RS.length:0}})()""")
        print('  ',r)
        t('wersja 204',r['ver']=='wersja 204',r['ver'])
        t('pasy ruchu i auto na pasie wyłączone',r['laneOn'] is False and r['leOn'] is False,r)
        t('dane o pasach nie są pobierane (ul. Marii Curie-Skłodowskiej)',r['lanew']==0 and r['vis']==0,r)
        t('stary moduł pasów nie rysuje niczego (0 wywołań w 6 klatkach)',r['lnb']==0 and not r['lnErr'],r)
        t('mapa z drogami narysowana',r['rs']>50,r['rs'])
        t('przełączniki „Pasy ruchu” i „Auto na pasie” ukryte w ustawieniach',r['labLane']=='none' and r['labLe']=='none',r)
        t('auto bez przesuwania na pas',r['free'] is None,r['free'])
        # zapisane dawniej ustawienia nie włączają starego modułu
        await pg.evaluate("LSput('laneOn',true);LSput('leOn',true)");await pg.reload();await pg.wait_for_timeout(4000)
        r2=await pg.evaluate("({laneOn,leOn})")
        t('zapamiętane dawniej „włączone” nie włącza starych pasów',r2['laneOn'] is False and r2['leOn'] is False,r2)
        # panel pasów przed skrzyżowaniem (nawigacja): strzałki pobierane z OpenStreetMap bez danych starego modułu
        H.SYNTH_ROUTE=ROUTE;cum,at=poly(ROUTE);la,lo,hd=at(0)
        await goto(pg,la,lo,hd=hd,speed=0,zoom=2.4,tilt=0,wait=1500)
        await plan(pg,*ROUTE[-1]);await pg.wait_for_timeout(2500)
        L=await pg.evaluate("""(async()=>{if(!route)return {err:'brak trasy'};const x=await fetchLanes(route,{off:route.len-3,type:'turn',mod:'left'});
          return x?{n:x.lanes.length,valid:x.valid,need:x.need,lanes:x.lanes.map(s=>[...s].join(''))}:{none:true,len:route.len}})()""")
        print('   panel pasów:',L)
        t('panel pasów: strzałki pasów przed skrętem w lewo (Oławska) wczytane z OpenStreetMap',L.get('n',0)>=4 and L.get('need')=='L' and L['valid'][0] is True and L['valid'][-1] is False,L)
        t('bez błędów strony',not logs,logs[:3])
        await b.close()
    t.end()
asyncio.run(main())
