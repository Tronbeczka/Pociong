# zestawienie zrzutów: python3 sheet.py out.png W rzędy... gdzie rząd = lista plików oddzielonych przecinkami
import sys
from PIL import Image,ImageDraw
out=sys.argv[1];W=int(sys.argv[2]);rows=[r.split(',') for r in sys.argv[3:]]
ims=[[Image.open(f).convert('RGB') if f!='-' else None for f in r] for r in rows]
def sz(im):return (W,int(im.height*W/im.width))
Hs=[max(sz(i)[1] for i in r if i) for r in ims]
S=Image.new('RGB',(max(len(r) for r in ims)*(W+6),sum(Hs)+6*len(Hs)),'white')
y=0
for r,hh,fr in zip(ims,Hs,rows):
    for k,(im,f) in enumerate(zip(r,fr)):
        if im:S.paste(im.resize(sz(im)),(k*(W+6),y));ImageDraw.Draw(S).text((k*(W+6)+4,y+4),f.split('/')[-1][:40],fill=(255,0,0))
    y+=hh+6
S.save(out)
