"""Usage: python3 name_print.py NAME [out.png]  -> 4500x5400 transparent Santa-hat name print file."""
import sys, os
from PIL import Image, ImageDraw, ImageFont
HERE=os.path.dirname(os.path.abspath(__file__))
FONT=os.path.join(HERE,'fonts/fontsource-dancing-script-5.3.0/files/dancing-script-latin-700-normal.woff')
def make(name):
    hat=Image.open(os.path.join(HERE,'hat_cut.png'))
    W,H=4500,5400; c=Image.new('RGBA',(W,H),(0,0,0,0))
    size=1100
    while True:
        f=ImageFont.truetype(FONT,size); bb=f.getbbox(name)
        if bb[2]-bb[0]<=4100 or size<500: break
        size-=50
    tw,th=bb[2]-bb[0],bb[3]-bb[1]
    ty=150+int(hat.height*0.95)
    tx=(W-tw)//2-bb[0]
    d=ImageDraw.Draw(c); d.text((tx,ty-bb[1]),name,font=f,fill=(255,255,255,255))
    hx=max(100,(W-tw)//2-250); c.alpha_composite(hat,(hx,150))
    return c.crop((0,0,W,H))
if __name__=='__main__':
    n=sys.argv[1]; out=sys.argv[2] if len(sys.argv)>2 else f'name_{n}.png'
    make(n).save(out); print(out)
