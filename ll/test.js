// testy jednostkowe modułu linii pasów (Wersja 206) na sztucznych drogach
const fs=require('fs');
global.rad=d=>d*Math.PI/180;global.deg=r=>r*180/Math.PI;
global.VC={sv:{w:5,m:4},rs:{w:10,m:7},tr:{w:12,m:8},sc:{w:14,m:9},pr:{w:17,m:11},mwl:{w:12,m:8},mw:{w:19,m:14}};
global.LANEW=new Map();global.laneVer=0;global.vd=1;global.dmK=1;
global.LSget=(k,d)=>d;global.lnFail=e=>{throw e};
global.bear=function(a,b,c,d){const y=Math.sin(rad(d-b))*Math.cos(rad(c)),x=Math.cos(rad(a))*Math.sin(rad(c))-Math.sin(rad(a))*Math.cos(rad(c))*Math.cos(rad(d-b));return (deg(Math.atan2(y,x))+360)%360};
global.angDiff=(a,b)=>{const d=Math.abs(a-b)%360;return d>180?360-d:d};
global.dist=(a,b,c,d)=>Math.hypot((a-c)*111195,(b-d)*111195*Math.cos(rad(a)));
global.lnTok=function(t){t=t.trim();if(t===''||t==='none'||t==='through')return 'S';if(t==='left'||t==='slight_left'||t==='sharp_left'||t==='merge_to_left')return 'L';if(t==='right'||t==='slight_right'||t==='sharp_right'||t==='merge_to_right')return 'R';if(t==='reverse')return 'U';return null};
global.lnParse=tag=>tag.split('|').map(l=>{const set=new Set();l.split(';').forEach(t=>{const k=lnTok(t);if(k)set.add(k)});if(!set.size)set.add('S');return set});
global.clCum=function(a){if(a.cum)return a.cum;const n=a.length>>1,c=[0];for(let i=1;i<n;i++)c.push(c[i-1]+Math.hypot(a[2*i]-a[2*i-2],a[2*i+1]-a[2*i-1]));a.cum=c;return c};
global.roadFill=(k,pal)=>pal[k==='mwl'?'mw':k];
(0,eval)(fs.readFileSync('/tmp/ll/ll.js','utf8').replace(/^const /gm,'var ').replace(/^let /gm,'var '));
const LAT0=51.1,LON0=17.03,W=40075016.686;
const D={lat:LAT0,lon:LON0,RS:[],bb:[-3000,-3000,3000,3000]};
const F=llFrame(D);
const toLL=(x,y)=>{const lon=(x/F.cl+F.cx)/W*360,my=(y/F.cl+F.cy)*2*Math.PI/W,lat=deg(2*Math.atan(Math.exp(my))-Math.PI/2);return [Math.round(lat*1e6)/1e6,Math.round(lon*1e6)/1e6]};
const road=(pts,k,od=0,lv=0)=>{const a=[];for(const p of pts)a.push(p[0],p[1]);a.k=k==='mwl'?'mw':k;a.kw=k;a.od=od;if(lv)a.lv=1;D.RS.push(a);return a};
let WID=1;const way=(pts,o)=>{const g=[];for(const p of pts){const q=toLL(p[0],p[1]);g.push(q[0],q[1])}const w=Object.assign({id:WID++,g,c:0,ow:0,nf:1,nb:1,tf:'',tb:'',k:'pr'},o);LANEW.set(w.id,w);laneVer++;return w};
const reset=()=>{D.RS=[];LANEW.clear();laneVer++;LL.ixD=null;LL.ix=null;LL.ends=null;D.llF=null;Object.assign(F,llFrame(D))};
// odczyt: przesunięcia linii (y przy danym x) dla drogi wzdłuż osi x
const at=(r,x,t)=>{const out=[];for(const l of r.L){if(t!=null&&l.t!==t)continue;const p=l.p;for(let i=0;i<p.length-2;i+=2){const x1=p[i],x2=p[i+2];if((x1-x)*(x2-x)<=0&&x1!==x2){const f=(x-x1)/(x2-x1);out.push(+(p[i+1]+(p[i+3]-p[i+1])*f).toFixed(2));break}}}return out.sort((a,b)=>a-b)};
let ok=0,n=0;const T=(name,c,info)=>{n++;if(c)ok++;console.log((c?'ok   ':'FAIL ')+name+(c?'':' '+JSON.stringify(info)))};
const near=(a,b,e=.15)=>a.length===b.length&&a.every((v,i)=>Math.abs(v-b[i])<=e);
const line=(x0,y0,x1,y1,st=10)=>{const L=Math.hypot(x1-x0,y1-y0),k=Math.max(1,Math.round(L/st)),r=[];for(let i=0;i<=k;i++)r.push([x0+(x1-x0)*i/k,y0+(y1-y0)*i/k]);return r};
// T1: jednokierunkowa 3 pasy (pr): dwie przerywane na ±4,27 m
reset();road(line(-400,0,400,0),'pr',1);let w=way(line(-200,0,200,0,50),{ow:1,nf:3,nb:0});let r=llWay(D,w);
T('1: jednokierunkowa 3 pasy – dwie linie przerywane na ±4,27 m',near(at(r,0,0),[-4.27,4.27])&&near(at(r,-150,0),[-4.27,4.27])&&at(r,0,1).length===0,{d:at(r,0,0),s:at(r,0,1)});
T('1: linie bez przerw; droga ciągnie się dalej bez danych o pasach – linie schodzą łagodnie na początku i końcu (do 30 m)',r.L.filter(l=>l.t===0).length===2&&r.L.every(l=>l.p[0]<-165&&l.p[l.p.length-2]>165),r.L.map(l=>[l.p[0],l.p[l.p.length-2]]));
reset();road(line(-200,0,200,0),'pr',1);w=way(line(-200,0,200,0,50),{ow:1,nf:3,nb:0});r=llWay(D,w);
T('1b: droga z mapy kończy się razem z danymi – linie na całej długości',r.L.filter(l=>l.t===0).length===2&&r.L.every(l=>l.p[0]<-197&&l.p[l.p.length-2]>197),r.L.map(l=>[l.p[0],l.p[l.p.length-2]]));
// T2: dwukierunkowa 2+2 (sc): przerywane ±5,2, ciągła na środku
reset();road(line(-400,0,400,0),'sc',0);w=way(line(-200,0,200,0,50),{ow:0,nf:2,nb:2,k:'sc'});r=llWay(D,w);
T('2: dwukierunkowa 2+2 – przerywane na ±5,2 m i ciągła na środku',near(at(r,0,0),[-5.2,5.2])&&near(at(r,0,1),[0]),{d:at(r,0,0),s:at(r,0,1)});
// T2b: 1+1 – bez linii (oś z mapy)
w=way(line(-200,0,200,0,50),{ow:0,nf:1,nb:1,k:'sc'});r=llWay(D,w);T('2b: 1+1 – bez linii (zostaje oś z mapy)',!!r.none,r);
// T2c: 2+1 – środek na osi drogi, dwa pasy w prawo, jeden w lewo
w=way(line(-200,0,200,0,50),{ow:0,nf:2,nb:1,k:'sc'});r=llWay(D,w);T('2c: dwukierunkowa 2+1 – środek na osi, jedna przerywana po prawej',near(at(r,0,0),[-5.2])&&near(at(r,0,1),[0]),{d:at(r,0,0),s:at(r,0,1)});
// T3: droga dwujezdniowa, jezdnie 16 m od siebie (pr, po 2 pasy): każda w swojej części, granica na środku
reset();road(line(-400,-8,400,-8),'pr',1);road(line(400,8,-400,8),'pr',1);
const wE=way(line(-200,-8,200,-8,50),{ow:1,nf:2,nb:0}),wW=way(line(200,8,-200,8,50),{ow:1,nf:2,nb:0});
const rE=llWay(D,wE),rW=llWay(D,wW);
T('3: dwujezdniowa – jezdnia wschodnia: przerywana na -10,4 m, ciągła granica na środku (0)',near(at(rE,0,0),[-10.4])&&near(at(rE,0,1),[0]),{d:at(rE,0,0),s:at(rE,0,1)});
T('3: jezdnia zachodnia: przerywana na +10,4 m, ta sama granica',near(at(rW,0,0),[10.4])&&near(at(rW,0,1),[0]),{d:at(rW,0,0),s:at(rW,0,1)});
// T3b: jezdnie daleko od siebie (40 m) – bez zwężania i bez granicy
reset();road(line(-400,-20,400,-20),'pr',1);road(line(400,20,-400,20),'pr',1);const wE2=way(line(-200,-20,200,-20,50),{ow:1,nf:2,nb:0});r=llWay(D,wE2);
T('3b: jezdnie 40 m od siebie – pełna szerokość, bez granicy',near(at(r,0,0),[-20])&&at(r,0,1).length===0,{d:at(r,0,0),s:at(r,0,1)});
// T4: skrzyżowanie z drogą tej samej klasy – przerwa ok. ±15 m
reset();road(line(-400,0,400,0),'pr',1);road(line(0,-300,0,300),'pr',0);w=way(line(-200,0,200,0,50),{ow:1,nf:3,nb:0});r=llWay(D,w);
const gap=x=>at(r,x,0).length;
T('4: skrzyżowanie z równie ważną drogą – linie kończą się na jej brzegu',gap(0)===0&&gap(10)===0&&gap(-10)===0&&gap(20)===2&&gap(-20)===2,{g0:gap(0),g10:gap(10),g20:gap(20),gm20:gap(-20)});
// T5: skrzyżowanie z mniej ważną ulicą – linie biegną dalej
reset();road(line(-400,0,400,0),'pr',1);road(line(0,-300,0,300),'rs',0);w=way(line(-200,0,200,0,50),{ow:1,nf:3,nb:0});r=llWay(D,w);
T('5: wlot mniej ważnej ulicy – linie bez przerwy',at(r,0,0).length===2&&r.L.filter(l=>l.t===0).length===2,{d:at(r,0,0),n:r.L.length});
// T5b: boczna ulica tej samej klasy z prawej (skrzyżowanie T): przerwa tylko po tej stronie… (cała szerokość w promieniu jej szerokości)
reset();road(line(-400,0,400,0),'pr',1);road(line(0,0,0,-300),'pr',0);w=way(line(-200,0,200,0,50),{ow:1,nf:3,nb:0});r=llWay(D,w);
T('5b: wlot równie ważnej ulicy z prawej – przerwa przy wlocie, dalej linie',at(r,0,0).length<2&&at(r,30,0).length===2&&at(r,-30,0).length===2,{d0:at(r,0,0),d30:at(r,30,0)});
// T6: przybywa pas (2 → 3) – łagodnie, bez skoku na styku
reset();road(line(-400,0,400,0),'pr',1);const wa=way(line(-200,0,0,0,50),{ow:1,nf:2,nb:0}),wb=way(line(0,0,200,0,50),{ow:1,nf:3,nb:0});
const ra=llWay(D,wa),rb=llWay(D,wb);
T('6: przed stykiem 2 pasy – linia na środku',near(at(ra,-50,0),[0])&&near(at(ra,-1,0),[0]),{a:at(ra,-50,0)});
const b1=at(rb,1,0),b15=at(rb,15,0),b40=at(rb,40,0);
T('6: tuż za stykiem ta sama linia (bez skoku), nowa wchodzi od lewej krawędzi',b1.length>=1&&Math.abs(b1[0])<.3&&(b1.length===1||b1[1]>10),{b1,b15,b40});
T('6: po ok. 30 m – układ 3 pasów',near(b40,[-4.27,4.27]),{b40});
let mono=true;for(let x=1;x<30;x+=2){const q=at(rb,x,0),q2=at(rb,x+2,0);if(q.length&&q2.length&&q2[0]>q[0]+.01)mono=false}T('6: linia przesuwa się płynnie (monotonicznie)',mono,{});
// T6b: ubywa pas za skrzyżowaniem – na styku w skrzyżowaniu bez zwężania przed nim
reset();road(line(-400,0,400,0),'pr',1);road(line(0,-300,0,300),'pr',0);const wc=way(line(-200,0,0,0,50),{ow:1,nf:3,nb:0}),wd=way(line(0,0,200,0,50),{ow:1,nf:2,nb:0});
r=llWay(D,wc);T('6b: pas kończy się na skrzyżowaniu – przed nim bez schodzenia linii',near(at(r,-25,0),[-4.27,4.27])&&near(at(r,-60,0),[-4.27,4.27]),{d25:at(r,-25,0)});
// T7: rozwidlenie 4 → 2+2 pod kątem ±12° – odnogi w swoich częściach, linie ciągłe z linią przed rozwidleniem
reset();const tg=Math.tan(rad(12));road(line(-400,0,0,0),'pr',1);road(line(0,0,300,300*tg),'pr',1);road(line(0,0,300,-300*tg),'pr',1);
const wA=way(line(-200,0,0,0,50),{ow:1,nf:4,nb:0}),wB=way(line(0,0,250,250*tg,25),{ow:1,nf:2,nb:0}),wC=way(line(0,0,250,-250*tg,25),{ow:1,nf:2,nb:0});
const rA=llWay(D,wA),rB=llWay(D,wB),rC=llWay(D,wC);
T('7: przed rozwidleniem 4 pasy: -6,4 / 0 / 6,4',near(at(rA,-20,0),[-6.4,0,6.4]),{a:at(rA,-20,0)});
let side=true,maxB=-1e9,minC=1e9;for(const l of rB.L){for(let i=0;i<l.p.length;i+=2){const x=l.p[i],y=l.p[i+1];if(y<-.35&&x>0)side=false}}for(const l of rC.L){for(let i=0;i<l.p.length;i+=2){const x=l.p[i],y=l.p[i+1];if(y>.35&&x>0)side=false}}
T('7: linie lewej odnogi nie wchodzą na prawą (i odwrotnie)',side,{});
const dB=at(rB,4,0),dC=at(rC,4,0);
T('7: zaraz za rozwidleniem linie odnóg na przedłużeniu linii przed nim (±6,4)',dB.length===1&&Math.abs(dB[0]-6.4)<1.3&&dC.length===1&&Math.abs(dC[0]+6.4)<1.3,{dB,dC});
T('7: granica odnóg (ciągła) między nimi',at(rB,30,1).length>=1&&at(rC,30,1).length>=1&&Math.abs(at(rB,30,1)[0]-at(rC,30,1)[0])<.3,{b:at(rB,30,1),c:at(rC,30,1)});
// T8: odwrócona jednokierunkowa (oneway=-1) – pasy liczone w kierunku jazdy
reset();road(line(400,0,-400,0),'pr',1);w=way(line(-200,0,200,0,50),{ow:-1,nf:0,nb:3});r=llWay(D,w);
T('8: oneway=-1 – dwie linie na ±4,27 m',near(at(r,0,0),[-4.27,4.27]),{d:at(r,0,0)});
// T9: bez drogi z mapy pod spodem – bez linii
reset();road(line(-400,50,400,50),'pr',1);w=way(line(-200,0,200,0,50),{ow:1,nf:3,nb:0});r=llWay(D,w);
T('9: brak drogi na mapie pod danymi OSM – bez linii',r.L.length===0,{n:r.L.length});
// T10: most nad drogą tej samej klasy – droga pod mostem bez przerwy na skrzyżowaniu (inny poziom)
reset();road(line(-400,0,400,0),'pr',1);road(line(0,-300,0,300),'pr',0,1);w=way(line(-200,0,200,0,50),{ow:1,nf:3,nb:0});r=llWay(D,w);
T('10: wiadukt nad drogą – na drodze pod nim linie bez przerwy (zasłania je wiadukt)',at(r,0,0).length===2,{d:at(r,0,0)});
// T11: ważniejsza droga obok (zachodzi na naszą) – zabiera swoją szerokość, bez granicy
reset();road(line(-400,0,400,0),'tr',1);road(line(-400,20,400,20),'pr',0);w=way(line(-200,0,200,0,50),{ow:1,nf:2,nb:0,k:'tr'});r=llWay(D,w);
const d11=at(r,0,0);T('11: obok ważniejsza droga – pasy do jej brzegu (-9,2…6,8 m), bez ciągłej granicy',d11.length===1&&Math.abs(d11[0]-(-9.2+(9.2+6.8)/2))<.2&&at(r,0,1).length===0,{d:d11,s:at(r,0,1)});
// T12: wydajność – sieć 60 dróg
reset();for(let i=0;i<30;i++){road(line(-1500,i*50-750,1500,i*50-750,20),'sc',0);road(line(i*50-750,-1500,i*50-750,1500,20),i%3?'rs':'pr',0)}
const ws=[];for(let i=0;i<30;i++){ws.push(way(line(-700,i*50-750,700,i*50-750,25),{ow:0,nf:2,nb:2,k:'sc'}))}
const t0=Date.now();let nl=0;for(const q of ws){const rr=llWay(D,q);nl+=rr.L.length}const ms=Date.now()-t0;
T('12: 30 dróg po 1,4 km w gęstej siatce – szybko',ms<1500,{ms,nl});console.log('   czas',ms,'ms, linii',nl);
// T13: kreski ciągłe na styku dwóch dróg (ten sam wzór, bez przeskoku)
reset();road(line(-400,0,400,0),'pr',1);const w13a=way(line(-200,0,-3,0,50),{ow:1,nf:3,nb:0}),w13b=way(line(-3,0,200,0,50),{ow:1,nf:3,nb:0});
const r13a=llWay(D,w13a),r13b=llWay(D,w13b);
const dsh=r=>{const out=[];for(const l of r.L){if(l.t)continue;const d=l.d;let a=null;for(let i=0;i<d.length;i+=2){if(isNaN(d[i])){a=null;continue}if(a===null){a=d[i];out.push([a,a])}else out[out.length-1][1]=d[i]}}return out};
const da=dsh(r13a).filter(q=>Math.abs(q[0])<4.4||true),db=dsh(r13b);
// kreski linii y≈-4.27: przedziały x; sprawdzamy, że wzór (kreska 5, przerwa 6) trzyma się na styku x=-3
const segs=[...dsh(r13a),...dsh(r13b)].filter(q=>true);
const xsA=[];for(const l of [...r13a.L,...r13b.L]){if(l.t||Math.abs(l.p[1]+4.27)>.2)continue;const d=l.d;let a=null;for(let i=0;i<d.length;i+=2){if(isNaN(d[i])){a=null;continue}if(a===null){a=d[i];xsA.push([a,a])}else xsA[xsA.length-1][1]=d[i]}}
xsA.sort((p,q)=>p[0]-q[0]);let reg=true;for(let i=1;i<xsA.length;i++){const st=xsA[i][0]-xsA[i-1][0];if(xsA[i][0]>-170&&xsA[i][0]<170&&Math.abs(st-11)>.3&&!(xsA[i-1][1]>-4&&xsA[i][0]<-2))reg=false}
const nearJ=xsA.filter(q=>q[0]>-20&&q[0]<15).map(q=>q.map(v=>+v.toFixed(1)));
T('13: na styku dróg wzór kresek bez przeskoku (co 11 m)',reg,{nearJ});
// T14: zakręt na styku dwóch dróg (kąt 24°) – linie łączą się bez uskoku
reset();{const a24=rad(24);road([[-300,0],[0,0],[300*Math.cos(a24),300*Math.sin(a24)]],'pr',1);
const wa=way(line(-200,0,0,0,50),{ow:1,nf:3,nb:0}),wb=way([[0,0],[200*Math.cos(a24),200*Math.sin(a24)]],{ow:1,nf:3,nb:0});
const ra=llWay(D,wa),rb=llWay(D,wb);let worst=0;
for(const la of ra.L){if(la.t)continue;const ex=la.p[la.p.length-2],ey=la.p[la.p.length-1];let bd=1e9;for(const lb of rb.L){if(lb.t)continue;bd=Math.min(bd,Math.hypot(lb.p[0]-ex,lb.p[1]-ey))}worst=Math.max(worst,bd)}
T('14: zakręt 24° na styku dróg – końce linii spotykają się (uskok < 0,15 m)',worst<.15,{worst});}
// T15: ostry narożnik (84°) na styku dwóch dróg – linie różnych dróg się nie przecinają
reset();{const a84=rad(84),ex=Math.cos(a84),ey=Math.sin(a84);road([[-300,0],[0,0],[300*ex,300*ey]],'sc',1);
const wa=way(line(-60,0,0,0,20),{ow:1,nf:3,nb:0,k:'sc'}),wb=way([[0,0],[60*ex,60*ey]],{ow:1,nf:3,nb:0,k:'sc'});
const ra=llWay(D,wa),rb=llWay(D,wb);let cr=0;
const segs=r=>{const out=[];for(const l of r.L){const p=l.p;for(let i=0;i<p.length-2;i+=2)out.push([p[i],p[i+1],p[i+2],p[i+3]])}return out};
for(const s1 of segs(ra))for(const s2 of segs(rb)){const d1x=s1[2]-s1[0],d1y=s1[3]-s1[1],d2x=s2[2]-s2[0],d2y=s2[3]-s2[1],den=d1x*d2y-d1y*d2x;if(Math.abs(den)<1e-9)continue;
  const t=((s2[0]-s1[0])*d2y-(s2[1]-s1[1])*d2x)/den,u=((s2[0]-s1[0])*d1y-(s2[1]-s1[1])*d1x)/den;if(t>.02&&t<.98&&u>.02&&u<.98)cr++}
T('15: narożnik 84° – linie się nie przecinają',cr===0,{cr,a:ra.L.length,b:rb.L.length});
// T16: łagodny łuk (promień 60 m) – linie bez przerw
reset();{const pts=[];for(let k=0;k<=60;k++){const a=rad(-90+k*1.5);pts.push([60*Math.cos(a),60+60*Math.sin(a)])}road(pts,'pr',1);const wc=way(pts.filter((_,i)=>i%5===0),{ow:1,nf:3,nb:0});const rc=llWay(D,wc);
T('16: łuk o promieniu 60 m – dwie linie bez przerw',rc.L.filter(l=>l.t===0).length===2,{n:rc.L.length,parts:rc.L.map(l=>l.p.length/2)})}}
// ---- Wersja 207: strzałki ----
const arrInfo=r=>(r.A||[]).map(a=>{const sh=a.sh;const tail=[sh[0],sh[1]];let tip=null;const hd=a.hd;tip=[hd[0],hd[1]];return {tail:tail.map(v=>+v.toFixed(2)),tip:tip.map(v=>+v.toFixed(2)),w:+a.w.toFixed(2),ws:+a.ws.toFixed(2),nh:hd.length/8}});
// T17: dojazd 3 pasy do skrzyżowania z równie ważną drogą (x=0), w lewo | prosto | prosto;w prawo
reset();road(line(-400,0,400,0),'pr',1);road(line(0,-300,0,300),'pr',0);
w=way(line(-200,0,0,0,50),{ow:1,nf:3,nb:0,tf:'left|through|through;right'});r=llWay(D,w);let ai=arrInfo(r);
const Hc=13.2*1.07+.8;
const first=ai.filter(a=>a.tail[0]>Math.max(...ai.map(q=>q.tail[0]))-1);
T('17: po jednej strzałce w pasie (pierwszy rząd przy skrzyżowaniu; na długim dojeździe drugi rząd wcześniej)',first.length===3&&ai.length%3===0,ai);
T('17: strzałki na środkach pasów (8,53 / 0 / -8,53 m)',near(first.map(a=>a.tail[1]).sort((a,b)=>a-b),[-8.53,0,8.53],.3),first.map(a=>a.tail));
T('17: grot ok. 3 m przed brzegiem skrzyżowania, cała strzałka przed nim',ai.every(a=>a.tip[0]<-Hc-1&&a.tail[0]<a.tip[0]-6)&&Math.max(...ai.map(a=>a.tip[0]))>-Hc-9,ai.map(a=>[a.tail[0],a.tip[0]]));
T('17: skręt w lewo – grot po lewej, prawy pas – dwa groty (prosto i w prawo)',first.filter(a=>a.nh===2).length===1&&first.filter(a=>a.nh===1).length===2,first.map(a=>a.nh));
// T18: wszystkie pasy prosto – bez strzałek
w=way(line(-200,0,0,0,50),{ow:1,nf:3,nb:0,tf:'through|through|through'});r=llWay(D,w);T('18: same „prosto” – bez strzałek',(r.A||[]).length===0,arrInfo(r));
// T19: inna liczba pasów niż w turn:lanes – bez strzałek
w=way(line(-200,0,0,0,50),{ow:1,nf:3,nb:0,tf:'left|through'});r=llWay(D,w);T('19: turn:lanes nie pasuje do liczby pasów – bez strzałek',(r.A||[]).length===0,arrInfo(r));
// T20: dwukierunkowa 2+2 między dwoma skrzyżowaniami – strzałki obu kierunków, każda przy swoim skrzyżowaniu
reset();road(line(-400,0,400,0),'pr',0);road(line(-150,-300,-150,300),'pr',0);road(line(150,-300,150,300),'pr',0);
w=way(line(-150,0,150,0,50),{ow:0,nf:2,nb:2,tf:'left|through',tb:'through|right'});r=llWay(D,w);ai=arrInfo(r);
const fw=ai.filter(a=>a.tip[0]>a.tail[0]),bw=ai.filter(a=>a.tip[0]<a.tail[0]);
T('20: dwukierunkowa – strzałki do przodu (prawe pasy, przy końcu) i pod prąd (lewe pasy, przy początku)',fw.length%2===0&&fw.length>=2&&bw.length===fw.length&&fw.every(a=>a.tip[0]>60&&a.tail[1]<0)&&bw.every(a=>a.tip[0]<-60&&a.tail[1]>0)&&Math.max(...fw.map(a=>a.tip[0]))>120&&Math.min(...bw.map(a=>a.tip[0]))<-120,ai);
// T21: krótki dojazd (10 m) – bez strzałek
reset();road(line(-400,0,400,0),'pr',1);road(line(0,-300,0,300),'pr',0);w=way(line(-24,0,0,0,24),{ow:1,nf:3,nb:0,tf:'left|through|right'});r=llWay(D,w);
T('21: za krótki dojazd – bez strzałek',(r.A||[]).length===0,arrInfo(r));
// T22: strzałki w obrębie swoich pasów (kształt nie wychodzi poza pas)
reset();road(line(-400,0,400,0),'pr',1);road(line(0,-300,0,300),'pr',0);w=way(line(-200,0,0,0,50),{ow:1,nf:3,nb:0,tf:'left|left;through|through;right'});r=llWay(D,w);
let inLane=true;const lw3=25.6/3;for(const a of r.A||[]){const yc=a.sh[1];for(const arr of [a.sh,a.hd])for(let i=0;i<arr.length;i+=2){if(isNaN(arr[i]))continue;if(Math.abs(arr[i+1]-yc)>lw3/2+.05)inLane=false}}
T('22: strzałki mieszczą się w swoich pasach',inLane&&(r.A||[]).length>=3&&(r.A||[]).length%3===0,arrInfo(r));
console.log(`WYNIK: ${ok}/${n}`);
