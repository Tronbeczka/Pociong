import asyncio,sys,os,math
sys.path.insert(0,'/tmp/pwt')
os.environ.setdefault('APP','/tmp/app/v196.html')
from h import *
TAG=sys.argv[1];SP=[[float(x) for x in a.split(',')] for a in sys.argv[2:]]
NIGHT=os.environ.get('NIGHT')=='1'
async def main():
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=SP[0][0],lon=SP[0][1],night=NIGHT,w=375,h=812,dpr=3)
        await pg.add_style_tag(content="*{visibility:hidden!important}#view,#view *{visibility:visible!important}")
        for k,(la,lo,hd,z,tl) in enumerate(SP):
            await goto(pg,la,lo,hd=hd,speed=2,zoom=z,tilt=tl,wait=1200);await fix(pg,la,lo,hd,0)
            for _ in range(40):
                ok=await pg.evaluate("(()=>{try{const c=vecCam(performance.now()),dr=Math.abs(((curRot-tgtRot)%360+540)%360-180);return !!vecData&&!vecBusy&&!lnBusy&&dist(vecData.lat,vecData.lon,c.lat,c.lon)<600&&dr<.4}catch(e){return true}})()")
                if ok:break
                await pg.wait_for_timeout(300)
            await settle(pg,1500)
            fn=f'/tmp/shots/{TAG}_{k}.png';await shot(pg,fn)
            q=await pg.evaluate("([la,lo])=>{const q=proj(la,lo);const v=document.getElementById('view').getBoundingClientRect();return q?[q.x+v.left,q.y+v.top]:null}",[la,lo])
            if q:
                from PIL import Image,ImageDraw
                im=Image.open(fn).convert('RGB');d=ImageDraw.Draw(im);x,y=q[0]*3,q[1]*3;d.ellipse((x-22,y-22,x+22,y+22),outline=(255,0,255),width=6);im.save(fn)
        if logs:print(logs[:3])
        await b.close()
asyncio.run(main())
