# Wersja 199: nowe jezdnie z pasami – obrys bez wcięć i schodków, linie nie wchodzą na inne jezdnie (skrzyżowania, rozwidlenia, jezdnie obok siebie), rozwidlenia od brzegów, mosty, czas liczenia
import asyncio,sys,os,math,json
sys.path.insert(0,'/tmp/pwt')
import h as H
from h import *
t=T()
JS="""()=>{window.__jzRaw=1;JZN=null;const D=vecData,s=scaleCur,c=vecCam(performance.now()),kx=111195*Math.cos(rad(D.lat)),ox=(c.lon-D.lon)*kx,oy=(c.lat-D.lat)*111195;
  const F=jzFrame(D,s,ox,oy,900);if(!F){window.__jzRaw=0;return {n:0}}
  for(const G of F.G)jzLines(F.N,F.B,G);window.__jzRaw=0;
  const res={n:F.G.length,dips:[],slope:[],cross:[],fork:[],xx:[],err:window.__lnErr||null,parts:0,bridges:0};
  const inPoly=(Lx,Rx,x,y)=>{const n=Lx.length/2;let c=false;const P=[];for(let k=0;k<n;k++)P.push(Lx[2*k],Lx[2*k+1]);for(let k=n-1;k>=0;k--)P.push(Rx[2*k],Rx[2*k+1]);
    for(let i=0,j=P.length-2;i<P.length;j=i,i+=2){const xi=P[i],yi=P[i+1],xj=P[j],yj=P[j+1];if(((yi>y)!==(yj>y))&&(x<(xj-xi)*(y-yi)/(yj-yi)+xi))c=!c}
    if(!c)return 0;let dm=1e9;for(let i=0,j=P.length-2;i<P.length;j=i,i+=2){const ax=P[j],ay=P[j+1],bx=P[i],by=P[i+1],vx=bx-ax,vy=by-ay,l2=vx*vx+vy*vy;let u=l2?((x-ax)*vx+(y-ay)*vy)/l2:0;u=u<0?0:u>1?1:u;dm=Math.min(dm,Math.hypot(x-ax-vx*u,y-ay-vy*u))}return dm};
  for(const G of F.G){const {gL,gR,LWs,T,i0,i1,h}=G;res.parts+=G.parts.length;if(G.parts.some(p=>p.z))res.bridges++;
    const lwd=F.B.LWk[LN_K[G.ch.kc]]||F.B.LWk.tr,W=2*Math.round(Math.max(40,8*lwd)/2/h)*h*.95,w=Math.round(W/h);
    for(const [nm,g] of [['L',gL],['P',gR]]){
      let worst=0,wi=-1,ms=0;
      for(let j=i0+1;j<i1;j++){const th=g[j]+.35*LWs[j];let a=-1,bb=-1;for(let i=j-1;i>=Math.max(i0,j-w);i--)if(g[i]>=th){a=i;break}if(a<0)continue;
        for(let k=j+1;k<=Math.min(i1,a+w);k++)if(g[k]>=th){bb=k;break}if(bb<0)continue;   // zwężenie krótsze niż okno domknięcia (takie mają być pominięte)
        const dp=Math.min(g[a],g[bb])-g[j];if(dp<=worst)continue;
        const E=nm==='L'?G.eL:G.eR,lim=g[j]+.1;let u=j,v=j;while(u>i0&&E[u-1]<=lim)u--;while(v<i1&&E[v+1]<=lim)v++;
        if((v-u)*h>=Math.max(40,8*lwd)+3.6*lwd-2)continue;   // zwężenie w danych dłuższe niż okno wygładzania – prawdziwe (np. 2 pasy między skrzyżowaniami)
        worst=dp;wi=j}
      for(let j=i0+1;j<=i1;j++)ms=Math.max(ms,Math.abs(g[j]-g[j-1])/h);
      if(wi>=0&&worst>=.35*LWs[wi])res.dips.push({id:G.ch.pcs[0].p.w.id,sd:nm,dep:+(worst/LWs[wi]).toFixed(2),t:Math.round(T[wi]),lat:+(D.lat+G.Y[wi]/111195).toFixed(6),lon:+(D.lon+G.X[wi]/kx).toFixed(6),pr:(()=>{const o=[];for(let q=Math.max(i0,wi-100);q<=Math.min(i1,wi+100);q+=8)o.push([q,+g[q].toFixed(1),+(nm==='L'?G.eL[q]:G.eR[q]).toFixed(1)]);return o})(),w});
      if(ms>.31){let mj=i0+1;for(let j=i0+1;j<=i1;j++)if(Math.abs(g[j]-g[j-1])/h>=ms-1e-9){mj=j;break}res.slope.push({id:G.ch.pcs[0].p.w.id,sd:nm,ms:+ms.toFixed(2),lat:+(D.lat+G.Y[mj]/111195).toFixed(6),lon:+(D.lon+G.X[mj]/kx).toFixed(6)})}}
    // linie na innych jezdniach z pasami (ten sam poziom): punkt głębiej niż 0,8 m w cudzym obrysie
    const R=G.lines&&G.lines.raw;if(R)for(const key of ['dash','div']){const a=R[key];
      for(let k=0;k<a.length;k+=3){const x=a[k],y=a[k+1],z=a[k+2];
        for(const Q of F.G){if(Q===G)continue;const b=Q.bb;if(x<b[0]||x>b[2]||y<b[1]||y>b[3])continue;const rk=jzRelK(G,Q);if(rk===1||rk===2)continue;   // (te same pasy dalej: dozwolone)
          const lim=rk===3?.3*Q.LWs[(Q.i0+Q.i1)>>1]+.3:.8;
          for(const p of Q.parts){if(p.z!==z)continue;const dd=inPoly(p.Lx,p.Rx,x,y);if(dd>lim){res.cross.push({id:G.ch.pcs[0].p.w.id,on:Q.ch.pcs[0].p.w.id,dd:+dd.toFixed(1),lat:+(D.lat+y/111195).toFixed(6),lon:+(D.lon+x/kx).toFixed(6)});break}}}}}
    // linie dwóch odnóg tego samego rozwidlenia nie krzyżują się (bez „X”)
    if(R)for(const Q of F.G){if(Q===G||Q.ch.id<G.ch.id||!jzRelK(G,Q))continue;const QR=Q.lines&&Q.lines.raw;if(!QR)continue;
      for(const a of R.pl){if(a.t==='edge')continue;for(const c of QR.pl){if(c.t==='edge'||c.z!==a.z)continue;
        for(let i=0;i+3<a.p.length;i+=2){const x1=a.p[i],y1=a.p[i+1],x2=a.p[i+2],y2=a.p[i+3];
          for(let j=0;j+3<c.p.length;j+=2){const x3=c.p[j],y3=c.p[j+1],x4=c.p[j+2],y4=c.p[j+3];
            if(Math.max(x1,x2)<Math.min(x3,x4)||Math.max(x3,x4)<Math.min(x1,x2)||Math.max(y1,y2)<Math.min(y3,y4)||Math.max(y3,y4)<Math.min(y1,y2))continue;
            const o=(px,py,qx,qy,rx,ry)=>(qx-px)*(ry-py)-(qy-py)*(rx-px);
            if(o(x1,y1,x2,y2,x3,y3)*o(x1,y1,x2,y2,x4,y4)<0&&o(x3,y3,x4,y4,x1,y1)*o(x3,y3,x4,y4,x2,y2)<0){
              const l1=Math.hypot(x2-x1,y2-y1)||1,l2=Math.hypot(x4-x3,y4-y3)||1,cs=Math.abs(((x2-x1)*(x4-x3)+(y2-y1)*(y4-y3))/l1/l2);
              if(cs<Math.cos(10*Math.PI/180)&&res.xx.length<30)res.xx.push({id:G.ch.pcs[0].p.w.id,on:Q.ch.pcs[0].p.w.id,t:a.t+'/'+c.t,lat:+(D.lat+y1/111195).toFixed(6),lon:+(D.lon+x1/kx).toFixed(6)})}}}}}}
    // rozwidlenie: brzeg zewnętrzny odnogi zaczyna się na brzegu jezdni sprzed rozwidlenia
    if(G.ch.fk)for(const at of [0,1]){const Fk=G.ch.fk[at];if(!Fk)continue;const TG=F.B.geo.get(Fk.T.ch.id);if(!TG)continue;
      const i=at?G.i1:G.i0,ti=Fk.T.at?TG.i1:TG.i0;const pt=(g,i,o)=>[g.X[i]+g.UY[i]*o,g.Y[i]-g.UX[i]*o];
      const eB=[pt(G,i,G.d[i]-G.gL[i]),pt(G,i,G.d[i]+G.gR[i])],eT=[pt(TG,ti,TG.d[ti]-TG.gL[ti]),pt(TG,ti,TG.d[ti]+TG.gR[ti])];
      const dmin=Math.min(...eB.map(p=>Math.min(...eT.map(q=>Math.hypot(p[0]-q[0],p[1]-q[1])))));res.fork.push(+dmin.toFixed(2))}
  }
  res.cross=res.cross.slice(0,40);return res}"""
PERF="""()=>{JZN=null;const D=vecData,s=scaleCur,c=vecCam(performance.now()),kx=111195*Math.cos(rad(D.lat)),ox=(c.lon-D.lon)*kx,oy=(c.lat-D.lat)*111195;
  const cv=document.createElement('canvas');cv.width=900;cv.height=900;const cx=cv.getContext('2d');cx.translate(450,450);cx.scale(s,-s);cx.translate(-ox,-oy);const pal=PAL[night?'night':'day'];
  const fr=()=>{const t0=performance.now();const F=jzFrame(D,s,ox,oy,900);if(F){jzCasing(cx,F,pal,4,true,s,0);jzBody(cx,F,pal,s,true,night,null,0,4);jzBody(cx,F,pal,s,true,night,null,1,4)}return performance.now()-t0};
  const cs=[];for(let r=0;r<3;r++){JZN=null;D.JZT=null;cs.push(fr())}cs.sort((x,y)=>x-y);const a=cs[1];JZN=null;D.JZT=null;fr();let n=1;   /* pierwsza klatka: mediana z 3 prób */
  while(n<60){const F=jzFrame(D,s,ox,oy,900);if(!F||!F.G.some(G=>!G.lines))break;fr();n++}
  const w=fr();return {cold:+a.toFixed(1),frames:n,warm:+w.toFixed(2)}}"""
PTS=[(51.10760,17.04640),(51.11160,17.05930),(51.11120,17.06070),(51.109189,17.051237),(51.1079,17.0385),(51.0971,17.0147),(51.1035,17.0310),(51.1092,17.0520),
     (51.1123,17.0590),(51.1175,16.9900),(51.0800,17.0150),(51.0830,17.0700),(51.0857,17.01165),(51.0700,16.9950),(51.0970,17.0159),(51.1300,16.9300)]
async def wait_ready(pg):
    last=None;same=0
    for _ in range(80):
        r=await pg.evaluate("(()=>{try{const c=vecCam(performance.now());if(!vecData||vecBusy||lnBusy||dist(vecData.lat,vecData.lon,c.lat,c.lon)>=600)return null;const D=vecData;return LANEW.size+'/'+D.LNJK+'/'+(signs?signs.v:0)+'/'+scaleCur.toFixed(3)}catch(e){return 'x'}})()")
        if r is not None and r==last:
            same+=1
            if same>=3:break
        else:same=0
        last=r;await pg.wait_for_timeout(400)
async def main():
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=PTS[0][0],lon=PTS[0][1])
        tot=dict(n=0,dips=[],slope=[],cross=[],fork=[],xx=[],parts=0,bridges=0);errs=[];perf=[]
        for la,lo in PTS:
            await goto(pg,la,lo,hd=0,speed=0,zoom=2.4,tilt=0,wait=1500);await wait_ready(pg)
            r=await pg.evaluate(JS)
            print('  ',(la,lo),'jezdnie',r.get('n'),'wcięcia',len(r.get('dips',[])),'stromo',len(r.get('slope',[])),'linie na innych',len(r.get('cross',[])),'X',len(r.get('xx',[])),'rozwidlenia',r.get('fork'),flush=True)
            for k in ['dips','slope','cross','fork','xx']:tot[k]+=r.get(k,[])
            tot['n']+=r.get('n',0);tot['parts']+=r.get('parts',0);tot['bridges']+=r.get('bridges',0)
            if r.get('err'):errs.append(r['err'])
            if len(perf)<6:perf.append(await pg.evaluate(PERF))
        print('   wcięcia:',tot['dips'][:8]);print('   stromo:',tot['slope'][:8]);print('   linie na innych jezdniach:',tot['cross'][:10]);print('   X:',tot['xx'][:10]);print('   czas:',perf)
        t('nowe jezdnie z pasami narysowane w wielu miejscach',tot['n']>=150,tot['n'])
        t('jezdnie na mostach rysowane w częściach (ziemia / most)',tot['bridges']>=3,tot['bridges'])
        t('brzeg bez wcięć (zwężenie ≥ 0,35 pasa i zaraz poszerzenie)',not tot['dips'],tot['dips'][:6])
        t('zmiana szerokości łagodna (≤ 0,3 m na metr)',not tot['slope'],tot['slope'][:6])
        t('linie pasów nie wchodzą na inne jezdnie z pasami (skrzyżowania, rozwidlenia, jezdnie obok siebie)',not tot['cross'],tot['cross'][:6])
        t('linie odnóg tego samego rozwidlenia się nie krzyżują',not tot['xx'],tot['xx'][:6])
        t('rozwidlenia: brzeg odnogi zaczyna się na brzegu jezdni sprzed rozwidlenia (≤ 0,6 m)',len(tot['fork'])>=4 and max(tot['fork'])<=.6,tot['fork'])
        t('bez błędów modułu',not errs,errs[:2])
        t('czas: pierwsza klatka ≤ 50 ms (w tym 7 ms na linie), kolejne ≤ 3 ms, linie gotowe w ≤ 25 klatkach',all(x['cold']<=50 and x['warm']<=3 and x['frames']<=25 for x in perf),perf)
        t('bez błędów strony',not logs,logs[:3])
        await b.close()
    t.end()
if __name__=="__main__":asyncio.run(main())
