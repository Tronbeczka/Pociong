import asyncio,sys,os,json
sys.path.insert(0,'/tmp/pwt')
from h import *
import t_jz as TJ
LA,LO,WID=float(sys.argv[1]),float(sys.argv[2]),int(sys.argv[3])
async def main():
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=LA,lon=LO)
        await goto(pg,LA,LO,hd=0,speed=0,zoom=2.4,tilt=0,wait=1500);await TJ.wait_ready(pg)
        await pg.evaluate("()=>{window.__dw=+(%s);window.__ds=+(%s)}"%(os.environ.get('DW','60'),os.environ.get('DS','3')))
        r=await pg.evaluate("""([la,lo,wid])=>{JZN=null;const D=vecData,s=scaleCur,c=vecCam(performance.now()),kx=111195*Math.cos(rad(D.lat)),ox=(c.lon-D.lon)*kx,oy=(c.lat-D.lat)*111195;
          const F=jzFrame(D,s,ox,oy,900);if(!F)return 'brak F';const G=F.G.find(g=>g.ch.pcs.some(q=>q.p.w.id===wid));if(!G)return 'brak G '+F.G.length;
          const x=(lo-D.lon)*kx,y=(la-D.lat)*111195;let bi=0,bd=1e9;for(let i=0;i<G.n;i++){const d=Math.hypot(G.X[i]-x,G.Y[i]-y);if(d<bd){bd=d;bi=i}}
          const out=[];for(let i=Math.max(0,bi-(+(window.__dw||60)));i<=Math.min(G.n-1,bi+(+(window.__dw||60)));i+=(+(window.__ds||3)))out.push([i,+G.T[i].toFixed(0),G.PI[i],G.PI[i]>=0?G.ch.pcs[G.PI[i]].p.w.id:-1,G.PI[i]>=0?G.ch.pcs[G.PI[i]].p.w.N:-1,+G.eL[i].toFixed(1),+G.eR[i].toFixed(1),+G.gL[i].toFixed(2),+G.gR[i].toFixed(2),+G.LW[i].toFixed(2)]);
          return {bi,bd,n:G.n,ow:G.ch.ow,Nref:G.ch.Nref,kc:G.ch.kc,out}}""",[LA,LO,WID])
        if isinstance(r,str):print(r)
        else:
            print({k:v for k,v in r.items() if k!='out'})
            for row in r['out']:print(row)
        await b.close()
asyncio.run(main())
