# Wersja 201: z bliska drogi w proporcjach bliższych prawdziwym (szerokość ×2,4 tylko przy oddaleniu) – skrzyżowania i drogi dwujezdniowe nie zlewają się w jedną plamę
src='/tmp/app/v200.html';dst='/tmp/app/v201.html'
s=open(src).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:80]);s=s.replace(a,b)
rep("""const rw=(k,s)=>Math.max(VC[k].w,VC[k].m*s*2.4)*dmK;   // z bliska drogi są szerokie na tyle, by auto mieściło się na pasie""",
"""// Wersja 201: drogi z mapy są szersze niż w rzeczywistości (czytelność z daleka i przy jeździe), ale przy dużym zbliżeniu (postój, powolna jazda,
// ręczne przybliżenie) mnożnik ×2,4 sprawiał, że jezdnie drogi dwujezdniowej, łącznice i wloty skrzyżowania zlewały się w jedną żółtą plamę
// (np. pl. Powstańców Warszawy przy moście Grunwaldzkim – przejścia, torowiska i wysepki „w środku jezdni”). Teraz mnożnik maleje łagodnie
// ze zbliżeniem: do 1,2 px/m bez zmian (2,4), przy jeździe po mieście (2 px/m) ok. 1,9, na postoju (2,8 px/m) ok. 1,55, z bliska (≥ 4,6 px/m) 1,05.
// Szerokość w pikselach i tak rośnie przy zbliżaniu (mnożnik maleje wolniej, niż rośnie skala).
const rwF=s=>s<=1.2?2.4:Math.max(1.05,2.4-Math.log(s/1.2));
const rw=(k,s)=>Math.max(VC[k].w,VC[k].m*s*rwF(s))*dmK;""")
rep('<span id="ver">wersja 200<','<span id="ver">wersja 201<')
open(dst,'w').write(s);print('zapisano',dst,len(s))
