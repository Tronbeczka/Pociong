# zrzut i szczegóły w miejscu problemu: miejsce startowe (lat,lon), potem punkt w układzie mapy (x,y) albo id drogi
import asyncio,sys,os,json
sys.path.insert(0,'/tmp/pwt')
from h import *
la,lo=[float(v) for v in sys.argv[1].split(',')];TAG=sys.argv[2];spots=sys.argv[3:]
INFO=r"""(id)=>{const w=LANEW.get(+id);if(!w)return 'brak drogi';const D=vecData,F=llFrame(D),T=llTrav(w),r=LL.res.get(w.id),ix=llIndex(D);
 const g=T.g,n=g.length/2,own=[];for(let i=0;i<n;i+=Math.max(1,Math.floor(n/8))){const q=llXY(F,g[2*i],g[2*i+1]);let best=null,bd=9;llQ(ix,q[0],q[1],8,S=>{let t=(q[0]-S.x1)*S.ux+(q[1]-S.y1)*S.uy;t=t<0?0:t>S.L?S.L:t;const d=Math.hypot(S.x1+S.ux*t-q[0],S.y1+S.uy*t-q[1]);if(d<bd){bd=d;best=S}});own.push(best?best.k+'/'+best.lv+'/'+bd.toFixed(1):'-')}
 const pre=llLink(w,T,true),suc=llLink(w,T,false);
 return {id:w.id,k:w.k,ow:w.ow,nf:w.nf,nb:w.nb,c:w.c,N:w.N,z:w.z,rb:w.rb,tf:w.tf,tb:w.tb,len:Math.round(llLenM(w,F)),own,pre:pre&&(pre.multi?'multi':pre.v.id+'/'+pre.nf+'+'+pre.nb),suc:suc&&(suc.multi?'multi':suc.v.id+'/'+suc.nf+'+'+suc.nb),
   lines:r&&r.L?r.L.map(l=>({t:l.t,z:l.z,k:l.k,w:+l.w.toFixed(1),n:l.p.length/2,a:[Math.round(l.p[0]),Math.round(l.p[1])],b:[Math.round(l.p[l.p.length-2]),Math.round(l.p[l.p.length-1])]})):r}}"""
async def main():
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=la,lon=lo)
        await goto(pg,la,lo,hd=0,speed=0,zoom=1.0,tilt=0,wait=800)
        for _ in range(90):
            r=await pg.evaluate("(()=>{try{return {n:LANEW.size,b:lnBusy||lnQ.length>0,q:LL.Q.length}}catch(e){return {n:1,b:false,q:0}}})()")
            if r['n']>0 and not r['b'] and r['q']==0:break
            await pg.wait_for_timeout(500)
        await pg.wait_for_timeout(1000)
        for k,sp in enumerate(spots):
            if ',' in sp:
                x,y=[float(v) for v in sp.split(',')]
                q=await pg.evaluate("(a)=>{const D=vecData,F=llFrame(D),W=LL_W,lon=(a[0]/F.cl+F.cx)/W*360,my=(a[1]/F.cl+F.cy)*2*Math.PI/W,lat=2*Math.atan(Math.exp(my))*180/Math.PI-90;return [lat,lon]}",[x,y])
                await goto(pg,q[0],q[1],hd=0,speed=0,zoom=2.8/2.8,tilt=0,wait=600)
                for _ in range(40):
                    if await pg.evaluate("LL.Q.length===0&&!lnBusy"):break
                    await pg.wait_for_timeout(400)
                await pg.wait_for_timeout(800);await pg.evaluate("()=>{vd=null}");await pg.wait_for_timeout(900)
                await pg.screenshot(path=f'/tmp/shots/{TAG}_{k}.png');print(k,'zrzut',q)
            else:
                r=await pg.evaluate(INFO,sp);print(json.dumps(r,ensure_ascii=False))
        await b.close()
asyncio.run(main())
