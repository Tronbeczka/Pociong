# Mały, lokalny zamiennik serwera Overpass (podzbiór języka Overpass QL) na danych z wyciągu OSM (osm.pkl).
# Obsługuje: unie ( ... ), zapytania node/way/nwr z filtrami tagów i przestrzennymi (bbox, around, bn., w.), zbiory ->.x, .x, przecięcia node.a.b, out (body/tags/geom/center/ids/qt/N).
import re,pickle,math,os
_D=None
def data():
    global _D
    if _D is None:
        d=pickle.load(open(os.environ.get('OSMPKL','/tmp/wro/osm.pkl'),'rb'))
        W=d['W'];N=d['N'];G=0.005
        wg={};ng={};n2w={};NC={}
        for wid,(tg,g) in W.items():
            la=[p[1] for p in g];lo=[p[2] for p in g]
            for cy in range(int(min(la)//G),int(max(la)//G)+1):
                for cx in range(int(min(lo)//G),int(max(lo)//G)+1):wg.setdefault((cy,cx),[]).append(wid)
            for nid,a,b in g:n2w.setdefault(nid,[]).append(wid);NC[nid]=(a,b)
        for nid,(a,b,tg) in N.items():ng.setdefault((int(a//G),int(b//G)),[]).append(nid);NC[nid]=(a,b)
        _D=dict(W=W,N=N,G=G,wg=wg,ng=ng,n2w=n2w,NC=NC)
    return _D

TAGF=re.compile(r'''\[\s*(!)?\s*(~)?\s*("(?:[^"\\]|\\.)*"|[A-Za-z0-9_:\-]+)\s*(?:(!=|=|!~|~)\s*("(?:[^"\\]|\\.)*"|[^\],]+?)\s*(,\s*i)?)?\s*\]''')
def unq(s):
    s=s.strip()
    if s.startswith('"'):s=s[1:-1].replace('\\"','"').replace('\\\\','\\')
    return s
def mk_tagf(neg,keyre,k,op,v,ci):
    k=unq(k);v=unq(v) if v is not None else None;fl=re.I if ci else 0
    if keyre:   # [~"kre"~"vre"]
        kr=re.compile(k);vr=re.compile(v,fl)
        return lambda t:any(kr.search(a) and vr.search(b) for a,b in t.items())
    if op is None:
        return (lambda t:k not in t) if neg else (lambda t:k in t)
    if op=='=':return lambda t:t.get(k)==v
    if op=='!=':return lambda t:t.get(k)!=v
    r=re.compile(v,fl)
    if op=='~':return lambda t:k in t and bool(r.search(t[k]))
    if op=='!~':return lambda t:not(k in t and r.search(t[k]))
def dm(a1,o1,a2,o2):
    return math.hypot((a1-a2)*111195,(o1-o2)*111195*math.cos(math.radians(a1)))
def segd(pa,po,a1,o1,a2,o2):
    kx=111195*math.cos(math.radians(pa));ax=(o1-po)*kx;ay=(a1-pa)*111195;bx=(o2-po)*kx;by=(a2-pa)*111195
    dx=bx-ax;dy=by-ay;L=dx*dx+dy*dy;t=0 if L==0 else max(0,min(1,-(ax*dx+ay*dy)/L))
    return math.hypot(ax+dx*t,ay+dy*t)
def seg_in_bb(a1,o1,a2,o2,s,w,n,e):
    if s<=a1<=n and w<=o1<=e:return True
    if s<=a2<=n and w<=o2<=e:return True
    # Liang–Barsky
    t0,t1=0.0,1.0;dx=o2-o1;dy=a2-a1
    for p,q in ((-dx,o1-w),(dx,e-o1),(-dy,a1-s),(dy,n-a1)):
        if p==0:
            if q<0:return False
        else:
            r=q/p
            if p<0:
                if r>t1:return False
                if r>t0:t0=r
            else:
                if r<t0:return False
                if r<t1:t1=r
    return True
class Ctx:
    def __init__(s):s.sets={'_':set()};s.out=[]
def cells_bb(D,s,w,n,e):
    G=D['G'];return [(cy,cx) for cy in range(int(s//G),int(n//G)+1) for cx in range(int(w//G),int(e//G)+1)]
def spatial_candidates(D,typ,sp,ctx):
    """zwraca zbiór kandydatów (typ,id) spełniających filtr przestrzenny"""
    kind,arg=sp
    W=D['W'];N=D['N'];out=set()
    if kind=='bb':
        s,w,n,e=arg
        if typ in('node','nwr'):
            for c in cells_bb(D,s,w,n,e):
                for nid in D['ng'].get(c,()):
                    a,b,_=N[nid]
                    if s<=a<=n and w<=b<=e:out.add(('n',nid))
        if typ in('way','nwr'):
            seen=set()
            for c in cells_bb(D,s,w,n,e):
                for wid in D['wg'].get(c,()):
                    if wid in seen:continue
                    seen.add(wid);g=W[wid][1]
                    if any(seg_in_bb(g[i][1],g[i][2],g[i+1][1],g[i+1][2],s,w,n,e) for i in range(len(g)-1)):out.add(('w',wid))
        return out
    if kind=='around':
        R,pts=arg
        la=[p[0] for p in pts];lo=[p[1] for p in pts];dla=R/111195+1e-4;dlo=R/(111195*math.cos(math.radians(la[0])))+1e-4
        s,w,n,e=min(la)-dla,min(lo)-dlo,max(la)+dla,max(lo)+dlo
        segs=[(pts[i],pts[i+1]) for i in range(len(pts)-1)] or [(pts[0],pts[0])]
        def near(a,b):return any(segd(a,b,p[0],p[1],q[0],q[1])<=R for p,q in segs)
        if typ in('node','nwr'):
            for c in cells_bb(D,s,w,n,e):
                for nid in D['ng'].get(c,()):
                    a,b,_=N[nid]
                    if near(a,b):out.add(('n',nid))
        if typ in('way','nwr'):
            seen=set()
            for c in cells_bb(D,s,w,n,e):
                for wid in D['wg'].get(c,()):
                    if wid in seen:continue
                    seen.add(wid);g=W[wid][1]
                    ok=False
                    for i in range(len(g)-1):
                        # odległość odcinka drogi od punktów/łamanej (przybliżenie: końce i środek odcinka)
                        for t in (0,.25,.5,.75,1):
                            a=g[i][1]+(g[i+1][1]-g[i][1])*t;b=g[i][2]+(g[i+1][2]-g[i][2])*t
                            if near(a,b):ok=True;break
                        if ok:break
                    if ok:out.add(('w',wid))
        return out
    if kind=='bn':   # drogi przechodzące przez węzły ze zbioru
        if typ in('way','nwr'):
            for t,i in ctx.sets.get(arg,set()):
                if t=='n':
                    for wid in D['n2w'].get(i,()):out.add(('w',wid))
        return out
    if kind=='w':    # węzły dróg ze zbioru
        if typ in('node','nwr'):
            for t,i in ctx.sets.get(arg,set()):
                if t=='w':
                    for nid,a,b in W[i][1]:out.add(('n',nid))
        return out
    if kind=='id':
        return {('n' if typ=='node' else 'w',arg)}
    return out
def tags_of(D,el):
    t,i=el
    if t=='n':
        x=D['N'].get(i);return x[2] if x else {}
    return D['W'][i][0]
def parse_query(st):
    """st: tekst zapytania typu 'way["highway"](bb)' itp. Zwraca (typ, sety_przecięcia, filtry_tagów, filtry_przestrzenne)"""
    m=re.match(r'(node|way|nwr|rel|relation)((?:\.[A-Za-z_][A-Za-z0-9_]*)*)',st)
    typ=m.group(1);inter=[x for x in m.group(2).split('.') if x];rest=st[m.end():]
    tf=[];sp=[]
    i=0
    while i<len(rest):
        c=rest[i]
        if c.isspace():i+=1;continue
        if c=='[':
            mm=TAGF.match(rest,i)
            if not mm:raise ValueError('filtr: '+rest[i:i+60])
            tf.append(mk_tagf(*mm.groups()));i=mm.end();continue
        if c=='(':
            j=rest.index(')',i);inner=rest[i+1:j].strip();i=j+1
            if inner.startswith('around:'):
                v=[float(x) for x in inner[7:].split(',')];R=v[0];pts=[(v[k],v[k+1]) for k in range(1,len(v)-1,2)]
                sp.append(('around',(R,pts)))
            elif re.match(r'^(bn|w|r|bw|br)\.',inner):
                k,name=inner.split('.',1);sp.append((k if k in('bn','w') else 'none',name))
            elif re.match(r'^-?\d+$',inner):sp.append(('id',int(inner)))
            else:
                v=[float(x) for x in inner.split(',')];sp.append(('bb',tuple(v)))
            continue
        raise ValueError('nieznane: '+rest[i:i+40])
    return typ,inter,tf,sp
def run_query(D,ctx,st):
    typ,inter,tf,sp=parse_query(st)
    if typ in('rel','relation'):return set()
    if sp:
        cand=None
        for f in sp:
            c=spatial_candidates(D,typ,f,ctx) if f[0]!='none' else set()
            cand=c if cand is None else cand&c
    elif inter:
        cand=None
        for nm in inter:
            c=ctx.sets.get(nm,set());cand=set(c) if cand is None else cand&c
        want={'node':'n','way':'w'}.get(typ)
        if want:cand={e for e in cand if e[0]==want}
    else:
        raise ValueError('zapytanie bez obszaru: '+st)
    if inter and sp:
        for nm in inter:cand&=ctx.sets.get(nm,set())
    return {e for e in cand if all(f(tags_of(D,e)) for f in tf)}
def split_top(body):
    """dzieli tekst na instrukcje na najwyższym poziomie (średniki poza nawiasami i cudzysłowami)"""
    out=[];dep=0;q=False;cur=''
    i=0
    while i<len(body):
        c=body[i]
        if q:
            cur+=c
            if c=='\\':cur+=body[i+1];i+=2;continue
            if c=='"':q=False
        elif c=='"':q=True;cur+=c
        elif c in '([':dep+=1;cur+=c
        elif c in ')]':dep-=1;cur+=c
        elif c==';' and dep==0:
            if cur.strip():out.append(cur.strip())
            cur=''
        else:cur+=c
        i+=1
    if cur.strip():out.append(cur.strip())
    return out
def ev_stmt(D,ctx,st):
    m=re.search(r'->\s*\.([A-Za-z_][A-Za-z0-9_]*)\s*$',st)
    target='_'
    if m:target=m.group(1);st=st[:m.start()].strip()
    if st.startswith('('):
        res=set()
        for sub in split_top(st[1:st.rindex(')')]):
            res|=ev_stmt(D,ctx,sub)
        ctx.sets['_']=res
    elif re.match(r'^\.[A-Za-z_][A-Za-z0-9_]*$',st):
        res=set(ctx.sets.get(st[1:],set()))
    else:
        res=run_query(D,ctx,st)
    ctx.sets[target]=res
    if target!='_':ctx.sets['_']=res
    return res
def fmt(D,el,mode):
    t,i=el
    if t=='n':
        a,b,tg=D['N'].get(i,(None,None,{})) if i in D['N'] else (*D['NC'][i],{})
        o={'type':'node','id':i}
        if 'ids' in mode:return o
        o['lat']=a;o['lon']=b
        if tg:o['tags']=tg
        return o
    tg,g=D['W'][i];o={'type':'way','id':i}
    if 'ids' in mode:return o
    if 'center' in mode:
        la=[p[1] for p in g];lo=[p[2] for p in g];o['center']={'lat':(min(la)+max(la))/2,'lon':(min(lo)+max(lo))/2}
    if 'tags' not in mode:o['nodes']=[p[0] for p in g]
    if 'geom' in mode:
        la=[p[1] for p in g];lo=[p[2] for p in g]
        o['bounds']={'minlat':min(la),'minlon':min(lo),'maxlat':max(la),'maxlon':max(lo)}
        o['geometry']=[{'lat':p[1],'lon':p[2]} for p in g]
    if tg:o['tags']=tg
    return o
def overpass(q):
    D=data();ctx=Ctx();out=[];seen=set()
    for st in split_top(q):
        if st.startswith('[out:') or st.startswith('[timeout') or re.match(r'^\[(out|timeout|maxsize|bbox)',st):continue
        m=re.match(r'^(?:\.([A-Za-z_][A-Za-z0-9_]*)\s+)?out\b(.*)$',st)
        if m:
            setn=m.group(1) or '_';mode=m.group(2)
            lim=re.search(r'\b(\d+)\s*$',mode.strip());lim=int(lim.group(1)) if lim else None
            els=sorted(ctx.sets.get(setn,set()),key=lambda e:(0 if e[0]=='n' else 1,e[1]))
            if lim:els=els[:lim]
            for e in els:out.append(fmt(D,e,mode))
            continue
        ev_stmt(D,ctx,st)
    return {'version':0.6,'generator':'lokalny zamiennik Overpass (testy)','elements':out}
if __name__=='__main__':
    import json,time,sys
    t=time.time()
    q='[out:json][timeout:25];(way["highway"~"^(primary|secondary)$"]["lanes"~"^([3-9]|1[0-9])"](51.10,17.02,51.12,17.05);way["highway"~"^(primary|secondary)$"]["turn:lanes"](51.10,17.02,51.12,17.05););out tags geom qt;'
    r=overpass(q);print('lanes',len(r['elements']),round(time.time()-t,2));t=time.time()
    q='[out:json][timeout:25];node["highway"~"^(stop|give_way)$"](51.10,17.02,51.12,17.05)->.w;(node["highway"~"^(traffic_signals|speed_camera|crossing)$"](51.10,17.02,51.12,17.05);node["traffic_calming"~"^(bump|hump|table|cushion)$"](51.10,17.02,51.12,17.05);)->.o;(.w;.o;)->.s;.s out body;way(bn.w)["highway"];out geom qt;'
    r=overpass(q);print('signs',len(r['elements']),{k:sum(1 for e in r['elements'] if e['type']==k) for k in('node','way')},round(time.time()-t,2));t=time.time()
    q='[out:json][timeout:20];node(around:4000,51.11,17.03)["railway"="level_crossing"];out;'
    r=overpass(q);print('lc',len(r['elements']),round(time.time()-t,2));t=time.time()
    q='[out:json][timeout:8];way(around:22,51.11192,17.06039)[highway][~"^turn:lanes"~"."];out tags geom;'
    r=overpass(q);print('turn',len(r['elements']),[e['tags'].get('turn:lanes') for e in r['elements']][:4],round(time.time()-t,2))
    q='[out:json][timeout:25];way(around:4000,51.11,17.03)["railway"~"^(rail|narrow_gauge|preserved)$"]["service"!~"."][!"bridge"][!"tunnel"]->.r;node(w.r)->.rn;way(bn.rn)["highway"]["highway"!~"^(footway|path|cycleway|steps|pedestrian|bridleway|construction|proposed|corridor|elevator)$"][!"bridge"][!"tunnel"]->.h;node(w.h)->.hn;(node.rn.hn;node(around:4000,51.11,17.03)["railway"="level_crossing"];);out;'
    r=overpass(q);print('x',len(r['elements']),round(time.time()-t,2))
