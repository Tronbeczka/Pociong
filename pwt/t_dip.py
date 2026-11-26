# Wersja 197: brzeg jezdni bez „wcięć” (zwęża się i zaraz znów rozszerza) i bez szczelin na stykach odcinków OSM – sprawdzane w wielu miejscach miasta
import asyncio,sys,os,math,json
sys.path.insert(0,'/tmp/pwt')
import h as H
from h import *
t=T()
JS="""()=>{const D=vecData,s=scaleCur,kx=111195*Math.cos(rad(D.lat)),ox=(vf.cam.lon-D.lon)*kx,oy=(vf.cam.lat-D.lat)*111195,V=lnVis(D,s,ox,oy,450);lnJuncs(D);
  const SPL=typeof lnSplits==='function'?lnSplits(V,s):[],TP=lnTapers(V,s,SPL.skip),PL=lnPlates(V,s),G=lnGroups(V,s),E=lnEnds(V);
  const flat=H=>{const r=[];for(const p of H)r.push(p[0],p[1]);return r};
  const bb=P=>{let a=1e9,b=1e9,c=-1e9,d=-1e9;for(let i=0;i<P.length;i+=2){a=Math.min(a,P[i]);b=Math.min(b,P[i+1]);c=Math.max(c,P[i]);d=Math.max(d,P[i+1])}return [a,b,c,d]};
  const POL=[];const addP=(P,ids)=>{if(P&&P.length>=6)POL.push({P,b:bb(P),ids})};   // ids: odcinki, do których należy wielokąt (klin, mostek, styk)
  for(const x of TP)addP(x.P,x.ids||null);for(const p of SPL)addP(p.P,p.ids||null);for(const j of (TP.J||[]))if(j.H.length>=3)addP(flat(j.H),[j.v.w.id,j.g.v.w.id]);
  const PLS=PL.map(p=>({P:flat(p.H),b:bb(flat(p.H)),cx:p.cx,cy:p.cy,R:p.R})),SPP=SPL.map(p=>p.P);
  const EPS=[];for(const g of G)for(let i=0;i<g.ep.length;i+=2)EPS.push([g.ep[i],g.ep[i+1],g.wpx/s/2]);
  const inPoly=(P,x,y)=>{let c=false;for(let i=0,j=P.length-2;i<P.length;j=i,i+=2){const xi=P[i],yi=P[i+1],xj=P[j],yj=P[j+1];if(((yi>y)!==(yj>y))&&(x<(xj-xi)*(y-yi)/(yj-yi)+xi))c=!c}return c};
  const inBody=(v,x,y)=>{const A=v.m.a,n=A.length/2,h=v.w.N*lnLanePx(v.w.kc,s)/s/2;   // pociągnięcie z uciętymi końcami (jak lnStroke) i zaokrąglonymi załamaniami
    for(let i=0;i<n-1;i++){const dx=A[2*i+2]-A[2*i],dy=A[2*i+3]-A[2*i+1],L2=dx*dx+dy*dy;if(L2<1e-9)continue;let u=((x-A[2*i])*dx+(y-A[2*i+1])*dy)/L2;if(i===0&&u<0)continue;if(i===n-2&&u>1)continue;u=u<0?0:u>1?1:u;
      if(Math.hypot(A[2*i]+dx*u-x,A[2*i+1]+dy*u-y)<=h)return true}return false};
  const mk=(bodies,cx,cy,R,plates,own)=>{const ids=new Set(bodies.map(v=>v.w.id)),pol=POL.filter(p=>p.b[0]<cx+R&&p.b[2]>cx-R&&p.b[1]<cy+R&&p.b[3]>cy-R&&(!own||!p.ids||p.ids.some(i=>ids.has(i)))),eps=EPS.filter(e=>Math.hypot(e[0]-cx,e[1]-cy)<R+e[2]&&(!own||bodies.some(v=>{const A=v.m.a,n=A.length/2;return Math.hypot(A[0]-e[0],A[1]-e[1])<1||Math.hypot(A[2*n-2]-e[0],A[2*n-1]-e[1])<1}))),
      pls=plates?PLS.filter(p=>p.b[0]<cx+R&&p.b[2]>cx-R&&p.b[1]<cy+R&&p.b[3]>cy-R):[];
    return (x,y)=>{for(const v of bodies)if(inBody(v,x,y))return true;for(const p of pol)if(x>=p.b[0]&&x<=p.b[2]&&y>=p.b[1]&&y<=p.b[3]&&inPoly(p.P,x,y))return true;
      for(const e of eps)if(Math.hypot(e[0]-x,e[1]-y)<=e[2])return true;for(const p of pls)if(Math.hypot(p.cx-x,p.cy-y)<=p.R&&inPoly(p.P,x,y))return true;return false}};
  const walk=(v,e,max)=>{const out=[];let cur=v,p=lnEndA((v.m0||v.m).a,e),tot=0;
    while(tot<max&&out.length<12){const C=lnConts(E,cur,p[0],p[1],p[2],p[3],.85,false);if(C.length!==1)break;const o=C[0];if(o.v===v||out.some(q=>q.v===o.v))break;
      const R=lnConts(E,o.v,o.p[0],o.p[1],o.p[2],o.p[3],.85,false);if(R.length!==1||R[0].v!==cur)break;   // rozwidlenie – koniec ciągu
      const m0=o.v.m0||o.v.m,L=m0.cum[m0.cum.length-1];out.push({v:o.v,e:o.e,s:tot,L});tot+=L;p=lnEndA(m0.a,1-o.e);cur=o.v}return out};
  const ptIn=(q,u)=>{const m0=q.v.m0||q.v.m,L=q.L,r=lnPtDir(m0.a,m0.cum,Math.max(0,Math.min(L,q.e?L-u:u)));return q.e?[r[0],r[1],-r[2],-r[3]]:r};   // oś z OSM, kierunek marszu
  const atJ=(v,e)=>{const CU=lnCuts(v,s,lnLanePx(v.w.kc,s)/s),L=v.m.cum[v.m.cum.length-1];return !!(CU&&CU.a.length&&(e?CU.a[CU.a.length-1]>=L-.5:CU.a[0]<=.5))};
  const JL=[],jk=new Set();   // styki: jedyne przedłużenie z obu stron, nie na skrzyżowaniu
  for(const v of V){const m0=v.m0||v.m;if(m0.a.length<4||!v.m.cum)continue;
    for(const e of [0,1]){const p=lnEndA(m0.a,e),C=lnConts(E,v,p[0],p[1],p[2],p[3],.85,false);if(C.length!==1)continue;const o=C[0];
      const R=lnConts(E,o.v,o.p[0],o.p[1],o.p[2],o.p[3],.85,false);if(R.length!==1||R[0].v!==v)continue;if(atJ(v,e)||atJ(o.v,o.e))continue;
      const k1=v.w.id+'|'+e,k2=o.v.w.id+'|'+o.e,k=k1<k2?k1+'/'+k2:k2+'/'+k1;if(jk.has(k))continue;jk.add(k);
      JL.push({v,e,g:{v:o.v,e:o.e,h:o.v.w.N*lnLanePx(o.v.w.kc,s)/s/2}})}}
  const dips=[],holes=[];let nj=0,ns=0;const seen=new Set();
  for(const j of JL){const v=j.v,e=j.e,m0=v.m0||v.m,Lv=m0.cum[m0.cum.length-1],p0=lnEndA(m0.a,e);
    if(Math.hypot(p0[0]-ox,p0[1]-oy)>320)continue;nj++;
    const fw=walk(v,e,45),bw=[{v,e,s:0,L:Lv}].concat(walk(v,1-e,45-Lv).map(q=>({v:q.v,e:q.e,s:q.s+Lv,L:q.L})));   // przed stykiem: v (od styku wstecz) i poprzednie odcinki
    const bodies=[v,...fw.map(q=>q.v),...bw.slice(1).map(q=>q.v)],LW=lnLanePx(v.w.kc,s)/s,inF=mk([...bodies],p0[0],p0[1],40,true,false);
    const RG=[...fw.map(q=>({v:q.v,a:q.s,b:q.s+q.L})),...bw.map(q=>({v:q.v,a:-(q.s+q.L),b:-q.s}))],IA=new Map();   // zakresy T odcinków ciągu
    const inAt=T=>{const k=Math.round(T/6);let f=IA.get(k);if(!f){const loc=[...new Set(RG.filter(r=>r.b>=T-20&&r.a<=T+20).map(r=>r.v))];f=mk(loc,p0[0],p0[1],110,false,true);IA.set(k,f)}return f};   // brzegi: tylko odcinki ciągu w pobliżu (±20 m) i ich kliny / mostki / styki
    // bw: idziemy od styku w tył; punkt w odległości d przed stykiem: w odcinku q od jego końca (1-e dla v) – kierunek marszu odwracamy, by patrzeć „do przodu”
    const inJ=(q,u)=>{const CU=lnCuts(q.v,s,lnLanePx(q.v.w.kc,s)/s);if(!CU)return false;const c=q.e?q.L-u:u;for(const A of [CU.a,CU.l,CU.r])if(A)for(let k=0;k<A.length;k+=2)if(A[k]-3<=c&&A[k+1]+3>=c)return true;return false};   // skrzyżowanie (tam brzegi wyznacza płyta skrzyżowania)
    const at=T=>{if(T>=0){let q=null;for(const x of fw)if(T>=x.s&&T<=x.s+x.L){q=x;break}if(!q||inJ(q,T-q.s))return null;return ptIn(q,T-q.s)}
      const d=-T;let q=null;for(const x of bw)if(d>=x.s&&d<=x.s+x.L){q=x;break}if(!q||inJ(q,d-q.s))return null;const r=ptIn(q,d-q.s);return [r[0],r[1],-r[2],-r[3]]};
    const S=[];
    for(let T=-44;T<=44;T+=1.5){const r=at(T);if(!r){S.push(null);continue}const [x,y,ux,uy]=r,nx=uy,ny=-ux;ns++;
      if(SPP.some(P=>inPoly(P,x,y))){S.push(null);continue}   // płyta rozwidlenia – tam brzegi wyznacza płyta
      const inA=inAt(T);if(!inA(x,y)){S.push([0,0,x,y]);continue}
      let l=0,rr=0;while(l<60&&inA(x-nx*(l+.5),y-ny*(l+.5)))l+=.5;while(rr<60&&inA(x+nx*(rr+.5),y+ny*(rr+.5)))rr+=.5;S.push([l,rr,x,y])}
    for(const sd of [0,1]){const W=S.map(q=>q?q[sd]:null);let best=null;
      for(let jx=1;jx<W.length-1;jx++){if(W[jx]==null)continue;let a=-1,b=-1;
        for(let i=Math.max(0,jx-40);i<jx;i++)if(W[i]!=null&&(jx-i)*1.5<=60)a=Math.max(a,W[i]);
        for(let k=jx+1;k<Math.min(W.length,jx+41);k++)if(W[k]!=null&&(k-jx)*1.5<=60){let ok=false;for(let i=Math.max(0,jx-40);i<jx;i++)if(W[i]!=null&&(k-i)*1.5<=60&&W[i]-W[jx]>=.35*LW){ok=true;break}if(ok)b=Math.max(b,W[k])}
        const dp=Math.min(a,b)-W[jx];if(a>=0&&b>=0&&dp>=.35*LW&&(!best||dp>best.dp))best={dp:+(dp/LW).toFixed(2),x:S[jx][2],y:S[jx][3]}}
      if(best){const k=Math.round(best.x/8)+','+Math.round(best.y/8)+','+sd;if(!seen.has(k)){seen.add(k);dips.push({id:v.w.id,sd:sd?'P':'L',dep:best.dp,lat:+(D.lat+best.y/111195).toFixed(6),lon:+(D.lon+best.x/kx).toFixed(6),W:W.map(x=>x==null?null:+(x/LW).toFixed(1)).join(' ')})}}}
    // szczeliny na samym styku: punkty w poprzek jezdni (w zakresie węższego z dwóch odcinków) tuż przed i tuż za stykiem
    const g=j.g,hA=v.w.N*LW/2,hB=g.h,pa=lnEndA(v.m.a,e),pb=lnEndA(g.v.m.a,g.e),nx=p0[3],ny=-p0[2];
    const ca=(pa[0]-p0[0])*nx+(pa[1]-p0[1])*ny,cb=(pb[0]-p0[0])*nx+(pb[1]-p0[1])*ny,lo=Math.max(ca-hA,cb-hB)+.4,hi=Math.min(ca+hA,cb+hB)-.4;
    let hc=0;for(let T=-1;T<=1.01;T+=.5)for(let x=lo;x<=hi;x+=.5){const px=p0[0]+p0[2]*T+nx*x,py=p0[1]+p0[3]*T+ny*x;if(!inF(px,py))hc++}
    if(hc)holes.push({id:v.w.id,to:g.v.w.id,n:hc,lat:+(D.lat+p0[1]/111195).toFixed(6),lon:+(D.lon+p0[0]/kx).toFixed(6)});
  }
  return {nj,ns,dips,holes}}"""
PTS=[(51.11185,17.05830),(51.11160,17.05930),(51.10760,17.04640),(51.109189,17.051237),(51.1079,17.0385),(51.1175,16.9900),(51.0800,17.0150),(51.0830,17.0700),
     (51.1123,17.0590),(51.1092,17.0520),(51.0450,17.0700),(51.1300,16.9300),(51.0857,17.01165),(51.1035,17.0310),(51.0700,16.9950),(51.0970,17.0159)]
async def main():
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=PTS[0][0],lon=PTS[0][1])
        res=[]
        for la,lo in PTS:
            await goto(pg,la,lo,hd=0,speed=0,zoom=2.4,tilt=0,wait=1500)
            last=None;same=0
            for _ in range(80):   # dane mapy i pasów wczytane wokół kamery, a zestaw odcinków przestał się zmieniać
                r=await pg.evaluate("(()=>{try{const c=vecCam(performance.now());if(!vecData||vecBusy||lnBusy||dist(vecData.lat,vecData.lon,c.lat,c.lon)>=600)return null;const D=vecData,kx=111195*Math.cos(rad(D.lat));return lnVis(D,scaleCur,(c.lon-D.lon)*kx,(c.lat-D.lat)*111195,450).length+'/'+LANEW.size+'/'+D.LNJK+'/'+(signs?signs.v:0)+'/'+scaleCur.toFixed(3)}catch(e){return 'x'}})()")
                if r is not None and r==last:
                    same+=1
                    if same>=3:break
                else:same=0
                last=r;await pg.wait_for_timeout(400)
            r=await pg.evaluate(JS);r['at']=(la,lo);res.append(r)
            print('  ',(la,lo),'styki',r['nj'],'wcięcia',len(r['dips']),'szczeliny',len(r['holes']),flush=True)
        nj=sum(r['nj'] for r in res);D=[d for r in res for d in r['dips']];Hh=[h for r in res for h in r['holes']]
        print('   wcięcia:',D[:12]);print('   szczeliny:',Hh[:12])
        t('styki odcinków jezdni z pasami (poza skrzyżowaniami) znalezione w wielu miejscach',nj>=60,nj)
        t('brzeg jezdni bez wcięć (zwężenie o ≥ 0,35 pasa i zaraz poszerzenie, na ≤ 60 m)',not D,D[:6])
        t('bez szczelin na stykach odcinków (tło nie prześwituje)',not Hh,Hh[:6])
        t('bez błędów strony',not logs,logs[:3])
        await b.close()
    t.end()
asyncio.run(main())
