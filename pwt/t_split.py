# Wersja 195: rozwidlenie jezdni (droga dwukierunkowa z pasami → dwie jednokierunkowe): obrys drogi bez przewężenia („schodzi się i rozjeżdża”)
import asyncio,sys,os,math,io
sys.path.insert(0,'/tmp/pwt')
import h as H
from h import *
from PIL import Image
t=T()
SPL=[(51.109189,17.051237,249.2,26),(51.097006,17.01591,299.9,55)]   # punkt rozwidlenia i kierunek końca drogi dwukierunkowej
WJS="""(a)=>{const D=vecData,s=scaleCur,kx=111195*Math.cos(rad(D.lat)),cx=(a[1]-D.lon)*kx,cy=(a[0]-D.lat)*111195,ux=Math.sin(a[2]*Math.PI/180),uy=Math.cos(a[2]*Math.PI/180),nx=uy,ny=-ux;
  const ox=(vf.cam.lon-D.lon)*kx,oy=(vf.cam.lat-D.lat)*111195,V=lnVis(D,s,ox,oy,800);lnJuncs(D);
  const SPL=typeof lnSplits==='function'?lnSplits(V,s):[];const TP=lnTapers(V,s,SPL.skip);
  const B=V.map(v=>({a:v.m.a,h:v.w.N*lnLanePx(v.w.kc,s)/s/2}));
  const inPoly=(P,x,y)=>{let c=false;for(let i=0,j=P.length-2;i<P.length;j=i,i+=2){const xi=P[i],yi=P[i+1],xj=P[j],yj=P[j+1];if(((yi>y)!==(yj>y))&&(x<(xj-xi)*(y-yi)/(yj-yi)+xi))c=!c}return c};
  const TPP=TP.map(t=>t.P?t.P:[t.x+t.nx*t.a,t.y+t.ny*t.a,t.fx+t.nx*t.b,t.fy+t.ny*t.b,t.fx-t.nx*t.b,t.fy-t.ny*t.b,t.x-t.nx*t.a,t.y-t.ny*t.a]);
  const road=(x,y)=>{for(const b of B){const A=b.a;for(let i=0;i+3<A.length;i+=2){const dx=A[i+2]-A[i],dy=A[i+3]-A[i+1],L2=dx*dx+dy*dy;let t=L2?((x-A[i])*dx+(y-A[i+1])*dy)/L2:0;t=t<0?0:t>1?1:t;if(Math.hypot(A[i]+dx*t-x,A[i+1]+dy*t-y)<=b.h)return true}}
    for(const P of TPP)if(inPoly(P,x,y))return true;for(const p of SPL)if(inPoly(p.P,x,y))return true;return false};
  const W=[];for(let d=-30;d<=70;d+=2){const px=cx+ux*d,py=cy+uy*d;if(!road(px,py)){W.push(null);continue}let l=0,r=0;while(l<90&&road(px-nx*(l+.5),py-ny*(l+.5)))l+=.5;while(r<90&&road(px+nx*(r+.5),py+ny*(r+.5)))r+=.5;W.push([l,r])}
  return W}"""
def dip(w):
    w=[x for x in w if x is not None]
    d=0
    for i in range(len(w)):
        a=max(w[:i]) if i else 0;b=max(w[i+1:]) if i<len(w)-1 else 0
        d=max(d,min(a,b)-w[i])
    return round(d,1)
async def main():
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=SPL[0][0],lon=SPL[0][1],night=True)
        await pg.add_style_tag(content="*{visibility:hidden!important}#view,#view *{visibility:visible!important}")
        res=[]
        for la,lo,hd,ln in SPL:
            await goto(pg,la,lo,hd=hd,speed=2,zoom=1.6,tilt=0,wait=1200);await fix(pg,la,lo,hd,0);await settle(pg,1500)
            n=0 if not await pg.evaluate("typeof lnSplits==='function'") else await pg.evaluate("""()=>{const D=vecData,s=scaleCur,ox=(vf.cam.lon-D.lon)*111195*Math.cos(rad(D.lat)),oy=(vf.cam.lat-D.lat)*111195,V=lnVis(D,s,ox,oy,800);lnJuncs(D);const S=lnSplits(V,s);
              return S.filter(p=>Math.hypot((p.P[0]+p.P[2])/2-ox,(p.P[1]+p.P[3])/2-oy)<40).length}""")
            w=await pg.evaluate(WJS,[la,lo,hd])
            w=w[:int((30+ln+8)/2)+1]   # od 30 m przed rozwidleniem do końca płyty
            L=[x[0] for x in w if x];R=[x[1] for x in w if x]
            res.append({'plyt':n,'dipL':dip(L),'dipR':dip(R)})
        print('  ',res)
        t('rozwidlenia wykryte (płyta zamiast klina)',all(r['plyt']>=1 for r in res),res)
        t('każdy brzeg drogi bez „fali” (nie cofa się o więcej niż 1,5 m, by potem znów się odsunąć)',all(r['dipL']<=1.5 and r['dipR']<=1.5 for r in res),res)
        t('bez błędów strony',not logs,logs[:3])
        await b.close()
    t.end()
asyncio.run(main())
