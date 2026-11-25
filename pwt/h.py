# Wspólne narzędzia testów (odbudowane w wersji 192): przeglądarka z lokalnymi danymi (kafelki OpenFreeMap okolic Wrocławia,
# zamiennik Overpass i OSRM na wyciągu OSM, przejazdy z repozytorium), sterowanie pozycją GPS i kamerą, zrzuty.
import os,json,asyncio,math,re,urllib.parse,time
from playwright.async_api import async_playwright
APP=os.environ.get('APP','/tmp/app/cur.html')
TILES='/tmp/wro/wro';REPO='/home/claude/pociong'
ORIGIN='https://tronbeczka.github.io/Pociong/'
_ovp=None;_osrm=None
STATS={'tiles':0,'tiles404':0,'ovp':0,'osrm':0,'blocked':set()}
def _lazy():
    global _ovp,_osrm
    if _ovp is None:
        import sys;sys.path.insert(0,'/tmp/pwt');import ovp,osrm;_ovp=ovp;_osrm=osrm
    return _ovp,_osrm
NOLANES=os.environ.get('NOLANES')=='1'
SYNTH_ROUTE=None   # lista (lat,lon): zamiennik OSRM zwraca tę trasę zamiast liczyć
OVP_OFF=False   # True: serwer Overpass „niedostępny” (mapa bez danych o pasach – jak w miejscach bez tych tagów)
INFL=[0,0.0]   # [liczba obsługiwanych żądań, czas ostatniego]
async def handler(route,req):
    INFL[0]+=1;INFL[1]=time.time()
    try:return await _handler(route,req)
    finally:INFL[0]-=1;INFL[1]=time.time()
async def _handler(route,req):
    u=req.url
    try:
        if u.startswith(ORIGIN) and (u==ORIGIN or u.split('?')[0].endswith(('/','index.html'))):
            return await route.fulfill(status=200,content_type='text/html; charset=utf-8',body=open(APP,'rb').read())
        if u.startswith('https://tiles.openfreemap.org/planet') and u.rstrip('/').endswith('planet'):
            return await route.fulfill(status=200,content_type='application/json',body=json.dumps({'tiles':['https://tiles.openfreemap.org/planet/20261101_080013_pt/{z}/{x}/{y}.pbf']}))
        m=re.match(r'https://tiles\.openfreemap\.org/planet/[^/]+/(\d+)/(\d+)/(\d+)\.pbf',u)
        if m:
            f=f'{TILES}/{m.group(1)}_{m.group(2)}_{m.group(3)}.pbf'
            if os.path.exists(f):
                STATS['tiles']+=1;return await route.fulfill(status=200,content_type='application/x-protobuf',body=open(f,'rb').read())
            STATS['tiles404']+=1;return await route.fulfill(status=404,body='')
        if 'overpass' in u and '/api/interpreter' in u:
            if OVP_OFF:return await route.fulfill(status=503,body='')
            q=None
            if req.method=='POST':
                pd=req.post_data or '';q=urllib.parse.parse_qs(pd).get('data',[pd])[0]
            else:q=urllib.parse.parse_qs(urllib.parse.urlparse(u).query).get('data',[''])[0]
            ov,_=_lazy();STATS['ovp']+=1
            if NOLANES and ('["lanes"' in q or 'turn:lanes' in q):   # miasto bez danych o pasach ruchu w OSM
                return await route.fulfill(status=200,content_type='application/json',body=json.dumps({'elements':[]}))
            try:r=ov.overpass(q)
            except Exception as e:
                STATS.setdefault('ovpErr',[]).append(str(e)[:200]+' :: '+q[:200]);r={'elements':[],'remark':'runtime error: test'}
            return await route.fulfill(status=200,content_type='application/json',body=json.dumps(r))
        if u.startswith('https://router.project-osrm.org/route/'):
            STATS['osrm']+=1
            if SYNTH_ROUTE:   # trasa narzucona przez test (lista (lat,lon)), z jednym krokiem
                co=[[b,a] for a,b in SYNTH_ROUTE];L=sum(math.hypot((SYNTH_ROUTE[i][0]-SYNTH_ROUTE[i-1][0])*111195,(SYNTH_ROUTE[i][1]-SYNTH_ROUTE[i-1][1])*111195*math.cos(math.radians(SYNTH_ROUTE[i][0]))) for i in range(1,len(SYNTH_ROUTE)))
                st=[{'maneuver':{'type':'depart','location':co[0]},'name':'Testowa','distance':L,'duration':L/12},{'maneuver':{'type':'arrive','location':co[-1]},'name':'','distance':0,'duration':0}]
                return await route.fulfill(status=200,content_type='application/json',body=json.dumps({'code':'Ok','routes':[{'geometry':{'type':'LineString','coordinates':co},'distance':L,'duration':L/12,'legs':[{'steps':st}]}]}))
            _,osr=_lazy()
            return await route.fulfill(status=200,content_type='application/json',body=json.dumps(osr.osrm(u)))
        if u.startswith('https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/'):
            f='/tmp/npmx/package/dist/'+('leaflet.js' if u.endswith('.js') else 'leaflet.css')
            return await route.fulfill(status=200,content_type='application/javascript' if f.endswith('.js') else 'text/css',body=open(f,'rb').read())
        m=re.match(r'https://raw\.githubusercontent\.com/Tronbeczka/Pociong/[^/]+/(.+?)(\?.*)?$',u)
        if m:
            f=os.path.join(REPO,m.group(1))
            if os.path.isfile(f):return await route.fulfill(status=200,content_type='application/json',body=open(f,'rb').read())
            return await route.fulfill(status=404,body='')
    except Exception as e:
        print('handler error',u[:120],e)
    STATS['blocked'].add(urllib.parse.urlparse(u).netloc)
    return await route.abort()
async def launch(p,w=390,h=844,lat=51.1079,lon=17.0385,night=False,dpr=2,ls=None,app=None):
    global APP
    if app:APP=app
    b=await p.chromium.launch(args=['--disable-gpu-vsync','--ignore-gpu-blocklist'])
    ctx=await b.new_context(viewport={'width':w,'height':h},device_scale_factor=dpr,is_mobile=True,has_touch=True,
        geolocation={'latitude':lat,'longitude':lon,'accuracy':5},permissions=['geolocation'],locale='pl-PL',timezone_id='Europe/Warsaw')
    await ctx.route('**/*',handler)
    L={'intro1':'1','autonight':'0'}
    if ls:L.update(ls)
    await ctx.add_init_script('(()=>{try{const L='+json.dumps(L)+';for(const k in L)if(localStorage.getItem(k)==null)localStorage.setItem(k,L[k])}catch(e){}})()')
    pg=await ctx.new_page();logs=[]
    pg.on('pageerror',lambda e:logs.append('pageerror: '+str(e)[:300]))
    pg.on('console',lambda m:logs.append('console: '+m.text[:300]) if m.type=='error' and 'net::ERR' not in m.text and 'Failed to load resource' not in m.text else None)
    await pg.goto(ORIGIN,wait_until='load')
    try:await pg.wait_for_function("()=>{try{return typeof gpsOk!=='undefined'&&typeof onPos==='function'}catch(e){return false}}",timeout=20000)
    except Exception as e:print('strona nie gotowa',logs[:5]);raise
    await pg.wait_for_timeout(500)
    await pg.evaluate("(n)=>{try{if(typeof night!=='undefined'&&night!==n){night=n;applyNight()}}catch(e){}}",night)
    await fix(pg,lat,lon,0,0)
    return b,pg,logs
async def fix(pg,lat,lon,hd=0,speed=0,acc=5):
    """odczyt GPS (czas testu rośnie co najmniej o 1 s na odczyt – bez odrzucania „skoków”)"""
    await pg.evaluate("""(a)=>{window.__T=Math.max((window.__T||Date.now())+1000,Date.now());onPos({coords:{latitude:a[0],longitude:a[1],speed:a[3],heading:a[2],accuracy:a[4]},timestamp:window.__T})}""",[lat,lon,hd,speed,acc])
async def cam(pg,zoom=None,tilt=None):
    await pg.evaluate("(a)=>{if(a[0]!=null)setZoom(a[0]);if(a[1]!=null){tiltDeg=a[1];tiltDyn=0;tiltOv=tiltGo=null;try{ovTilt=null}catch(e){}try{tiltLbl()}catch(e){}applyRot()}}",[zoom,tilt])
async def goto(pg,lat,lon,hd=0,speed=0,zoom=2.4,tilt=50,wait=1500):
    """ustawia auto w punkcie (dwa odczyty w kierunku jazdy), kamerę i czeka na kafelki"""
    k=111195*math.cos(math.radians(lat))
    for d in (-6,0):
        await fix(pg,lat+d*math.cos(math.radians(hd))/111195,lon+d*math.sin(math.radians(hd))/k,hd,speed)
        await pg.wait_for_timeout(150)
    await cam(pg,zoom,tilt)
    # kolejne odczyty w tym samym miejscu (jak GPS co sekundę) – po dużym skoku mapa doczytuje się wokół kamery dopiero, gdy kamera dojdzie do auta
    for _ in range(3):
        await pg.wait_for_timeout(400);await fix(pg,lat,lon,hd,speed)
    # dopóki dane mapy są wczytane daleko od kamery (np. w połowie drogi kamery po skoku) – kolejny odczyt GPS, jak w prawdziwej jeździe co sekundę
    for _ in range(30):
        far=await pg.evaluate("(()=>{try{const c=vecCam(performance.now());return vecBusy||!vecData||dist(vecData.lat,vecData.lon,c.lat,c.lon)>600}catch(e){return false}})()")
        if not far:break
        await pg.wait_for_timeout(500);await fix(pg,lat,lon,hd,speed)
    await settle(pg,wait)
async def settle(pg,wait=1500,maxw=15000):
    """czeka aż kafelki i dane mapy się wczytają (brak oczekujących kafelków), potem jeszcze `wait` ms"""
    t0=time.time()
    while time.time()-t0<maxw/1000:
        r=await pg.evaluate("(()=>{try{return {v:!!vecData,b:!!vecBusy||!!lnBusy||lnQ.length>0}}catch(e){return {v:true,b:false}}})()")
        if r['v'] and not r['b'] and INFL[0]==0 and time.time()-INFL[1]>.7:break
        await pg.wait_for_timeout(200)
    await pg.wait_for_timeout(wait)
async def shot(pg,path,clip=None):
    await pg.screenshot(path=path,clip=clip)
def P(*a):print(*a,flush=True)
def roadpos(lat,lon,classes=None,rev=False):
    """najbliższy punkt na drodze (z wyciągu OSM) i kierunek drogi w tym miejscu; classes – dozwolone klasy highway"""
    import sys;sys.path.insert(0,'/tmp/pwt');from ovp import data
    D=data();W=D['W'];G=D['G'];best=None;bd=1e18
    k=111195*math.cos(math.radians(lat))
    for R in range(1,12):
      if best:break
      for cy in range(int(lat//G)-R,int(lat//G)+R+1):
        for cx in range(int(lon//G)-R,int(lon//G)+R+1):
            for wid in D['wg'].get((cy,cx),()):
                tg,g=W[wid]
                if 'highway' not in tg:continue
                if classes and tg['highway'] not in classes:continue
                for i in range(len(g)-1):
                    ax=(g[i][2]-lon)*k;ay=(g[i][1]-lat)*111195;bx=(g[i+1][2]-lon)*k;by=(g[i+1][1]-lat)*111195
                    dx=bx-ax;dy=by-ay;L=dx*dx+dy*dy;t=0 if L==0 else max(0,min(1,-(ax*dx+ay*dy)/L))
                    d=math.hypot(ax+dx*t,ay+dy*t)
                    if d<bd:bd=d;best=(g[i][1]+(g[i+1][1]-g[i][1])*t,g[i][2]+(g[i+1][2]-g[i][2])*t,(math.degrees(math.atan2(dx,dy))+360)%360,tg)
    la,lo,h,tg=best
    if rev:h=(h+180)%360
    return la,lo,h,tg

class T:
    """licznik sprawdzeń testu"""
    def __init__(s):s.ok=0;s.n=0
    def __call__(s,name,c,info=''):
        s.n+=1;s.ok+=bool(c);print(('ok   ' if c else 'FAIL ')+name,('' if c else str(info)[:400]),flush=True)
    def end(s):print(f'WYNIK: {s.ok}/{s.n}',flush=True)
async def plan(pg,lat,lon,frm=None):
    """trasa przez planer (cel; opcjonalnie start) – przycisk „Jedź”"""
    js="(a)=>{F.to.pt={lat:a[0],lon:a[1],label:'Cel'};F.to.el.value='Cel';"+("F.from.pt={lat:a[2],lon:a[3],label:'Start'};F.from.el.value='Start';" if frm else "")+"}"
    await pg.evaluate(js,[lat,lon]+(list(frm) if frm else []))
    await pg.evaluate("document.getElementById('pick').style.display='flex'")
    await pg.evaluate("document.getElementById('go').click()")
def poly(co):
    cum=[0]
    for i in range(1,len(co)):cum.append(cum[-1]+math.hypot((co[i][0]-co[i-1][0])*111195,(co[i][1]-co[i-1][1])*111195*math.cos(math.radians(co[i][0]))))
    def at(d):
        i=1
        while i<len(cum)-1 and cum[i]<d:i+=1
        L=cum[i]-cum[i-1];t=(d-cum[i-1])/L if L else 0
        la=co[i-1][0]+(co[i][0]-co[i-1][0])*t;lo=co[i-1][1]+(co[i][1]-co[i-1][1])*t
        h=(math.degrees(math.atan2((co[i][1]-co[i-1][1])*math.cos(math.radians(la)),co[i][0]-co[i-1][0]))+360)%360
        return la,lo,h
    return cum,at
def osrm_route(a,b):
    _,osr=_lazy();j=osr.osrm(f'https://router.project-osrm.org/route/v1/driving/{a[1]},{a[0]};{b[1]},{b[0]}?x')
    return [(c[1],c[0]) for c in j['routes'][0]['geometry']['coordinates']],j
