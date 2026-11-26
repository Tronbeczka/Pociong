# Wersja 199: płynna zmiana skali – linie pasów nie znikają (poprzednia skala do czasu policzenia nowej), nowa geometria najwyżej co 250 ms
import asyncio,sys,os,math,json
sys.path.insert(0,'/tmp/pwt')
from h import *
import t_jz as TJ
t=T()
async def main():
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=51.1116,lon=17.0593)
        await goto(pg,51.1116,17.0593,hd=297,speed=0,zoom=1.0,tilt=0,wait=1500);await TJ.wait_ready(pg);await pg.wait_for_timeout(1500)
        r=await pg.evaluate("""async()=>{const D=vecData,kx=111195*Math.cos(rad(D.lat)),c=vecCam(performance.now()),ox=(c.lon-D.lon)*kx,oy=(c.lat-D.lat)*111195;
          const cv=document.createElement('canvas');cv.width=600;cv.height=600;const cx=cv.getContext('2d');const pal=PAL[night?'night':'day'];
          const res=[];let s=.75,nb=0,miss=0,maxms=0,keys=new Set(),had=new Set();
          for(let f=0;f<90;f++){s*=0.9977;const t0=performance.now();const F=jzFrame(D,s,ox,oy,600);
            if(F){cx.setTransform(1,0,0,1,0,0);cx.translate(300,300);cx.scale(s,-s);cx.translate(-ox,-oy);jzBody(cx,F,pal,s,false,night,null,0,4);
              keys.add(F.B.key);const now=new Set();for(const G of F.G){const has=!!(G.lines||G.old);if(had.has(G.ch.id)&&!has)miss++;if(has)now.add(G.ch.id)}had=now}
            maxms=Math.max(maxms,performance.now()-t0);await new Promise(r=>setTimeout(r,16))}
          return {frames:90,buckets:keys.size,miss,maxms:+maxms.toFixed(1),s0:scaleCur,s1:s}}""")
        print('  ',r)
        t('płynne oddalanie przy małej skali (90 klatek po ok. 16 ms, skala 0,75→0,61): nowa geometria rzadko (≤ 8 razy)',r['buckets']<=8,r)
        t('linie nie znikają: jezdnia, która miała linie, ma je w kolejnej klatce (nowe albo z poprzedniej skali)',r['miss']==0,r)
        t('bez błędów strony',not logs,logs[:3])
        await b.close()
    t.end()
asyncio.run(main())
