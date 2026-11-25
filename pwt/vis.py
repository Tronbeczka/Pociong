# Zrzuty porównawcze (sama mapa, bez przycisków): VIS_OUT=katalog APP=plik python3 vis.py  [ONLY=litery]
import asyncio,sys,os
sys.path.insert(0,'/tmp/pwt')
import h as H
from h import *
PTS=[('A',51.1079,17.0385,None),('B',51.1175,16.9900,('primary',)),('C',51.0800,17.0150,('residential',)),('D',51.0830,17.0700,('trunk','primary')),
     ('E',51.1123,17.0590,('primary','secondary')),('F',51.1092,17.0520,('primary','secondary')),('G',51.0450,17.0700,('tertiary','residential','unclassified')),
     ('H',51.1300,16.9300,('motorway',)),('I',51.0857,17.01165,('primary','secondary')),('J',51.1900,17.1500,('unclassified','tertiary','residential')),
     ('K',51.1035,17.0310,('tertiary','secondary')),('M',51.0700,16.9950,('residential','tertiary'))]
OUT=os.environ.get('VIS_OUT','/tmp/vis/x');os.makedirs(OUT,exist_ok=True)
ONLY=os.environ.get('ONLY');VARS=os.environ.get('VARS','d3,n3,d2').split(',')
HIDE="*{visibility:hidden!important}#view,#view *{visibility:visible!important}#jp,#intro,#wait,#alarm{display:none!important}"
async def main():
    async with async_playwright() as p:
        for night in (False,True):
            vs=[v for v in VARS if (v[0]=='n')==night]
            if not vs:continue
            b,pg,logs=await launch(p,lat=PTS[0][1],lon=PTS[0][2],night=night)
            await pg.add_style_tag(content=HIDE)
            for nm,la,lo,cl in PTS:
                if ONLY and nm not in ONLY:continue
                a,o,hd,tg=roadpos(la,lo,cl)
                await goto(pg,a,o,hd=hd,speed=2,zoom=2.4,tilt=50,wait=1200)
                await fix(pg,a,o,hd,0)   # postój: kierunek zostaje, a auto nie „przewiduje” ruchu – zrzuty powtarzalne
                for _ in range(40):   # mapa wczytana wokół kamery i obrót mapy doszedł do kierunku jazdy
                    ok=await pg.evaluate("(()=>{try{const c=vecCam(performance.now()),dr=Math.abs(((curRot-tgtRot)%360+540)%360-180);return !!vecData&&!vecBusy&&!lnBusy&&dist(vecData.lat,vecData.lon,c.lat,c.lon)<600&&dr<.4}catch(e){return true}})()")
                    if ok:break
                    await pg.wait_for_timeout(300)
                    if _%6==5:await fix(pg,a,o,hd,0)
                for v in vs:
                    z,tl={'3':(2.4,50),'2':(1.0,0),'z':(5,0),'f':(0.5,50)}[v[1]]
                    await cam(pg,zoom=z,tilt=tl);await settle(pg,1800,8000)
                    await shot(pg,f'{OUT}/{nm}_{v}.png')
                await cam(pg,zoom=2.4,tilt=50)
            if logs:print('logs',logs[:4])
            await b.close()
asyncio.run(main())
