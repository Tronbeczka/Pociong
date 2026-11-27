import asyncio,sys,os,json
sys.path.insert(0,'/tmp/pwt')
from h import *
async def main():
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=51.1115,lon=17.0600)
        await goto(pg,51.1115,17.0600,hd=0,speed=0,zoom=1.0,tilt=0,wait=800)
        for _ in range(90):
            r=await pg.evaluate("(()=>{try{return !lnBusy&&lnQ.length===0&&LL.Q.length===0&&LANEW.size>0}catch(e){return false}})()")
            if r:break
            await pg.wait_for_timeout(500)
        await pg.wait_for_timeout(3000);await pg.evaluate("()=>{vd=null}");await pg.wait_for_timeout(2000)
        r=await pg.evaluate("""()=>{const D=vecData,F=llFrame(D),Z=(signs&&(signs.zeb||signs.haz))||[],out=[];const zs=Z.filter(s=>s.kind==='crossing'&&s.cr!=='unmarked').map(s=>{const q=llXY(F,s.lat,s.lon);return [q[0],q[1],s.cr||'']});
          for(const r of LL.res.values()){if(!r||!r.A||!r.A.length)continue;const dx=(r.lon0-D.lon)/360*LL_W*F.cl,dy=(llMy(r.lat0)-F.cy)*F.cl;
            for(const a of r.A){const x=a.sh[0]+dx,y=a.sh[1]+dy;let bd=1e9,bz=null;for(const z of zs){const d=Math.hypot(z[0]-x,z[1]-y);if(d<bd){bd=d;bz=z}}if(bd<25)out.push({id:r.id,zv:r.zv,tail:[Math.round(x),Math.round(y)],zeb:bz&&[Math.round(bz[0]),Math.round(bz[1]),bz[2]],d:+bd.toFixed(1),w:LANEW.get(r.id).tf})}}
          return {sv:signs&&signs.v,nz:zs.length,out:out.slice(0,12)}}""")
        print(json.dumps(r,ensure_ascii=False))
        await b.close()
asyncio.run(main())
