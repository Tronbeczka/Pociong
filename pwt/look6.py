# zrzuty z liniami pasów (Wersja 206): czeka na dane o pasach i obliczenie linii; argumenty: TAG lat,lon,hd,s(px/m),tilt ...
import asyncio,sys,os
sys.path.insert(0,'/tmp/pwt')
from h import *
TAG=sys.argv[1];shots=[a.split(',') for a in sys.argv[2:]]
async def main():
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=float(shots[0][0]),lon=float(shots[0][1]),night=os.environ.get('NIGHT')=='1')
        for i,(la,lo,hd,s,tl) in enumerate(shots):
            await pg.evaluate("()=>{gpsOk=null}")
            sp=float(os.environ.get('SPEED','0'))
            await goto(pg,float(la),float(lo),hd=float(hd),speed=sp,zoom=float(s)/(2.8 if sp<7 else 2.05 if sp<13.9 else 1.5 if sp<22.2 else 1.1),tilt=float(tl),wait=1000)
            for _ in range(80):
                r=await pg.evaluate("(()=>{try{return {n:LANEW.size,b:lnBusy||lnQ.length>0,q:typeof LL!=='undefined'?LL.Q.length:0,t:performance.now()}}catch(e){return {n:1,b:false,q:0,t:1e9}}})()")
                if r['n']>0 and not r['b'] and r['q']==0:break
                await pg.wait_for_timeout(500)
            await pg.wait_for_timeout(1500)
            await pg.evaluate("()=>{vd=null}");await pg.wait_for_timeout(1200)
            st=await pg.evaluate("(()=>{try{return {lanew:LANEW.size,res:LL.res.size,n:LL.n,ms:Math.round(LL.ms),groups:LL.P?LL.P.list.length:0,err:window.__lnErr||null}}catch(e){return String(e)}})()")
            print(i,st,flush=True)
            await pg.screenshot(path=f'/tmp/shots/{TAG}_{i}.png')
        if logs:print('błędy',logs[:3])
        await b.close()
asyncio.run(main())
