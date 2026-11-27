# Wersja 207: strzałki kierunków na jezdni. Uruchomienie: APP=v207.html python3 t_v207.py
import asyncio,sys,os,math,json
sys.path.insert(0,'/tmp/pwt')
import h as H
from h import *
t=T()
APP=os.environ.get('APP','/tmp/app/v207.html')
AQA=r"""()=>{const D=vecData,ix=llIndex(D),F=llFrame(D),cm=vecCam(performance.now()),cc=llXY(F,cm.lat,cm.lon);
 const Z=((typeof signs!=='undefined'&&signs&&(signs.zeb||signs.haz))||[]).filter(s=>s.kind==='crossing'&&s.cr!=='unmarked').map(s=>llXY(F,s.lat,s.lon));
 const A=[];for(const r of LL.res.values()){if(!r||!r.A)continue;const dx=(r.lon0-D.lon)/360*LL_W*F.cl,dy=(llMy(r.lat0)-F.cy)*F.cl;
   for(const a of r.A){const pts=[];for(const arr of [a.sh,a.hd])for(let i=0;i<arr.length;i+=2){if(arr[i]!==arr[i])continue;pts.push([arr[i]+dx,arr[i+1]+dy])}
     const c=pts.reduce((s,p)=>[s[0]+p[0]/pts.length,s[1]+p[1]/pts.length],[0,0]);if(Math.hypot(c[0]-cc[0],c[1]-cc[1])>800)continue;A.push({id:r.id,z:a.z,pts,c,w:a.w})}}
 let out=0,zeb=0,ovl=0;
 const outEx=[];for(const a of A){for(const p of a.pts){let inside=false,bd=1e9,bk='';llQ(ix,p[0],p[1],18,S=>{let t=(p[0]-S.x1)*S.ux+(p[1]-S.y1)*S.uy;t=t<0?0:t>S.L?S.L:t;const d=Math.hypot(S.x1+S.ux*t-p[0],S.y1+S.uy*t-p[1]);if(d-S.H<bd){bd=d-S.H;bk=S.k+'/'+S.lv}if(inside||S.lv!==a.z)return;if(d<=S.H+.3)inside=true});if(!inside){out++;if(outEx.length<4)outEx.push({id:a.id,z:a.z,p:p.map(v=>Math.round(v)),excess:+bd.toFixed(2),k:bk,w:+a.w.toFixed(1)});break}}
   for(const z of Z){if(a.pts.some(p=>Math.hypot(p[0]-z[0],p[1]-z[1])<1.5)){zeb++;break}}}
 for(let i=0;i<A.length;i++)for(let j=i+1;j<A.length;j++){const a=A[i],b=A[j];if(a.z!==b.z)continue;const d=Math.hypot(a.c[0]-b.c[0],a.c[1]-b.c[1]);if(d<Math.min(a.w,b.w)*.7)ovl++}
 return {arrows:A.length,out,zeb,ovl,outEx}}"""
async def ready(pg,maxs=45):
    for _ in range(maxs*2):
        r=await pg.evaluate("(()=>{try{return {n:LANEW.size,b:lnBusy||lnQ.length>0,q:LL.Q.length}}catch(e){return {n:1,b:false,q:0}}})()")
        if r['n']>0 and not r['b'] and r['q']==0:return True
        await pg.wait_for_timeout(500)
    return False
async def main():
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=51.1115,lon=17.0600,app=APP)
        await goto(pg,51.1115,17.0600,hd=0,speed=0,zoom=1.0,tilt=0,wait=800);await ready(pg);await pg.wait_for_timeout(2500)
        v=await pg.evaluate("document.getElementById('ver').textContent");t('wersja 207',v=='wersja 207',v)
        tot=0
        for name,la,lo in [('pl. Grunwaldzki',51.1115,17.0600),('pl. Powstańców Warszawy',51.1066,17.0450),('Kazimierza Wielkiego',51.1095,17.0300),('Traugutta/Podwale',51.1072,17.0425)]:
            await pg.evaluate("()=>{gpsOk=null}");await goto(pg,la,lo,hd=0,speed=0,zoom=1.0,tilt=0,wait=600);await ready(pg);await pg.wait_for_timeout(1500)
            q=await pg.evaluate(AQA);print('  ',name,q);tot+=q['arrows']
            t(f'{name}: strzałki na jezdni (w pasie drogi), nie na przejściach dla pieszych, bez nakładania',q['out']==0 and q['zeb']==0 and q['ovl']==0,q)
        t('strzałki są (łącznie w 4 miejscach co najmniej 40)',tot>=40,tot)
        # rysowanie: grupy strzałek trafiają na mapę przy zbliżeniu postoju, a znikają przy dużym oddaleniu
        r=await pg.evaluate("""async()=>{const cnt=s=>LL.P?LL.P.alist.filter(g=>g.z===0&&llArr&&s>=1&&g.w*s>=11).length:0;vd=null;await new Promise(r=>setTimeout(r,700));const near=cnt(scaleCur);
           setZoom(.25);await new Promise(r=>setTimeout(r,2500));const far=cnt(scaleCur),sf=scaleCur;setZoom(1);await new Promise(r=>setTimeout(r,1500));return {near,far,sf:+sf.toFixed(2),alist:LL.P?LL.P.alist.length:0}}""")
        t('przy zbliżeniu postoju strzałki rysowane, przy oddaleniu (0,7 px/m) – nie',r['alist']>0 and r['near']>0 and r['far']==0,r)
        # wyłączenie linii pasów wyłącza też strzałki
        await pg.evaluate("()=>{const e=document.getElementById('laneCb');e.checked=false;e.onchange()}");await pg.wait_for_timeout(800)
        r2=await pg.evaluate("""async()=>{let n=0;const o=llDraw;llDraw=function(c,D,s){if(llOn&&LL.P&&LL.P.alist.length)n++;return o.apply(this,arguments)};vd=null;await new Promise(r=>setTimeout(r,800));llDraw=o;return {n,llOn}}""")
        await pg.evaluate("()=>{const e=document.getElementById('laneCb');e.checked=true;e.onchange()}")
        t('wyłączone linie pasów – bez strzałek',r2['n']==0 and r2['llOn'] is False,r2)
        t('bez błędów strony',not logs,logs[:3])
        await b.close()
    t.end()
asyncio.run(main())
