# pomiar okienka komunikatu o znakach i przejściach (#sig) dla najdłuższych tekstów, różne szerokości ekranu i rozmiary interfejsu
import asyncio,sys,os,json
sys.path.insert(0,'/tmp/pwt')
from h import *
TXT=['Za 170 m znak STOP','Za 170 m ustąp pierwszeństwa','Za 170 m odcinkowy pomiar prędkości · limit 120','Za 170 m fotoradar · limit 120','Za 170 m próg zwalniający','Za 170 m przejście dla pieszych']
async def main():
    out=[]
    async with async_playwright() as p:
        for (w,h_) in [(390,844),(375,667),(360,740),(320,568),(844,390)]:
            for ui in (0,1,2):
                b,pg,logs=await launch(p,w=w,h=h_,lat=51.1095,lon=17.03,ls={'uiSize':str(ui)})
                await pg.wait_for_timeout(800)
                r=await pg.evaluate("""(T)=>{const el=document.getElementById('sig'),st=document.getElementById('sigt');document.getElementById('sigi').innerHTML=SIG_ICON.crossing;el.classList.add('on');const out=[];
                  for(const t of T){st.textContent=t;const b=el.getBoundingClientRect(),sb=st.getBoundingClientRect();out.push({t:t.slice(9,30),w:Math.round(b.width),h:Math.round(b.height),over:el.scrollWidth-el.clientWidth,txtRight:Math.round(sb.right-b.right),left:Math.round(b.left),right:Math.round(window.innerWidth-b.right)})}
                  return {font:getComputedStyle(st).fontFamily.slice(0,40),fs:getComputedStyle(el).fontSize,ui:document.body.className.match(/ui\\d/)?.[0]||'ui0',out}}""",TXT)
                bad=[o for o in r['out'] if o['over']>0 or o['txtRight']>0]
                print(w,'x',h_,r['ui'],r['fs'],'przepełnione:',len(bad),[ (o['t'],o['w'],o['over'],o['txtRight']) for o in bad][:4],flush=True)
                if w==390 and ui==0:
                    await pg.evaluate("(t)=>{document.getElementById('sigt').textContent=t}",TXT[2]);await pg.wait_for_timeout(300)
                    await pg.screenshot(path='/tmp/shots/sig_before.png',clip={'x':0,'y':120,'width':390,'height':140})
                await b.close()
asyncio.run(main())
