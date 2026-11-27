# Wersja 208: komunikat o znakach / przejściach mieści się w okienku na różnych telefonach (szerokość, rozmiar interfejsu, poziomo). APP=v208.html python3 t_v208.py
import asyncio,sys,os,json
sys.path.insert(0,'/tmp/pwt')
from h import *
t=T()
APP=os.environ.get('APP','/tmp/app/v208.html')
TXT=['Za 10 m znak STOP','Za 170 m ustąp pierwszeństwa','Za 170 m odcinkowy pomiar prędkości · limit 120','Za 170 m fotoradar · limit 120','Za 170 m próg zwalniający','Za 170 m przejście dla pieszych']
JS="""(T)=>{const el=document.getElementById('sig'),st=document.getElementById('sigt');document.getElementById('sigi').innerHTML=SIG_ICON.crossing;el.style.transition='none';el.classList.add('on');
  const btn=['setfab','repfab','sndfab','compass'].map(id=>document.getElementById(id)).filter(e=>e&&getComputedStyle(e).display!=='none').map(e=>e.getBoundingClientRect()).filter(r=>r.width>0);
  const out=[];for(const t of T){st.textContent=t;const b=el.getBoundingClientRect(),sb=st.getBoundingClientRect(),lh=parseFloat(getComputedStyle(st).lineHeight)||17;
    const hit=btn.some(r=>!(r.right<=b.left||r.left>=b.right||r.bottom<=b.top||r.top>=b.bottom));
    out.push({t:t.slice(9,34),w:Math.round(b.width),h:Math.round(b.height),lines:Math.round(sb.height/lh),over:el.scrollWidth-el.clientWidth,outR:Math.round(sb.right-b.right),outL:Math.round(b.left-sb.left),
      inScreen:b.left>=0&&b.right<=innerWidth,hit,cx:Math.round((b.left+b.right)/2)})}
  return out}"""
async def main():
    async with async_playwright() as p:
        for (w,h_) in [(390,844),(375,667),(360,740),(320,568),(414,896),(844,390)]:
            for ui in (0,2):
                b,pg,logs=await launch(p,w=w,h=h_,lat=51.1095,lon=17.03,app=APP,ls={'uiSize':str(ui)})
                await pg.wait_for_timeout(700)
                r=await pg.evaluate(JS,TXT)
                bad=[o for o in r if o['over']>0 or o['outR']>0 or o['outL']>0 or not o['inScreen'] or o['hit'] or o['lines']>3]
                print(f'   {w}x{h_} ui{ui}:',[(o['t'][:12],o['w'],o['h'],o['lines']) for o in r])
                t(f'{w}×{h_}, rozmiar interfejsu {ui}: każdy komunikat w okienku, okienko na ekranie i nie pod przyciskami, najwyżej 3 linie',not bad,bad)
                if w==375 and ui==0:
                    shots=[]
                    for k,tx in enumerate([TXT[5],TXT[2],TXT[0]]):
                        await pg.evaluate("(t)=>{document.getElementById('sigt').textContent=t}",tx);await pg.wait_for_timeout(200)
                        await pg.screenshot(path=f'/tmp/shots/sig_after{k}.png',clip={'x':0,'y':120,'width':375,'height':130})
                t('bez błędów strony',not logs,logs[:2]) if (w==390 and ui==0) else None
                await b.close()
    t.end()
asyncio.run(main())
