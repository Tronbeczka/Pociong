# Pasy ruchu (dane OSM): wczytanie, płyty skrzyżowań, rondo (wybór pasa), gładka linia trasy, plan pasa na trasie.
import asyncio,sys,os,math
sys.path.insert(0,'/tmp/pwt')
import h as H
from h import *
t=T()
KINK="""()=>{const o=window.__rt;if(!o)return null;const P=o.pts,kx=111195*Math.cos(rad(P[0][0])),xy=q=>[(q[1]-P[0][1])*kx,(q[0]-P[0][0])*111195],M=P.map(xy);
  // narożniki samej geometrii trasy (prawdziwe skręty na skrzyżowaniu) – tam ostry róg linii jest zgodny z drogą
  const R=route.pts.map(xy),C=[];for(let i=1;i<R.length-1;i++){const u=[R[i][0]-R[i-1][0],R[i][1]-R[i-1][1]],v=[R[i+1][0]-R[i][0],R[i+1][1]-R[i][1]],lu=Math.hypot(...u),lv=Math.hypot(...v);if(lu<.01||lv<.01)continue;if(Math.acos(Math.max(-1,Math.min(1,(u[0]*v[0]+u[1]*v[1])/(lu*lv))))*180/Math.PI>30)C.push(R[i])}
  const seg=[],pos=[];let a=M[0],d0=0;for(let i=1;i<M.length;i++){const d=Math.hypot(M[i][0]-a[0],M[i][1]-a[1]);if(d>=4){seg.push([M[i][0]-a[0],M[i][1]-a[1]]);pos.push(a);d0+=d;a=M[i]}if(d0>400)break}
  let mx=0,k=0,n=0;for(let i=1;i<seg.length;i++){const u=seg[i-1],v=seg[i],c=(u[0]*v[0]+u[1]*v[1])/(Math.hypot(...u)*Math.hypot(...v));const ang=Math.acos(Math.max(-1,Math.min(1,c)))*180/Math.PI;n++;
    if(C.some(q=>Math.hypot(q[0]-pos[i][0],q[1]-pos[i][1])<18))continue;if(ang>mx)mx=ang;if(ang>40)k++}
  return {n,mx:Math.round(mx),k,corners:C.length}}"""
async def main():
    async with async_playwright() as p:
        la,lo,hd,tg=roadpos(51.0857,17.01165,('primary',))
        b,pg,logs=await launch(p,lat=la,lon=lo)
        await goto(pg,la,lo,hd=hd,speed=2,zoom=2.4,tilt=0,wait=2500)
        r=await pg.evaluate("({n:LANEW.size})")
        t('dane o pasach wczytane (Hallera × Powstańców Śląskich)',r['n']>50,r)
        r=await pg.evaluate("""()=>{const D=vecData,s=scaleCur,ox=(vf.cam.lon-D.lon)*111195*Math.cos(rad(D.lat)),oy=(vf.cam.lat-D.lat)*111195,V=lnVis(D,s,ox,oy,800);lnJuncs(D);const P=lnPlates(V,s);return {v:V.length,p:P.length}}""")
        t('drogi z pasami widoczne i płyty skrzyżowań policzone',r['v']>3 and r['p']>=1,r)
        r=await pg.evaluate("""()=>{const L=lnParse('through|through|through;right|right'),o={};
          const mk=(mod,exit)=>({type:'roundabout',mod,exit,off:100});
          for(const [k,mod,ex] of [['lewo','left',3],['prawo','right',1],['prosto','straight',2]]){const st=mk(mod,ex),v=lnValidFor(L,st);st.lanes={lanes:L,valid:v.valid,need:v.need,side:v.side};const pf=lnPref(null,st);o[k]=pf&&pf.b}
          return o}""")
        t('rondo: zjazd w lewo – lewy pas, w prawo – prawy, prosto – prawy z „prosto”',r=={'lewo':0,'prawo':3,'prosto':2},r)
        # trasa przez skrzyżowanie z pasami: linia trasy gładka
        A=(51.0905,17.0135);B=(51.0800,17.0080)
        co,j=osrm_route(A,B);cum,at=poly(co)
        la,lo,hd=at(0);await goto(pg,la,lo,hd=hd,speed=0,zoom=None,tilt=None,wait=1500)
        await pg.evaluate("window.__dbgRt=o=>{window.__rt=o}")
        await plan(pg,*B);await pg.wait_for_timeout(2500)
        res=[]
        for k in range(0,40):
            d=min(cum[-1]-5,k*12);la,lo,hd=at(d);await fix(pg,la,lo,hd,12);await pg.wait_for_timeout(150)
            if k%10==9:await pg.wait_for_timeout(800);res.append(await pg.evaluate(KINK))
        t('linia trasy bez załamań (> 40° na 4 m) poza prawdziwymi skrętami drogi',all(x and x['n']>10 and x['k']==0 for x in res),res)
        t('bez błędów strony',not logs,logs[:4])
        await b.close()
    t.end()
asyncio.run(main())
