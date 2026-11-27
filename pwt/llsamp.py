import asyncio,sys,os,json
sys.path.insert(0,'/tmp/pwt')
from h import *
la,lo=[float(v) for v in sys.argv[1].split(',')];ids=sys.argv[2:]
JS=r"""(id)=>{const w=LANEW.get(+id),D=vecData,F=llFrame(D),ix=llIndex(D),T=llTrav(w),g=T.g,n=g.length/2,out=[];
 for(let i=0;i<n;i++){const q=llXY(F,g[2*i],g[2*i+1]);out.push([Math.round(q[0]*10)/10,Math.round(q[1]*10)/10])}
 // odcinki z mapy w promieniu 30 m od początku: klasa, kąt, odległość
 const p0=out[0],near=[];llQ(ix,p0[0],p0[1],30,S=>{let t=(p0[0]-S.x1)*S.ux+(p0[1]-S.y1)*S.uy;t=t<0?0:t>S.L?S.L:t;const d=Math.hypot(S.x1+S.ux*t-p0[0],S.y1+S.uy*t-p0[1]);if(d<20)near.push([S.k,S.lv,Math.round(Math.atan2(S.uy,S.ux)*180/Math.PI),+d.toFixed(1),S.pi,Math.round(S.L)])});
 const r=LL.res.get(w.id);return {pts:out,near:near.sort((a,b)=>a[3]-b[3]).slice(0,12),lines:r&&r.L?r.L.map(l=>Array.from(l.p).map(v=>Math.round(v*10)/10).slice(0,8)):null}}"""
async def main():
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=la,lon=lo)
        await goto(pg,la,lo,hd=0,speed=0,zoom=1.0,tilt=0,wait=800)
        for _ in range(90):
            r=await pg.evaluate("(()=>{try{return !lnBusy&&lnQ.length===0&&LL.Q.length===0&&LANEW.size>0}catch(e){return false}})()")
            if r:break
            await pg.wait_for_timeout(500)
        for i in ids:print(i,json.dumps(await pg.evaluate(JS,i)))
        await b.close()
asyncio.run(main())
