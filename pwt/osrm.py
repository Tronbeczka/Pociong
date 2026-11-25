# Lokalny zamiennik serwera tras OSRM (testy): najkrótsza czasowo trasa po drogach z wyciągu OSM, kroki w formacie OSRM.
import math,heapq,re,os,pickle
from ovp import data
SPD={'motorway':33,'trunk':25,'primary':15,'secondary':13,'tertiary':11,'unclassified':9,'residential':8,'living_street':4,'service':5,'road':8,
     'motorway_link':18,'trunk_link':14,'primary_link':11,'secondary_link':10,'tertiary_link':9}
_G=None
def dm(a1,o1,a2,o2):return math.hypot((a1-a2)*111195,(o1-o2)*111195*math.cos(math.radians(a1)))
def brg(a1,o1,a2,o2):return (math.degrees(math.atan2((o2-o1)*math.cos(math.radians(a1)),a2-a1))+360)%360
def graph():
    global _G
    if _G:return _G
    D=data();W=D['W'];adj={};NC=D['NC']
    for wid,(tg,g) in W.items():
        hw=tg.get('highway')
        if hw not in SPD:continue
        if tg.get('access') in('no','private') or tg.get('motor_vehicle') in('no','private') or tg.get('area')=='yes':continue
        if hw=='service' and tg.get('service') in('parking_aisle','drive-through','emergency_access'):continue
        ow=tg.get('oneway');rb=tg.get('junction') in('roundabout','circular')
        fwd=True;bwd=not(ow in('yes','1','true') or rb or hw in('motorway',));
        if ow=='-1':fwd,bwd=False,True
        if ow=='no':bwd=True
        sp=SPD[hw]
        for i in range(len(g)-1):
            a=g[i];b=g[i+1];L=dm(a[1],a[2],b[1],b[2])
            if fwd:adj.setdefault(a[0],[]).append((b[0],L,L/sp,wid))
            if bwd:adj.setdefault(b[0],[]).append((a[0],L,L/sp,wid))
    deg={}
    for wid,(tg,g) in W.items():
        if tg.get('highway') in SPD:
            for k,(nid,_,_) in enumerate(g):deg[nid]=deg.get(nid,0)+(1 if k in(0,len(g)-1) else 2)
    # siatka węzłów grafu do szukania najbliższego
    grid={}
    for nid in adj:
        a,b=NC[nid];grid.setdefault((int(a/.002),int(b/.002)),[]).append(nid)
    _G=dict(adj=adj,NC=NC,grid=grid,deg=deg)
    return _G
def nearest(G,la,lo):
    best=None;bd=1e18
    for r in range(0,6):
        for cy in range(int(la/.002)-r,int(la/.002)+r+1):
            for cx in range(int(lo/.002)-r,int(lo/.002)+r+1):
                for nid in G['grid'].get((cy,cx),()):
                    a,b=G['NC'][nid];d=dm(la,lo,a,b)
                    if d<bd:bd=d;best=nid
        if best is not None and r>=1:break
    return best
def route(pts):
    G=graph();W=data()['W'];path=[];edges=[]
    for (la1,lo1),(la2,lo2) in zip(pts,pts[1:]):
        s=nearest(G,la1,lo1);t=nearest(G,la2,lo2)
        dist={s:0};prev={};pq=[(0,s)]
        while pq:
            d,u=heapq.heappop(pq)
            if u==t:break
            if d>dist.get(u,1e18):continue
            for v,L,T,wid in G['adj'].get(u,()):
                nd=d+T
                if nd<dist.get(v,1e18):dist[v]=nd;prev[v]=(u,L,T,wid);heapq.heappush(pq,(nd,v))
        if t not in prev and s!=t:return None
        seq=[];v=t
        while v!=s:u,L,T,wid=prev[v];seq.append((u,v,L,T,wid));v=u
        seq.reverse()
        if not path:path.append(s)
        for e in seq:path.append(e[1]);edges.append(e)
    return path,edges
def name_of(tg):return tg.get('name') or tg.get('ref') or ''
def steps_of(path,edges):
    G=graph();W=data()['W'];NC=G['NC'];steps=[]
    def mod(dt):
        a=(dt+540)%360-180
        if abs(a)<20:return 'straight'
        if a>=150 or a<=-150:return 'uturn'
        s='right' if a>0 else 'left'
        if abs(a)<45:return 'slight '+s
        if abs(a)>120:return 'sharp '+s
        return s
    def pos(n):a,b=NC[n];return [b,a]
    cur={'type':'depart','modifier':'','name':name_of(W[edges[0][4]][0]),'dist':0,'dur':0,'loc':pos(path[0]),'exit':None}
    i=0
    while i<len(edges):
        u,v,L,T,wid=edges[i];tg=W[wid][0]
        cur['dist']+=L;cur['dur']+=T
        if i+1<len(edges):
            u2,v2,L2,T2,wid2=edges[i+1];tg2=W[wid2][0]
            b1=brg(*NC[u],*NC[v]);b2=brg(*NC[u2],*NC[v2])
            rb1=tg.get('junction') in('roundabout','circular');rb2=tg2.get('junction') in('roundabout','circular')
            if rb2 and not rb1:
                # wjazd na rondo: policz zjazdy do wyjazdu
                j=i+1;ex=0;bin_=b1
                while j<len(edges) and W[edges[j][4]][0].get('junction') in('roundabout','circular'):
                    if G['deg'].get(edges[j][1],0)>=3:ex+=1
                    j+=1
                bout=brg(*NC[edges[j][0]],*NC[edges[j][1]]) if j<len(edges) else b2
                steps.append(cur);cur={'type':'roundabout','modifier':mod(bout-bin_),'name':name_of(W[edges[j][4]][0]) if j<len(edges) else '','dist':0,'dur':0,'loc':pos(v),'exit':max(1,ex)}
                # kroki przejazdu po rondzie doliczamy do kroku „rondo”
                for k in range(i+1,j):cur['dist']+=edges[k][2];cur['dur']+=edges[k][3]
                i=j;continue
            dt=b2-b1;m=mod(dt);n1=name_of(tg);n2=name_of(tg2)
            if (m!='straight' and G['deg'].get(v,0)>=3) or (n1!=n2 and G['deg'].get(v,0)>=3 and m not in('straight',)):
                steps.append(cur);cur={'type':'turn' if n1!=n2 or m!='straight' else 'continue','modifier':m,'name':n2,'dist':0,'dur':0,'loc':pos(v),'exit':None}
            elif n1!=n2 and G['deg'].get(v,0)>=3:
                steps.append(cur);cur={'type':'new name','modifier':'straight','name':n2,'dist':0,'dur':0,'loc':pos(v),'exit':None}
        i+=1
    steps.append(cur);steps.append({'type':'arrive','modifier':'','name':'','dist':0,'dur':0,'loc':pos(path[-1]),'exit':None})
    out=[]
    for s in steps:
        m={'type':s['type'],'location':s['loc']}
        if s['modifier']:m['modifier']=s['modifier']
        if s['exit']:m['exit']=s['exit']
        out.append({'maneuver':m,'name':s['name'],'distance':round(s['dist'],1),'duration':round(s['dur'],1)})
    return out
def osrm(url):
    m=re.search(r'/route/v1/driving/([^?]+)',url)
    pts=[(float(b),float(a)) for a,b in (x.split(',') for x in m.group(1).split(';'))]
    r=route(pts)
    if not r:return {'code':'NoRoute','routes':[]}
    path,edges=r;NC=graph()['NC']
    coords=[[NC[n][1],NC[n][0]] for n in path]
    dist=sum(e[2] for e in edges);dur=sum(e[3] for e in edges)
    st=steps_of(path,edges)
    return {'code':'Ok','routes':[{'geometry':{'type':'LineString','coordinates':coords},'distance':round(dist,1),'duration':round(dur,1),
        'legs':[{'steps':st,'distance':round(dist,1),'duration':round(dur,1)}]}],'waypoints':[]}
if __name__=='__main__':
    import time,json;t=time.time()
    j=osrm('https://router.project-osrm.org/route/v1/driving/17.0385,51.1079;17.0600,51.1180?overview=full&geometries=geojson&steps=true')
    r=j['routes'][0];print(round(time.time()-t,1),'s',round(r['distance']),'m',len(r['geometry']['coordinates']),'pkt')
    for s in r['legs'][0]['steps']:print(' ',s['maneuver']['type'],s['maneuver'].get('modifier',''),s['maneuver'].get('exit',''),s['name'],s['distance'])
