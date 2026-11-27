# Ruszanie mapą na wolnym telefonie (procesor spowolniony CDP): czasy malowania mapy przy przeciąganiu palcem i przy zbliżaniu dwoma palcami
import asyncio,sys,os,json,statistics
sys.path.insert(0,'/tmp/pwt')
from h import *
import t_jz as TJ
RATE=float(os.environ.get('RATE','4'))
LA,LO,HD=51.10850,17.04780,250
INSTR="""()=>{window.__pt=[];window.__nb=0;window.__pr=[];const o=paintVec;paintVec=function(){const t=performance.now();window.__pr.push((vd?'p':'N')+(typeof rwLv!=='undefined'?rwLv:''));const r=o.apply(this,arguments);window.__pt.push(+(performance.now()-t).toFixed(1));return r};
  window.__jt={};for(const f of ['jzCasing','jzBody','jzHalo','jzFrame','jzLines','jzGeo']){if(typeof window[f]!=='function')continue;const of=window[f];window[f]=function(){const t=performance.now();try{return of.apply(this,arguments)}finally{window.__jt[f]=(window.__jt[f]||0)+performance.now()-t}}}
  if(typeof jzBucket==='function'){const ob=jzBucket;jzBucket=function(N,s){const n0=N.bk.size,B=ob(N,s);if(N.bk.size!==n0||!N.bk.has(B.key))window.__nb++;return B}}
  window.__fr=[];let lt=performance.now();const tick=()=>{const t=performance.now();window.__fr.push(t-lt);lt=t;if(window.__frOn)requestAnimationFrame(tick)};window.__frOn=true;requestAnimationFrame(tick)}"""
async def run(app):
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=LA,lon=LO,app=app)
        await goto(pg,LA,LO,hd=HD,speed=0,zoom=1.0,tilt=50,wait=1500);await TJ.wait_ready(pg);await pg.wait_for_timeout(2000)
        cdp=await pg.context.new_cdp_session(pg);await cdp.send('Emulation.setCPUThrottlingRate',{'rate':RATE})
        await pg.evaluate(INSTR);await pg.wait_for_timeout(1500)
        res={}
        # 1) przeciąganie palcem (mysz → zdarzenia wskaźnika): 300 px w dół i 200 w bok w 1,5 s, potem z powrotem
        await pg.evaluate("()=>{window.__pt=[];window.__fr=[];window.__nb=0;window.__pr=[];window.__jt={}}")
        await pg.mouse.move(195,420);await pg.mouse.down()
        for i in range(1,61):await pg.mouse.move(195+200*i/60,420+300*i/60);await pg.wait_for_timeout(16)
        for i in range(59,-1,-1):await pg.mouse.move(195+200*i/60,420+300*i/60);await pg.wait_for_timeout(16)
        await pg.mouse.up();await pg.wait_for_timeout(800)
        res['pan']=await pg.evaluate("()=>({jt:Object.fromEntries(Object.entries(window.__jt).map(([k,v])=>[k,+v.toFixed(1)])),pt:window.__pt.slice(),nb:window.__nb,fr:window.__fr.slice(),vq,vqCap:typeof vqCap!=='undefined'?vqCap:null})")
        # 2) zbliżanie dwoma palcami: skala ×2,2 w ok. 1,5 s i z powrotem (jak setZoom w obsłudze gestu)
        await pg.evaluate("()=>{window.__pt=[];window.__fr=[];window.__nb=0;window.__pr=[];window.__jt={}}")
        for d in [1.013]*60+[1/1.013]*60:
            await pg.evaluate("(d)=>{ovwOff();setZoom(zoomMul*d);updRecenter()}",d);await pg.wait_for_timeout(16)
        await pg.wait_for_timeout(1200)
        res['zoom']=await pg.evaluate("()=>({pr:window.__pr.join(' '),pt:window.__pt.slice(),nb:window.__nb,fr:window.__fr.slice(),vq,vqCap:typeof vqCap!=='undefined'?vqCap:null,s:scaleCur})")
        await b.close()
        return res,logs
def summ(r):
    pt=r['pt'];fr=[x for x in r['fr'][2:]]
    return dict(paints=len(pt),paint_max=max(pt) if pt else 0,paint_med=statistics.median(pt) if pt else 0,slow110=sum(1 for x in pt if x>110),
                frame_max=round(max(fr),1) if fr else 0,frames_over50=sum(1 for x in fr if x>50),buckets=r['nb'],vq=round(r['vq'],2),vqCap=r['vqCap'])
async def main():
    for app in sys.argv[1:]:
        r,logs=await run(app)
        print(os.path.basename(app),'przeciąganie',summ(r['pan']),'pasy:',r['pan'].get('jt'),'malowania:',r['pan']['pt'])
        print(os.path.basename(app),'zbliżanie  ',summ(r['zoom']));print('   przyczyny (p: ruch, N: wymuszone; liczba = poziom):',r['zoom'].get('pr'))
        if logs:print('   błędy',logs[:3])
asyncio.run(main())
