# Wersja 197: ciągła linia dzieląca kierunki na jezdniach dwukierunkowych o różnej liczbie pasów w każdą stronę; auto i linia trasy na narysowanym pasie
import asyncio,sys,os,math,json
sys.path.insert(0,'/tmp/pwt')
import h as H
from h import *
t=T()
DIV="""()=>{const D=vecData,s=scaleCur,ox=(vf.cam.lon-D.lon)*111195*Math.cos(rad(D.lat)),oy=(vf.cam.lat-D.lat)*111195,V=lnVis(D,s,ox,oy,900);
  // linia dzieląca kierunki na rysunku: punkt na końcu odcinka (oś rysunku + przesunięcie do linii między pasami w przeciwnych kierunkach)
  const div=(v,e)=>{const a=v.m.a,n=a.length/2,i=e?n-1:0,j=e?n-2:1,dx=a[2*i]-a[2*j],dy=a[2*i+1]-a[2*j+1],L=Math.hypot(dx,dy)||1;const ux=(e?1:-1)*dx/L,uy=(e?1:-1)*dy/L;   // kierunek rysowania
    const w=v.w,LW=lnLanePx(w.kc,s)/s,x=(-w.N/2+w.nb+w.c/2)*LW;return [a[2*i]+uy*x,a[2*i+1]-ux*x]};
  const ends=[];for(const v of V){const a=(v.m0||v.m).a,n=a.length/2;if(n<2||v.w.ow!==0||!v.w.nf||!v.w.nb)continue;for(const e of [0,1]){const i=e?n-1:0,j=e?n-2:1,dx=a[2*i]-a[2*j],dy=a[2*i+1]-a[2*j+1],L=Math.hypot(dx,dy)||1;ends.push({v,e,x:a[2*i],y:a[2*i+1],ux:dx/L,uy:dy/L})}}
  let n=0,bad=0,worst=0,asym=0;
  for(const A of ends)for(const B of ends){if(A.v.w.id>=B.v.w.id)continue;if(Math.hypot(A.x-B.x,A.y-B.y)>1.5)continue;if(-(A.ux*B.ux+A.uy*B.uy)<.85)continue;
    const p=div(A.v,A.e),q=div(B.v,B.e),d=Math.hypot(p[0]-q[0],p[1]-q[1]),LW=lnLanePx(A.v.w.kc,s)/s;n++;if(A.v.w.nf!==A.v.w.nb||B.v.w.nf!==B.v.w.nb)asym++;
    if(d>.12*LW)bad++;worst=Math.max(worst,d/LW)}
  return {n,asym,bad,worst:+worst.toFixed(2)}}"""
CAR="""(al)=>{const D=vecData,s=scaleCur,R=route,p=routeAt(R,al),a=routeAt(R,al-4),b=routeAt(R,al+4),h=rad(bear(a[0],a[1],b[0],b[1])),off=lnOffPx(R,al);if(off==null)return {none:1};
  const kx=111195*Math.cos(rad(D.lat)),om=off/s,px=(p[1]-D.lon)*kx+Math.cos(h)*om,py=(p[0]-D.lat)*111195-Math.sin(h)*om;   // punkt auta/trasy (w prawo od kierunku jazdy o om metrów)
  const ox=(vf.cam.lon-D.lon)*kx,oy=(vf.cam.lat-D.lat)*111195,V=lnVis(D,s,ox,oy,1200);let best=null,bd=1e9;
  for(const v of V){const A=v.m.a;for(let i=0;i+3<A.length;i+=2){const dx=A[i+2]-A[i],dy=A[i+3]-A[i+1],L2=dx*dx+dy*dy;if(L2<1e-6)continue;let t=((px-A[i])*dx+(py-A[i+1])*dy)/L2;t=t<0?0:t>1?1:t;
    const cx=A[i]+dx*t,cy=A[i+1]+dy*t,d=Math.hypot(px-cx,py-cy),L=Math.sqrt(L2),dot=(dx/L)*Math.sin(h)+(dy/L)*Math.cos(h);if(Math.abs(dot)<.8)continue;const hw=v.w.N*lnLanePx(v.w.kc,s)/s/2;if(d>hw+1)continue;
    if(d<bd){bd=d;const lat=((px-cx)*dy-(py-cy)*dx)/L;best={v,lat,fwd:dot>0}}}}   // lat: + = w prawo od kierunku rysowania
  if(!best)return {nomatch:1};
  const w=best.v.w,LW=lnLanePx(w.kc,s)/s,k=(best.lat+w.N/2*LW)/LW,ki=Math.floor(k),fr=k-ki;
  const okLane=best.fwd?(ki>=w.nb+w.c&&ki<w.N):(ki>=0&&ki<w.nb);
  return {id:w.id,nf:w.nf,nb:w.nb,fwd:best.fwd,k:+k.toFixed(2),okLane,cen:Math.abs(fr-.5)<.3}}"""
PTS=[(51.11185,17.05830),(51.11080,17.05600),(51.11500,17.06070),(51.0857,17.01165),(51.1175,16.9900),(51.1079,17.0385)]
async def main():
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=PTS[0][0],lon=PTS[0][1])
        res=[]
        for la,lo in PTS:
            await goto(pg,la,lo,hd=0,speed=0,zoom=2.4,tilt=0,wait=1500)
            res.append(await pg.evaluate(DIV))
        print('   styki:',res)
        n=sum(r['n'] for r in res);asym=sum(r['asym'] for r in res);bad=sum(r['bad'] for r in res)
        t('styki jezdni dwukierunkowych znalezione (w tym z różną liczbą pasów w każdą stronę)',n>=10 and asym>=4,res)
        t('linia dzieląca kierunki ciągła na każdym styku (przesunięcie < 0,12 szerokości pasa)',bad==0,res)
        # trasa ul. Marii Curie-Skłodowskiej na zachód (3+2, 2+3, 2+2 pasy) – auto i linia trasy na narysowanym pasie w swoim kierunku
        co=[tuple(q) for q in json.load(open('/tmp/pwt/curie_route.json'))];H.SYNTH_ROUTE=co;cum,at=poly(co);B=co[-1]
        la,lo,hd=at(0);await goto(pg,la,lo,hd=hd,speed=0,zoom=2.4,tilt=0,wait=1500)
        await plan(pg,*B);await pg.wait_for_timeout(2500)
        cr=[]
        for k in range(0,18):
            d=min(cum[-1]-5,k*8);la,lo,hd=at(d);await fix(pg,la,lo,hd,8);await pg.wait_for_timeout(150)
            if k%2==1:
                await pg.wait_for_timeout(400);al=await pg.evaluate("route.along")
                for dd in (6,18,30):
                    if al+dd<cum[-1]-20:cr.append(await pg.evaluate(CAR,al+dd))
        got=[c for c in cr if 'okLane' in c]
        print('   pas trasy:',[(c['nf'],c['nb'],c['k'],c['okLane']) for c in got][:30])
        asy=[c for c in got if c['nf']!=c['nb']]
        t('linia trasy na ul. Marii Curie-Skłodowskiej (także na odcinkach z różną liczbą pasów w każdą stronę)',len(got)>=10 and len(asy)>=4,cr[:6])
        t('linia trasy na narysowanym pasie w kierunku jazdy (nie na przeciwnym pasie)',all(c['okLane'] for c in got),[c for c in got if not c['okLane']][:5])
        t('… i na środku pasa, nie na linii między pasami (co najmniej 80% próbek)',sum(1 for c in got if c['cen'])>=.8*len(got),[c for c in got if not c['cen']][:5])
        t('bez błędów strony',not logs,logs[:3])
        await b.close()
    t.end()
asyncio.run(main())
