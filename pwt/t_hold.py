# Wersja 193: przeciąganie mapy, gdy telefon jest chwilowo zajęty (np. zaraz po wybraniu trasy) – nie może zamienić się w „przytrzymanie” (wybór miejsca)
import asyncio,sys,os,math
sys.path.insert(0,'/tmp/pwt')
import h as H
from h import *
t=T()
async def TE(cdp,typ,pts):await cdp.send('Input.dispatchTouchEvent',{'type':typ,'touchPoints':[{'x':x,'y':y,'id':i} for i,(x,y) in pts]})
async def main():
    async with async_playwright() as p:
        la,lo=51.1079,17.0385
        b,pg,logs=await launch(p,lat=la,lon=lo)
        cdp=await pg.context.new_cdp_session(pg)
        await goto(pg,la,lo,hd=90,speed=0,zoom=None,tilt=None,wait=1500)
        await pg.evaluate("(()=>{const o=window.mapHold;window.mapHold=function(){window.__held=(window.__held||0)+1;return o&&o.apply(this,arguments)}})()")
        res=[]
        for rep in range(4):
            await pg.evaluate("recenter()");await pg.wait_for_timeout(1500)
            await pg.evaluate("window.__held=0")
            # telefon zajęty przez 1,2 s chwilę po dotknięciu; palec w tym czasie przesuwa się o 150 px
            await pg.evaluate("(()=>{let n=0;const f=()=>{const t=performance.now();while(performance.now()-t<420){}if(++n<4)setTimeout(f,0)};setTimeout(f,60)})()")   # kilka długich zadań z rzędu (jak po wybraniu trasy)
            await TE(cdp,'touchStart',[(1,(200,400))])
            async def moves():
                for k in range(1,13):
                    await TE(cdp,'touchMove',[(1,(200,400+150*k/12))])
            task=asyncio.create_task(moves());await asyncio.sleep(.25)
            await task
            await pg.wait_for_timeout(300);await TE(cdp,'touchEnd',[]);await pg.wait_for_timeout(500)
            r=await pg.evaluate("({held:window.__held||0,free:freeCam})");res.append(r)
            await pg.evaluate("try{hidePin&&hidePin()}catch(e){}")
        print('  ',res)
        t('zajęty telefon: przeciąganie przesuwa mapę, nie wybiera miejsca (4 próby)',all(r['held']==0 and r['free'] for r in res),res)
        # zwykłe przytrzymanie dalej działa
        await pg.evaluate("recenter()");await pg.wait_for_timeout(1500);await pg.evaluate("window.__held=0")
        await TE(cdp,'touchStart',[(1,(200,400))]);await pg.wait_for_timeout(900);await TE(cdp,'touchEnd',[]);await pg.wait_for_timeout(300)
        t('przytrzymanie palca nadal wybiera miejsce',await pg.evaluate("window.__held")==1)
        await pg.evaluate("window.__held=0")
        await pg.evaluate("setTimeout(()=>{const t=performance.now();while(performance.now()-t<1200){}},60)")
        await TE(cdp,'touchStart',[(1,(200,400))]);await pg.wait_for_timeout(2200);await TE(cdp,'touchEnd',[]);await pg.wait_for_timeout(300)
        t('… także gdy telefon był w tym czasie zajęty',await pg.evaluate("window.__held")==1)
        t('bez błędów strony',not logs,logs[:3])
        await b.close()
    t.end()
asyncio.run(main())
