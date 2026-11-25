# Podstawy: wczytanie, mapa, noc/dzień, nachylenie, planowanie trasy, nawigacja w jeździe, zjazd z trasy i nowa trasa, koniec trasy.
import asyncio,sys,os,math
sys.path.insert(0,'/tmp/pwt')
import h as H
from h import *
t=T()
PIX="""(()=>{const c=document.getElementById('vmap'),x=c.getContext('2d'),W=c.width,Hh=c.height,d=x.getImageData(0,Math.round(Hh*.3),W,Math.round(Hh*.4)).data;
  const m=new Map();let n=0;for(let i=0;i<d.length;i+=4*7){const k=(d[i]>>4)+'|'+(d[i+1]>>4)+'|'+(d[i+2]>>4);m.set(k,(m.get(k)||0)+1);n++}
  return {colors:m.size,n,top:[...m.values()].sort((a,b)=>b-a)[0]/n}})()"""
async def main():
    async with async_playwright() as p:
        A=(51.1100,17.0310);B=(51.1009,17.0420)
        co,j=osrm_route(A,B);cum,at=poly(co)
        la,lo,hd=at(0)
        b,pg,logs=await launch(p,lat=la,lon=lo)
        await goto(pg,la,lo,hd=hd,speed=0,zoom=None,tilt=None,wait=2000)
        r=await pg.evaluate("({v:!!vecData,err:vecErr,rs:vecData&&vecData.RS?vecData.RS.length:0,ver:(document.getElementById('setVer')||{}).textContent||''})")
        t('mapa wektorowa wczytana (drogi, bez błędu)',r['v'] and not r['err'] and r['rs']>50,r)
        px=await pg.evaluate(PIX)
        t('mapa narysowana (wiele kolorów, tło nie dominuje)',px['colors']>40 and px['top']<.8,px)
        await pg.evaluate("document.getElementById('night').click()");await pg.wait_for_timeout(1200)
        n1=await pg.evaluate("night");px2=await pg.evaluate(PIX)
        t('przełącznik nocy działa',n1 is True and px2['colors']>30,(n1,px2))
        await pg.evaluate("document.getElementById('night').click()");await pg.wait_for_timeout(800)
        tl=[]
        for _ in range(3):
            await pg.evaluate("document.getElementById('tilt').click()");await pg.wait_for_timeout(400);tl.append(await pg.evaluate("tiltDeg"))
        t('przycisk nachylenia przechodzi przez 3 stany',len(set(tl))==3,tl)
        # trasa przez planer
        await plan(pg,*B);await pg.wait_for_timeout(3000)
        r=await pg.evaluate("({r:!!route,n:route&&route.pts.length,st:route&&route.steps?route.steps.length:0,big:document.getElementById('big').textContent,dist:document.getElementById('dist').textContent})")
        t('trasa wyznaczona i nawigacja wystartowała',r['r'] and r['n']>10 and r['st']>=2,r)
        t('baner manewru ma treść',len(r['big'].strip())>0 and len(r['dist'].strip())>0,r)
        # jazda 700 m
        al=[];D0=None
        for k in range(0,70):
            d=min(cum[-1]-5,k*10);la,lo,hd=at(d);await fix(pg,la,lo,hd,10);await pg.wait_for_timeout(120)
            if k%10==0:al.append(round(await pg.evaluate("route.along")))
        t('postęp na trasie rośnie w czasie jazdy',all(al[i+1]>al[i] for i in range(len(al)-1)) and al[-1]>500,al)
        o0=H.STATS['osrm']
        # zjazd z trasy: 150 m w bok
        la,lo,hd=at(700)
        for k in range(1,16):
            await fix(pg,la+k*10/111195*math.cos(math.radians(hd+90)),lo+k*10/(111195*math.cos(math.radians(la)))*math.sin(math.radians(hd+90)),(hd+90)%360,10);await pg.wait_for_timeout(300)
        await pg.wait_for_timeout(3000)
        t('po zjechaniu z trasy aplikacja wyznacza nową trasę',H.STATS['osrm']>o0,(o0,H.STATS['osrm']))
        t('bez błędów strony',not logs,logs[:4])
        await b.close()
    t.end()
asyncio.run(main())
