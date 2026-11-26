import asyncio,sys,os,json
sys.path.insert(0,'/tmp/pwt')
from h import *
import t_jz as TJ
JS="""()=>{JZN=null;const D=vecData,s=scaleCur,c=vecCam(performance.now()),kx=111195*Math.cos(rad(D.lat)),ox=(c.lon-D.lon)*kx,oy=(c.lat-D.lat)*111195;
  const F=jzFrame(D,s,ox,oy,900);if(!F)return [];const out=[];
  for(const G of F.G){if(!G.ch.fk)continue;for(const at of [0,1]){const Fk=G.ch.fk[at];if(!Fk)continue;
    const TG=F.B.geo.get(Fk.T.ch.id),SG=F.B.geo.get(Fk.S.ch.id);if(!TG)continue;const i=at?G.i1:G.i0,ti=Fk.T.at?TG.i1:TG.i0;
    const pt=(g,i,o)=>[g.X[i]+g.UY[i]*o,g.Y[i]-g.UX[i]*o];
    const eB=[pt(G,i,G.d[i]-G.gL[i]),pt(G,i,G.d[i]+G.gR[i])],eT=[pt(TG,ti,TG.d[ti]-TG.gL[ti]),pt(TG,ti,TG.d[ti]+TG.gR[ti])];
    const dmin=Math.min(...eB.map(p=>Math.min(...eT.map(q=>Math.hypot(p[0]-q[0],p[1]-q[1])))));if(dmin<=.6)continue;
    out.push({b:G.ch.sig.slice(0,40),at,i,n:G.n,i0:G.i0,i1:G.i1,tAt:Fk.T.at,ti,tn:TG.n,ti0:TG.i0,ti1:TG.i1,trunk:Fk.T.ch.sig.slice(0,40),sib:Fk.S.ch.sig.slice(0,30),dmin:+dmin.toFixed(2),
      node:[+G.X[i].toFixed(1),+G.Y[i].toFixed(1)],tnode:[+TG.X[ti].toFixed(1),+TG.Y[ti].toFixed(1)],ow:G.ch.ow,tow:TG.ch.ow,bshow:G.ch.show,tshow:TG.ch.show,
      lat:+(D.lat+G.Y[i]/111195).toFixed(6),lon:+(D.lon+G.X[i]/kx).toFixed(6),bdir:[+G.UX[i].toFixed(2),+G.UY[i].toFixed(2)],tdir:[+TG.UX[ti].toFixed(2),+TG.UY[ti].toFixed(2)],
      bg:[+G.gL[i].toFixed(1),+G.gR[i].toFixed(1),+G.d[i].toFixed(1)],tg:[+TG.gL[ti].toFixed(1),+TG.gR[ti].toFixed(1),+TG.d[ti].toFixed(1)],sg:SG?[+SG.gL[Fk.S.at?SG.n-1:0].toFixed(1),+SG.gR[Fk.S.at?SG.n-1:0].toFixed(1)]:null,L:+G.ch.L.toFixed(0),tL:+TG.ch.L.toFixed(0)})}}
  return out}"""
async def main():
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=TJ.PTS[0][0],lon=TJ.PTS[0][1])
        seen=set()
        for la,lo in TJ.PTS:
            await goto(pg,la,lo,hd=0,speed=0,zoom=2.4,tilt=0,wait=1500);await TJ.wait_ready(pg)
            for x in await pg.evaluate(JS):
                k=(x['b'],x['at'])
                if k in seen:continue
                seen.add(k);print(json.dumps(x))
        await b.close()
asyncio.run(main())
