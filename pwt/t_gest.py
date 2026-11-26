# Gesty i wydajność: długa trasa w widoku całej trasy, przesuwanie mapy w podglądzie i w jeździe, „zawieszony” dotyk, dwa palce, lot kamery w trakcie przeciągania.
import asyncio,sys,os,math
sys.path.insert(0,'/tmp/pwt')
import h as H
from h import *
t=T()
la0,lo0=51.10,17.03
H.SYNTH_ROUTE=[(la0+i*0.0009,lo0+0.3*math.sin(i/300)+i*0.00045) for i in range(3000)]
CAM="()=>({lat:vf.cam.lat,lon:vf.cam.lon,s:scaleCur,free:freeCam,ovw:!!ovw,gl:!!panGlide,np:window.__ptrs?window.__ptrs():-1})"
def mv(a,b):return math.hypot((a['lat']-b['lat'])*111195,(a['lon']-b['lon'])*111195*math.cos(math.radians(a['lat'])))
async def TE(cdp,typ,pts):await cdp.send('Input.dispatchTouchEvent',{'type':typ,'touchPoints':[{'x':x,'y':y,'id':i} for i,(x,y) in pts]})
async def drag(pg,cdp,x,y,dx,dy,steps=12,mid=None):
    await TE(cdp,'touchStart',[(1,(x,y))])
    for k in range(1,steps+1):
        await TE(cdp,'touchMove',[(1,(x+dx*k/steps,y+dy*k/steps))]);await pg.wait_for_timeout(20)
        if mid and k==steps//2:await mid()
    await TE(cdp,'touchEnd',[]);await pg.wait_for_timeout(300)
async def main():
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=la0,lon=lo0)
        cdp=await pg.context.new_cdp_session(pg)
        await goto(pg,la0,lo0,hd=0,speed=0,zoom=None,tilt=None,wait=1500)
        await pg.evaluate("(()=>{const o=window.drawRouteTop;window.__dr=[];window.drawRouteTop=function(){const t=performance.now();const r=o.apply(this,arguments);window.__dr.push(performance.now()-t);return r};window.__dbgRt=o=>{window.__rt=o}})()")
        R=H.SYNTH_ROUTE
        await plan(pg,R[-1][0],R[-1][1],frm=R[0]);await pg.wait_for_timeout(4000)
        await pg.evaluate("window.__dr=[]");await pg.wait_for_timeout(2500)
        r=await pg.evaluate("(()=>{const o=window.__dr.slice().sort((a,b)=>a-b);return {len:Math.round(route.len/1000),n:o.length,med:o[o.length>>1],p90:o[Math.floor(o.length*.9)],pts:window.__rt&&window.__rt.pts.length}})()")
        print('   widok całej trasy:',r)
        t('długa trasa, widok całej trasy: linia z rozsądnej liczby punktów (< 5000)',r['pts'] and r['pts']<5000,r)
        t('… rysowanie linii trasy szybkie (mediana ≤ 5 ms, 90% ≤ 10 ms)',r['n']>20 and r['med']<=5 and r['p90']<=10,r)
        a=await pg.evaluate(CAM);await drag(pg,cdp,200,300,0,150);c=await pg.evaluate(CAM)
        t('podgląd trasy: przeciąganie przesuwa mapę (o ok. 150 px)',abs(mv(a,c)*a['s']-150)<25 and not c['ovw'],(mv(a,c)*a['s'],c))
        await pg.evaluate("document.getElementById('view').dispatchEvent(new PointerEvent('pointerdown',{pointerId:77,isPrimary:true,pointerType:'touch',clientX:120,clientY:420,bubbles:true}))")
        a=await pg.evaluate(CAM);await drag(pg,cdp,200,300,60,120);c=await pg.evaluate(CAM)
        t('po „zawieszonym” dotyku przeciąganie jednym palcem przesuwa mapę',abs(mv(a,c)*a['s']-math.hypot(60,120))<25 and abs(c['s']/a['s']-1)<.02,(mv(a,c)*a['s'],a['s'],c['s']))
        t('… i nie zostają zapamiętane palce',c['np']==0,c)
        await pg.evaluate("""(()=>{const v=document.getElementById('view');v.dispatchEvent(new PointerEvent('pointerdown',{pointerId:78,isPrimary:true,pointerType:'touch',clientX:120,clientY:420,bubbles:true}));
          document.getElementById('zin').dispatchEvent(new PointerEvent('pointerup',{pointerId:78,isPrimary:true,pointerType:'touch',clientX:350,clientY:600,bubbles:true}))})()""")
        t('koniec dotyku nad przyciskiem: mapa zapomina ten palec',await pg.evaluate("window.__ptrs()")==0)
        await TE(cdp,'touchStart',[(1,(150,300)),(2,(250,400))])
        for k in range(1,6):await TE(cdp,'touchMove',[(1,(150-k*4,300-k*4)),(2,(250+k*4,400+k*4))]);await pg.wait_for_timeout(20)
        await TE(cdp,'touchEnd',[(1,(130,280))]);await pg.wait_for_timeout(900)
        b1=await pg.evaluate(CAM)
        for k in range(1,11):await TE(cdp,'touchMove',[(2,(270,420+k*10))]);await pg.wait_for_timeout(20)
        await TE(cdp,'touchEnd',[]);await pg.wait_for_timeout(300);c=await pg.evaluate(CAM)
        t('po zbliżaniu dwoma palcami pozostały palec przesuwa mapę',abs(mv(b1,c)*c['s']-100)<25 and abs(c['s']/b1['s']-1)<.02,(mv(b1,c)*c['s'],b1['s'],c['s']))
        async def mid():await pg.evaluate("fitFly(false)")
        await drag(pg,cdp,200,300,0,160,steps=16,mid=mid)
        await pg.wait_for_timeout(1800);c=await pg.evaluate(CAM)
        t('lot kamery zaczęty w trakcie przeciągania: palec wygrywa',not c['ovw'] and not c['gl'] and c['free'],c)
        await pg.evaluate("""(()=>{window.__st=[];let last='';const t0=performance.now();const f=()=>{const k=[freeCam?1:0,panGlide?(panGlide.keep?'K':(panGlide.fly?'F':'G')):'-',ovw?1:0,window.preview?1:0,window.__ptrs?window.__ptrs():-1].join('');if(k!==last){window.__st.push(Math.round(performance.now()-t0)+':'+k);last=k}requestAnimationFrame(f)};f();
          const on=window.onPos;})()""")
        await pg.evaluate("exitPreview(false);document.getElementById('start').click()");await pg.wait_for_timeout(2500)
        await pg.evaluate("window.__st.push('drag:'+Math.round(performance.now()))")
        a=await pg.evaluate(CAM);await drag(pg,cdp,200,300,0,150);c=await pg.evaluate(CAM)
        ok=mv(a,c)>20 and c['free']
        if not ok:print('   stan:',await pg.evaluate("window.__st.slice(-40)"))
        t('jazda z trasą: przeciąganie przesuwa mapę',ok,(mv(a,c),c))
        await pg.evaluate("recenter()");await pg.wait_for_timeout(2000)
        await pg.evaluate("routeOverview()");await pg.wait_for_timeout(2500)
        a=await pg.evaluate(CAM);await drag(pg,cdp,200,300,0,150);c=await pg.evaluate(CAM)
        t('przegląd trasy w czasie jazdy: przeciąganie przesuwa mapę',abs(mv(a,c)*a['s']-150)<25 and not c['ovw'],(mv(a,c)*a['s'],c))
        t('bez błędów strony',not logs,logs[:3])
        await b.close()
    t.end()
asyncio.run(main())
