// ================= Wersja 199–200: jezdnie z pasami od nowa – etap 1: obrys jezdni i linie pasów =================
// Stary moduł (wersje 138–197) rysował każdy odcinek OSM osobno i łatał styki (kliny, płyty, mostki), więc na rozwidleniach i skrzyżowaniach
// wychodziły schodki, wcięcia i krzyżujące się linie. Teraz:
// 1) kolejne odcinki tej samej jezdni (jedyne przedłużenie z obu stron, ten sam poziom, ten sam rodzaj ruchu) tworzą jeden ciąg – jeden wielokąt, bez styków,
// 2) Wersja 200: jezdnia ma dokładnie szerokość zwykłej drogi z mapy pod nią (w wersji 199 każdy pas miał pół szerokości drogi, więc droga z 4–6 pasami
//    była 2–3 razy szersza od mapy i zakrywała przejścia, torowiska i chodniki), a pasy dzielą tę szerokość między siebie,
// 3) zmiana liczby pasów jest łagodna (linie rozchodzą się albo schodzą stopniowo), krótkie zmiany (np. odcinek w środku skrzyżowania) są pomijane,
// 4) tam, gdzie ciąg przechodzi w zwykłą drogę innej klasy, szerokość zmienia się łagodnie,
// 5) na rozwidleniu odnogi wychodzą z węzła w kierunku jezdni sprzed rozwidlenia; jezdnie, które leżą obok siebie i na siebie nachodzą (odnogi tuż za
//    rozwidleniem, dwie jezdnie drogi dwujezdniowej), dzielą wspólne miejsce według liczby pasów – bez poszerzania drogi i bez nakładania linii,
// 6) linie znikają tam, gdzie leży inna droga (skrzyżowania; boczna ulica przerywa tylko linie po swojej stronie),
// 7) koniec jezdni bez dalszej drogi jest zaokrąglony jak zwykłe drogi na mapie.
var jzOn=true,JZN=null;
const JZ_DT=1,JZ_SLOPE=.3,JZ_MIN_S=.6;
function jzDir(a,n,e){   // kierunek „na zewnątrz” odcinka na końcu e (z ostatnich ≥ 5 m)
  const i=e?n-1:0,x=a[2*i],y=a[2*i+1];let k=e?i-1:i+1,dx=0,dy=0;
  while(k>=0&&k<n){dx=x-a[2*k];dy=y-a[2*k+1];if(dx*dx+dy*dy>=25)break;k+=e?-1:1}
  const L=Math.hypot(dx,dy)||1;return [dx/L,dy/L];
}
function jzLeaves(w,e){return (w.ow===1&&e===1)||(w.ow===-1&&e===0)}   // ruch jednokierunkowy opuszcza odcinek na tym końcu
// siatka odcinków zwykłych dróg z mapy (do zakończeń ciągów i do przerw w liniach na skrzyżowaniach)
function jzTiles(D){
  if(D.JZT)return D.JZT;
  const G=new Map(),CS=25,add=(cx,cy,o)=>{const k=((cx&32767)<<15)|(cy&32767);let l=G.get(k);if(!l)G.set(k,l=[]);l.push(o)};   // klucz: mała liczba całkowita (obszar mapy to kilka km, więc bez kolizji)
  for(const ra of (D.RS||[])){
    const k=ra.k;if(!k||k==='sv')continue;
    for(let i=0;i+3<ra.length;i+=2){
      const x1=ra[i],y1=ra[i+1],x2=ra[i+2],y2=ra[i+3],L=Math.hypot(x2-x1,y2-y1);if(L<.05)continue;
      const o={x1,y1,x2,y2,ux:(x2-x1)/L,uy:(y2-y1)/L,L,k,ra,i,lv:ra.lv?1:0};
      const a0=Math.floor(Math.min(x1,x2)/CS),a1=Math.floor(Math.max(x1,x2)/CS),b0=Math.floor(Math.min(y1,y2)/CS),b1=Math.floor(Math.max(y1,y2)/CS);
      for(let cx=a0;cx<=a1;cx++)for(let cy=b0;cy<=b1;cy++)add(cx,cy,o);
    }
  }
  return D.JZT={G,CS};
}
var jzQ=0;
function jzTileNear(T,x,y,r){   // odcinki zwykłych dróg w promieniu r od punktu (bez powtórzeń – znacznik zapytania zamiast zbioru)
  const out=[],CS=T.CS,a0=Math.floor((x-r)/CS),a1=Math.floor((x+r)/CS),b0=Math.floor((y-r)/CS),b1=Math.floor((y+r)/CS),q=++jzQ;
  for(let cx=a0;cx<=a1;cx++)for(let cy=b0;cy<=b1;cy++){const l=T.G.get(((cx&32767)<<15)|(cy&32767));if(l)for(const o of l)if(o.q!==q){o.q=q;out.push(o)}}
  return out;
}
// sieć ciągów jezdni z danymi o pasach (raz na dane mapy i dane o pasach)
function jzNet(D){
  if(JZN&&JZN.D===D&&JZN.ver===laneVer)return JZN;
  const kx=111195*Math.cos(rad(D.lat)),bb=D.bb||[-1e9,-1e9,1e9,1e9],M=300,P=[],node=new Map();
  const la0=D.lat+(bb[1]-M)/111195,la1=D.lat+(bb[3]+M)/111195,lo0=D.lon+(bb[0]-M)/kx,lo1=D.lon+(bb[2]+M)/kx;
  const nk=(la,lo)=>((Math.round((la-D.lat)*1e6)&32767)<<15)|(Math.round((lo-D.lon)*1e6)&32767);   // węzeł: skrót (mała liczba); ten sam węzeł = te same współrzędne (sprawdzane niżej)
  for(const w of LANEW.values()){
    const g=w.g,n0=g.length/2;if(n0<2||!(w.N>0))continue;
    let wb=w.jzb;if(!wb){wb=w.jzb=[1e9,1e9,-1e9,-1e9];for(let i=0;i<g.length;i+=2){if(g[i]<wb[0])wb[0]=g[i];if(g[i]>wb[2])wb[2]=g[i];if(g[i+1]<wb[1])wb[1]=g[i+1];if(g[i+1]>wb[3])wb[3]=g[i+1]}}
    if(wb[2]<la0||wb[0]>la1||wb[3]<lo0||wb[1]>lo1)continue;
    let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;const t=[];
    for(let i=0;i<n0;i++){const x=(g[2*i+1]-D.lon)*kx,y=(g[2*i]-D.lat)*111195;
      if(t.length&&Math.hypot(x-t[t.length-2],y-t[t.length-1])<.05)continue;
      t.push(x,y);if(x<x0)x0=x;if(x>x1)x1=x;if(y<y0)y0=y;if(y>y1)y1=y}
    if(t.length<4||x1<bb[0]-M||x0>bb[2]+M||y1<bb[1]-M||y0>bb[3]+M)continue;
    const a=Float64Array.from(t),n=a.length/2;let L=0;for(let i=1;i<n;i++)L+=Math.hypot(a[2*i]-a[2*i-2],a[2*i+1]-a[2*i-1]);
    const p={w,a,n,L,i:P.length,lk:[null,null],cd:[null,null],u:[jzDir(a,n,0),jzDir(a,n,1)],k:[nk(g[0],g[1]),nk(g[2*n0-2],g[2*n0-1])],c:[g[0],g[1],g[2*n0-2],g[2*n0-1]]};P.push(p);
    for(const e of [0,1]){let l=node.get(p.k[e]);if(!l)node.set(p.k[e],l=[]);l.push({p,e})}
  }
  // przedłużenia: drugi koniec w tym samym węźle, kierunek prawie na wprost (do 60°), ten sam poziom, ruch jednokierunkowy przechodzi z odcinka w odcinek
  for(const p of P)for(const e of [0,1]){
    const c=[],u=p.u[e],w=p.w;
    for(const q of node.get(p.k[e])){if(q.p===p||q.p.c[2*q.e]!==p.c[2*e]||q.p.c[2*q.e+1]!==p.c[2*e+1])continue;const v=q.p.w,uq=q.p.u[q.e];
      if(-(u[0]*uq[0]+u[1]*uq[1])<.5)continue;   // (wjazd na most to ta sama jezdnia – jeden ciąg, rysowany poziomami)
      if(w.ow!==0&&v.ow!==0&&jzLeaves(w,e)===jzLeaves(v,q.e))continue;
      c.push(q)}
    p.cd[e]=c;
  }
  for(const p of P)for(const e of [0,1]){const c=p.cd[e];if(c.length!==1)continue;const q=c[0],b=q.p.cd[q.e];
    if(b.length===1&&b[0].p===p&&(p.w.ow===0)===(q.p.w.ow===0))p.lk[e]=q}
  // ciągi
  const C=[],seen=new Uint8Array(P.length),END=new Map();
  for(const p0 of P){if(seen[p0.i])continue;
    let cur=p0,ce=0,loop=false,g=0;
    while(cur.lk[ce]&&g++<2000){const nb=cur.lk[ce];if(nb.p===p0){loop=true;break}cur=nb.p;ce=1-nb.e}
    if(loop){cur=p0;ce=0}
    const pcs=[];let q=cur,qe=ce;g=0;
    while(q&&!seen[q.i]&&g++<2000){seen[q.i]=1;pcs.push({p:q,fwd:qe===0});const nb=q.lk[1-qe];if(!nb)break;q=nb.p;qe=nb.e}
    const ch=jzChain(pcs,loop,C.length);C.push(ch);
    END.set(ch.pcs[0].p.i+'|'+(ch.pcs[0].fwd?0:1),{ch,at:0});
    const z=ch.pcs[ch.pcs.length-1];END.set(z.p.i+'|'+(z.fwd?1:0),{ch,at:1});
  }
  // rozwidlenia i połączenia: koniec jezdni z dwoma przedłużeniami, z których każde ma tylko ją
  for(const p of P)for(const e of [0,1]){const c=p.cd[e];if(c.length!==2)continue;
    if(!c.every(q=>{const b=q.p.cd[q.e];return b.length===1&&b[0].p===p}))continue;
    const u=p.u[e];if(!c.every(q=>{const v=q.p.u[q.e];return -(u[0]*v[0]+u[1]*v[1])>=.82}))continue;   // ostrzejsze rozejście to skrzyżowanie, nie rozwidlenie
    const T=END.get(p.i+'|'+e),B=c.map(q=>END.get(q.p.i+'|'+q.e));
    if(!T||!B[0]||!B[1]||B[0].ch===B[1].ch||B.some(b=>b.ch===T.ch))continue;
    for(let k=0;k<2;k++){B[k].ch.fk=B[k].ch.fk||[null,null];B[k].ch.fk[B[k].at]={T,S:B[1-k]}}
    T.ch.ft=T.ch.ft||[null,null];T.ch.ft[T.at]=B;
  }
  // zakończenia: czy dalej biegnie zwykła droga z mapy (wtedy jezdnia zwęża się do jej szerokości)
  const TT=jzTiles(D);
  for(const ch of C){if(ch.closed)continue;
    ch.tail=[null,null];if(!ch.show&&!ch.fk&&!ch.ft)continue;
    for(const at of [0,1]){if(ch.fk&&ch.fk[at]||ch.ft&&ch.ft[at])continue;
      const pe=at?ch.pcs[ch.pcs.length-1]:ch.pcs[0],lv=pe.p.w.z?1:0;
      const A=ch.a,n=A.length/2,i=at?n-1:0,x=A[2*i],y=A[2*i+1],u=jzDir(A,n,at);
      let best=null,bd=1e9;
      for(const o of jzTileNear(TT,x+u[0]*12,y+u[1]*12,5)){
        const cs=o.ux*u[0]+o.uy*u[1];if(Math.abs(cs)<.85||o.lv!==lv)continue;
        const px=x+u[0]*12,py=y+u[1]*12,t=Math.max(0,Math.min(o.L,(px-o.x1)*o.ux+(py-o.y1)*o.uy)),qx=o.x1+o.ux*t,qy=o.y1+o.uy*t,dd=Math.hypot(px-qx,py-qy);
        if(dd<4&&dd<bd){bd=dd;best={o,dir:cs>0?1:-1}}
      }
      if(best){ch.tail[at]=jzTailPts(best.o,best.dir,x,y,u,70);ch.tail[at].lv=lv}
    }
  }
  const sorted=C.slice().sort((a,b)=>jzRank(a.kc)-jzRank(b.kc));
  const prev=JZN;if(prev)prev.prev=null;   // poprzednia sieć: jej linie rysujemy, dopóki nowe się nie policzą (bez znikania linii po doczytaniu danych)
  JZN={D,ver:laneVer,C,sorted,bk:new Map(),prev};
  return JZN;
}
function jzRank(kc){const k=LN_K[kc];return ['sv','rs','tr','sc','pr','mwl','mw'].indexOf(k)}
// punkty przedłużenia ciągu wzdłuż zwykłej drogi z mapy (od końca ciągu, długość ok. L)
function jzTailPts(o,dir,x,y,u,L){
  const ra=o.ra,pts=[x,y];let px=x,py=y,acc=0;
  // rzut punktu 12 m dalej na odcinek, potem kolejne wierzchołki drogi w kierunku dir
  const sx=x+u[0]*12,sy=y+u[1]*12,t=Math.max(0,Math.min(o.L,(sx-o.x1)*o.ux+(sy-o.y1)*o.uy));
  let cx=o.x1+o.ux*t,cy=o.y1+o.uy*t;acc+=Math.hypot(cx-px,cy-py);pts.push(cx,cy);px=cx;py=cy;
  let i=dir>0?o.i+2:o.i;   // indeks następnego wierzchołka w kierunku jazdy
  while(acc<L&&i>=0&&i+1<ra.length){const qx=ra[i],qy=ra[i+1],d=Math.hypot(qx-px,qy-py);if(d>.05){pts.push(qx,qy);acc+=d;px=qx;py=qy}i+=dir>0?2:-2}
  if(acc<L){const n=pts.length/2,ux=pts[2*n-2]-pts[2*n-4],uy=pts[2*n-1]-pts[2*n-3],l=Math.hypot(ux,uy)||1;pts.push(px+ux/l*(L-acc),py+uy/l*(L-acc))}
  return {pts,k:o.k};
}
// klasa zwykłej drogi z mapy leżącej pod odcinkiem (z niej szerokość jezdni – taka jak na mapie); brak – klasa z danych o pasach
function jzTileK(TT,p){
  if(p.tk!==undefined)return p.tk;
  const a=p.a,n=p.n,v=new Map(),lv=p.w.z?1:0;let acc=0,f=0;const F=[.2,.5,.8];
  for(let i=1;i<n&&f<3;i++){const x1=a[2*i-2],y1=a[2*i-1],dx=a[2*i]-x1,dy=a[2*i+1]-y1,l=Math.hypot(dx,dy);if(l<1e-6)continue;
    while(f<3&&acc+l>=F[f]*p.L){const t=(F[f]*p.L-acc)/l,x=x1+dx*t,y=y1+dy*t,ux=dx/l,uy=dy/l;
      for(const o of jzTileNear(TT,x,y,3)){if(o.lv!==lv||Math.abs(o.ux*ux+o.uy*uy)<.9)continue;
        const q=Math.max(0,Math.min(o.L,(x-o.x1)*o.ux+(y-o.y1)*o.uy)),dd=Math.hypot(x-o.x1-o.ux*q,y-o.y1-o.uy*q);if(dd<=2.5)v.set(o.k,(v.get(o.k)||0)+1)}
      f++}
    acc+=l}
  let k=LN_K[p.w.kc]||'tr',b=0;for(const [kk,c] of v)if(c>b){b=c;k=kk}
  return p.tk=k;
}
// ciąg: oś (punkty co JZ_DT m), dla każdej próbki – odcinek, kierunek, liczba pasów
function jzChain(pcs,closed,id){
  // jezdnia jednokierunkowa: ciąg w kierunku ruchu
  const f=pcs[0],w0=f.p.w;
  if(w0.ow!==0&&((w0.ow===1)!==f.fwd)){pcs.reverse();for(const q of pcs)q.fwd=!q.fwd}
  const ax=[],tp=[];let L=0;
  for(let j=0;j<pcs.length;j++){const q=pcs[j],a=q.p.a,n=q.p.n;q.s0=L;
    for(let k=0;k<n;k++){const i=q.fwd?k:n-1-k,x=a[2*i],y=a[2*i+1];
      if(ax.length){const dx=x-ax[ax.length-2],dy=y-ax[ax.length-1],d=Math.hypot(dx,dy);if(d<.05)continue;L+=d}
      ax.push(x,y)}
    q.s1=L;}
  const a=Float64Array.from(ax),n=a.length/2,cum=new Float64Array(n);for(let i=1;i<n;i++)cum[i]=cum[i-1]+Math.hypot(a[2*i]-a[2*i-2],a[2*i+1]-a[2*i-1]);
  // klasa drogi przeważająca na długości
  const kl=new Map();for(const q of pcs)kl.set(q.p.w.kc,(kl.get(q.p.w.kc)||0)+(q.s1-q.s0));
  let kc=pcs[0].p.w.kc,bm=-1;for(const [k,v] of kl)if(v>bm){bm=v;kc=k}
  const ow=w0.ow===0?0:1;
  // liczba pasów w ciągu (dla jednokierunkowej – przeważająca, od niej liczymy lewy brzeg)
  const nl=new Map();for(const q of pcs){const N=q.p.w.N;nl.set(N,(nl.get(N)||0)+(q.s1-q.s0))}
  let Nref=pcs[0].p.w.N;bm=-1;for(const [k,v] of nl)if(v>bm){bm=v;Nref=k}
  let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;for(let i=0;i<n;i++){const x=a[2*i],y=a[2*i+1];if(x<x0)x0=x;if(x>x1)x1=x;if(y<y0)y0=y;if(y>y1)y1=y}
  return {id,pcs,a,cum,L:cum[n-1],closed,ow,kc,Nref,bb:[x0,y0,x1,y1],fk:null,ft:null,tail:null,show:pcs.some(q=>q.p.w.multi),get sig(){return this._s||(this._s=this.pcs.map(q=>q.p.w.id+(q.fwd?'+':'-')).join(','))}};
}
// punkt i kierunek na łamanej (a, cum) w odległości t
function jzAt(a,cum,t){
  const n=cum.length;if(t<=0){const L=Math.hypot(a[2]-a[0],a[3]-a[1])||1;return [a[0],a[1],(a[2]-a[0])/L,(a[3]-a[1])/L]}
  if(t>=cum[n-1]){const L=Math.hypot(a[2*n-2]-a[2*n-4],a[2*n-1]-a[2*n-3])||1;return [a[2*n-2],a[2*n-1],(a[2*n-2]-a[2*n-4])/L,(a[2*n-1]-a[2*n-3])/L]}
  let lo=0,hi=n-1;while(hi-lo>1){const m=(lo+hi)>>1;if(cum[m]<=t)lo=m;else hi=m}
  const L=cum[hi]-cum[lo]||1,f=(t-cum[lo])/L,dx=a[2*hi]-a[2*lo],dy=a[2*hi+1]-a[2*lo+1];
  return [a[2*lo]+dx*f,a[2*lo+1]+dy*f,dx/L,dy/L];
}
// ---- geometria ciągu dla danej skali (szerokość pasa w metrach zależy od skali tylko przy oddaleniu) ----
function jzKey(s){return ['rs','tr','sc','pr','mwl','mw'].map(k=>Math.round(Math.log(rw(k,s)/s)/Math.log(1.05))).join(',')}
function jzBucket(N,s){
  const key=jzKey(s);let B=N.bk.get(key);
  // przy płynnej zmianie skali nowa geometria najwyżej co 250 ms (w międzyczasie poprzednia – różnica szerokości kilka %); potem dorysowanie
  if(!B&&N.lastB&&performance.now()-N.lastT<250){if(!jzBucket.t)jzBucket.t=setTimeout(()=>{jzBucket.t=0;try{vd=null}catch(e){}},260);return N.lastB}
  if(!B){if(N.bk.size>6){const L=N.lastB;N.bk.clear();if(L)N.bk.set(L.key,L)}const TWk={};for(const k of ['sv','rs','tr','sc','pr','mwl','mw'])TWk[k]=rw(k,s)/2/s;   // połowa szerokości zwykłej drogi z mapy (tyle ma jezdnia z pasami)
    B={key,s,LWk:TWk,TWk,bld:new Set(),geo:new Map(),grid:new Map(),gridOf:new Set(),sig:new Map(),from:N.lastB||null};if(B.from)B.from.from=null;N.bk.set(key,B);N.lastT=performance.now()}   /* (bez łańcucha starych skal w pamięci) */
  N.lastB=B;return B;
}
// przesuwne maksimum / minimum w oknie ±h próbek (kolejka monotoniczna)
function jzSlide(v,h,mx){
  const n=v.length,o=new Float64Array(n),q=new Int32Array(n);let qh=0,qt=0,r=-1;
  for(let i=0;i<n;i++){
    while(r<Math.min(n-1,i+h)){r++;while(qt>qh&&(mx?v[q[qt-1]]<=v[r]:v[q[qt-1]]>=v[r]))qt--;q[qt++]=r}
    while(q[qh]<i-h)qh++;
    o[i]=v[q[qh]];
  }
  return o;
}
// łagodna zmiana: średnia z „rozszerzenia” i „zwężenia” stożkiem o nachyleniu m (zmiana zaczyna się przed stykiem i kończy za nim)
function jzRamp(v,m){
  {let c=true;for(let i=1;i<v.length;i++)if(v[i]!==v[0]){c=false;break}if(c)return Float64Array.from(v)}   // stała wartość – bez liczenia
  const n=v.length,up=Float64Array.from(v),lo=Float64Array.from(v),o=new Float64Array(n);
  for(let i=1;i<n;i++){up[i]=Math.max(up[i],up[i-1]-m);lo[i]=Math.min(lo[i],lo[i-1]+m)}
  for(let i=n-2;i>=0;i--){up[i]=Math.max(up[i],up[i+1]-m);lo[i]=Math.min(lo[i],lo[i+1]+m)}
  for(let i=0;i<n;i++)o[i]=(up[i]+lo[i])/2;
  // średnia krocząca z 11 próbek: bez załamania w środku zmiany i z łagodnym początkiem i końcem
  const r=new Float64Array(n),K=5,at=i=>o[i<0?0:i>=n?n-1:i];let acc=0;
  for(let i=-K;i<=K;i++)acc+=at(i);
  for(let i=0;i<n;i++){r[i]=acc/(2*K+1);acc+=at(i+K+1)-at(i-K)}
  return r;
}
// geometria ciągu: najpierw przebieg szerokości (wystarcza sąsiadom), potem – gdy potrzebny rysunek – rozwidlenia, druga jezdnia, przycięcie i obrys
function jzGeo(N,B,ch,full){
  let G=B.geo.get(ch.id);
  if(!G)G=jzProf(N,B,ch);
  if(!G)return null;
  if(full!==false&&G.st===0){G.st=1;jzDone(N,B,G);G.st=2}   // (st 1: w trakcie – wywołanie zwrotne dostaje G bez dokończenia)
  return G;
}
function jzProf(N,B,ch){
  if(B.bld.has(ch.id))return null;B.bld.add(ch.id);   // (ciąg w trakcie liczenia – np. wzajemne rozwidlenia)
  try{
  let G;const dt=JZ_DT,TWk=B.TWk,TT=jzTiles(N.D);
  // oś: przedłużenie na początku (odwrócone) + ciąg + przedłużenie na końcu
  const ax=[];let t0=0;
  const T0=ch.tail&&ch.tail[0],T1=ch.tail&&ch.tail[1];
  if(T0){const p=T0.pts;for(let i=p.length-2;i>=2;i-=2)ax.push(p[i],p[i+1])}
  const st=ax.length/2;for(let i=0;i<ch.a.length;i+=2)ax.push(ch.a[i],ch.a[i+1]);
  if(T1){const p=T1.pts;for(let i=2;i<p.length;i+=2)ax.push(p[i],p[i+1])}
  const A=Float64Array.from(ax),na=A.length/2,cum=new Float64Array(na);for(let i=1;i<na;i++)cum[i]=cum[i-1]+Math.hypot(A[2*i]-A[2*i-2],A[2*i+1]-A[2*i-1]);
  t0=cum[st];   // t ciągu = t osi − t0
  const Ltot=cum[na-1],n=Math.max(2,Math.round(Ltot/dt)+1),h=Ltot/(n-1);
  const X=new Float64Array(n),Y=new Float64Array(n),T=new Float64Array(n),W2=new Float64Array(n),nA=new Float64Array(n),nB=new Float64Array(n),nC=new Float64Array(n),PI=new Int32Array(n),ZZ=new Uint8Array(n);
  const lanes=(i,q)=>{const w=q.p.w;if(ch.ow===0){nA[i]=q.fwd?w.nb:w.nf;nB[i]=q.fwd?w.nf:w.nb;nC[i]=w.c||0}else{nA[i]=0;nC[i]=0;nB[i]=w.N}};   // A: pasy po lewej (w stronę przeciwną), B: po prawej, C: środkowe
  let pj=0;
  for(let i=0;i<n;i++){const ta=i*h,p=jzAt(A,cum,ta);X[i]=p[0];Y[i]=p[1];const t=ta-t0;T[i]=t;
    if(t<-.01&&T0){W2[i]=TWk[T0.k]||TWk.tr;PI[i]=-1;ZZ[i]=T0.lv;lanes(i,ch.pcs[0]);continue}   // przedłużenie: szerokość zwykłej drogi, pasy jak na końcu ciągu
    if(t>ch.L+.01&&T1){W2[i]=TWk[T1.k]||TWk.tr;PI[i]=-2;ZZ[i]=T1.lv;lanes(i,ch.pcs[ch.pcs.length-1]);continue}
    while(pj<ch.pcs.length-1&&t>ch.pcs[pj].s1)pj++;while(pj>0&&t<ch.pcs[pj].s0)pj--;
    const q=ch.pcs[pj];W2[i]=TWk[jzTileK(TT,q.p)]||TWk.tr;PI[i]=pj;ZZ[i]=q.p.w.z?1:0;lanes(i,q);
  }
  // krótkie zmiany liczby pasów pomijamy (domknięcie i otwarcie), potem zmiany łagodne: pas przybywa / ubywa na ok. 3 szerokościach drogi
  let lwd=0;for(let i=0;i<n;i++)lwd+=W2[i];lwd/=n;
  const hw=Math.round((Math.max(40,8*lwd)+3.6*lwd)/2/h),ho=Math.round(Math.max(10,lwd)/2/h),mN=h/(3*lwd);
  const cl=v=>{const c=jzSlide(jzSlide(v,hw,true),hw,false);return jzSlide(jzSlide(c,ho,false),ho,true)};
  const fA=jzRamp(cl(nA),mN),fB=jzRamp(cl(nB),mN),fC=jzRamp(cl(nC),mN),NT=new Float64Array(n);for(let i=0;i<n;i++)NT[i]=Math.max(1,fA[i]+fB[i]+fC[i]);
  // szerokość: zmiana klasy drogi łagodnie; przy rozwidleniu – w węźle jak jezdnia sprzed rozwidlenia
  const wn=jzRamp(W2,JZ_SLOPE*h);
  if(ch.fk)for(const at of [0,1]){const F=ch.fk[at];if(!F)continue;const TG=jzGeo(N,B,F.T.ch,false);if(!TG)continue;
    const ti=F.T.at?TG.n-1:0,n0=at?n-1:0,dW=TG.wn[ti]-wn[n0];if(Math.abs(dW)<.01)continue;const Lw=Math.max(20,5*Math.abs(dW));   /* (krótki ciąg: zmiana nie kończy się w nim, ale nie jest stroma) */
    for(let k=0;k<n;k++){const ds=at?ch.L-T[k]:T[k];if(ds<-.5||ds>=Lw)continue;const v=Math.max(0,ds)/Lw;wn[k]+=dW*(1-v*v*(3-2*v))}}
  // kierunek osi: różnica środkowa ±2 m (wygładza załamania)
  const UX=new Float64Array(n),UY=new Float64Array(n),k2=Math.max(1,Math.round(2/h));
  for(let i=0;i<n;i++){const a=Math.max(0,i-k2),b=Math.min(n-1,i+k2),dx=X[b]-X[a],dy=Y[b]-Y[a],l=Math.hypot(dx,dy)||1;UX[i]=dx/l;UY[i]=dy/l}
  const LWs=new Float64Array(n);for(let i=0;i<n;i++)LWs[i]=2*wn[i]/NT[i];
  G={ch,n,h,X,Y,T,UX,UY,wn,gL:Float64Array.from(wn),gR:Float64Array.from(wn),nA:fA,nB:fB,nC:fC,NT,LWs,PI,ZZ,A,cumA:cum,t0,d:new Float64Array(n),i0:0,i1:n-1,lines:null,ok:false,fp:[null,null],sq:new Uint8Array(n)};
  B.geo.set(ch.id,G);B.sig.set(ch.sig,G);
  {const PB=N.prev&&N.prev.bk.get(B.key),PG=PB&&PB.sig.get(ch.sig);   // ten sam ciąg w poprzednich danych: jego linie (przesunięte do nowego układu) do czasu policzenia nowych
    if(PG&&(PG.lines||PG.old)&&PG.n===n){const pd=N.prev.D,kx=111195*Math.cos(rad(N.D.lat)),L=PG.lines||PG.old.L,o=PG.lines?[0,0]:PG.old.o;
      G.old={L,o:[o[0]+(pd.lon-N.D.lon)*kx,o[1]+(pd.lat-N.D.lat)*111195]}}
    else if(B.from){const QG=B.from.geo.get(ch.id);if(QG&&QG.lines)G.old={L:QG.lines,o:[0,0]}}}   // ta sama sieć, poprzednia skala
  G.st=0;return G;
  }finally{B.bld.delete(ch.id)}
}
function jzDone(N,B,G){
  const {ch,n,T}=G,T0=ch.tail&&ch.tail[0],T1=ch.tail&&ch.tail[1],TWk=B.TWk;
  if(ch.fk)for(const at of [0,1]){const F=ch.fk[at];if(F)try{jzFork(N,B,G,at,F)}catch(e){lnFail(e)}}
  try{jzSqueeze(N,B,G)}catch(e){lnFail(e)}
  const {gL,gR,NT,LWs}=G;for(let k=0;k<n;k++)LWs[k]=(gL[k]+gR[k])/NT[k];
  // przycięcie przedłużeń tam, gdzie jezdnia osiągnęła już szerokość zwykłej drogi
  if(T1){let i=n-1;for(let k=0;k<n;k++)if(T[k]>ch.L){const tl=TWk[T1.k]||TWk.tr;if(Math.abs(gL[k]-tl)<.05&&Math.abs(gR[k]-tl)<.05){i=k;break}}G.i1=Math.max(0,i)}
  if(T0){let i=0;for(let k=n-1;k>=0;k--)if(T[k]<0){const tl=TWk[T0.k]||TWk.tr;if(Math.abs(gL[k]-tl)<.05&&Math.abs(gR[k]-tl)<.05){i=k;break}}G.i0=Math.min(G.i1,i)}
  jzOutline(G);G.ok=true;
}
// rozwidlenie / połączenie: odnoga wychodzi z węzła w kierunku jezdni sprzed rozwidlenia – w węźle ten sam przekrój (bez szczeliny i schodka),
// dalej przekrój stopniowo obraca się do własnego kierunku odnogi (bez zawinięcia brzegu)
function jzFork(N,B,G,at,F){
  const ch=G.ch,TG=jzGeo(N,B,F.T.ch,false);if(!TG)return;
  const n=G.n,ti=F.T.at?TG.n-1:0,sT=F.T.at?1:-1,sg=at?-1:1,n0=at?n-1:0;
  const uTx=sT*TG.UX[ti],uTy=sT*TG.UY[ti];   // kierunek jezdni w stronę odnóg
  const pt=(a,dist)=>{const T=G.T,t=a?ch.L-dist:dist;if(t>=T[n-1])return n-1;if(t<=T[0])return 0;let lo=0,hi=n-1;while(hi-lo>1){const m=(lo+hi)>>1;if(T[m]<=t)lo=m;else hi=m}return t-T[lo]<T[hi]-t?lo:hi};
  const dist=k=>{const v=at?ch.L-G.T[k]:G.T[k];return v<0&&v>-.5?0:v};   // (węzeł: zaokrąglenie)
  const i10=pt(at,Math.min(10,ch.L*.5)),nx=G.X[n0],ny=G.Y[n0];let bx=G.X[i10]-nx,by=G.Y[i10]-ny;const bl=Math.hypot(bx,by)||1;bx/=bl;by/=bl;
  const th=Math.acos(Math.max(-1,Math.min(1,bx*uTx+by*uTy))),wB=2*G.wn[n0],om=Math.max(wB,2*TG.wn[ti]),Lb=Math.min(ch.L*.45,Math.max(12,3*th*om));
  G.fp[at]={w:G.NT[n0],th};   // (pierwszeństwo linii: więcej pasów, potem bardziej na wprost)
  for(let k=0;k<n;k++){const ds=dist(k);if(ds<0||ds>=Lb)continue;const v=ds/Lb,w=1-v*v*(3-2*v);
    let ux=sg*G.UX[k]*(1-w)+uTx*w,uy=sg*G.UY[k]*(1-w)+uTy*w;const l=Math.hypot(ux,uy)||1;G.UX[k]=sg*ux/l;G.UY[k]=sg*uy/l}
}
// powiązanie dwóch ciągów na rozwidleniu: 0 – brak, 1 – jezdnia i jej odnoga, 2 – druga odnoga (ta ma pierwszeństwo), 3 – druga odnoga (tamta ma pierwszeństwo:
// szersza albo bardziej na wprost – jej linie biegną dalej, a linie tej znikają tam, gdzie wchodzą na nią)
function jzRelK(G,Q){
  const a=G.ch,b=Q.ch;
  if(a.fk)for(let at=0;at<2;at++){const F=a.fk[at];if(!F)continue;if(F.T.ch===b)return 1;
    if(F.S.ch===b){const p=G.fp[at],q=Q.fp[F.S.at];if(!p||!q)return 2;const dw=q.w-p.w;
      return dw>.25||(Math.abs(dw)<=.25&&(q.th<p.th-.02||(Math.abs(q.th-p.th)<=.02&&b.id<a.id)))?3:2}}
  if(b.fk)for(const F of b.fk)if(F&&F.T.ch===a)return 1;
  return 0;
}
// jezdnie leżące obok siebie (prawie równolegle, ten sam poziom), które na siebie nachodzą – odnogi tuż za rozwidleniem, dwie jezdnie drogi
// dwujezdniowej, jezdnia zbierająca obok głównej: wspólne miejsce dzielą według liczby pasów (każda zwęża się od strony sąsiadki, nie poszerza drogi);
// jezdnie w przeciwnych kierunkach zostawiają między sobą wąski pas rozdziału
function jzSqueeze(N,B,G){
  const ch=G.ch;
  if(!N.ax){const g=new Map(),CS=32;   // siatka odcinków osi wszystkich rysowanych ciągów
    for(const q of N.C){if(!q.show)continue;const a=q.a,n=a.length/2;
      for(let j=0;j<n-1;j++){const x1=a[2*j],y1=a[2*j+1],vx=a[2*j+2]-x1,vy=a[2*j+3]-y1,L=Math.hypot(vx,vy);if(L<.05)continue;const o={q,j,x1,y1,ux:vx/L,uy:vy/L,L};
        const c0=Math.floor(Math.min(x1,x1+vx)/CS),c1=Math.floor(Math.max(x1,x1+vx)/CS),r0=Math.floor(Math.min(y1,y1+vy)/CS),r1=Math.floor(Math.max(y1,y1+vy)/CS);
        for(let cx=c0;cx<=c1;cx++)for(let cy=r0;cy<=r1;cy++){const k=((cx&32767)<<15)|(cy&32767);let l=g.get(k);if(!l)g.set(k,l=[]);l.push(o)}}}
    N.ax={g,CS}}
  const {g,CS}=N.ax,n=G.n,{X,Y,UX,UY,wn,NT,ZZ}=G;
  const tb=q=>{if(ch.fk)for(const F of ch.fk)if(F&&F.T.ch===q)return true;if(q.fk)for(const F of q.fk)if(F&&F.T.ch===ch)return true;return false};   // jezdnia i jej odnoga stykają się końcami, nie bokami
  let wmax=0,tmax=0;for(let k=0;k<n;k++)wmax=Math.max(wmax,wn[k]);for(const k in B.TWk)tmax=Math.max(tmax,B.TWk[k]);
  const R=wmax+tmax+1,gap=2.5/B.s,ST=3,limL=new Float64Array(n).fill(1e9),limR=new Float64Array(n).fill(1e9),cells=new Set(),rel=new Map(),hits=[],side=new Map();
  for(let k=0;k<n;k+=ST){const x=X[k],y=Y[k],ux=UX[k],uy=UY[k],nx=uy,ny=-ux,wG=wn[k];   // n: w prawo
    cells.clear();for(let l=-R;l<=R+.01;l+=CS/2)cells.add(((Math.floor((x+nx*l)/CS)&32767)<<15)|(Math.floor((y+ny*l)/CS)&32767));
    for(const ck of cells){const l=g.get(ck);if(!l)continue;
      for(const o of l){const q=o.q;if(q===ch)continue;const c=o.ux*ux+o.uy*uy;if(Math.abs(c)<.82)continue;
        let r=rel.get(q);if(r===undefined){r=tb(q);rel.set(q,r)}if(r)continue;
        const nv=nx*o.uy-ny*o.ux;if(Math.abs(nv)<1e-6)continue;const wx=o.x1-x,wy=o.y1-y;
        const lam=(wx*o.uy-wy*o.ux)/nv,mu=(wx*ny-wy*nx)/nv;if(mu<-.5||mu>o.L+.5||Math.abs(lam)>R)continue;   // przecięcie prostej przekroju z osią sąsiadki
        const QG=jzGeo(N,B,q,false);if(!QG)continue;const qi=Math.max(0,Math.min(QG.n-1,Math.round((q.cum[o.j]+Math.max(0,Math.min(o.L,mu))+QG.t0)/QG.h)));
        if(QG.ZZ[qi]!==ZZ[k])continue;
        const wQ=QG.wn[qi],o1=Math.max(-wG,lam-wQ),o2=Math.min(wG,lam+wQ);if(o2<=o1)continue;   // część wspólna pasów obu jezdni (w przekroju tej)
        hits.push({k,q,lam,o1,o2,f:NT[k]/(NT[k]+QG.NT[qi]),gp:c<0?gap/2:0});
        if(Math.abs(lam)>.5)side.set(q,(side.get(q)||0)+lam)}}}
  // rozwidlenie: zewnętrzny brzeg odnogi w węźle dokładnie na brzegu jezdni sprzed rozwidlenia (ta mogła być zwężona przez swoją sąsiadkę)
  const FX=[];if(ch.fk)for(const at of [0,1]){const F=ch.fk[at];if(!F)continue;const TG=jzGeo(N,B,F.T.ch);if(!TG||TG.st!==2)continue;const ti=F.T.at?TG.n-1:0;
    const tl=F.T.at?TG.gL[ti]:TG.gR[ti],tr=F.T.at?TG.gR[ti]:TG.gL[ti];FX.push({at,S:F.S.ch,eL:at?tr:tl,eR:at?tl:tr})}   // brzegi jezdni w układzie tej odnogi
  if(!hits.length&&!FX.length)return;
  // strona sąsiadki: tuż przy wspólnym węźle osie prawie się pokrywają, więc tam – strona, po której leży dalej
  for(const H of hits){const sd=Math.abs(H.lam)>Math.max(1,.25*wn[H.k])?H.lam:(side.get(H.q)||H.lam),k=H.k;
    if(sd>=0){const pp=H.o1+(H.o2-H.o1)*H.f-H.gp;if(pp<limR[k])limR[k]=pp}   // sąsiadka po prawej: ta bierze lewą część wspólnego miejsca
    else{const pp=H.o2-(H.o2-H.o1)*H.f+H.gp;if(-pp<limL[k])limL[k]=-pp}}
  // próbki pośrednie: ostrożniej (mniejsza z sąsiednich), potem łagodnie: dolna obwiednia o nachyleniu JZ_SLOPE i średnia z 11 próbek
  for(const lim of [limL,limR]){
    for(let k=0;k<n;k++)if(k%ST){const a=k-k%ST,b=Math.min(n-1,a+ST);lim[k]=Math.min(lim[a],lim[b])}
    const m=JZ_SLOPE*G.h;for(let k=1;k<n;k++)lim[k]=Math.min(lim[k],lim[k-1]+m);for(let k=n-2;k>=0;k--)lim[k]=Math.min(lim[k],lim[k+1]+m);
    const K=5,at=i=>Math.min(1e6,lim[i<0?0:i>=n?n-1:i]);let acc=0;for(let i=-K;i<=K;i++)acc+=at(i);const sm=new Float64Array(n);
    for(let i=0;i<n;i++){sm[i]=acc/(2*K+1);acc+=at(i+K+1)-at(i-K)}
    for(let k=0;k<n;k++)lim[k]=sm[k]}
  for(const X of FX){const sd=side.get(X.S),outL=sd===undefined||sd>0,outR=sd===undefined||sd<0,n0=X.at?n-1:0;   // druga odnoga po prawej → zewnętrzny brzeg lewy
    const Lj=Math.max(15,5*Math.max(outL?Math.abs(Math.min(limL[n0],wn[n0])-X.eL):0,outR?Math.abs(Math.min(limR[n0],wn[n0])-X.eR):0));   // zmiana najwyżej ok. 0,3 m na metr
    for(let k=0;k<n;k++){const ds=Math.max(0,X.at?ch.L-G.T[k]:G.T[k]);if(ds>=Lj)continue;const v=ds/Lj,w=v*v*(3-2*v);
      if(outL)limL[k]=X.eL*(1-w)+Math.min(limL[k],wn[k])*w;if(outR)limR[k]=X.eR*(1-w)+Math.min(limR[k],wn[k])*w}}
  const {gL,gR,sq}=G,VA=new Float64Array(n),VB=new Float64Array(n),m=JZ_SLOPE*G.h;
  for(let k=0;k<n;k++){let a=Math.min(gL[k],limL[k]),b=Math.min(gR[k],limR[k]);const mw=.3*wn[k];
    if(a+b<mw){let e=mw-a-b;const ea=Math.min(e/2,gL[k]-a);a+=ea;e-=ea;const eb=Math.min(e,gR[k]-b);b+=eb;e-=eb;if(e>0)a+=Math.min(e,gL[k]-a)}   // (najwęższa jezdnia: 0,3 szerokości – nie szerzej niż droga)
    VA[k]=a;VB[k]=b}
  // ostatecznie: zmiana najwyżej JZ_SLOPE m na metr (dolna obwiednia) i bez załamań (średnia z 7 próbek); nigdy szerzej niż droga z mapy
  for(const [g,V] of [[gL,VA],[gR,VB]]){
    for(let k=1;k<n;k++)V[k]=Math.min(V[k],V[k-1]+m);for(let k=n-2;k>=0;k--)V[k]=Math.min(V[k],V[k+1]+m);
    const K=3,at=i=>V[i<0?0:i>=n?n-1:i];let acc=0;for(let i=-K;i<=K;i++)acc+=at(i);
    for(let k=0;k<n;k++){const v=acc/(2*K+1);acc+=at(k+K+1)-at(k-K);if(v<g[k]-.01)sq[k]=1;g[k]=Math.min(g[k],v)}}
}
// obrys: lewy i prawy brzeg oraz wielokąt; koniec ciągu bez dalszej drogi – zaokrąglony jak zwykłe drogi na mapie
function jzOutline(G){
  const {X,Y,UX,UY,gL,gR,d,ZZ,i0,i1,ch}=G,parts=[],ext=.6;
  const cap0=!ch.closed&&i0===0&&!(ch.tail&&ch.tail[0])&&!(ch.fk&&ch.fk[0])&&!(ch.ft&&ch.ft[0]),cap1=!ch.closed&&i1===G.n-1&&!(ch.tail&&ch.tail[1])&&!(ch.fk&&ch.fk[1])&&!(ch.ft&&ch.ft[1]);
  const arc=(ax,ay,bx,by,fx,fy,out)=>{const cx=(ax+bx)/2,cy=(ay+by)/2,lx=ax-cx,ly=ay-cy;   // półokrąg od a do b przez stronę f
    for(let q=1;q<8;q++){const t=q*Math.PI/8,c=Math.cos(t),sn=Math.sin(t),r=Math.hypot(lx,ly);out.push(cx+lx*c+fx*r*sn,cy+ly*c+fy*r*sn)}};
  let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
  for(let a=i0;a<=i1;){let b=a;while(b<i1&&ZZ[b+1]===ZZ[a])b++;const e=Math.min(i1,b+1);   // część na jednym poziomie (z próbką graniczną)
    const m=e-a+1,Lx=new Float64Array(2*m),Rx=new Float64Array(2*m),c0=cap0&&a===i0,c1=cap1&&e===i1;
    for(let k=0;k<m;k++){const i=a+k,rx=UY[i],ry=-UX[i],l=d[i]-gL[i],r=d[i]+gR[i];let ox=0,oy=0;
      if(k===0&&!c0){ox=-UX[i]*ext;oy=-UY[i]*ext}else if(k===m-1&&!c1){ox=UX[i]*ext;oy=UY[i]*ext}
      Lx[2*k]=X[i]+rx*l+ox;Lx[2*k+1]=Y[i]+ry*l+oy;Rx[2*k]=X[i]+rx*r+ox;Rx[2*k+1]=Y[i]+ry*r+oy}
    const A0=[],A1=[];
    if(c0)arc(Rx[0],Rx[1],Lx[0],Lx[1],-UX[a],-UY[a],A0);   // od prawego do lewego brzegu przez tył
    if(c1)arc(Lx[2*m-2],Lx[2*m-1],Rx[2*m-2],Rx[2*m-1],UX[e],UY[e],A1);   // od lewego do prawego przez przód
    const P=new Path2D(),EL=new Path2D(),ER=new Path2D();
    P.moveTo(Lx[0],Lx[1]);for(let k=1;k<m;k++)P.lineTo(Lx[2*k],Lx[2*k+1]);for(let k=0;k<A1.length;k+=2)P.lineTo(A1[k],A1[k+1]);
    for(let k=m-1;k>=0;k--)P.lineTo(Rx[2*k],Rx[2*k+1]);for(let k=0;k<A0.length;k+=2)P.lineTo(A0[k],A0[k+1]);P.closePath();
    if(A0.length){EL.moveTo(Rx[0],Rx[1]);for(let k=0;k<A0.length;k+=2)EL.lineTo(A0[k],A0[k+1]);EL.lineTo(Lx[0],Lx[1])}else EL.moveTo(Lx[0],Lx[1]);
    for(let k=1;k<m;k++)EL.lineTo(Lx[2*k],Lx[2*k+1]);for(let k=0;k<A1.length;k+=2)EL.lineTo(A1[k],A1[k+1]);if(A1.length)EL.lineTo(Rx[2*m-2],Rx[2*m-1]);
    ER.moveTo(Rx[0],Rx[1]);for(let k=1;k<m;k++)ER.lineTo(Rx[2*k],Rx[2*k+1]);
    for(let k=0;k<2*m;k+=2)for(const A of [Lx,Rx]){const x=A[k],y=A[k+1];if(x<x0)x0=x;if(x>x1)x1=x;if(y<y0)y0=y;if(y>y1)y1=y}
    for(const A of [A0,A1])for(let k=0;k<A.length;k+=2){const x=A[k],y=A[k+1];if(x<x0)x0=x;if(x>x1)x1=x;if(y<y0)y0=y;if(y>y1)y1=y}
    parts.push({z:ZZ[a],a,b:e,P,EL,ER,Lx,Rx,A0,A1});
    a=b+1;
  }
  G.parts=parts;G.bb=[x0,y0,x1,y1];
}
// ---- linie: pasy (przerywane), linia dzieląca kierunki (ciągła), cienka krawędź przy brzegu; przerwy tam, gdzie leży inna droga ----
function jzRegister(B,G){
  if(B.gridOf.has(G.ch.id))return;B.gridOf.add(G.ch.id);
  const CS=16;for(let k=G.i0;k<=G.i1;k++)B.mx=Math.max(B.mx||0,Math.max(G.gL[k],G.gR[k])+Math.abs(G.d[k]));
  for(let k=G.i0;k<=G.i1;k++){const key=Math.floor(G.X[k]/CS)+'|'+Math.floor(G.Y[k]/CS);let l=B.grid.get(key);if(!l)B.grid.set(key,l=[]);l.push(G,k)}
}
function jzLines(N,B,G){
  if(G.lines)return G.lines;
  const ch=G.ch,D=N.D,TT=jzTiles(D),mg=1.0,CS=16,{X,Y,UX,UY,gL,gR,d,LWs,T,ZZ,i0,i1,nA,nB,nC,NT}=G,ins=2/B.s,m=i1-i0+1;
  // geometria sąsiednich ciągów (do przerw na skrzyżowaniach)
  const b=G.bb,R=80;
  for(const q of N.C){if(!q.show&&!q.fk&&!q.ft)continue;const c=q.bb;if(c[2]<b[0]-R||c[0]>b[2]+R||c[3]<b[1]-R||c[1]>b[3]+R)continue;
    const Q=jzGeo(N,B,q);if(Q&&Q.ok)jzRegister(B,Q)}
  jzRegister(B,G);
  // strefy skrzyżowań: odcinki osi tego ciągu, przy których przechodzi inna droga (odległość odcinek–odcinek) – tylko tam liczymy przerwy dokładnie
  const segD=(ax,ay,bx,by,cx,cy,dx,dy)=>{   // najmniejsza odległość dwóch odcinków
    const ps=(px,py,x1,y1,x2,y2)=>{const vx=x2-x1,vy=y2-y1,l2=vx*vx+vy*vy;let t=l2?((px-x1)*vx+(py-y1)*vy)/l2:0;t=t<0?0:t>1?1:t;return Math.hypot(px-x1-vx*t,py-y1-vy*t)};
    const o=(px,py,qx,qy,rx,ry)=>(qx-px)*(ry-py)-(qy-py)*(rx-px);
    if(o(ax,ay,bx,by,cx,cy)*o(ax,ay,bx,by,dx,dy)<0&&o(cx,cy,dx,dy,ax,ay)*o(cx,cy,dx,dy,bx,by)<0)return 0;
    return Math.min(ps(ax,ay,cx,cy,dx,dy),ps(bx,by,cx,cy,dx,dy),ps(cx,cy,ax,ay,bx,by),ps(dx,dy,ax,ay,bx,by))};
  const GA=G.A,GC=G.cumA,na=GC.length;let emax=0;
  const GB=new Float64Array(4*na);for(let j=0;j<na-1;j++){const x1=GA[2*j],y1=GA[2*j+1],x2=GA[2*j+2],y2=GA[2*j+3];GB[4*j]=Math.min(x1,x2);GB[4*j+1]=Math.min(y1,y2);GB[4*j+2]=Math.max(x1,x2);GB[4*j+3]=Math.max(y1,y2)}
  const bbx=(j,x0,y0,x1,y1,r)=>GB[4*j]<=x1+r&&GB[4*j+2]>=x0-r&&GB[4*j+1]<=y1+r&&GB[4*j+3]>=y0-r;   // szybkie odrzucenie par odcinków
  for(let i=i0;i<=i1;i++)emax=Math.max(emax,Math.max(gL[i],gR[i])+Math.abs(d[i]));
  const zone=new Uint8Array(m),markT=(ta,tb)=>{const a=Math.max(i0,Math.floor((ta-G.t0-T[0]+ 0)/G.h)-3),z=Math.min(i1,Math.ceil((tb-G.t0-T[0])/G.h)+3);for(let k=a;k<=z;k++)zone[k-i0]=1};
  const relT=[],relC=new Map(),isRel=Q=>{let r=relC.get(Q);if(r===undefined){r=jzRelK(G,Q);relC.set(Q,r)}return r};
  for(const o of jzTileNear(TT,(b[0]+b[2])/2,(b[1]+b[3])/2,Math.hypot(b[2]-b[0],b[3]-b[1])/2+20)){
    const hw=B.TWk[o.k]||B.TWk.tr,r=hw+emax+mg+1;
    if(Math.max(o.x1,o.x2)<b[0]-r||Math.min(o.x1,o.x2)>b[2]+r||Math.max(o.y1,o.y2)<b[1]-r||Math.min(o.y1,o.y2)>b[3]+r)continue;
    let own=false,near=[],best=1e9,bj=-1;
    const ox0=Math.min(o.x1,o.x2),oy0=Math.min(o.y1,o.y2),ox1=Math.max(o.x1,o.x2),oy1=Math.max(o.y1,o.y2);
    for(let j=0;j<na-1;j++){if(!bbx(j,ox0,oy0,ox1,oy1,r))continue;const x1=GA[2*j],y1=GA[2*j+1],x2=GA[2*j+2],y2=GA[2*j+3];
      const dd=segD(x1,y1,x2,y2,o.x1,o.y1,o.x2,o.y2);if(dd>r)continue;near.push(j);
      const mx=(o.x1+o.x2)/2,my=(o.y1+o.y2)/2,vx=x2-x1,vy=y2-y1,l2=vx*vx+vy*vy;let t=l2?((mx-x1)*vx+(my-y1)*vy)/l2:0;t=t<0?0:t>1?1:t;
      const dm=Math.hypot(mx-x1-vx*t,my-y1-vy*t);if(dm<best){best=dm;bj=j}}
    if(!near.length)continue;
    if(bj>=0){const x1=GA[2*bj],y1=GA[2*bj+1],x2=GA[2*bj+2],y2=GA[2*bj+3],l=Math.hypot(x2-x1,y2-y1)||1;   // ta sama ulica: wzdłuż osi i w obrębie jezdni
      if(best<=emax+1&&Math.abs(o.ux*(x2-x1)/l+o.uy*(y2-y1)/l)>=.906)own=true}
    if(own)continue;
    if(ch.fk||ch.ft){   // droga z mapy pod drugą odnogą / jezdnią sprzed rozwidlenia – to nie skrzyżowanie
      const mx=(o.x1+o.x2)/2,my=(o.y1+o.y2)/2,gx=Math.floor(mx/CS),gy=Math.floor(my/CS);let cov=false;
      for(let a=gx-1;a<=gx+1&&!cov;a++)for(let bq=gy-1;bq<=gy+1&&!cov;bq++){const l=B.grid.get(a+'|'+bq);if(!l)continue;
        for(let j=0;j<l.length;j+=2){const Q=l[j],q=l[j+1];if(Q===G||!isRel(Q))continue;const dx=mx-Q.X[q],dy=my-Q.Y[q];
          if(Math.abs(dx*Q.UX[q]+dy*Q.UY[q])>Q.h*.75)continue;if(Math.abs(dx*Q.UY[q]-dy*Q.UX[q])<=2.5&&Math.abs(o.ux*Q.UX[q]+o.uy*Q.UY[q])>=.8){cov=true;break}}}
      if(cov)continue}
    relT.push(o);for(const j of near)markT(GC[j],GC[j+1]);
  }
  {const x0=b[0]-R,x1=b[2]+R,y0=b[1]-R,y1=b[3]+R;   // inne ciągi z pasami: odcinki ich osi blisko osi tego ciągu
    for(const q of N.C){if(q===ch)continue;const c=q.bb;if(c[2]<x0||c[0]>x1||c[3]<y0||c[1]>y1)continue;const Q=B.geo.get(q.id);if(!Q||!Q.ok)continue;
      let qe=0;for(let i=Q.i0;i<=Q.i1;i++)qe=Math.max(qe,Math.max(Q.gL[i],Q.gR[i])+Math.abs(Q.d[i]));const r=qe+emax+mg+1,QA=Q.A,QC=Q.cumA;
      for(let k=0;k<QC.length-1;k++){const cx=QA[2*k],cy=QA[2*k+1],dx=QA[2*k+2],dy=QA[2*k+3];
        if(Math.max(cx,dx)<b[0]-r||Math.min(cx,dx)>b[2]+r||Math.max(cy,dy)<b[1]-r||Math.min(cy,dy)>b[3]+r)continue;
        const qx0=Math.min(cx,dx),qy0=Math.min(cy,dy),qx1=Math.max(cx,dx),qy1=Math.max(cy,dy);
        for(let j=0;j<na-1;j++)if(bbx(j,qx0,qy0,qx1,qy1,r)&&segD(GA[2*j],GA[2*j+1],GA[2*j+2],GA[2*j+3],cx,cy,dx,dy)<=r)markT(GC[j],GC[j+1])}}}
  const hid=(x,y,ux,uy,k,tp)=>{
    const lv=ZZ[k];
    for(const o of relT){
      if(o.lv!==lv||Math.abs(o.ux*ux+o.uy*uy)>=.906)continue;   // (relT: odcinki zwykłych dróg przecinających ten ciąg)
      const tp=(x-o.x1)*o.ux+(y-o.y1)*o.uy;if(tp<-mg||tp>o.L+mg)continue;
      const dl=Math.abs((x-o.x1)*o.uy-(y-o.y1)*o.ux),hw=B.TWk[o.k]||B.TWk.tr;if(dl>hw+mg)continue;
      return true}
    const cx=Math.floor(x/CS),cy=Math.floor(y/CS),rc=Math.ceil(((B.mx||0)+mg+1)/CS);   // tyle komórek, by sięgnąć osi najszerszej jezdni
    for(let a=cx-rc;a<=cx+rc;a++)for(let bq=cy-rc;bq<=cy+rc;bq++){const l=B.grid.get(a+'|'+bq);if(!l)continue;
      for(let j=0;j<l.length;j+=2){const Q=l[j],q=l[j+1];if(Q===G||Q.ZZ[q]!==lv)continue;
        const dx=x-Q.X[q],dy=y-Q.Y[q],al=dx*Q.UX[q]+dy*Q.UY[q];if(Math.abs(al)>Q.h*.75)continue;
        const lat=dx*Q.UY[q]-dy*Q.UX[q]-Q.d[q];
        const rk=isRel(Q);if(rk){const e=.3*Q.LWs[q];if(lat<-Q.gL[q]+e||lat>Q.gR[q]-e)continue;if(tp==='edge'||rk===3)return true;continue}   // ten sam układ pasów: linie biegną dalej
        if(lat<-Q.gL[q]-mg||lat>Q.gR[q]+mg)continue;
        return true}}   // każda inna jezdnia z pasami (także równoległa – np. dwie jezdnie drogi dwujezdniowej, które przy pogrubieniu na siebie nachodzą): tam bez linii
    return false};
  const defs=[],pm=5/B.s;   // linie tylko na pasach szerszych niż ok. 5 px (inaczej zlewają się w kreskowanie)
  let mA=0,mB=0,mN=0;for(let i=i0;i<=i1;i++){mA=Math.max(mA,Math.ceil(nA[i]));mB=Math.max(mB,Math.ceil(nB[i]));mN=Math.max(mN,Math.ceil(NT[i]))}
  const le=i=>d[i]-gL[i];   // lewy brzeg; pasy kolejno od lewej: A (ruch w przeciwną stronę), C (środkowe), B
  if(ch.ow===0){
    defs.push({t:'div',x:i=>le(i)+(nA[i]+nC[i]/2)*LWs[i],ex:i=>nA[i]>=.6&&nB[i]>=.6&&LWs[i]>=.8*pm});
    for(let j=1;j<mA;j++)defs.push({t:'dash',x:i=>le(i)+j*LWs[i],ex:i=>nA[i]-j>=.3&&LWs[i]>=pm});
    for(let j=1;j<mB;j++)defs.push({t:'dash',x:i=>le(i)+(nA[i]+nC[i]+j)*LWs[i],ex:i=>nB[i]-j>=.3&&LWs[i]>=pm});
  }else for(let j=1;j<mN;j++)defs.push({t:'dash',x:i=>le(i)+j*LWs[i],ex:i=>NT[i]-j>=.3&&LWs[i]>=pm});
  defs.push({t:'edge',x:i=>d[i]-gL[i]+ins,ex:()=>true},{t:'edge',x:i=>d[i]+gR[i]-ins,ex:()=>true});
  let lav=0;for(let i=i0;i<=i1;i++)lav+=LWs[i];lav/=Math.max(1,i1-i0+1);
  const P=[0,1].map(()=>({dash:new Path2D(),div:new Path2D(),edge:new Path2D()})),lwd=Math.max(lav,.6*(B.TWk[LN_K[ch.kc]]||B.TWk.tr)),per=1.35*lwd,dl=.55*lwd;
  let nseg=0,nvis=0;if(window.__jzFull)zone.fill(1);   // (test: sprawdzanie każdej próbki)
  const raw=window.__jzRaw?{dash:[],div:[],pl:[]}:null;   // (test: punkty linii, łamane)
  for(const df of defs){
    const vis=new Uint8Array(m),px=new Float64Array(2*m);
    for(let i=i0;i<=i1;i++){const k=i-i0;if(!df.ex(i))continue;const x=df.x(i),qx=X[i]+UY[i]*x,qy=Y[i]-UX[i]*x;px[2*k]=qx;px[2*k+1]=qy;vis[k]=zone[k]&&hid(qx,qy,UX[i],UY[i],i,df.t)?0:1;nvis+=vis[k]}
    // odcinki widoczne (co najmniej 2 m)
    let k=0;
    while(k<m){if(!vis[k]){k++;continue}let e=k;while(e+1<m&&vis[e+1])e++;
      if(T[i0+e]-T[i0+k]>=(df.t==='div'?Math.max(2,1.5*lwd):df.t==='dash'?1.2*per:Math.max(2,.8*lwd))){nseg++;   /* krótkie kawałki między przerwami (pojedyncza kreska na skrzyżowaniu) wyglądają jak przypadkowe ślady */
        if(df.t==='dash'){   // kreski w stałym rytmie wzdłuż całego ciągu
          const ta=T[i0+k],tb=T[i0+e];for(let u=Math.floor(ta/per)*per;u<tb;u+=per){const u0=Math.max(ta,u),u1=Math.min(tb,u+dl);if(u1-u0<Math.max(.3,dl*.4))continue;   // bez okruchów kresek przy przerwach
            const pa=jzInterp(T,px,i0,k,e,u0),pb=jzInterp(T,px,i0,k,e,u1),zq=ZZ[i0+Math.min(e,Math.max(k,Math.round(((u0+u1)/2-T[i0])/G.h)))]|0,pd=P[zq].dash;pd.moveTo(pa[0],pa[1]);const pl=raw?[pa[0],pa[1]]:null;
            for(let q=k;q<=e;q++){const tq=T[i0+q];if(tq>u0&&tq<u1){pd.lineTo(px[2*q],px[2*q+1]);if(raw){raw.dash.push(px[2*q],px[2*q+1],zq);pl.push(px[2*q],px[2*q+1])}}}pd.lineTo(pb[0],pb[1]);if(raw){raw.dash.push(pa[0],pa[1],zq,pb[0],pb[1],zq);pl.push(pb[0],pb[1]);raw.pl.push({t:'dash',z:zq,p:pl})}}
        }else{let q=k;while(q<=e){const z=ZZ[i0+q];let r=q;while(r<e&&ZZ[i0+r+1]===z)r++;const re=Math.min(e,r+1),p=P[z][df.t];   // osobno na ziemi i na moście
            p.moveTo(px[2*q],px[2*q+1]);for(let w=q+1;w<=re;w++)p.lineTo(px[2*w],px[2*w+1]);if(raw&&df.t==='div')for(let w=q;w<=re;w++)raw.div.push(px[2*w],px[2*w+1],z);
            if(raw){const pl=[];for(let w=q;w<=re;w++)pl.push(px[2*w],px[2*w+1]);raw.pl.push({t:df.t,z,p:pl})}q=r+1}}
      }
      k=e+1}
  }
  return G.lines={P,nseg,nvis,zone,raw};
}
function jzInterp(T,px,i0,k,e,u){   // punkt linii w miejscu u (t ciągu) między próbkami k..e
  let lo=k,hi=e;while(hi-lo>1){const m=(lo+hi)>>1;if(T[i0+m]<=u)lo=m;else hi=m}
  const ta=T[i0+lo],tb=T[i0+hi],f=tb>ta?Math.max(0,Math.min(1,(u-ta)/(tb-ta))):0;
  return [px[2*lo]+(px[2*hi]-px[2*lo])*f,px[2*lo+1]+(px[2*hi+1]-px[2*lo+1])*f];
}
// ---- rysowanie ----
function jzFrame(D,s,ox,oy,S){
  if(!jzOn||!LANEW.size||s<JZ_MIN_S||!D)return null;
  const N=jzNet(D),B=jzBucket(N,s),r=S/2/s*1.25+90,out=[];
  for(const ch of N.sorted){if(!ch.show)continue;const b=ch.bb;if(b[2]<ox-r-80||b[0]>ox+r+80||b[3]<oy-r-80||b[1]>oy+r+80)continue;
    const G=jzGeo(N,B,ch);if(G&&G.ok&&G.i1>G.i0)out.push(G)}
  return out.length?{N,B,G:out,dl:performance.now()+7}:null;   // dl: w tej klatce linie liczymy najwyżej ok. 7 ms (reszta w następnych)
}
function jzHalo(c,F,col,add,s,pick){   // poświata / chodnik / cień wokół jezdni: wielokąt i jego brzegi grubszą kreską
  c.lineJoin='round';c.lineCap='butt';
  for(const G of F.G){if(pick&&!pick(G.ch.kc))continue;c.fillStyle=typeof col==='function'?col(G.ch.kc):col;c.strokeStyle=c.fillStyle;c.lineWidth=add/s;
    for(const p of G.parts)if(!p.z){c.fill(p.P);c.stroke(p.EL);c.stroke(p.ER)}}
  c.lineCap='round';
}
function jzCasing(c,F,pal,cwz,dm,s,z){
  c.lineJoin='round';c.lineCap='butt';c.lineWidth=(cwz+(dm?1.2:0))/s;
  for(const G of F.G){const kc=G.ch.kc;c.strokeStyle=kc===1?pal.csMw:kc===2?pal.csPr:kc===3?pal.csSc:pal.casing;for(const p of G.parts)if(p.z===(z||0)){c.stroke(p.EL);c.stroke(p.ER)}}
  c.lineCap='round';
}
function jzBody(c,F,pal,s,dm,night,under,z,cwz){
  const STL=lnStyle(pal,night),GZ=F.G.filter(G=>G.parts.some(p=>p.z===z));if(!GZ.length)return;
  if(z){   // most / wiadukt: cień, obwódka i jasny brzeg jak na zwykłym moście, potem jezdnia
    const shw=night?'rgba(0,0,0,.45)':'rgba(70,58,35,.24)',cs=night?'#080b12':'#8a8577',ed=night?'rgba(170,185,225,.22)':'rgba(255,255,255,.6)';c.lineJoin='round';c.lineCap='butt';
    c.save();c.translate(3.2/s,-3.2/s);c.fillStyle=c.strokeStyle=shw;c.lineWidth=(cwz+3)/s;for(const G of GZ)for(const p of G.parts)if(p.z){c.fill(p.P);c.stroke(p.EL);c.stroke(p.ER)}c.restore();
    c.strokeStyle=cs;c.lineWidth=(cwz+(s>=.5?2.2:1.2)+(dm?1.2:0))/s;for(const G of GZ)for(const p of G.parts)if(p.z){c.stroke(p.EL);c.stroke(p.ER)}
    if(s>=.5){c.strokeStyle=ed;c.lineWidth=1.4/s;for(const G of GZ)for(const p of G.parts)if(p.z){c.stroke(p.EL);c.stroke(p.ER)}}
  }
  for(const G of GZ){c.fillStyle=roadFill(LN_K[G.ch.kc],pal,night);for(const p of G.parts)if(p.z===z)c.fill(p.P)}
  if(under)try{under()}catch(e){}
  c.lineCap='butt';c.lineJoin='round';c.setLineDash([]);
  let wait=false;
  for(const G of GZ){let L=G.lines,o=null;
    if(!L){if(performance.now()<F.dl){try{L=jzLines(F.N,F.B,G)}catch(e){lnFail(e);continue}}else{wait=true;if(G.old){L=G.old.L;o=G.old.o}else continue}}
    if(o){c.save();c.translate(o[0],o[1])}
    const k=LN_K[G.ch.kc],light=!night&&(k==='tr'||k==='rs'||k==='sv'),lpx=G.LWs[(G.i0+G.i1)>>1]*s,lw=Math.max(1.7,Math.min(4.6,lpx*.1));
    const LP=L.P[z];
    c.strokeStyle=night?'rgba(10,14,24,.55)':'rgba(105,95,75,.30)';c.lineWidth=1.2/s;c.stroke(LP.edge);   // cienka krawędź jak na zwykłych drogach
    if(light){c.strokeStyle='rgba(118,112,100,.62)';c.lineWidth=lw*.8/s;c.stroke(LP.dash);c.strokeStyle='rgba(118,112,100,.78)';c.lineWidth=lw*.9/s;c.stroke(LP.div)}
    else{if(STL.dashOut){c.strokeStyle=STL.dashOut;c.lineWidth=(lw+1.8)/s;c.stroke(LP.dash);c.lineWidth=(lw*1.1+1.8)/s;c.stroke(LP.div)}
      c.strokeStyle=STL.dash;c.lineWidth=lw/s;c.stroke(LP.dash);c.strokeStyle=STL.solid;c.lineWidth=lw*1.1/s;c.stroke(LP.div)}
    if(o)c.restore();
  }
  c.lineCap='round';
  if(wait&&!jzBody.t)jzBody.t=setTimeout(()=>{jzBody.t=0;try{vd=null}catch(e){}},30);   // reszta linii w następnym malowaniu mapy
}
