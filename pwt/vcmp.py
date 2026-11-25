# Porównanie dwóch katalogów zrzutów: odsetek zmienionych pikseli i obraz różnic (stary | nowy | różnice)
import sys,os
from PIL import Image,ImageChops
A,B,OUT=sys.argv[1],sys.argv[2],sys.argv[3];os.makedirs(OUT,exist_ok=True)
TH=int(os.environ.get('TH','24'))
for f in sorted(os.listdir(A)):
    if not f.endswith('.png') or not os.path.exists(os.path.join(B,f)):continue
    a=Image.open(os.path.join(A,f)).convert('RGB');b=Image.open(os.path.join(B,f)).convert('RGB')
    d=ImageChops.difference(a,b).convert('L').point(lambda v:255 if v>TH else 0)
    n=d.histogram()[255];pct=100*n/(a.width*a.height)
    print(f'{f:14s} {pct:6.2f}%')
    if pct>.05:
        W=a.width//2;Hh=a.height//2
        m=Image.new('RGB',(W*3+12,Hh),'white')
        m.paste(a.resize((W,Hh)),(0,0));m.paste(b.resize((W,Hh)),(W+6,0))
        red=Image.new('RGB',a.size,(255,0,0));base=Image.blend(b,Image.new('RGB',b.size,'white'),.6);base.paste(red,(0,0),d)
        m.paste(base.resize((W,Hh)),(2*W+12,0));m.save(os.path.join(OUT,f))
