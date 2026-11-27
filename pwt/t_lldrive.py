# jazda przez miasto (50 km/h, procesor 4× wolniejszy): czasy malowania mapy i pracy w tle (linie pasów) – porównanie wersji
import asyncio,sys,os,json,statistics,math
sys.path.insert(0,'/tmp/pwt')
from h import *
RATE=float(os.environ.get('RATE','4'))
A=(51.1115,17.0600);B=(51.1135,17.0225)
INSTR="""()=>{window.__pt=[];const o=paintVec;paintVec=function(){const t=performance.now();const r=o.apply(this,arguments);window.__pt.push(+(performance.now()-t).toFixed(1));return r};
  window.__lp=[];if(typeof llPump==='function'){const op=llPump;llPump=function(){const t=performance.now();const r=op.apply(this,arguments);window.__lp.push(+(performance.now()-t).toFixed(1));return r}}
  window.__fr=[];let lt=performance.now();const tick=()=>{const t=performance.now();window.__fr.push(t-lt);lt=t;requestAnimationFrame(tick)};requestAnimationFrame(tick)}"""
async def run(app,co):
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=co[0][0],lon=co[0][1],app=app)
        cum,at=poly(co);la,lo,hd=at(0)
        await goto(pg,la,lo,hd=hd,speed=0,zoom=None,tilt=50,wait=1500)
        for _ in range(60):
            r=await pg.evaluate("(()=>{try{return !lnBusy&&lnQ.length===0&&(typeof LL==='undefined'||LL.Q.length===0)}catch(e){return true}})()")
            if r:break
            await pg.wait_for_timeout(500)
        await pg.wait_for_timeout(1500)
        cdp=await pg.context.new_cdp_session(pg);await cdp.send('Emulation.setCPUThrottlingRate',{'rate':RATE})
        await pg.evaluate(INSTR)
        d=0.0;L=cum[-1]
        while d<L-30:
            la,lo,hd=at(d);await fix(pg,la,lo,hd,14);await pg.wait_for_timeout(300);d+=14
        r=await pg.evaluate("()=>({pt:window.__pt,lp:window.__lp,fr:window.__fr.slice(5),vq,n:typeof LL!=='undefined'?LL.n:0})")
        await b.close()
        return r,logs,L
def summ(r):
    pt=r['pt'];lp=r['lp'];fr=r['fr']
    return dict(paints=len(pt),paint_max=max(pt) if pt else 0,paint_med=statistics.median(pt) if pt else 0,paint_sum=round(sum(pt)),bg=len(lp),bg_max=max(lp) if lp else 0,bg_sum=round(sum(lp)),
                fr_over50=sum(1 for x in fr if x>50),fr_over100=sum(1 for x in fr if x>100),vq=round(r['vq'],2),ll=r['n'])
async def main():
    co,j=osrm_route(A,B)
    for app in sys.argv[1:]:
        r,logs,L=await run(app,co)
        print(os.path.basename(app),'trasa',round(L),'m',summ(r),'błędy' if logs else '',logs[:2])
asyncio.run(main())
