import asyncio,sys,os,json,statistics
sys.path.insert(0,'/tmp/pwt')
from h import *
import t_jz as TJ
async def main():
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=51.1076,lon=17.0464)
        for la,lo in [(51.1076,17.0464),(51.0971,17.0147)]:
            await goto(pg,la,lo,hd=0,speed=0,zoom=2.4,tilt=0,wait=1500);await TJ.wait_ready(pg)
            r=await pg.evaluate("""()=>{const res={tiles:[],net:[],geo:[],tot:[]};for(let rep=0;rep<15;rep++){JZN=null;const D=vecData,s=scaleCur,c=vecCam(performance.now()),kx=111195*Math.cos(rad(D.lat)),ox=(c.lon-D.lon)*kx,oy=(c.lat-D.lat)*111195;
              D.JZT=null;const t0=performance.now();jzTiles(D);const t1=performance.now();const N=jzNet(D);const t2=performance.now();jzFrame(D,s,ox,oy,900);const t3=performance.now();
              res.tiles.push(t1-t0);res.net.push(t2-t1);res.geo.push(t3-t2);res.tot.push(t3-t0)}
              const st=a=>{a.sort((x,y)=>x-y);return [+a[0].toFixed(1),+a[a.length>>1].toFixed(1)]};return {tiles:st(res.tiles),net:st(res.net),geo:st(res.geo),tot:st(res.tot)}}""")
            print((la,lo),'min/mediana',r)
        await b.close()
asyncio.run(main())
