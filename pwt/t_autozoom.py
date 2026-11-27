# Wersja 203: jazda ze zmianą prędkości (kamera oddala się przy 25 i 50 km/h) – szerokość dróg i jezdnie z pasami bez zmian (bez „skakania”); bez cieni budynków
import asyncio,sys,os,math,json
sys.path.insert(0,'/tmp/pwt')
from h import *
import t_jz as TJ
t=T()
async def main():
    async with async_playwright() as p:
        la,lo,hd=51.10594,17.04327,19.6   # ul. Traugutta / Pl. Społeczny – w stronę mostu Grunwaldzkiego
        b,pg,logs=await launch(p,lat=la,lon=lo)
        await goto(pg,la,lo,hd=hd,speed=0,zoom=1.0,tilt=50,wait=1500);await TJ.wait_ready(pg);await pg.wait_for_timeout(1500)
        await pg.evaluate("""()=>{window.__nb=0;window.__lv=[];const ob=jzBucket;jzBucket=function(N,s){const had=N.bk.size,B=ob(N,s);if(N.bk.size!==had)window.__nb++;return B};
          const od=drawVec;drawVec=function(){const r=od.apply(this,arguments);const l=window.__lv;if(!l.length||l[l.length-1]!==rwLv)l.push(rwLv);return r}}""")
        k=111195*math.cos(math.radians(la));x=0.0
        sp=[0,0,5,12,20,30,38,45,52,58,62,60,55,45,35,25,15,8,0,0,0]
        s_seen=[]
        for v in sp:
            ms=v/3.6;x+=ms
            await fix(pg,la+x*math.cos(math.radians(hd))/111195,lo+x*math.sin(math.radians(hd))/k,hd,ms)
            await pg.wait_for_timeout(1000)
            s_seen.append(round(await pg.evaluate("()=>scaleCur"),2))
        await pg.wait_for_timeout(1500)
        r=await pg.evaluate("()=>({nb:window.__nb,lv:window.__lv,sn:bld3Draw.sn||0,BLD_SH:typeof BLD_SH!=='undefined'?BLD_SH:null})")
        print('   skale:',s_seen);print('  ',r)
        t('jazda 0–62–0 km/h: kamera zmienia zbliżenie',max(s_seen)/min(s_seen)>1.4,s_seen)
        t('… a szerokość dróg zostaje ta sama (jeden poziom) i jezdnie z pasami nie liczą się od nowa',len(r['lv'])==1 and r['nb']==0,r)
        t('bez cieni budynków',r['BLD_SH'] is False,r)
        t('bez błędów strony',not logs,logs[:3])
        await b.close()
    t.end()
asyncio.run(main())
