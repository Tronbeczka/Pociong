import asyncio,sys,os,json
sys.path.insert(0,'/tmp/pwt')
from h import *
PT=[float(x) for x in os.environ['PT'].split(',')];CL=tuple(os.environ.get('CL','').split(',')) if os.environ.get('CL') else None
async def main():
    async with async_playwright() as p:
        a,o,hd,tg=roadpos(PT[0],PT[1],CL)
        b,pg,logs=await launch(p,lat=a,lon=o,night=os.environ.get('NIGHT')=='1')
        await goto(pg,a,o,hd=hd,speed=2,zoom=float(os.environ.get('Z','2.4')),tilt=float(os.environ.get('TILT','50')),wait=2500)
        await shot(pg,os.environ.get('OUTF','/tmp/shots/probe.png'))
        if os.environ.get('JS'):print(json.dumps(await pg.evaluate(os.environ['JS']))[:3000])
        print(tg)
        await b.close()
asyncio.run(main())
