import asyncio,sys,os,json
sys.path.insert(0,'/tmp/pwt')
from h import *
import t_jz as TJ
PL=[(51.10850,17.04780,250),(51.1116,17.0593,297),(51.0971,17.0147,0)]
async def main():
    for app in sys.argv[1:]:
        async with async_playwright() as p:
            b,pg,logs=await launch(p,lat=PL[0][0],lon=PL[0][1],app=app)
            for la,lo,hd in PL:
                await goto(pg,la,lo,hd=hd,speed=0,zoom=1.0,tilt=50,wait=1200);await TJ.wait_ready(pg);await pg.wait_for_timeout(1000)
                r=await pg.evaluate("""()=>{const R={net:[],geo:[],lines:[],tot:[]};for(let k=0;k<9;k++){JZN=null;vecData.JZT=null;const D=vecData,s=scaleCur,c=vecCam(performance.now()),kx=111195*Math.cos(rad(D.lat)),ox=(c.lon-D.lon)*kx,oy=(c.lat-D.lat)*111195;
                  const t0=performance.now();jzNet(D);const t1=performance.now();const F=jzFrame(D,s,ox,oy,900);const t2=performance.now();for(const G of F.G)G.lines=jzLines(F.N,F.B,G);const t3=performance.now();
                  R.net.push(t1-t0);R.geo.push(t2-t1);R.lines.push(t3-t2);R.tot.push(t3-t0)}
                  const st=a=>{a.sort((x,y)=>x-y);return [+a[0].toFixed(1),+a[a.length>>1].toFixed(1)]};return {net:st(R.net),geo:st(R.geo),lines:st(R.lines),tot:st(R.tot)}}""")
                print(os.path.basename(app),(la,lo),'min/mediana',r)
            await b.close()
asyncio.run(main())
