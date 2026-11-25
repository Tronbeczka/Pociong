# jazda po trasie (OSRM-zamiennik) ze zrzutami co N m: python3 drive.py nazwa lat1 lon1 lat2 lon2 [co_ile_m] [noc]
import asyncio,sys,os,json,math
sys.path.insert(0,'/tmp/pwt')
import h as H
from h import *
nm=sys.argv[1];A=(float(sys.argv[2]),float(sys.argv[3]));B=(float(sys.argv[4]),float(sys.argv[5]))
EVERY=float(sys.argv[6]) if len(sys.argv)>6 else 200;NIGHT=len(sys.argv)>7 and sys.argv[7]=='1'
OUT=os.environ.get('OUT','/tmp/shots/drv');os.makedirs(OUT,exist_ok=True)
SPEED=float(os.environ.get('SPEED','11'))
async def main():
    import osrm
    j=osrm.osrm(f'https://router.project-osrm.org/route/v1/driving/{A[1]},{A[0]};{B[1]},{B[0]}?x')
    co=[(c[1],c[0]) for c in j['routes'][0]['geometry']['coordinates']]
    cum=[0]
    for i in range(1,len(co)):cum.append(cum[-1]+math.hypot((co[i][0]-co[i-1][0])*111195,(co[i][1]-co[i-1][1])*111195*math.cos(math.radians(co[i][0]))))
    def at(d):
        i=1
        while i<len(cum)-1 and cum[i]<d:i+=1
        L=cum[i]-cum[i-1];t=(d-cum[i-1])/L if L else 0
        la=co[i-1][0]+(co[i][0]-co[i-1][0])*t;lo=co[i-1][1]+(co[i][1]-co[i-1][1])*t
        h=(math.degrees(math.atan2((co[i][1]-co[i-1][1])*math.cos(math.radians(la)),co[i][0]-co[i-1][0]))+360)%360
        return la,lo,h
    print('trasa',round(cum[-1]),'m',len(co),'pkt',flush=True)
    async with async_playwright() as p:
        b,pg,logs=await launch(p,lat=co[0][0],lon=co[0][1],night=NIGHT)
        la,lo,h=at(0)
        await goto(pg,la,lo,hd=h,speed=0,zoom=None,tilt=None,wait=1500)
        await pg.evaluate("(a)=>{F.to.pt={lat:a[0],lon:a[1],label:'Cel'};F.to.el.value='Cel'}",[B[0],B[1]])
        await pg.evaluate("document.getElementById('pick').style.display='flex'")
        await pg.evaluate("document.getElementById('go').click()");await pg.wait_for_timeout(2500)
        d=0;nxt=0;k=0
        while d<cum[-1]-30:
            la,lo,h=at(d);await fix(pg,la,lo,h,SPEED);await pg.wait_for_timeout(1000 if d>=nxt-SPEED*2 else 250)
            if d>=nxt:
                await settle(pg,600,6000)
                await shot(pg,f'{OUT}/{nm}_{k:02d}.png');k+=1;nxt+=EVERY
            d+=SPEED
        print('zrzutów',k,'logs',logs[:4],flush=True)
        await b.close()
asyncio.run(main())
