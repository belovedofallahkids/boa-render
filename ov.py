from PIL import Image, ImageDraw, ImageFont
F='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; FA='/home/claude/boa-render/assets/fonts/NotoKufiArabic.ttf'
T={'de':('Wer hat die Götzen','zerbrochen?','Prophet Ibrahim (Abraham)','ltr',F),
   'ar':('مَن كسّر التماثيل؟','','قصة النبي إبراهيم عليه السلام','rtl',FA),
   'en':('Who Broke','the Idols?','Prophet Abraham','ltr',F),
   'fr':('Qui a brisé','les idoles ?','Le prophète Abraham','ltr',F)}
for k,(a,a2,b,d,ff) in T.items():
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); dr=ImageDraw.Draw(im)
    sz0=84 if k=='de' else 96
    rows=[(170,a,sz0,(255,214,90,255))]+([(285,a2,sz0,(255,214,90,255))] if a2 else [])+[(1330,b,60,(255,255,255,255))]
    for y,txt,sz,col in rows:
        f=ImageFont.truetype(ff,sz)
        w=dr.textlength(txt,font=f,direction=d) if d=='rtl' else dr.textlength(txt,font=f)
        kw={'direction':d} if d=='rtl' else {}
        dr.text(((1080-w)/2,y),txt,font=f,fill=col,stroke_width=8,stroke_fill=(20,20,60,255),**kw)
    f=ImageFont.truetype(F,44); txt='@BelovedOfAllahKids'; w=dr.textlength(txt,font=f)
    dr.rounded_rectangle(((1080-w)/2-30,1700,(1080+w)/2+30,1780),radius=40,fill=(20,20,60,170))
    dr.text(((1080-w)/2,1712),txt,font=f,fill=(255,255,255,255))
    im.save(f'ov_{k}.png')
