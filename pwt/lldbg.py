# diagnostyka: drogi z liniami pasów w pobliżu punktu ekranu (x,y w px CSS): kierunek, pasy, poprzednik/następnik, faza
import asyncio,sys,os,json
sys.path.insert(0,'/tmp/pwt')
from h import *
la,lo,hd,s,tl=[float(v) for v in sys.argv[1].split(',')];pts=[tuple(map(float,a.split(','))) for a in sys.argv[2:]]
JS=r"""(pt)=>{const q=unprojPt(pt[0],pt[1]);if(!q)return 'brak';const D=vecData,F=llFrame(D),c=llXY(F,q.lat,q.lon),out=[];
 for(const r of LL.res.values()){if(!r||!r.L||!r.L.length)continue;const w=LANEW.get(r.id);if(!w)continue;
   let best=1e9;for(const l of r.L){const p=l.p;for(let i=0;i<p.length;i+=2){const d=Math.hypot(p[i]-c[0],p[i+1]-c[1]);if(d<best)best=d}}
   if(best>25)continue;const T=llTrav(w),pre=llLink(w,T,true),suc=llLink(w,T,false);
   out.push({id:w.id,d:+best.toFixed(1),ow:w.ow,nf:w.nf,nb:w.nb,k:w.k,len:Math.round(llLenM(w,F)),ph:+(LL.ph.get(w.id)||0).toFixed(2),
     pre:pre?(pre.multi?'multi':{id:pre.v.id,same:pre.same,nf:pre.nf,nb:pre.nb}):null,suc:suc?(suc.multi?'multi':{id:suc.v.id,same:suc.same,nf:suc.nf,nb:suc.nb}):null,
     lines:r.L.map(l=>l.t+':'+Math.round(Math.hypot(l.p[0]-c[0],l.p[1]-c[1]))+'-'+Math.round(Math.hypot(l.p[l.p.length-2]-c[0],l.p[l.p.length-1]-c[1]))).join(' '),
     tags:{lanes:w.N,tf:w.tf,tb:w.tb}})}
 out.sort((a,b)=>a.d-b.d);return {q:[+q.lat.toFixed(6),+q.lon.toFixed(6)],out:out.slice(0,6)}}"""
async def main():
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=la,lon=lo)
        await goto(pg,la,lo,hd=hd,speed=0,zoom=s/2.8,tilt=tl,wait=1000)
        for _ in range(80):
            r=await pg.evaluate("(()=>{try{return {n:LANEW.size,b:lnBusy||lnQ.length>0,q:LL.Q.length}}catch(e){return {n:1,b:false,q:0}}})()")
            if r['n']>0 and not r['b'] and r['q']==0:break
            await pg.wait_for_timeout(500)
        await pg.wait_for_timeout(1500);await pg.evaluate("()=>{vd=null}");await pg.wait_for_timeout(800)
        for pt in pts:
            r=await pg.evaluate(JS,list(pt));print(json.dumps(r,ensure_ascii=False,indent=None))
        await b.close()
asyncio.run(main())
