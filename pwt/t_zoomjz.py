# Wersja 202: zbliżanie dwoma palcami – w trakcie gestu jezdnie z pasami nie liczą się od nowa (szerokość dróg „zamrożona”),
# po zdjęciu palców: jeden poziom szerokości dla zwykłych dróg i jezdni z pasami, linie dla widocznych fragmentów gotowe w ciągu ok. 2 s
import asyncio,sys,os,math,json
sys.path.insert(0,'/tmp/pwt')
from h import *
import t_jz as TJ
t=T()
async def main():
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=51.10850,lon=17.04780)
        await goto(pg,51.10850,17.04780,hd=250,speed=0,zoom=1.0,tilt=50,wait=1500);await TJ.wait_ready(pg);await pg.wait_for_timeout(2000)
        await pg.evaluate("""()=>{window.__nb=0;const ob=jzBucket;jzBucket=function(N,s){const had=N.bk.size,B=ob(N,s);if(N.bk.size!==had)window.__nb++;return B};
          window.__pp=window.__ptrs;window.__ptrs=()=>window.__fing?2:window.__pp()}""")
        lv0=await pg.evaluate("()=>rwLv")
        # gest: palce na ekranie, skala ×1,013 przez 50 kroków (2,8 → ok. 5 px/m), potem ×1/1,013 przez 70 kroków (do ok. 2,2 px/m)
        await pg.evaluate("()=>{window.__fing=true;window.__nb=0}")
        for d in [1.013]*50+[1/1.013]*70:
            await pg.evaluate("(d)=>{ovwOff();setZoom(zoomMul*d);updRecenter()}",d);await pg.wait_for_timeout(20)
        r1=await pg.evaluate("()=>({nb:window.__nb,lv:rwLv,s:scaleCur})")
        print('   w trakcie gestu:',r1)
        t('w trakcie gestu (palce na ekranie) jezdnie z pasami nie liczą się od nowa i szerokość dróg się nie zmienia',r1['nb']==0 and r1['lv']==lv0,dict(r1,lv0=lv0))
        await pg.evaluate("()=>{window.__fing=false}")
        ok=None
        for i in range(40):
            await pg.wait_for_timeout(100)
            r2=await pg.evaluate("""()=>{const F=jzFrame.last;   /* ostatnio malowany obszar */
              return {lv:rwLv,want:rwLvFor(scaleCur),key:F&&F.B.key,cur:jzKey(scaleCur),pend:F?jzPending(F):-1,stale:!!(JZN&&JZN.stale)}}""")
            if r2['lv']==r2['want'] and r2['key']==r2['cur'] and r2['pend']==0:ok=(i+1)*100;break
        print('   po geście:',r2,'gotowe po',ok,'ms')
        t('po zdjęciu palców: szerokość dróg i jezdni z pasami dla nowej skali, linie w widoku gotowe w ≤ 4 s',ok is not None,r2)
        t('bez błędów strony',not logs,logs[:3])
        await b.close()
    t.end()
asyncio.run(main())
