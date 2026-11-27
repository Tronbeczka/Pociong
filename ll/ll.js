// ================= Wersja 206: linie pasów na jezdni – od nowa, tylko linie na drogach z mapy =================
// Wersje 138–203 rysowały drogi z pasami jako osobne „nakładki” (własna szerokość i wypełnienie, płyty skrzyżowań), więc na skrzyżowaniach,
// rozwidleniach i przy zmianie liczby pasów wychodziły schodki, plamy i krzyżujące się linie. Teraz:
// 1) droga zostaje dokładnie taka, jak na mapie – dokładamy tylko cienkie linie: przerywane między pasami jednego kierunku i ciągłą na środku drogi
//    dwukierunkowej (w miejscu osi z mapy, w tym samym kolorze, więc ją zakrywa); buspasy są zwykłymi pasami (bez oznaczeń),
// 2) pasy dzielą tę szerokość drogi, którą widać na mapie (klasa drogi z kafelków w danym miejscu); położenie z OSM przeliczamy tak jak kafelki (Merkator),
// 3) gdy obok biegnie jezdnia tej samej klasy i ich pasy na mapie na siebie zachodzą (druga jezdnia drogi dwujezdniowej, rozwidlenie), każda bierze
//    swoją część wspólnego miejsca (granica – ciągła linia); ważniejsza droga (rysowana nad naszą) zabiera swoją szerokość, mniej ważna leży pod naszą,
// 4) linie kończą się na brzegu skrzyżowania z drogą co najmniej tak samo ważną (jak oś jezdni od wersji 193); przez wloty mniej ważnych ulic biegną dalej,
// 5) zmiana liczby pasów poza skrzyżowaniem: linie rozchodzą się albo schodzą łagodnie na ok. 30 m (nowy pas przy osi; pas do skrętu w prawo – przy krawężniku),
// 6) geometria jest w metrach i nie zależy od przybliżenia: liczymy ją raz, w tle (po kilka ms), więc przesuwanie i zbliżanie mapy niczego nie przelicza.
var llOn=LSget('llOn',true)!==false;
const LL_RK={sv:0,rs:1,tr:2,sc:3,pr:4,mwl:5,mw:5},LL_KI={sv:0,rs:1,tr:2,sc:3,pr:4,mwl:5,mw:6},LL_DASH=[5,6],LL_DS=2,LL_W=40075016.686;
const LLP=LL_DASH[0]+LL_DASH[1];   // okres linii przerywanej [m]
const LL={nearIds:new Set(),dirty:false,ph:new Map(),res:new Map(),Q:[],inQ:new Set(),T:0,ver:0,P:null,ixD:null,ix:null,rpAt:0,ends:null,endsV:-1,scanKey:'',scanCam:null,col:new Map(),Hmax:0,n:0,ms:0};
const llH=k=>VC[k]?VC[k].m*1.2:0;   // połowa szerokości jezdni klasy k na mapie [m] (od ok. 0,7 px/m szerokość to VC.m·s·2,4; widok kierowcy: +7% po obu stronach – zapas w maskach)
const llMy=la=>LL_W/(2*Math.PI)*Math.log(Math.tan(Math.PI/4+rad(la)/2));
function llFrame(D){if(D.llF)return D.llF;return D.llF={cl:Math.cos(rad(D.lat)),cx:D.lon/360*LL_W,cy:llMy(D.lat)}}
const llXY=(F,la,lo)=>[(lo/360*LL_W-F.cx)*F.cl,(llMy(la)-F.cy)*F.cl];
// siatka odcinków dróg z kafelków (RS) bieżącej mapy: klasa rysowania, ważność, poziom (most), kierunek jednokierunkowej
function llIndex(D,budget){   // budget [ms]: buduj kawałkami (zwraca null, dopóki nie skończy); bez – od razu całą
  if(LL.ixD===D&&LL.ix)return LL.ix;
  let B=LL.ixB;if(!B||B.D!==D)B=LL.ixB={D,pi:0,G:new Map(),S:[],Hm:0};
  const R=D.RS||[],CS=16,G=B.G,S=B.S,t0=performance.now();
  for(;B.pi<R.length;B.pi++){
    if(budget&&(B.pi&63)===0&&performance.now()-t0>budget)return null;
    const a=R[B.pi],k=a.kw||a.k;if(!(k in LL_RK))continue;const n=a.length>>1,H=llH(k);if(H>B.Hm)B.Hm=H;
    for(let i=0;i<n-1;i++){const x1=a[2*i],y1=a[2*i+1],x2=a[2*i+2],y2=a[2*i+3],dx=x2-x1,dy=y2-y1,L=Math.hypot(dx,dy);if(L<.05)continue;
      const id=S.length;S.push({x1,y1,ux:dx/L,uy:dy/L,L,pi:B.pi,k,r:LL_RK[k],lv:a.lv?1:0,od:a.od||0,H});
      const u0=Math.floor((Math.min(x1,x2)-1)/CS),u1=Math.floor((Math.max(x1,x2)+1)/CS),v0=Math.floor((Math.min(y1,y2)-1)/CS),v1=Math.floor((Math.max(y1,y2)+1)/CS);
      for(let u=u0;u<=u1;u++)for(let v=v0;v<=v1;v++){const key=u*65536+v;let l=G.get(key);if(!l)G.set(key,l=[]);l.push(id)}}}
  LL.Hmax=B.Hm;LL.ix={G,S,CS,st:new Uint32Array(S.length),sp:0,co:new Map()};LL.ixD=D;LL.ixB=null;return LL.ix;
}
function llCorners(ix,D,pi){   // ostre wierzchołki ciągu drogi z mapy: [x,y,kąt,...] (skręt ponad 35° między kierunkami 3 m przed i za wierzchołkiem)
  let c=ix.co.get(pi);if(c)return c;c=[];const a=D.RS[pi],n=a.length>>1;
  if(n>=3){const cum=clCum(a),L=cum[n-1],at=s=>{s=s<0?0:s>L?L:s;let i=0;while(i<n-2&&cum[i+1]<s)i++;const l=cum[i+1]-cum[i],f=l>0?(s-cum[i])/l:0;return [a[2*i]+(a[2*i+2]-a[2*i])*f,a[2*i+1]+(a[2*i+3]-a[2*i+1])*f]};
    for(let i=1;i<n-1;i++){const s=cum[i];if(s<1||s>L-1)continue;const p=[a[2*i],a[2*i+1]],q0=at(s-3),q1=at(s+3),v1x=p[0]-q0[0],v1y=p[1]-q0[1],v2x=q1[0]-p[0],v2y=q1[1]-p[1],th=Math.abs(Math.atan2(v1x*v2y-v1y*v2x,v1x*v2x+v1y*v2y));if(th>.61)c.push(p[0],p[1],th)}}
  ix.co.set(pi,c);return c;
}
function llCap(S,x,y,nx,ny,Hm){   // przesunięcia o, dla których punkt (x,y)+o·n leży w pasie drogi S (odcinek z okrągłymi końcami, promień Hm); null – żadne
  let lo=1e9,hi=-1e9;
  const e=(x-S.x1)*S.uy-(y-S.y1)*S.ux,sn=nx*S.uy-ny*S.ux,p0=(x-S.x1)*S.ux+(y-S.y1)*S.uy,pn=nx*S.ux+ny*S.uy;
  let a1,a2,b1,b2;
  if(Math.abs(sn)<1e-9){if(Math.abs(e)>Hm){a1=1;a2=0}else{a1=-1e9;a2=1e9}}else{a1=(-Hm-e)/sn;a2=(Hm-e)/sn;if(a1>a2){const q=a1;a1=a2;a2=q}}
  if(Math.abs(pn)<1e-9){if(p0<0||p0>S.L){b1=1;b2=0}else{b1=-1e9;b2=1e9}}else{b1=-p0/pn;b2=(S.L-p0)/pn;if(b1>b2){const q=b1;b1=b2;b2=q}}
  const s1=Math.max(a1,b1),s2=Math.min(a2,b2);if(s1<=s2){lo=s1;hi=s2}
  for(let k=0;k<2;k++){const ex=S.x1+(k?S.ux*S.L:0),ey=S.y1+(k?S.uy*S.L:0),dx=x-ex,dy=y-ey,b=nx*dx+ny*dy,c=dx*dx+dy*dy-Hm*Hm,dd=b*b-c;if(dd>=0){const r=Math.sqrt(dd);if(-b-r<lo)lo=-b-r;if(-b+r>hi)hi=-b+r}}
  return lo<=hi?[lo,hi]:null;
}
function llQ(ix,x,y,r,f){   // f(odcinek) dla każdego odcinka w kwadracie ±r (każdy raz)
  const CS=ix.CS,st=ix.st,sp=++ix.sp,u0=Math.floor((x-r)/CS),u1=Math.floor((x+r)/CS),v0=Math.floor((y-r)/CS),v1=Math.floor((y+r)/CS);
  for(let u=u0;u<=u1;u++)for(let v=v0;v<=v1;v++){const l=ix.G.get(u*65536+v);if(!l)continue;for(let z=0;z<l.length;z++){const id=l[z];if(st[id]===sp)continue;st[id]=sp;f(ix.S[id])}}
}
// końce dróg z danymi o pasach (wspólne węzły OSM) – do szukania dalszego ciągu jezdni
const llEK=(la,lo)=>Math.round(la*1e6)+','+Math.round(lo*1e6);
function llEnds(){
  if(LL.ends&&LL.endsV===laneVer)return LL.ends;
  if(!LL.ends||LANEW.size<LL.endsN){LL.ends=new Map();LL.endsIn=new Set()}   // dane przycięte (daleko za nami) – od nowa
  const M=LL.ends,IN=LL.endsIn;
  for(const w of LANEW.values()){if(IN.has(w.id))continue;IN.add(w.id);const g=w.g,n=g.length/2;for(const e of [0,n-1]){const key=llEK(g[2*e],g[2*e+1]);let l=M.get(key);if(!l)M.set(key,l=[]);l.push(w,e)}}
  LL.endsV=laneVer;LL.endsN=LANEW.size;return M;
}
function llTrav(w){   // droga w kierunku jazdy: jednokierunkowa „pod prąd” (oneway=-1) – odwrócona geometria, pasy do przodu = nb
  const g=w.g;
  if(w.ow===-1){const n=g.length/2,r=new Array(g.length);for(let i=0;i<n;i++){r[2*i]=g[2*(n-1-i)];r[2*i+1]=g[2*(n-1-i)+1]}return {g:r,two:false,nf:w.nb,nb:0,tf:w.tb||''}}
  if(w.ow===1)return {g,two:false,nf:w.nf,nb:0,tf:w.tf||''};
  return {g,two:true,nf:w.nf,nb:w.nb,tf:w.tf||'',tb:w.tb||''};
}
// jedyna droga z danymi o pasach, z której wjeżdżamy na naszą (atStart) albo na którą z niej zjeżdżamy – w tym samym kierunku (±40°); pasy w układzie naszej drogi
function llLink(w,T,atStart){
  const g=T.g,n=g.length/2,e=atStart?0:n-1,l=llEnds().get(llEK(g[2*e],g[2*e+1]));if(!l)return null;
  const i0=atStart?0:n-2,brW=bear(g[2*i0],g[2*i0+1],g[2*i0+2],g[2*i0+3]);
  let hit=null,cnt=0,best=null,bd=1e9;
  for(let z=0;z<l.length;z+=2){const v=l[z],ve=l[z+1];if(v===w)continue;const vn=v.g.length/2,vEnd=ve===vn-1;
    let ok,same;   // same: kierunek rysowania v zgodny z kierunkiem jazdy przez styk
    if(atStart){if(v.ow===1){ok=vEnd;same=true}else if(v.ow===-1){ok=!vEnd;same=false}else{ok=true;same=vEnd}}
    else{if(v.ow===1){ok=!vEnd;same=true}else if(v.ow===-1){ok=vEnd;same=false}else{ok=true;same=!vEnd}}
    if(!ok||(v.ow===0)!==T.two)continue;   // jezdnia jednokierunkowa przechodząca w dwukierunkową (i odwrotnie) to rozwidlenie – bez przejścia
    const vg=v.g,b=ve===0?bear(vg[0],vg[1],vg[2],vg[3]):bear(vg[2*vn-4],vg[2*vn-3],vg[2*vn-2],vg[2*vn-1]);
    // b – kierunek rysowania v przy styku; kierunek jazdy: zgodny albo odwrotny
    const tb=same?b:(b+180)%360;
    const ad=angDiff(tb,brW);if(ad>40)continue;
    cnt++;hit={v,same};if(ad<bd){bd=ad;best=hit}
  }
  if(cnt!==1)return cnt?{multi:1,main:best}:null;   // main: najbardziej „na wprost” – tylko do ciągłości wzoru kresek
  const v=hit.v,s=hit.same;
  if(v.ow===1)return {v,same:s,nf:v.nf,nb:0,tf:v.tf||''};
  if(v.ow===-1)return {v,same:s,nf:v.nb,nb:0,tf:v.tb||''};
  return {v,same:s,nf:s?v.nf:v.nb,nb:s?v.nb:v.nf,tf:(s?v.tf:v.tb)||''};
}
// faza kresek na początku drogi (w kierunku jazdy): ciąg dróg, z których jedyną wjeżdżamy na następną, ma ciągły wzór kresek (bez „przeskoku” na stykach)
function llLenM(w,F){if(w.llL!=null)return w.llL;const g=llTrav(w).g,n=g.length/2;let L=0,p=llXY(F,g[0],g[1]);for(let i=1;i<n;i++){const q=llXY(F,g[2*i],g[2*i+1]);L+=Math.hypot(q[0]-p[0],q[1]-p[1]);p=q}return w.llL=L}
function llPhase(w,F){
  const M=LL.ph;if(M.has(w.id))return M.get(w.id);
  const ch=[],seen=new Set();let cur=w;
  while(cur&&!seen.has(cur.id)&&ch.length<80){seen.add(cur.id);if(M.has(cur.id)){ch.push({w:cur,l:null});break}const l0=llLink(cur,llTrav(cur),true),l=l0&&l0.multi?l0.main:l0,ok=l&&l.v;ch.push({w:cur,l:ok?l:null});if(!ok)break;cur=l.v}
  const top=ch[ch.length-1].w;if(!M.has(top.id))M.set(top.id,0);
  for(let i=ch.length-2;i>=0;i--){const l=ch[i].l,p=ch[i+1].w,pv=M.get(p.id);
    M.set(ch[i].w.id,p.ow===0&&!l.same?((LL_DASH[0]-pv)%LLP+LLP)%LLP:(pv+llLenM(p,F))%LLP)}   // dwukierunkowa rysowana „pod prąd”: wzór odbity
  return M.get(w.id);
}
// kreski linii przerywanej: punkty (xs,ys) z długością wzdłuż drogi (ss); kreska tam, gdzie (faza+s) mod okres < długość kreski; wynik – płaska lista, NaN między kreskami
function llDashes(xs,ys,ss,ph){
  const out=[],DA=LL_DASH[0],on=s=>((ph+s)%LLP+LLP)%LLP<DA;let pen=false;
  const put=(x,y)=>{out.push(x,y)};
  for(let i=0;i<xs.length;i++){
    if(i===0){if(on(ss[0])){put(xs[0],ys[0]);pen=true}continue}
    const sa=ss[i-1],sb=ss[i];let s0=sa;
    while(true){const p=((ph+s0)%LLP+LLP)%LLP,nx=s0+(p<DA?DA-p:LLP-p);if(nx>=sb)break;   // kolejna granica kreski w tym odcinku
      const f=(nx-sa)/(sb-sa||1),x=xs[i-1]+(xs[i]-xs[i-1])*f,y=ys[i-1]+(ys[i]-ys[i-1])*f;
      if(pen){put(x,y);out.push(NaN,NaN);pen=false}else{put(x,y);pen=true}
      s0=nx+1e-6;}
    if(pen)put(xs[i],ys[i]);
  }
  if(pen)out.push(NaN,NaN);
  // kreski krótsze niż 1 m (ucięte na końcu biegu) pomijamy
  const res=[];let st=0;for(let i=0;i<=out.length;i+=2){if(i===out.length||isNaN(out[i])){if(i-st>=4){let L=0;for(let q=st+2;q<i;q+=2)L+=Math.hypot(out[q]-out[q-2],out[q+1]-out[q-1]);if(L>=1){for(let q=st;q<i;q++)res.push(out[q]);res.push(NaN,NaN)}}st=i+2}}
  return Float32Array.from(res);
}
// do ok. 8 m drogi sąsiedniej za stykiem, w kierunku jazdy naszej drogi (pred: przed początkiem, succ: za końcem) – kierunek drogi przy styku liczymy tak samo po obu stronach
function llCtx(l,atStart){
  if(!l)return null;const v=l.v,g=v.g,n=g.length/2;if(!v||n<2)return null;
  const fwd=v.ow===1||(v.ow===0&&l.same);   // kierunek rysowania v zgodny z kierunkiem jazdy przez styk
  // pred (atStart): v kończy się na styku → punkty od końca v (bez samego styku), odwrócone do kolejności jazdy; succ: od początku v
  const idx=[];if(atStart){if(fwd)for(let i=n-2;i>=0;i--)idx.push(i);else for(let i=1;i<n;i++)idx.push(i)}else{if(fwd)for(let i=1;i<n;i++)idx.push(i);else for(let i=n-2;i>=0;i--)idx.push(i)}
  const out=[];let L=0,pa=atStart?(fwd?n-1:0):(fwd?0:n-1);
  for(const i of idx){L+=dist(g[2*pa],g[2*pa+1],g[2*i],g[2*i+1]);out.push(g[2*i],g[2*i+1]);pa=i;if(L>=8)break}
  return out;
}
const llRT=tag=>{if(!tag)return 0;let n=0;for(const l of lnParse(tag))if(l.has('R')&&!l.has('S')&&!l.has('L'))n++;return n};   // pasy tylko do skrętu w prawo
const llSm=t=>t<=0?0:t>=1?1:t*t*(3-2*t);
// linie pasów jednej drogi z danymi OSM w układzie mapy D: [{t:0 przerywana / 1 ciągła, k: klasa drogi pod linią, z: poziom, w: najwęższy pas [m], p: punkty}]
function llWay(D,w){
  const T=llTrav(w),two=T.two,NF=T.nf|0,NB=T.nb|0;
  if(two?(Math.max(NF,NB)<2||NF<1||NB<1||w.c>0):NF<2)return {id:w.id,none:1,full:true};   // 1+1 i pas środkowy: zostaje oś z mapy
  const F=llFrame(D),ix=llIndex(D),g=T.g,n=g.length/2;
  const PX=new Float64Array(n),PY=new Float64Array(n),CU=new Float64Array(n);
  for(let i=0;i<n;i++){const q=llXY(F,g[2*i],g[2*i+1]);PX[i]=q[0];PY[i]=q[1];if(i)CU[i]=CU[i-1]+Math.hypot(PX[i]-PX[i-1],PY[i]-PY[i-1])}
  const len=CU[n-1];if(!(len>=6))return {id:w.id,none:1,full:true};
  // oś z kawałkiem sąsiednich dróg za stykami (kierunek przy styku taki sam po obu stronach – linie łączą się bez uskoku)
  const l0=llLink(w,T,true),l1=llLink(w,T,false),c0=llCtx(l0&&l0.multi?l0.main:l0,true),c1=llCtx(l1&&l1.multi?l1.main:l1,false);
  const EX=[],EY=[];if(c0)for(let i=c0.length-2;i>=0;i-=2){const q=llXY(F,c0[i],c0[i+1]);EX.push(q[0]);EY.push(q[1])}
  const e0=EX.length;for(let i=0;i<n;i++){EX.push(PX[i]);EY.push(PY[i])}if(c1)for(let i=0;i<c1.length;i+=2){const q=llXY(F,c1[i],c1[i+1]);EX.push(q[0]);EY.push(q[1])}
  const EN=EX.length,EC=new Float64Array(EN);for(let i=1;i<EN;i++)EC[i]=EC[i-1]+Math.hypot(EX[i]-EX[i-1],EY[i]-EY[i-1]);
  const s0=EC[e0],EL=EC[EN-1];
  const at=s=>{s=s<0?0:s>EL?EL:s;let a=0,b=EN-1;while(b-a>1){const c=(a+b)>>1;if(EC[c]<=s)a=c;else b=c}const L=EC[b]-EC[a],f=L>0?(s-EC[a])/L:0;return [EX[a]+(EX[b]-EX[a])*f,EY[a]+(EY[b]-EY[a])*f]};
  // próbki co 2 m (i koniec); kierunek z punktów 3 m przed i za próbką (wygładzony, ciągły przez styki)
  const m=Math.max(2,Math.ceil(len/LL_DS)+1),X=new Float64Array(m),Y=new Float64Array(m),SS=new Float64Array(m),TX=new Float64Array(m),TY=new Float64Array(m);
  // narożniki: wierzchołek osi (także styk z sąsiednią drogą), na którym droga skręca o ponad 35° – linie przerwane jak na skrzyżowaniu (na długości H·tg(kąt/2)+2 m z obu stron)
  const CO=[],Hw=llH(w.k)||10;
  for(let i=1;i<EN-1;i++){const s=EC[i],p=at(s),a=at(s-3),b=at(s+3),v1x=p[0]-a[0],v1y=p[1]-a[1],v2x=b[0]-p[0],v2y=b[1]-p[1],th=Math.abs(Math.atan2(v1x*v2y-v1y*v2x,v1x*v2x+v1y*v2y));
    if(th>.61)CO.push(s,Hw*Math.tan(Math.min(1.4,th)/2)+2)}
  const TU=new Float64Array(m);   // skręt drogi na ±6 m [rad], ze znakiem (+ w lewo) – linie po wewnętrznej stronie ciasnego łuku zwijałyby się i krzyżowały
  for(let j=0;j<m;j++){const s=Math.min(len,j*len/(m-1)),p=at(s0+s),a=at(s0+s-3),b=at(s0+s+3),ux=b[0]-a[0],uy=b[1]-a[1],ul=Math.hypot(ux,uy)||1;X[j]=p[0];Y[j]=p[1];SS[j]=s;TX[j]=ux/ul;TY[j]=uy/ul;
    const q0=at(s0+s-6),q1=at(s0+s+6),v1x=p[0]-q0[0],v1y=p[1]-q0[1],v2x=q1[0]-p[0],v2y=q1[1]-p[1];TU[j]=Math.atan2(v1x*v2y-v1y*v2x,v1x*v2x+v1y*v2y)}
  // każda próbka: droga z mapy pod nami (szerokość, klasa, poziom), granice pasma (sąsiednie jezdnie) i przedziały zasłonięte przez skrzyżowania
  const OK=new Uint8Array(m),HH=new Float64Array(m),OC=new Float64Array(m),LL_=new Float64Array(m),RR=new Float64Array(m),SL=new Uint8Array(m),SR=new Uint8Array(m),KK=new Array(m),ZV=new Uint8Array(m);
  const MK=[];   // MK[j] – płaska lista przedziałów [o1,o2] przesunięć w poprzek drogi zasłoniętych w próbce j
  const Hmax=LL.Hmax||16.8;
  for(let j=0;j<m;j++){
    const x=X[j],y=Y[j],tx=TX[j],ty=TY[j],nx=-ty,ny=tx;
    let own=null,od=1e9,oc=0;   // droga z mapy pod nami: najbliższa, a przy kilku (węzeł skrzyżowania, koniec mostu) – ta sama klasa i ten sam poziom co w OSM
    llQ(ix,x,y,5.5,S=>{const ca=S.ux*tx+S.uy*ty;if(Math.abs(ca)<.906)return;if(!two&&S.od&&S.od*ca<0)return;
      let t=(x-S.x1)*S.ux+(y-S.y1)*S.uy;t=t<0?0:t>S.L?S.L:t;const qx=S.x1+S.ux*t-x,qy=S.y1+S.uy*t-y,d=Math.hypot(qx,qy);if(d>5)return;
      const sc=d+(S.k===w.k||(S.k==='mwl'&&w.k==='mw')?0:2.5)+(S.lv===(w.z?1:0)?0:3);if(sc<od){od=sc;own=S;oc=qx*nx+qy*ny}});
    if(!own){MK.push(null);continue}
    const H=own.H,r=own.r,lv=own.lv;let L=H,R=H,sl=0,sr=0;const mk=[];
    llQ(ix,x,y,H+Hmax+1.5,S=>{
      if(S===own||S.lv!==lv||S.r<r)return;   // inny poziom (most nad/pod nami); mniej ważna droga leży pod naszą
      const ca=S.ux*tx+S.uy*ty;
      if(Math.abs(ca)>=.866){   // biegnie obok (do 30°): gdzie nasz przekrój poprzeczny przecina jej oś (także gdy odnoga rozwidlenia odchodzi pod kątem)
        const e=(x-S.x1)*S.uy-(y-S.y1)*S.ux,sn=nx*S.uy-ny*S.ux;if(Math.abs(sn)<.3)return;
        const lat=-e/sn,p=(x+lat*nx-S.x1)*S.ux+(y+lat*ny-S.y1)*S.uy;if(p<-1||p>S.L+1)return;
        const al=Math.abs(lat),opp=!two&&S.od&&S.od*ca<0,HS=S.H/Math.abs(ca);   // HS: jej połowa szerokości mierzona wzdłuż naszego przekroju
        if(!opp&&S.k===own.k&&(al<1||(al<4&&Math.abs(ca)>.996)))return;   // ta sama droga (zakładka kafelków, kolejny odcinek); odnoga rozwidlenia odchodzi pod kątem – to sąsiad; ważniejsza droga przy węźle (dochodzi pod małym kątem) – też
        if(al>=H+HS)return;
        let b,sp;if(S.r===r){b=al*H/(H+HS);sp=1}else{b=al-HS;sp=0}
        if(lat>0){if(b<L){L=b;sl=sp}}else{if(b<R){R=b;sr=sp}}
      }else{   // przecina: skrzyżowanie z drogą co najmniej tak samo ważną (pas drogi z okrągłymi końcami, jak na mapie)
        if(S.pi===own.pi)return;   // ten sam ciąg drogi z mapy skręca – narożniki osobno (llCorners)
        const iv=llCap(S,x,y,nx,ny,S.H*1.07+.8);if(iv)mk.push(iv[0],iv[1]);
      }
    });
    {const cs=llCorners(ix,D,own.pi);for(let q=0;q<cs.length;q+=3)if(Math.hypot(cs[q]-x,cs[q+1]-y)<H*Math.tan(Math.min(1.4,cs[q+2])/2)+2){mk.push(-1e9,1e9);break}}   // narożnik drogi z mapy: jak skrzyżowanie
    OK[j]=1;HH[j]=H;OC[j]=oc;LL_[j]=Math.min(L,H-.4);RR[j]=Math.min(R,H-.4);SL[j]=sl&&L<H-.6?1:0;SR[j]=sr&&R<H-.6?1:0;KK[j]=own.k;ZV[j]=lv;MK.push(mk.length?mk:null);
  }
  // krótkie przerwy w dopasowaniu (szew kafelków) – uzupełniamy; poziom drogi – większość próbek
  for(let j=1;j<m-1;j++)if(!OK[j]){let a=j-1,b=j+1;while(b<m&&!OK[b]&&b-j<3)b++;if(OK[a]&&b<m&&OK[b]&&b-a<=4){for(let q=a+1;q<b;q++){const f=(q-a)/(b-a);OK[q]=2;HH[q]=HH[a]+(HH[b]-HH[a])*f;OC[q]=OC[a]+(OC[b]-OC[a])*f;LL_[q]=Math.min(LL_[a],LL_[b]);RR[q]=Math.min(RR[a],RR[b]);SL[q]=SL[a]&SL[b];SR[q]=SR[a]&SR[b];KK[q]=KK[a];ZV[q]=ZV[a];MK[q]=MK[a]||MK[b]}j=b}}
  // granice pasma: zmiana najwyżej 0,3 m na metr (linie odchylają się najwyżej o ok. 17°) – łagodnie przed zwężeniem, nie wchodząc na sąsiednią jezdnię
  const env=A=>{const st=.3*len/(m-1);for(let j=1;j<m;j++)if(OK[j]&&OK[j-1])A[j]=Math.min(A[j],A[j-1]+st);for(let j=m-2;j>=0;j--)if(OK[j]&&OK[j+1])A[j]=Math.min(A[j],A[j+1]+st)};
  env(LL_);env(RR);
  // przejścia: inna liczba pasów na sąsiedniej drodze (poza skrzyżowaniem) – zmiana na ok. 30 m po stronie drogi z większą liczbą pasów
  const masked0=j=>!OK[j]||(MK[j]&&MK[j].some((v,i)=>i%2===0&&v<=OC[j]+.5&&MK[j][i+1]>=OC[j]-.5));
  const cont=(atStart)=>{const j=atStart?0:m-1,sx=atStart?-1:1,px=X[j]+TX[j]*sx*8,py=Y[j]+TY[j]*sx*8;let ok=false;
    llQ(ix,px,py,3.5,S=>{if(ok)return;const ca=S.ux*TX[j]+S.uy*TY[j];if(Math.abs(ca)<.9)return;let t=(px-S.x1)*S.ux+(py-S.y1)*S.uy;t=t<0?0:t>S.L?S.L:t;if(Math.hypot(S.x1+S.ux*t-px,S.y1+S.uy*t-py)<3)ok=true});return ok};
  const nb_=(atStart)=>{const l=atStart?l0:l1;if(l&&l.multi)return null;if(l)return l;return cont(atStart)?{nf:1,nb:two?1:0,tf:'',imp:1}:null};
  const LR=Math.max(12,Math.min(30,len*.45));
  const pre=masked0(0)?null:nb_(true),suc=masked0(m-1)?null:nb_(false);
  const grp=(N,pv,sv,tfW,tfP,tfS)=>{   // liczba pasów grupy w próbkach (ułamkowa w przejściu) i strona, przy której pas przybywa
    const A=new Float64Array(m).fill(N);let anc='c';   // 'c' – pasy liczone od krawężnika (nowy pas przy osi), 'm' – od osi (nowy przy krawężniku)
    if(pv!=null&&pv>=1&&pv<N){for(let j=0;j<m&&SS[j]<LR;j++)A[j]=Math.min(A[j],pv+(N-pv)*llSm(SS[j]/LR));if(llRT(tfW)-llRT(tfP)>=N-pv)anc='m'}
    if(sv!=null&&sv>=1&&sv<N){for(let j=m-1;j>=0&&len-SS[j]<LR;j--)A[j]=Math.min(A[j],sv+(N-sv)*llSm((len-SS[j])/LR))}
    return {A,anc};
  };
  const GF=grp(NF,pre&&pre.nf,suc&&suc.nf,T.tf,pre&&pre.tf,suc&&suc.tf),GB=two?grp(NB,pre&&pre.nb,suc&&suc.nb,'','',''):null;
  // przesunięcia linii w poprzek drogi (od osi OSM, w lewo dodatnie) w próbce j; null – brak linii
  const slots=[];
  const addSlot=(t,fo,wf)=>slots.push({t,fo,wf});
  const kmaxF=Math.ceil(NF)-1,kmaxB=two?Math.ceil(NB)-1:0;
  if(!two){
    for(let k=1;k<=kmaxF;k++)addSlot(0,j=>{const nf=GF.A[j];if(k>=nf)return null;const W=RR[j]+LL_[j],l=W/nf;return GF.anc==='c'?-RR[j]+k*l:LL_[j]-k*l},j=>(RR[j]+LL_[j])/GF.A[j]);
  }else{
    for(let k=1;k<=kmaxF;k++)addSlot(0,j=>{const nf=GF.A[j];if(k>=nf)return null;const W=RR[j]+OC[j],l=W/nf;return GF.anc==='c'?-RR[j]+k*l:OC[j]-k*l},j=>(RR[j]+OC[j])/GF.A[j]);
    for(let k=1;k<=kmaxB;k++)addSlot(0,j=>{const nb=GB.A[j];if(k>=nb)return null;const W=LL_[j]-OC[j],l=W/nb;return GB.anc==='c'?LL_[j]-k*l:OC[j]+k*l},j=>(LL_[j]-OC[j])/GB.A[j]);
    addSlot(1,j=>OC[j],j=>Math.min((RR[j]+OC[j])/GF.A[j],(LL_[j]-OC[j])/GB.A[j]));   // środek drogi dwukierunkowej
  }
  addSlot(1,j=>SL[j]?LL_[j]:null,()=>99);addSlot(1,j=>SR[j]?-RR[j]:null,()=>99);   // granica z sąsiednią jezdnią tej samej klasy
  const nat=j=>two?Math.min(HH[j]/NF,HH[j]/NB):2*HH[j]/NF;   // naturalna szerokość pasa (bez zwężeń)
  const out=[];let minW=99;const ph0=llPhase(w,F);
  for(const sl of slots){
    let run=null,rs=null,px=0,py=0,rk=null,rz=0,rw=99,rl=0;
    const flush=()=>{if(run&&run.length>=4&&rl>=(sl.t?6:10)){const it={t:sl.t,k:rk,z:rz,w:rw,p:Float32Array.from(run)};
        if(sl.t===0){const xs=[],ys=[];for(let i=0;i<run.length;i+=2){xs.push(run[i]);ys.push(run[i+1])}it.d=llDashes(xs,ys,rs,ph0);if(rw<minW)minW=rw}
        out.push(it)}run=null;rs=null;rl=0;rw=99};
    for(let j=0;j<m;j++){
      let o=OK[j]?sl.fo(j):null,ok=o!=null&&isFinite(o);
      if(ok){const lw=sl.wf(j);if(!(lw>=Math.max(2,.4*nat(j))))ok=false;else if(sl.t===0&&lw<rw&&run)rw=lw;else if(!run&&sl.t===0)rw=lw}
      if(ok&&(o<-RR[j]-.05||o>LL_[j]+.05))ok=false;
      if(ok&&CO.length){const sj=s0+SS[j];for(let q=0;q<CO.length;q+=2)if(Math.abs(sj-CO[q])<CO[q+1]){ok=false;break}}
      if(ok&&Math.abs(TU[j])>.1){const Rc=6/Math.abs(TU[j]),inner=TU[j]>0?o:-o;if(inner>.75*Rc||(Rc<6&&Math.abs(o)>.75*Rc))ok=false}   // ciasny łuk (narożnik): linie dalej od osi niż promień łuku – przerwa
      if(ok&&MK[j]){const a=MK[j];for(let i=0;i<a.length;i+=2)if(o>=a[i]-.25&&o<=a[i+1]+.25){ok=false;break}}
      if(!ok){flush();continue}
      const qx=X[j]-TY[j]*o,qy=Y[j]+TX[j]*o;
      if(run){const sx=qx-px,sy=qy-py;if(sx*TX[j]+sy*TY[j]<.2*LL_DS){flush();}}   // linia „cofa się” (ciasny łuk po wewnętrznej) – przerwa
      if(run&&ZV[j]!==rz)flush();   // z ziemi na most (i z powrotem): osobne linie (rysowane w innym miejscu kolejności)
      if(!run){run=[];rs=[];rk=KK[j];rz=ZV[j]}
      else rl+=Math.hypot(qx-px,qy-py);
      run.push(qx,qy);rs.push(SS[j]);px=qx;py=qy;
    }
    flush();
  }
  let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;for(let i=0;i<n;i++){if(PX[i]<x0)x0=PX[i];if(PX[i]>x1)x1=PX[i];if(PY[i]<y0)y0=PY[i];if(PY[i]>y1)y1=PY[i]}
  const bb=D.bb,full=!!bb&&x0-60>bb[0]&&y0-60>bb[1]&&x1+60<bb[2]&&y1+60<bb[3];   // całe otoczenie drogi było w danych mapy – wynik zostaje po przeładowaniu mapy
  return {id:w.id,D,lat0:D.lat,lon0:D.lon,full,L:out,near:LL.nearIds.has(w.id)};
}
// kolejka w tle: drogi w promieniu ok. 1,1 km od kamery (najbliższe najpierw), po 6 ms; po skończeniu (albo co 0,5 s) – jedno przemalowanie mapy
function llWant(D,cam){
  if(!llOn||!LANEW.size||!D||!D.RS)return;
  const key=laneVer+'|'+D.lat+','+D.lon;
  if(LL.scanKey===key&&LL.scanCam&&dist(LL.scanCam.lat,LL.scanCam.lon,cam.lat,cam.lon)<150)return;
  LL.scanKey=key;LL.scanCam={lat:cam.lat,lon:cam.lon};
  const F=llFrame(D),c=llXY(F,cam.lat,cam.lon),bb=D.bb,list=[];
  for(const w of LANEW.values()){
    const r=LL.res.get(w.id);if(r&&(r.D===D||r.full))continue;if(LL.inQ.has(w.id))continue;
    let b=w.llb;if(!b){const g=w.g;let a0=90,a1=-90,o0=180,o1=-180;for(let i=0;i<g.length;i+=2){if(g[i]<a0)a0=g[i];if(g[i]>a1)a1=g[i];if(g[i+1]<o0)o0=g[i+1];if(g[i+1]>o1)o1=g[i+1]}b=w.llb=[a0,o0,a1,o1]}
    const p=llXY(F,b[0],b[1]),q=llXY(F,b[2],b[3]);
    if(bb&&(q[0]<bb[0]||p[0]>bb[2]||q[1]<bb[1]||p[1]>bb[3]))continue;   // poza danymi mapy
    const dx=Math.max(0,p[0]-c[0],c[0]-q[0]),dy=Math.max(0,p[1]-c[1],c[1]-q[1]),d=Math.hypot(dx,dy);if(d>1100)continue;
    list.push([d,w.id]);
  }
  if(!list.length)return;
  list.sort((a,b)=>a[0]-b[0]);for(const [d,id] of list){LL.Q.push(id);LL.inQ.add(id);if(d<700)LL.nearIds.add(id);else LL.nearIds.delete(id)}
  if(!LL.T)LL.T=setTimeout(llPump,0);
}
function llPump(){
  LL.T=0;const t0=performance.now(),D=vecData;let done=0;
  if(D&&LL.Q.length&&!llIndex(D,5)){LL.ms+=performance.now()-t0;LL.T=setTimeout(llPump,16);return}   // nowa mapa: najpierw siatka odcinków (kawałkami)
  if(D)llEnds();
  while(LL.Q.length&&performance.now()-t0<6){const id=LL.Q.shift();LL.inQ.delete(id);const w=LANEW.get(id);if(!w||!D)continue;
    let r=null;try{r=llWay(D,w)}catch(e){r=null;lnFail(e)}
    LL.res.set(id,r||{id,none:1,D,full:false});done++;LL.n++;
    if(r&&r.L&&r.L.length&&r.near)LL.dirty=true}
  LL.ms+=performance.now()-t0;
  if(done){LL.ver++;const now=performance.now();if(LL.dirty&&(!LL.Q.length||now-LL.rpAt>600)){LL.rpAt=now;LL.dirty=false;vd=null}}   // przemalowanie tylko dla linii w pobliżu kamery
  if(LL.Q.length)LL.T=setTimeout(llPump,16);
}
// ścieżki do rysowania w układzie bieżącej mapy, w grupach: poziom | rodzaj linii | klasa drogi | najwęższy pas (linie znikają, gdy pas ma mniej niż ok. 6,5 px)
const LL_WB=[8,6,4.5,3.4,2.4],LL_PR=1300;
function llPaths(D,cam){
  const F=llFrame(D),c=cam?llXY(F,cam.lat,cam.lon):[0,0];let P=LL.P;
  if(P&&P.D===D&&P.ver===LL.ver&&P.ln===LANEW.size&&Math.hypot(c[0]-P.cx,c[1]-P.cy)<450)return P;
  if(!P||P.D!==D||P.ln>LANEW.size||Math.hypot(c[0]-P.cx,c[1]-P.cy)>=450)P=LL.P={D,cx:c[0],cy:c[1],G:new Map(),in:new Map(),list:[],ver:-1,ln:0};   // od nowa: inna mapa, przycięte dane, kamera daleko
  P.ver=LL.ver;P.ln=LANEW.size;let add=false;
  for(const r of LL.res.values()){if(!r||!r.L||!r.L.length||P.in.get(r.id)===r||!LANEW.has(r.id))continue;
    if(P.in.has(r.id)){LL.P=null;return llPaths(D,cam)}   // linie tej drogi policzone od nowa – ścieżki budujemy od nowa
    const dx=(r.lon0-D.lon)/360*LL_W*F.cl,dy=(llMy(r.lat0)-F.cy)*F.cl;   // linie liczone dla poprzednich danych mapy: przesunięcie układu
    const p0=r.L[0].p;if(Math.hypot(p0[0]+dx-P.cx,p0[1]+dy-P.cy)>LL_PR)continue;   // daleko od miejsca budowy ścieżek
    P.in.set(r.id,r);add=true;
    for(const l of r.L){const bk=l.t?0:l.w>=8?0:l.w>=6?1:l.w>=4.5?2:l.w>=3.4?3:4,gk=l.z*1000+l.t*100+bk*10+(LL_KI[l.k]||0);
      let gr=P.G.get(gk);if(!gr)P.G.set(gk,gr={z:l.z,t:l.t,k:l.k,mw:l.t?0:LL_WB[bk],p:new Path2D()});
      const p=l.d||l.p;let mv=true;for(let i=0;i<p.length;i+=2){const x=p[i];if(x!==x){mv=true;continue}if(mv){gr.p.moveTo(x+dx,p[i+1]+dy);mv=false}else gr.p.lineTo(x+dx,p[i+1]+dy)}}}
  if(add||!P.list.length)P.list=[...P.G.values()].sort((a,b)=>a.t-b.t);
  return P;
}
function llRGB(s){if(typeof s!=='string')return null;let q=/^#([0-9a-f]{6})$/i.exec(s);if(q){const v=parseInt(q[1],16);return [v>>16&255,v>>8&255,v&255]}
  q=/^#([0-9a-f]{3})$/i.exec(s);if(q){const h=q[1];return [0,1,2].map(i=>parseInt(h[i]+h[i],16))}q=/^rgba?\(([^)]+)\)/i.exec(s);if(q){const a=q[1].split(',').map(Number);if(a.length>=3&&a.slice(0,3).every(isFinite))return a.slice(0,3)}return null}
function llColor(k,pal,night,dm){   // kolor osi jezdni z mapy (półprzezroczysty) nałożony na wypełnienie tej klasy drogi – nieprzezroczysty, więc ciągła linia zakrywa przerywaną oś
  const key=k+'|'+(night?1:0)+(dm?1:0)+'|'+pal.bg+'|'+pal[k==='mwl'?'mw':k];let v=LL.col.get(key);if(v)return v;
  const ax=dm?(night?[225,232,255,.8]:[120,108,85,.78]):(night?[215,225,255,.55]:[105,95,75,.55]),f=llRGB(roadFill(k,pal,night));
  v=f?'rgb('+[0,1,2].map(i=>Math.round(f[i]+(ax[i]-f[i])*ax[3])).join(',')+')':'rgba('+ax.join(',')+')';LL.col.set(key,v);return v;
}
function llDraw(c,D,s,pal,night,dm,z,cam){   // z: 0 – drogi na ziemi (przed mostami), 1 – na mostach i wiaduktach (po nich)
  if(!llOn||s<.75||!LL.res.size)return;
  const P=llPaths(D,cam);if(!P.list.length)return;
  const lw=(dm?Math.max(1.5,2.1*Math.min(1.8,s)):Math.max(1.1,1.6*Math.min(1.6,s)))/s;
  c.save();c.lineCap='butt';c.lineJoin='round';
  for(const gr of P.list){if(gr.z!==z||(gr.t===0&&gr.mw*s<6.5))continue;
    c.strokeStyle=llColor(gr.k,pal,night,dm);c.lineWidth=gr.t?lw*1.2:lw;c.stroke(gr.p)}   // kreski są już w geometrii (wzór ciągły wzdłuż całej drogi)
  c.restore();
}
