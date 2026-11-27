# Wersja 207: strzałki kierunków na jezdni (moduł /tmp/ll/ll.js podmieniany w wersji 206)
import sys
src,dst=sys.argv[1],sys.argv[2]
s=open(src).read();LLJS=open('/tmp/ll/ll.js').read()
a=s.index('// ================= Wersja 206: linie pasów na jezdni');b=s.index("{const e=$('laneCb');if(e){e.checked=llOn;")
assert a<b and b-a<60000,(a,b)
s=s[:a]+LLJS+s[b:]
assert s.count('<span id="ver">wersja 206<')==1
s=s.replace('<span id="ver">wersja 206<','<span id="ver">wersja 207<')
open(dst,'w').write(s);print('zapisano',dst)
