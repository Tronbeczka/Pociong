# Wersja 208: komunikat o znaku / przejściu dla pieszych / fotoradarze mieści się w okienku (zawijanie tekstu, szersze okienko)
import sys
src,dst=sys.argv[1],sys.argv[2]
s=open(src).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:80]);s=s.replace(a,b)
rep("""</style>""","""/* Wersja 208: komunikat o znaku przy drodze (przejście dla pieszych, STOP, fotoradar…) mieści się w okienku. Dotąd tekst był w jednej linii (bez zawijania)
   w okienku o szerokości ekranu minus 140 px – na węższych telefonach „przejście dla pieszych”, „ustąp pierwszeństwa”, a „odcinkowy pomiar prędkości” wszędzie
   wychodziły poza okienko i pod przyciski z prawej. Teraz okienko zajmuje miejsce od lewego brzegu do kolumny przycisków (wyśrodkowane w nim), a długi tekst
   zawija się w dwie wyrównane linie (okienko z zaokrąglonymi rogami zamiast „pigułki”). */
#sig{left:10px;right:68px;margin:0 auto;width:max-content;max-width:calc(100% - 78px);transform:translateY(-8px);white-space:normal;border-radius:22px}
#sig.on{transform:translateY(0)}
#sigt{min-width:0;line-height:1.22;text-wrap:balance}
</style>""",1)
rep('<span id="ver">wersja 207<','<span id="ver">wersja 208<')
open(dst,'w').write(s);print('zapisano',dst)
