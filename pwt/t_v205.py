# Wersja 205: (1) po wyszukaniu miejsca przycisk „do auta” (i „Wróć do mojej pozycji”) wraca do auta – ostatniej pozycji z GPS – a nie do oglądanego miejsca;
# (2) panel strzałek pasów u góry ekranu przed skrzyżowaniami: dane pobierane w tle wzdłuż trasy (także gdy zapytanie o pojedynczy manewr się nie uda);
# na jezdni nic się nie rysuje. Uruchomienie: APP=wersja.html python3 t_v205.py
import asyncio,sys,os,math,json
sys.path.insert(0,'/tmp/pwt')
import h as H
from h import *
t=T()
A=(51.1100,17.0310);B=(51.1009,17.0420)   # auto (A) i wyszukane miejsce (B), ok. 1,3 km
ST="""()=>{const c=vecCam(performance.now()),c0=vecCam0(performance.now()),ci=document.getElementById('carIcon');
  return {browse:!!window.browse,preview:!!window.preview,cam:c?[c.lat,c.lon]:null,car:c0?[c0.lat,c0.lon]:null,nofix:document.body.classList.contains('nofix'),
    carVis:getComputedStyle(ci).display!=='none',rc:getComputedStyle(document.getElementById('recenter')).display,freeCam,watch:watchId!=null}}"""
NOGPS="()=>{const g=navigator.geolocation;Object.defineProperty(g,'watchPosition',{value:()=>4242,configurable:true,writable:true});Object.defineProperty(g,'clearWatch',{value:()=>{},configurable:true,writable:true})}"
def dm(a,b):return math.hypot((a[0]-b[0])*111195,(a[1]-b[1])*111195*math.cos(math.radians(a[0])))
async def browse_to_B(pg):
    await pg.evaluate("(b)=>enterBrowse({lat:b[0],lon:b[1],title:'Test',sub:'',label:'Test'})",list(B));await pg.wait_for_timeout(2500)
    await pg.mouse.move(195,420);await pg.mouse.down()
    for i in range(1,21):await pg.mouse.move(195+5*i,420+7*i);await pg.wait_for_timeout(16)
    await pg.mouse.up();await pg.wait_for_timeout(600)
    await pg.evaluate(NOGPS)   # telefon nie podał jeszcze nowej pozycji (przeglądarka testowa podaje ją od razu)
    return await pg.evaluate(ST)
async def main():
    ver=os.environ.get('VER','wersja 205')
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=A[0],lon=A[1])
        await goto(pg,A[0],A[1],hd=90,speed=0,zoom=None,tilt=0,wait=1500)
        v=await pg.evaluate("document.getElementById('ver').textContent")
        t(ver,v==ver,v)
        # 1) wyszukane miejsce → przesunięcie mapy → przycisk „do auta”
        r0=await browse_to_B(pg)
        t('podgląd wyszukanego miejsca: mapa przy nim, przycisk „do auta” widoczny',r0['browse'] and dm(r0['cam'],B)<400 and r0['rc']!='none',r0)
        await pg.evaluate("document.getElementById('recenter').click()");await pg.wait_for_timeout(1500)
        r1=await pg.evaluate(ST)
        print('   po „do auta”:',r1,'od auta',round(dm(r1['cam'],A)),'m, od miejsca',round(dm(r1['cam'],B)),'m')
        t('przycisk „do auta”: koniec podglądu, GPS włączony',not r1['browse'] and not r1['preview'] and r1['watch'],r1)
        t('… mapa wraca do auta (ostatnia pozycja z GPS), a nie do wyszukanego miejsca',dm(r1['cam'],A)<60 and dm(r1['car'],A)<30,(round(dm(r1['cam'],A)),round(dm(r1['cam'],B))))
        t('… auto szare, dopóki nie przyjdzie nowy odczyt GPS',r1['nofix'] and r1['carVis'],r1)
        await fix(pg,A[0]+2e-5,A[1],90,0);await pg.wait_for_timeout(1200)
        r2=await pg.evaluate(ST)
        t('… po odczycie GPS auto zwykłe, w miejscu z GPS',not r2['nofix'] and dm(r2['car'],(A[0]+2e-5,A[1]))<15,r2)
        # 2) „Wróć do mojej pozycji (GPS)”
        await browse_to_B(pg)
        await pg.evaluate("document.getElementById('brwBack').click()");await pg.wait_for_timeout(1500)
        r3=await pg.evaluate(ST)
        t('„Wróć do mojej pozycji”: od razu przy aucie (bez czekania na GPS)',not r3['browse'] and dm(r3['cam'],A)<60 and r3['nofix'],(r3,round(dm(r3['cam'],A))))
        await fix(pg,A[0],A[1],90,0);await pg.wait_for_timeout(800)
        # 2b) „Prowadź tutaj”: trasa od auta, nie od wyszukanego miejsca (telefon jeszcze bez nowego odczytu)
        for wait in (3000,35000):
            await browse_to_B(pg)
            if wait>3000:await pg.wait_for_timeout(wait)   # dłuższe oglądanie: ostatni odczyt GPS starszy niż 30 s – trasa czeka na odczyt z telefonu
            await pg.evaluate("()=>{Object.defineProperty(navigator.geolocation,'getCurrentPosition',{value:(ok)=>{setTimeout(()=>ok({coords:{latitude:%f,longitude:%f,accuracy:5}}),1500)},configurable:true,writable:true})}"%A)
            await pg.evaluate("document.getElementById('brwGo').click()");await pg.wait_for_timeout(6000)
            rg=await pg.evaluate("()=>route?{start:route.pts[0],len:Math.round(route.len)}:null")
            t(f'„Prowadź tutaj” (oglądanie {wait//1000} s): trasa od auta do wyszukanego miejsca',rg is not None and dm(rg['start'],A)<150 and dm(rg['start'],B)>800 and rg['len']>800,(rg,rg and round(dm(rg['start'],A))))   # start trasy: najbliższa droga przy aucie (ok. 90 m od punktu A)
            await pg.evaluate("()=>{try{clearRoute()}catch(e){}}");await fix(pg,A[0],A[1],90,0);await pg.wait_for_timeout(800)
        # 2c) podgląd śledzonego kierowcy (link „śledź”): przycisk „do auta” wraca do niego, jak dotąd
        await pg.evaluate("(b)=>{enterBrowse({lat:b[0],lon:b[1],title:'Kierowca',sub:'',label:'Kierowca'});window.brwLive=true}",list(B));await pg.wait_for_timeout(2000)
        await pg.mouse.move(195,420);await pg.mouse.down()
        for i in range(1,21):await pg.mouse.move(195+5*i,420+7*i);await pg.wait_for_timeout(16)
        await pg.mouse.up();await pg.wait_for_timeout(600)
        await pg.evaluate("document.getElementById('recenter').click()");await pg.wait_for_timeout(1500)
        rl=await pg.evaluate(ST)
        t('podgląd śledzonego kierowcy: „do auta” wraca do kierowcy (podgląd zostaje)',rl['browse'] and dm(rl['cam'],B)<60,(rl,round(dm(rl['cam'],B))))
        await pg.evaluate("document.getElementById('brwBack').click()");await pg.wait_for_timeout(800);await fix(pg,A[0],A[1],90,0);await pg.wait_for_timeout(800)
        # 3) bez żadnej znanej pozycji: auto szare w miejscu, mapa nie skacze
        await pg.evaluate("()=>{gpsOk=null;try{localStorage.removeItem('lastpos')}catch(e){}}")
        await browse_to_B(pg)
        await pg.evaluate("document.getElementById('recenter').click()");await pg.wait_for_timeout(1200)
        r4=await pg.evaluate(ST)
        t('bez znanej pozycji: koniec podglądu, auto szare (czeka na GPS)',not r4['browse'] and r4['nofix'] and r4['watch'],r4)
        await fix(pg,A[0],A[1],90,0);await pg.wait_for_timeout(1500)
        r5=await pg.evaluate(ST)
        t('… pierwszy odczyt GPS: mapa przy aucie, auto zwykłe',dm(r5['cam'],A)<60 and not r5['nofix'],(r5,round(dm(r5['cam'],A))))
        t('bez błędów strony (część 1)',not logs,logs[:3])
        await b.close()
    # 4) panel strzałek pasów w czasie nawigacji (dwa przebiegi: zwykły i z nieudanym zapytaniem o pojedynczy manewr)
    for fail in (False,True):
        async with async_playwright() as p:
            la,lo,hd,tg=roadpos(51.10690,17.04720,('primary','secondary','tertiary'),False)
            b,pg,logs=await launch(p,lat=la,lon=lo)
            await goto(pg,la,lo,hd=hd,speed=0,zoom=None,tilt=50,wait=1500)
            await pg.evaluate("(()=>{window.__lnb=0;const f=lnBody;window.lnBody=function(){window.__lnb++;return f.apply(this,arguments)};return 0})()")
            if fail:await pg.evaluate("()=>{const of=fetchOverpass;fetchOverpass=function(q){if(/around:22/.test(q))return Promise.reject(new Error('test: brak odpowiedzi'));return of.apply(this,arguments)}}")
            for k in range(4):await fix(pg,la,lo,hd,0);await pg.wait_for_timeout(700)
            n0=await pg.evaluate("LANEW.size")
            await plan(pg,51.104,17.0395);await pg.wait_for_timeout(4000)
            seen={};cnt=0;arrows=[]
            L=await pg.evaluate("route?route.len:0")
            d=0.0
            while d<L-20:
                q=await pg.evaluate("(d)=>{if(!route)return null;const a=routeAt(route,d),b=routeAt(route,Math.min(route.len,d+6));return [a[0],a[1],bear(a[0],a[1],b[0],b[1])]}",d)
                if q is None:print('   trasa zakończona przy',round(d),'m');break
                await fix(pg,q[0],q[1],q[2],9);await pg.wait_for_timeout(350)
                r=await pg.evaluate("()=>{const e=document.getElementById('lanes');return {i:nav?nav.i:-1,d:nav?Math.round(nav.d):0,show:getComputedStyle(e).display!=='none',key:e.dataset.key||'',st:nav&&route.steps[nav.i]?route.steps[nav.i].type+' '+(route.steps[nav.i].mod||''):''}}")
                if r['show']:seen.setdefault(r['i'],[r['key'],r['d'],r['st']]);cnt+=1
                if r['show'] and 30<r['d']<200:   # strzałki na jezdni przed manewrem (drawLaneArrow): ile razy rysuje
                    na=await pg.evaluate("()=>{let n=0;const s=mx.stroke,f=mx.fill;mx.stroke=function(){n++;return s.apply(this,arguments)};mx.fill=function(){n++;return f.apply(this,arguments)};try{drawLaneArrow()}finally{mx.stroke=s;mx.fill=f}return n}")
                    arrows.append(na)
                d+=9
            z=await pg.evaluate("""()=>{const D=vecData,s=scaleCur,kx=111195*Math.cos(rad(D.lat)),c=vecCam(performance.now());
               return {lanew:LANEW.size,lnb:window.__lnb,vis:lnVis(D,s,(c.lon-D.lon)*kx,(c.lat-D.lat)*111195,600).length,lp:route&&route.lp?1:0,free:freeLanePos(),laneOn,err:window.__lnErr||null}}""")
            tag='(zapytanie o manewr nieudane) ' if fail else ''
            print('  ',tag,'panel przy krokach:',seen,'dane:',z,'przed trasą:',n0)
            t(tag+'bez trasy dane o pasach nie są pobierane',n0==0,n0)
            t(tag+'w nawigacji dane o pasach pobrane w tle',z['lanew']>0,z)
            t(tag+'panel przed skrętem w prawo (Traugutta): 3 pasy, właściwy prawy',2 in seen and seen[2][0].startswith('L|L|LR') and 'false,false,true' in seen[2][0],seen.get(2))
            t(tag+'panel przed skrętem w lewo (Podwale): 4 pasy, właściwe dwa lewe',5 in seen and seen[5][0].startswith('L|L|S|S') and 'true,true,false,false' in seen[5][0],seen.get(5))
            print('   strzałki na jezdni (liczba rysowań w kolejnych klatkach):',arrows[:12])
            t(tag+'bez strzałek pasów na jezdni przed manewrem (tylko panel u góry)',len(arrows)>3 and max(arrows)==0,arrows[:12])
            t(tag+'na jezdni nic nie rysujemy (bez linii pasów, auto i trasa bez przesuwania na pas)',z['lnb']==0 and z['vis']==0 and z['lp']==0 and z['free'] is None and z['laneOn'] is False and not z['err'],z)
            t(tag+'bez błędów strony',not logs,logs[:3])
            await b.close()
    t.end()
asyncio.run(main())
