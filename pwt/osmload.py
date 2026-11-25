# Wczytuje wyciąg OSM (pbf) do prostych struktur: drogi/tory (tagi + węzły + geometria) i węzły z tagami. Wynik w pickle.
import osmium,pickle,sys
SRC=sys.argv[1];DST=sys.argv[2]
NODE_KEYS={'highway','railway','traffic_calming','enforcement','traffic_sign','crossing','barrier','amenity','traffic_signals'}
class H(osmium.SimpleHandler):
    def __init__(s):super().__init__();s.W={};s.N={}
    def node(s,n):
        if any(k in NODE_KEYS for k in (t.k for t in n.tags)):
            s.N[n.id]=(n.location.lat,n.location.lon,{t.k:t.v for t in n.tags})
    def way(s,w):
        tg={t.k:t.v for t in w.tags}
        if 'highway' in tg or tg.get('railway') in ('rail','tram','light_rail','narrow_gauge','preserved','subway'):
            try:
                g=[(nd.ref,nd.location.lat,nd.location.lon) for nd in w.nodes]
            except osmium.InvalidLocationError:
                g=[(nd.ref,nd.location.lat,nd.location.lon) for nd in w.nodes if nd.location.valid()]
            if len(g)>=2:s.W[w.id]=(tg,g)
h=H();h.apply_file(SRC,locations=True)
pickle.dump({'W':h.W,'N':h.N},open(DST,'wb'),protocol=5)
print('ways',len(h.W),'nodes',len(h.N))
