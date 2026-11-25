import asyncio,sys,os
sys.path.insert(0,'/tmp/pwt')
import h as H
from h import *
PTS=[('A_dominikanski',51.1079,17.0385,None,False),('B_legnicka',51.1175,16.9900,('primary',),False),('C_osiedlowa',51.0800,17.0150,('residential',),False),
     ('D_dwujezdniowa',51.0830,17.0700,('trunk','primary'),False),('E_rondo',51.1123,17.0590,('primary','secondary'),False),('F_most',51.1092,17.0520,('primary','secondary'),False),
     ('G_przedmiescie',51.0450,17.0700,('tertiary','residential','unclassified'),False),('H_autostrada',51.1300,16.9300,('motorway',),False),('I_hallera',51.0857,17.01165,('primary','secondary'),False),
     ('J_wies',51.1900,17.1500,('unclassified','tertiary','residential'),False)]
OUT=os.environ.get('OUT','/tmp/shots/g');os.makedirs(OUT,exist_ok=True)
MODES=os.environ.get('MODES','day,night,top').split(',')
ONLY=os.environ.get('ONLY')
async def main():
    H.OVP_OFF=os.environ.get('OVP_OFF')=='1'
    async with async_playwright() as p:
        for night in ([False] if 'night' not in MODES else [False,True]):
            b,pg,logs=await launch(p,lat=PTS[0][1],lon=PTS[0][2],night=night)
            for nm,la,lo,cl,rv in PTS:
                if ONLY and nm[0] not in ONLY:continue
                a,o,hd,tg=roadpos(la,lo,cl,rv)
                await goto(pg,a,o,hd=hd,speed=float(os.environ.get("SPD","2")),zoom=2.4,tilt=50,wait=2500)
                if (night and 'night' in MODES) or (not night and 'day' in MODES):
                    await shot(pg,f'{OUT}/{nm}_{"n" if night else "d"}.png')
                if not night and 'top' in MODES:
                    await cam(pg,zoom=1.0,tilt=0);await settle(pg,2000)
                    await shot(pg,f'{OUT}/{nm}_top.png');await cam(pg,zoom=2.4,tilt=50)
                print(nm,tg.get('highway'),tg.get('name'),tg.get('lanes'),round(hd))
            print('logs',logs[:4])
            await b.close()
    print('ovpErr',H.STATS.get('ovpErr',[])[:3])
asyncio.run(main())
