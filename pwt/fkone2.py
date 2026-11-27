import asyncio,sys,os,json
sys.path.insert(0,'/tmp/pwt')
from h import *
import t_jz as TJ
LA,LO,SIG=float(sys.argv[1]),float(sys.argv[2]),sys.argv[3]
async def main():
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=LA,lon=LO)
        await goto(pg,LA,LO,hd=0,speed=0,zoom=2.4,tilt=0,wait=1500);await TJ.wait_ready(pg)
        r=await pg.evaluate("""(sig)=>{JZN=null;const D=vecData,s=scaleCur,c=vecCam(performance.now()),kx=111195*Math.cos(rad(D.lat)),ox=(c.lon-D.lon)*kx,oy=(c.lat-D.lat)*111195;
          const F=jzFrame(D,s,ox,oy,900);const G=F.G.find(g=>g.ch.sig.startsWith(sig));if(!G)return 'brak';const out={TW:F.B.TWk,s,fk:[]};
          const TT=jzTiles(D);out.tk=G.ch.pcs.map(q=>jzTileK(TT,q.p)+':'+q.p.w.k+':'+LN_K[q.p.w.kc]);
          for(const at of [0,1]){const Fk=G.ch.fk&&G.ch.fk[at];if(!Fk)continue;const TG=F.B.geo.get(Fk.T.ch.id);const ti=Fk.T.at?TG.n-1:0,n0=at?G.n-1:0;
            out.fk.push({at,tAt:Fk.T.at,TGst:TG.st,Ttk:Fk.T.ch.pcs.map(q=>jzTileK(TT,q.p)),Twn:TG.wn[ti],TgL:TG.gL[ti],TgR:TG.gR[ti],wn:[...G.wn.slice(at?n0-6:n0,at?n0+1:n0+7)].map(v=>+v.toFixed(2)),gL:[...G.gL.slice(at?n0-6:n0,at?n0+1:n0+7)].map(v=>+v.toFixed(2)),gR:[...G.gR.slice(at?n0-6:n0,at?n0+1:n0+7)].map(v=>+v.toFixed(2)),sq:[...G.sq.slice(at?n0-6:n0,at?n0+1:n0+7)]})}
          return out}""",SIG)
        print(json.dumps(r)[:3000])
        await b.close()
asyncio.run(main())
