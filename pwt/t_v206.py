# Wersja 206: linie pasów na jezdni (tylko linie na drogach z mapy). Uruchomienie: APP=v206.html REF=v205.html python3 t_v206.py
import asyncio,sys,os,math,json
sys.path.insert(0,'/tmp/pwt')
import h as H
from h import *
import llqa as QA
t=T()
APP=os.environ.get('APP','/tmp/app/v206.html');REF=os.environ.get('REF','/tmp/app/v205.html')
async def ready(pg,maxs=45):
    for _ in range(maxs*2):
        r=await pg.evaluate("(()=>{try{return {n:LANEW.size,b:lnBusy||lnQ.length>0,q:(typeof LL!=='undefined'?LL.Q.length:0)}}catch(e){return {n:1,b:false,q:0}}})()")
        if r['n']>0 and not r['b'] and r['q']==0:return True
        await pg.wait_for_timeout(500)
    return False
HASH="""()=>{const c=document.getElementById('vmap'),x=c.getContext('2d'),d=x.getImageData(0,0,c.width,c.height).data;let h1=0;for(let i=0;i<d.length;i+=4)h1=(h1*31+d[i]+(d[i+1]<<8)+(d[i+2]<<16))>>>0;return h1}"""
async def main():
    async with async_playwright() as p:
        la,lo=51.1115,17.0600
        b,pg,logs=await launch(p,lat=la,lon=lo,app=APP)
        await goto(pg,la,lo,hd=0,speed=0,zoom=1.0,tilt=0,wait=800)
        ok=await ready(pg)
        v=await pg.evaluate("document.getElementById('ver').textContent");t('wersja 206',v=='wersja 206',v)
        r=await pg.evaluate("""()=>({llOn,laneOn,leOn,lanew:LANEW.size,res:LL.res.size,withL:[...LL.res.values()].filter(r=>r&&r.L&&r.L.length).length,route:!!route,
            lab:getComputedStyle(document.getElementById('laneCb').closest('label')).display,chk:document.getElementById('laneCb').checked})""")
        print('  ',r)
        t('bez trasy: dane o pasach pobrane wokół auta i linie policzone',ok and r['lanew']>100 and r['withL']>50 and not r['route'],r)
        t('stary moduł pasów nadal wyłączony (laneOn, auto na pasie)',r['laneOn'] is False and r['leOn'] is False,r)
        t('przełącznik „Linie pasów na jezdni” widoczny i włączony',r['lab']!='none' and r['chk'] is True and r['llOn'] is True,r)
        # rysowanie: ile grup linii i czy stary moduł nie rysuje
        d=await pg.evaluate("""async()=>{window.__lnb=0;const f=lnBody;window.lnBody=function(){window.__lnb++;return f.apply(this,arguments)};let n=0;const o=llDraw;llDraw=function(c,D,s,pal,night,dm,z){const P=LL.P;const r=o.apply(this,arguments);n++;return r};
            vd=null;await new Promise(r=>setTimeout(r,900));const P=LL.P;llDraw=o;return {calls:n,groups:P?P.list.length:0,lnb:window.__lnb,free:freeLanePos(),lp:route&&route.lp?1:0}}""")
        t('linie rysowane na mapie (grupy ścieżek), stary moduł nic nie rysuje',d['calls']>=2 and d['groups']>5 and d['lnb']==0 and d['free'] is None,d)
        # kontrola jakości w trzech miejscach
        for name,qa,qo in [('pl. Grunwaldzki',51.1115,17.0600),('pl. Powstańców Warszawy',51.1066,17.0450),('Kazimierza Wielkiego',51.1095,17.0300)]:
            await pg.evaluate("()=>{gpsOk=null}");await goto(pg,qa,qo,hd=0,speed=0,zoom=1.0,tilt=0,wait=600);await ready(pg);await pg.wait_for_timeout(800)
            q=await pg.evaluate(QA.JS)
            print('  ',name,{k:q[k] for k in ('lines','cross','out','tot','dup')})
            t(f'{name}: linie różnych dróg się nie przecinają, nie wychodzą poza jezdnię',q['lines']>40 and q['cross']==0 and q['out']==0,q)
        # zbliżanie i przesuwanie: nic się nie przelicza
        n0=await pg.evaluate("LL.n")
        for dz in [1.02]*40+[1/1.02]*40:
            await pg.evaluate("(d)=>{ovwOff();setZoom(zoomMul*d);updRecenter()}",dz);await pg.wait_for_timeout(16)
        await pg.mouse.move(195,420);await pg.mouse.down()
        for i in range(1,31):await pg.mouse.move(195+4*i,420+6*i);await pg.wait_for_timeout(16)
        await pg.mouse.up();await pg.wait_for_timeout(1200)
        n1=await pg.evaluate("LL.n");t('zbliżanie i przesuwanie mapy nie przelicza linii',n1==n0,(n0,n1))
        # wyłączenie w ustawieniach: mapa jak w wersji 205
        await pg.evaluate("()=>{const e=document.getElementById('laneCb');e.checked=false;e.onchange()}");await pg.wait_for_timeout(1200)
        r2=await pg.evaluate("()=>({llOn,ls:localStorage.getItem('llOn')})")
        t('wyłączenie: llOn=false i zapamiętane',r2['llOn'] is False and r2['ls']=='false',r2)
        await pg.evaluate("()=>{const e=document.getElementById('laneCb');e.checked=true;e.onchange()}");await pg.wait_for_timeout(800)
        t('bez błędów strony',not logs,logs[:3])
        await b.close()
    # z wyłączonymi liniami płótno mapy piksel w piksel jak w wersji 205
    hs=[]
    for app in (REF,APP):
        async with async_playwright() as p:
            b,pg,logs=await launch(p,lat=51.1066,lon=17.0450,app=app,ls={'llOn':'false'})
            await goto(pg,51.1066,17.0450,hd=20,speed=0,zoom=1.0,tilt=0,wait=2500)
            await pg.evaluate("()=>{vd=null}");await pg.wait_for_timeout(900)
            hs.append(await pg.evaluate(HASH));await b.close()
    t('linie wyłączone: mapa piksel w piksel jak w wersji 205',hs[0]==hs[1],hs)
    t.end()
asyncio.run(main())
