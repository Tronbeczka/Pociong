# kontrola jakości linii pasów (Wersja 206) w wielu miejscach: przecięcia linii różnych dróg, linie poza jezdnią, zdublowane linie
import asyncio,sys,os,json
sys.path.insert(0,'/tmp/pwt')
from h import *
PLACES=[('pl. Grunwaldzki',51.1115,17.0600),('most Grunwaldzki / pl. Powstańców',51.1066,17.0450),('Traugutta',51.1062,17.0460),('Legnicka',51.1165,16.9900),
        ('pl. Jana Pawła II',51.1135,17.0225),('Kazimierza Wielkiego',51.1095,17.0300),('Hallera',51.0905,17.0010),('Krzywoustego',51.1370,17.0700)]
JS=r"""()=>{const D=vecData,ix=llIndex(D),L=[],F0=llFrame(D),cm=vecCam(performance.now()),cc=llXY(F0,cm.lat,cm.lon),RAD=800;
 for(const r of LL.res.values()){if(!r||!r.L)continue;const dx=(r.lon0-D.lon)/360*LL_W*F0.cl,dy=(llMy(r.lat0)-F0.cy)*F0.cl;
   for(const l of r.L){const p=new Float64Array(l.p.length);let near=false;for(let i=0;i<p.length;i+=2){p[i]=l.p[i]+dx;p[i+1]=l.p[i+1]+dy;if(Math.hypot(p[i]-cc[0],p[i+1]-cc[1])<RAD)near=true}if(near)L.push({id:r.id,t:l.t,z:l.z,k:l.k,p})}}
 // siatka odcinków linii
 const G=new Map(),CS=10,seg=[];
 L.forEach((l,li)=>{const p=l.p;for(let i=0;i<p.length-2;i+=2){const s={li,i,x1:p[i],y1:p[i+1],x2:p[i+2],y2:p[i+3]};const id=seg.length;seg.push(s);
   const u0=Math.floor(Math.min(s.x1,s.x2)/CS),u1=Math.floor(Math.max(s.x1,s.x2)/CS),v0=Math.floor(Math.min(s.y1,s.y2)/CS),v1=Math.floor(Math.max(s.y1,s.y2)/CS);
   for(let u=u0;u<=u1;u++)for(let v=v0;v<=v1;v++){const k=u*65536+v;let a=G.get(k);if(!a)G.set(k,a=[]);a.push(id)}}});
 const X=(a,b)=>{const d1x=a.x2-a.x1,d1y=a.y2-a.y1,d2x=b.x2-b.x1,d2y=b.y2-b.y1,den=d1x*d2y-d1y*d2x;if(Math.abs(den)<1e-9)return null;
   const t=((b.x1-a.x1)*d2y-(b.y1-a.y1)*d2x)/den,u=((b.x1-a.x1)*d1y-(b.y1-a.y1)*d1x)/den;if(!(t>.02&&t<.98&&u>.02&&u<.98))return null;
   const ang=Math.asin(Math.min(1,Math.abs(den)/(Math.hypot(d1x,d1y)*Math.hypot(d2x,d2y))))*180/Math.PI;if(ang<10)return null;return [a.x1+d1x*t,a.y1+d1y*t,ang]};
 let cross=[],seen=new Set();
 for(const a of G.values())for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++){const s1=seg[a[i]],s2=seg[a[j]];if(s1.li===s2.li)continue;const l1=L[s1.li],l2=L[s2.li];if(l1.z!==l2.z)continue;
   const key=Math.min(a[i],a[j])+'_'+Math.max(a[i],a[j]);if(seen.has(key))continue;seen.add(key);const q=X(s1,s2);if(q)cross.push({q:q.map(v=>Math.round(v)),a:l1.id+':'+l1.t,b:l2.id+':'+l2.t})}
 // poza jezdnią: punkt linii dalej od osi każdej drogi (ten sam poziom, nie mniej ważna niż 'rs') niż jej połowa szerokości
 let out=0,outEx=[],tot=0;
 for(const l of L){const p=l.p;for(let i=0;i<p.length;i+=6){tot++;const x=p[i],y=p[i+1];let inside=false;
   llQ(ix,x,y,18,S=>{if(inside||S.lv!==l.z)return;let t=(x-S.x1)*S.ux+(y-S.y1)*S.uy;t=t<0?0:t>S.L?S.L:t;if(Math.hypot(S.x1+S.ux*t-x,S.y1+S.uy*t-y)<=S.H+.3)inside=true});
   if(!inside){out++;if(outEx.length<5)outEx.push([Math.round(x),Math.round(y),l.id])}}}
 // zdublowane linie przerywane: dwie linie różnych dróg bliżej niż 0,6 m i równolegle
 let dup=0,dupEx=[];const done=new Set();
 for(const a of G.values())for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++){const s1=seg[a[i]],s2=seg[a[j]];const l1=L[s1.li],l2=L[s2.li];if(l1.id===l2.id||l1.t||l2.t||l1.z!==l2.z)continue;
   const mx=(s1.x1+s1.x2)/2,my=(s1.y1+s1.y2)/2,dx=s2.x2-s2.x1,dy=s2.y2-s2.y1,L2=dx*dx+dy*dy;if(L2<.01)continue;let t=((mx-s2.x1)*dx+(my-s2.y1)*dy)/L2;if(t<0||t>1)continue;
   const d=Math.hypot(s2.x1+dx*t-mx,s2.y1+dy*t-my);if(d<.6){const key=l1.id+'_'+l2.id;if(!done.has(key)){done.add(key);dup++;if(dupEx.length<5)dupEx.push([Math.round(mx),Math.round(my),l1.id,l2.id])}}}
 return {lines:L.length,res:LL.res.size,cross:cross.length,crossEx:cross.slice(0,6),out,tot,outEx,dup,dupEx,err:window.__lnErr||null}}"""
async def main():
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=PLACES[0][1],lon=PLACES[0][2])
        for name,la,lo in PLACES:
            await pg.evaluate("()=>{gpsOk=null}")   # skok o kilka km: bez odrzucania odczytu jako „nierealnego skoku”
            await goto(pg,la,lo,hd=0,speed=0,zoom=1.0,tilt=0,wait=800)
            cm=await pg.evaluate("()=>{const c=vecCam(performance.now());return [c.lat,c.lon]}")
            print('   kamera',[round(v,5) for v in cm],flush=True)
            for _ in range(90):
                r=await pg.evaluate("(()=>{try{return {n:LANEW.size,b:lnBusy||lnQ.length>0,q:LL.Q.length}}catch(e){return {n:1,b:false,q:0}}})()")
                if r['n']>0 and not r['b'] and r['q']==0:break
                await pg.wait_for_timeout(500)
            await pg.wait_for_timeout(1200)
            r=await pg.evaluate(JS)
            print(name,json.dumps(r,ensure_ascii=False),flush=True)
        if logs:print('błędy',logs[:3])
        await b.close()
if __name__=='__main__':asyncio.run(main())
