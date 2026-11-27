# Wersja 200: nowy moduł jezdni (szerokość jak zwykła droga z mapy, pasy dzielą ją między siebie) – podmiana modułu z wersji 199
src='/tmp/app/v199.html';dst='/tmp/app/v200.html'
s=open(src).read()
a=s.index('// ================= Wersja 199: jezdnie z pasami od nowa');b=s.index('// ---- plan pasa dla trasy ----',a)
jz=open('/tmp/jz/jz.js').read()
s=s[:a]+jz.rstrip('\n')+'\n'+s[b:]
assert s.count('<span id="ver">wersja 199<')==1
s=s.replace('<span id="ver">wersja 199<','<span id="ver">wersja 200<')
open(dst,'w').write(s);print('zapisano',dst,len(s))
