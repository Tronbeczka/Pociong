# Wersja 193: czyste skrzyżowania na drogach z mapy – osie kończą się przed skrzyżowaniem, wloty bocznych ulic przerywają linię krawędziową
import asyncio,sys,os,math,json
sys.path.insert(0,'/tmp/pwt')
import h as H
from h import *
t=T()
JS="""()=>{const D=vecData,s=scaleCur,CC=D.CLC,J=D.CLJ;if(!CC||!J)return {none:true};
  const c=document.createElement('canvas').getContext('2d');c.lineWidth=1.5;
  let n=0,inCut=0,inFull=0,mainKept=0,mainN=0;
  for(const j of J){
    const ks=new Set(j.arms.map(a=>a.k));
    if(ks.size===1&&ks.has('rs')&&j.arms.length>=4){n++;   // skrzyżowanie równorzędnych ulic osiedlowych
      if(CC.CP.cl_rs&&c.isPointInStroke(CC.CP.cl_rs,j.x,j.y))inCut++;
      if(D.P.cl_rs&&c.isPointInStroke(D.P.cl_rs,j.x,j.y))inFull++;}
    // ulica ważniejsza (tr/sc/pr) z boczną osiedlową: oś głównej biegnie dalej przez wlot
    const hi=j.arms.filter(a=>a.r>=2&&a.pt&&a.pt.r===a.r),lo=j.arms.filter(a=>a.r===1);
    const alone=j.arms.length===3&&!J.some(o=>o!==j&&Math.hypot(o.x-j.x,o.y-j.y)<35);   // bez innego skrzyżowania w pobliżu (jego przerwa sięga tutaj)
    if(alone&&hi.length===2&&lo.length===1&&hi[0].k===hi[1].k){const P=CC.CP['cl_'+hi[0].k],F=D.P['cl_'+hi[0].k];if(P&&F&&c.isPointInStroke(F,j.x,j.y)){mainN++;if(c.isPointInStroke(P,j.x,j.y))mainKept++}}
  }
  return {nj:J.length,mp:CC.MP.length,n,inCut,inFull,mainN,mainKept,s}}"""
async def main():
    async with async_playwright() as p:
        la,lo,hd,tg=roadpos(51.0800,17.0150,('residential',))
        b,pg,logs=await launch(p,lat=la,lon=lo)
        await goto(pg,la,lo,hd=hd,speed=2,zoom=2.4,tilt=50,wait=2500)
        r=await pg.evaluate(JS)
        print('  ',r)
        t('skrzyżowania dróg z mapy wykryte, wloty policzone',not r.get('none') and r['nj']>200 and r['mp']>=3,r)
        t('skrzyżowania ulic osiedlowych: bez osi w środku (było: oś przez środek)',r['n']>=10 and r['inCut']<=r['n']*.1 and r['inFull']>=r['n']*.6,r)
        t('ulica ważniejsza przy bocznej osiedlowej: oś biegnie dalej przez wlot',r['mainN']>=3 and r['mainKept']>=r['mainN']*.9,r)
        # dzień/noc, 2D/3D i oddalenie – bez błędów, osie i wloty liczone przy każdym zbliżeniu
        for z,tl in ((1.0,0),(0.5,50),(4,0)):
            await cam(pg,zoom=z,tilt=tl);await pg.wait_for_timeout(1200)
        await pg.evaluate("document.getElementById('night').click()");await pg.wait_for_timeout(1500)
        t('bez błędów strony (zbliżenia, noc)',not logs and not await pg.evaluate("window.__errs||null"),logs[:3])
        await b.close()
    t.end()
asyncio.run(main())
