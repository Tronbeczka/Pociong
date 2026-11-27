// testy modułu jezdni na danych syntetycznych (bez przeglądarki)
const fs=require('fs');
global.Path2D=class{constructor(){this.c=[]}moveTo(x,y){this.c.push(['M',x,y])}lineTo(x,y){this.c.push(['L',x,y])}closePath(){this.c.push(['Z'])}};
global.rad=x=>x*Math.PI/180;global.LN_K=['tr','mw','pr','sc','rs','sv'];
const VC={sv:{w:5,m:4},rs:{w:10,m:7},tr:{w:12,m:8},sc:{w:14,m:9},pr:{w:17,m:11},mwl:{w:12,m:8},mw:{w:19,m:14}};
global.rw=(k,s)=>Math.max(VC[k].w,VC[k].m*s*2.4);global.laneVer=1;global.LANEW=new Map();
global.lnFail=e=>{throw e};global.window={};
eval(fs.readFileSync(process.argv[2]||'/tmp/jz/jz.js','utf8')+';global.jz={jzNet,jzBucket,jzGeo,jzLines,jzLinesR,jzBlocks,jzFrame,jzTiles};');
const D0={lat:51.1,lon:17.0,bb:[-2000,-2000,2000,2000],RS:[]};
const kx=111195*Math.cos(rad(51.1));
const ll=(x,y)=>[+(D0.lat+y/111195).toFixed(7),+(D0.lon+x/kx).toFixed(7)];
let nid=1;
function way(pts,o){const g=[];for(const [x,y] of pts){const q=ll(x,y);g.push(q[0],q[1])}
  const w=Object.assign({id:nid++,k:'tr',kc:0,nf:1,nb:1,c:0,ow:0,N:2,multi:true,tf:'',tb:'',xf:0,xb:0,rb:0,z:0,g},o);
  w.N=w.ow===0?w.nf+w.nb+w.c:(w.ow===1?w.nf:w.nb);w.multi=w.N>=3||w.ow!==0;LANEW.set(w.id,w);return w}
let fails=0;const ok=(name,c,info)=>{console.log((c?'ok   ':'FAIL ')+name+(c?'':' '+JSON.stringify(info)));if(!c)fails++};
const s=2.4;
function reset(){LANEW.clear();laneVer++;D0.RS=[];delete D0.JZT;global.JZN=null}
// 1) Curie: 3+3, 3+2, 3+2, 2+3, 2+3, 2+3 – jeden ciąg, lewy brzeg bez wcięcia (3→2→3 na 42 m), prawy łagodnie 3→2
reset();
const cut=[0,32,56,74,90,100,133],lan=[[3,3],[3,2],[3,2],[2,3],[2,3],[2,3]];
for(let i=0;i<6;i++)way([[cut[i],0],[cut[i+1],0]],{nf:lan[i][0],nb:lan[i][1]});
let N=jz.jzNet(D0),B=jz.jzBucket(N,s);
ok('Curie: jeden ciąg z 6 odcinków',N.C.length===1&&N.C[0].pcs.length===6,N.C.map(c=>c.pcs.length));
let G=jz.jzGeo(N,B,N.C[0]);const LW=B.LWk.tr;
const gl=[...G.gL],gr=[...G.gR];
ok('lewy brzeg stały (3 pasy) – bez wcięcia',Math.max(...gl)-Math.min(...gl)<.01,[Math.min(...gl)/LW,Math.max(...gl)/LW]);
ok('szerokość jak zwykła droga z mapy (stała, bez poszerzania o pasy)',Math.max(...gl,...gr)-Math.min(...gl,...gr)<.01&&Math.abs(gl[0]-B.TWk.tr)<.01,[gl[0],B.TWk.tr]);
{const nt=[...G.NT];let mx=0;for(let i=1;i<nt.length;i++)mx=Math.max(mx,Math.abs(nt[i]-nt[i-1]));
 ok('liczba pasów 6→5 zmienia się łagodnie (najwyżej 1 pas na 3 szerokości drogi)',Math.round(nt[0])===6&&Math.round(nt[nt.length-1])===5&&mx<=G.h/(3*B.TWk.tr)+1e-6,[nt[0],nt[nt.length-1],mx])}
let L=jz.jzLines(N,B,G);ok('linie pasów narysowane',L.nseg>=5,L.nseg);
// 2) rozwidlenie: 2+2 na wschód, potem jezdnia na wschód (2 pasy, na południe) i jezdnia na zachód (2 pasy, z północy)
reset();
way([[-200,0],[0,0]],{nf:2,nb:2});
const A=[];for(let x=0;x<=200;x+=10)A.push([x,-30*(x/200)**1.5]);way(A,{ow:1,nf:2,nb:0});
const Bp=[];for(let x=200;x>=0;x-=10)Bp.push([x,30*(x/200)**1.5]);way(Bp,{ow:1,nf:2,nb:0});
N=jz.jzNet(D0);B=jz.jzBucket(N,s);
ok('rozwidlenie: 3 ciągi',N.C.length===3,N.C.length);
const br=N.C.filter(c=>c.fk);ok('rozwidlenie rozpoznane (2 odnogi)',br.length===2,br.length);
for(const c of br){const g=jz.jzGeo(N,B,c);const at=c.fk[0]?0:1;
  // brzeg zewnętrzny względem osi drogi przed rozwidleniem (y=0): odnoga południowa – prawy brzeg ≤ −2 pasy i nie wraca do środka
  let worst=0,prev=null,back=0;
  for(let q=0;q<=g.i1-g.i0;q++){const k=at?g.i1-q:g.i0+q;if(g.T[k]>120&&at===0||at===1&&c.L-g.T[k]>120)continue;
    const rx=g.UY[k],ry=-g.UX[k],south=c.a[1]+c.a[c.a.length-1]<0;
    const eL=g.Y[k]+ry*(g.d[k]-g.gL[k]),eR=g.Y[k]+ry*(g.d[k]+g.gR[k]);const outer=south?Math.min(eL,eR):Math.max(eL,eR);
    if(prev==null)prev=outer;else{prev=south?Math.min(prev,outer):Math.max(prev,outer);back=Math.max(back,south?outer-prev:prev-outer)}}
  const g0=at===0?g.i0:g.i1,rx0=g.UY[g0],ry0=-g.UX[g0];const eL0=g.Y[g0]+ry0*(g.d[g0]-g.gL[g0]),eR0=g.Y[g0]+ry0*(g.d[g0]+g.gR[g0]);
  const south=c.a[1]+c.a[c.a.length-1]<0,outer0=south?Math.min(eL0,eR0):Math.max(eL0,eR0);
  const inner0=south?Math.max(eL0,eR0):Math.min(eL0,eR0);
  ok('odnoga '+(south?'południowa':'północna')+': brzeg zewnętrzny zaczyna się na brzegu drogi sprzed rozwidlenia',Math.abs(Math.abs(outer0)-LW)<.3,[outer0/LW]);
  ok('… a wewnętrzny przy osi (odnogi dzielą jezdnię, nie nachodzą na siebie)',Math.abs(inner0)<=1.2&&(south?inner0<=0.01:inner0>=-.01),inner0);
  ok('… i nie wraca do środka (bez wcięcia; cofnięcie ≤ 0,05 pasa)',back<=.05*LW,back/LW);
}
// 3) koniec danych o pasach: dalej zwykła droga (tr) – zwężenie do jej szerokości
reset();
way([[-300,0],[0,0]],{nf:2,nb:2,k:'pr',kc:2});D0.RS=[Object.assign([0,0,150,0,300,0],{k:'tr'})];
N=jz.jzNet(D0);B=jz.jzBucket(N,s);G=jz.jzGeo(N,B,N.C[0]);
ok('przedłużenie wzdłuż zwykłej drogi',!!(N.C[0].tail&&N.C[0].tail[1]),N.C[0].tail);
ok('na końcu jezdnia ma szerokość zwykłej drogi',Math.abs(G.gL[G.i1]-LW)<.06&&Math.abs(G.gR[G.i1]-LW)<.06,[G.gL[G.i1]/LW,G.gR[G.i1]/LW]);
ok('… a przed końcem ciągu (−60 m) szerokość drogi głównej (pr)',(()=>{const k=G.T.findIndex(t=>t>=-60);return Math.abs(G.gL[k]-B.TWk.pr)<.01})(),null);
// 4) skrzyżowanie: droga z mapy w poprzek (x=100) i boczna ulica od północy (x=200)
reset();
way([[-300,0],[400,0]],{nf:2,nb:2});D0.RS=[Object.assign([100,-200,100,200],{k:'tr'}),Object.assign([200,0,200,200],{k:'tr'})];
N=jz.jzNet(D0);B=jz.jzBucket(N,s);G=jz.jzGeo(N,B,N.C[0]);L=jz.jzLines(N,B,G);
const segs=p=>{const o=[];let cur=null;for(const c of p.c){if(c[0]==='M'){cur=[[c[1],c[2]]];o.push(cur)}else if(c[0]==='L')cur.push([c[1],c[2]])}return o};
const dv=segs(L.P[0].div);const inX=(a,b)=>dv.some(sg=>sg.some(p=>p[0]>a&&p[0]<b));
ok('linia środkowa przerwana na skrzyżowaniu (x=100 ± 10 m)',!inX(91,109),dv.map(sg=>[sg[0][0].toFixed(1),sg[sg.length-1][0].toFixed(1)]));
ok('… i jest przed i za skrzyżowaniem',inX(0,80)&&inX(120,180),null);
const ed=segs(L.P[0].edge),north=ed.filter(sg=>sg[0][1]>0),south=ed.filter(sg=>sg[0][1]<0);
ok('boczna ulica od północy przerywa krawędź północną',!north.some(sg=>sg.some(p=>p[0]>193&&p[0]<207)),north.map(sg=>[sg[0][0].toFixed(0),sg[sg.length-1][0].toFixed(0)]));
ok('… a krawędź południowa biegnie dalej',south.some(sg=>sg.some(p=>p[0]>193&&p[0]<207)),south.map(sg=>[sg[0][0].toFixed(0),sg[sg.length-1][0].toFixed(0)]));
const dsh=segs(L.P[0].dash);ok('kreski między pasami w rytmie (długość ok. 0,55 pasa)',dsh.length>20&&dsh.every(sg=>{let l=0;for(let i=1;i<sg.length;i++)l+=Math.hypot(sg[i][0]-sg[i-1][0],sg[i][1]-sg[i-1][1]);return l<=.56*LW}),dsh.length);
// 5) most: ziemia – most – ziemia, te same pasy: jeden ciąg, trzy części (poziomy), bez zmiany szerokości
reset();
way([[-300,0],[-50,0]],{nf:2,nb:2});way([[-50,0],[150,0]],{nf:2,nb:2,z:1});way([[150,0],[400,0]],{nf:2,nb:2});
N=jz.jzNet(D0);B=jz.jzBucket(N,s);
ok('most: jeden ciąg z trzech odcinków',N.C.length===1&&N.C[0].pcs.length===3,N.C.map(c=>c.pcs.length));
G=jz.jzGeo(N,B,N.C[0]);
ok('… trzy części: ziemia, most, ziemia',G.parts.length===3&&G.parts.map(p=>p.z).join('')==='010',G.parts.map(p=>p.z));
ok('… szerokość stała (bez zwężenia przed mostem)',Math.max(...G.gL)-Math.min(...G.gL)<.01&&Math.max(...G.gR)-Math.min(...G.gR)<.01,null);
L=jz.jzLines(N,B,G);const s0=segs(L.P[0].div),s1=segs(L.P[1].div);
ok('… linia środkowa i na ziemi, i na moście',s0.length>=2&&s1.length>=1,[s0.length,s1.length]);
// 6) Wersja 202: linie liczone fragmentami (ok. 300 m) – te same kreski i linie co przy liczeniu całego ciągu naraz
reset();
way([[-800,0],[900,0]],{nf:2,nb:2});D0.RS=[Object.assign([-410,-200,-410,200],{k:'tr'}),Object.assign([-100,0,-100,200],{k:'tr'}),Object.assign([300,-200,300,200],{k:'tr'}),Object.assign([598,-200,598,200],{k:'tr'})];
N=jz.jzNet(D0);B=jz.jzBucket(N,s);G=jz.jzGeo(N,B,N.C[0]);L=jz.jzLines(N,B,G);
{const LB=jz.jzBlocks(G),parts=LB.map(bl=>jz.jzLinesR(N,B,G,bl.a,bl.b));
 const key=sg=>sg[0][0].toFixed(3)+','+sg[0][1].toFixed(3),fullD=new Set(segs(L.P[0].dash).map(key)),blkD=[];for(const P of parts)for(const sg of segs(P.P[0].dash))blkD.push(key(sg));
 const setB=new Set(blkD);
 ok('fragmenty: tyle samo kresek co dla całego ciągu, bez podwójnych',LB.length>=5&&blkD.length===setB.size&&setB.size===fullD.size&&[...fullD].every(k=>setB.has(k)),[LB.length,fullD.size,setB.size,blkD.length]);
 const cov=(P,t)=>{const xs=[];for(const sg of segs(P[0][t]))for(let i=1;i<sg.length;i++)xs.push([Math.min(sg[i-1][0],sg[i][0]),Math.max(sg[i-1][0],sg[i][0]),sg[i][1].toFixed(2)]);return xs};
 const inCov=(xs,x,y)=>xs.some(c=>c[2]===y&&x>=c[0]-1e-6&&x<=c[1]+1e-6);
 const fl=cov(L.P,'div'),bk=[].concat(...parts.map(p=>cov(p.P,'div')));let same=true;
 for(let x=-799;x<=899;x+=0.5){const a=inCov(fl,x,fl.length?fl[0][2]:'0.00'),b2=inCov(bk,x,fl.length?fl[0][2]:'0.00');if(a!==b2){same=false;break}}
 ok('… linia środkowa w tych samych miejscach (z przerwami na skrzyżowaniach)',same&&fl.length>0,fl.length)}
console.log(fails?('BŁĘDY: '+fails):'WSZYSTKO OK');
