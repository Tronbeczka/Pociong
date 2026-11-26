# Wersja 196: płyty skrzyżowań nie zalewają narożników między ulicami (dawniej otoczka wypukła łączyła kilka skrzyżowań – do 250 m)
import asyncio,sys,os,math,json
sys.path.insert(0,'/tmp/pwt')
import h as H
from h import *
t=T()
JS="""()=>{const D=vecData,s=Math.max(scaleCur,1),V=[];
  for(const w of LANEW.values()){if(!w.multi)continue;const m=lnMetres(D,w);const ox=(vf.cam.lon-D.lon)*111195*Math.cos(rad(D.lat)),oy=(vf.cam.lat-D.lat)*111195;if(Math.hypot((m.b[0]+m.b[2])/2-ox,(m.b[1]+m.b[3])/2-oy)>700)continue;V.push({w,m,D})}
  lnJuncs(D);const P=lnPlates(V,s);
  const B=V.map(v=>({a:v.m.a,h:v.w.N*lnLanePx(v.w.kc,s)/s/2}));
  const inBody=(x,y)=>{for(const b of B){const A=b.a;for(let i=0;i+3<A.length;i+=2){const dx=A[i+2]-A[i],dy=A[i+3]-A[i+1],L2=dx*dx+dy*dy;let t=L2?((x-A[i])*dx+(y-A[i+1])*dy)/L2:0;t=t<0?0:t>1?1:t;if(Math.hypot(A[i]+dx*t-x,A[i+1]+dy*t-y)<=b.h*1.05)return true}}return false};
  const inPoly=(Hh,x,y)=>{let c=false;for(let i=0,j=Hh.length-1;i<Hh.length;j=i++){const a=Hh[i],b=Hh[j];if(((a[1]>y)!==(b[1]>y))&&(x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]))c=!c}return c};
  let tot=0,out=0,worst=0;
  for(const p of P){let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;for(const q of p.H){x0=Math.min(x0,q[0]);x1=Math.max(x1,q[0]);y0=Math.min(y0,q[1]);y1=Math.max(y1,q[1])}
    let n=0,o=0;for(let x=x0;x<=x1;x+=2)for(let y=y0;y<=y1;y+=2){if(!inPoly(p.H,x,y))continue;if(p.R&&Math.hypot(x-p.cx,y-p.cy)>p.R)continue;n++;if(!inBody(x,y))o++}
    tot+=n;out+=o;if(n)worst=Math.max(worst,Math.round(o*4))}
  return {plates:P.length,area:tot*4,poza:out*4,worst}}"""
PTS=[(51.112909,17.005963),(51.10791,17.021192),(51.111885,17.060784),(51.117936,17.03168),(51.0857,17.01165)]
async def main():
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=PTS[0][0],lon=PTS[0][1])
        res=[]
        for la,lo in PTS:
            await goto(pg,la,lo,hd=0,speed=0,zoom=2.4,tilt=0,wait=1500)
            res.append(await pg.evaluate(JS))
        print('  ',res)
        t('płyty skrzyżowań są (wypełniają szczeliny)',sum(r['plates'] for r in res)>=8,res)
        t('płyty nie wychodzą poza jezdnie: poza drogami ≤ 5% powierzchni płyt, żadna płyta > 300 m² poza drogą',sum(r['poza'] for r in res)<=.05*max(1,sum(r['area'] for r in res)) and max(r['worst'] for r in res)<=300,res)
        t('bez błędów strony',not logs,logs[:3])
        await b.close()
    t.end()
asyncio.run(main())
