# Wersja 204: powrót do dróg z wersji 198 – płótno mapy (drogi) takie samo jak w 198, brak modułu jezdni z pasami (199–203), szerokość dróg ×2,4 jak w 198;
# cienie budynków i budowli wyłączone (jak w 203), cienie drzew zostają. Uruchomienie: python3 t_v204b.py <wersja198.html> <wersja204.html>
import asyncio,sys,os,math,json,hashlib
sys.path.insert(0,'/tmp/pwt')
from h import *
import t_jz as TJ
t=T()
SPOTS=[(51.10594,17.04327,19.6,1.0,50),(51.10850,17.04780,250,1.0,0),(51.10660,17.04500,20,2.2,0)]   # Traugutta → most Grunwaldzki (3D), pl. Grunwaldzki, pl. Powstańców Warszawy z bliska
HASH="""()=>{const c=document.getElementById('vmap'),x=c.getContext('2d'),d=x.getImageData(0,0,c.width,c.height).data;let h1=0,h2=0;
  for(let i=0;i<d.length;i+=4){h1=(h1*31+d[i]+(d[i+1]<<8)+(d[i+2]<<16))>>>0;h2=(h2+d[i]*7+d[i+1]*13+d[i+2]*17)>>>0}return [c.width,c.height,h1,h2].join('/')}"""
async def one(p,app,la,lo,hd,zm,tl):
    b,pg,logs=await launch(p,lat=la,lon=lo,app=app)
    await goto(pg,la,lo,hd=hd,speed=0,zoom=zm,tilt=tl,wait=1500);await TJ.wait_ready(pg);await pg.wait_for_timeout(2500)
    r=await pg.evaluate("""()=>({ver:document.getElementById('ver').textContent,jz:typeof jzFrame,JZN:typeof JZN,rwLv:typeof rwLv,
       rwPr:rw('pr',2.8)/dmK,rwRs:rw('rs',1)/dmK,rwSc:rw('sc',4.5)/dmK,BLD_SH:typeof BLD_SH!=='undefined'?BLD_SH:null})""")
    h=[]
    for _ in range(3):
        await pg.evaluate("()=>{vd=null}");await pg.wait_for_timeout(700);h.append(await pg.evaluate(HASH))
    sn=[]
    if tl:
        await pg.evaluate("()=>{if(vecData)vecData.TR=null}")   # bez drzew: liczymy tylko cienie budynków i budowli
        for _ in range(8):
            await pg.wait_for_timeout(250);sn.append(await pg.evaluate("()=>bld3Draw.sn||0"))
    await b.close()
    return r,h,sn,logs
async def main():
    a198,a204=sys.argv[1],sys.argv[2]
    async with async_playwright() as p:
        for (la,lo,hd,zm,tl) in SPOTS:
            r8,h8,s8,l8=await one(p,a198,la,lo,hd,zm,tl)
            r4,h4,s4,l4=await one(p,a204,la,lo,hd,zm,tl)
            print('  ',(la,lo,zm,tl),'198:',r8,h8[-1],s8,' 204:',r4,h4[-1],s4)
            V=os.environ.get('VER','wersja 204');t(f'{la:.4f},{lo:.4f} zbliżenie {zm}: {V}',r4['ver']==V,r4['ver'])
            t('… brak modułu jezdni z pasami z wersji 199–203',r4['jz']=='undefined' and r4['JZN']=='undefined' and r4['rwLv']=='undefined',r4)
            t('… szerokość dróg jak w 198 (×2,4)',abs(r4['rwPr']-11*2.8*2.4)<1e-9 and abs(r4['rwRs']-max(10,7*2.4))<1e-9 and abs(r4['rwSc']-9*4.5*2.4)<1e-9 and (r4['rwPr'],r4['rwRs'],r4['rwSc'])==(r8['rwPr'],r8['rwRs'],r8['rwSc']),(r4,r8))
            t('… płótno mapy (drogi, tło, tory) piksel w piksel jak w '+os.environ.get('REF','198'),h4[-1]==h8[-1],(h8,h4))
            if tl:
                t('… cienie budynków: w 198 są, w 204 brak' if os.environ.get('REF_SH','1')=='1' else '… bez cieni budynków',(max(s8)>50 or os.environ.get('REF_SH','1')=='0') and max(s4)==0 and r4['BLD_SH'] is False,(s8,s4))
            t('… bez błędów strony',not l4,l4[:3])
    t.end()
asyncio.run(main())
