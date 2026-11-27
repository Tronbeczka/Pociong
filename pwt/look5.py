# zrzut w punkcie z zadaną skalą (px/m) zamiast mnożnika: zoom = s/2.8 przy prędkości 0
import asyncio,sys,os
sys.path.insert(0,'/tmp/pwt')
from h import *
TAG=sys.argv[1];shots=[a.split(',') for a in sys.argv[2:]]
async def main():
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=float(shots[0][0]),lon=float(shots[0][1]))
        for i,(la,lo,hd,s,tl) in enumerate(shots):
            await goto(pg,float(la),float(lo),hd=float(hd),speed=0,zoom=float(s)/2.8,tilt=float(tl),wait=1500)
            for _ in range(30):
                if await pg.evaluate("(()=>{try{return LANEW.size>0&&!lnBusy&&!vecBusy}catch(e){return true}})()"):break
                await pg.wait_for_timeout(400)
            await pg.wait_for_timeout(2500)
            await pg.evaluate("()=>{vd=null}");await pg.wait_for_timeout(1200)
            await pg.screenshot(path=f'/tmp/shots/{TAG}_{i}.png')
        await b.close()
asyncio.run(main())
