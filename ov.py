from PIL import Image, ImageDraw, ImageFont
F='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
T={'de':('Das Meer teilt sich!','Prophet Musa (Mose)','ltr'),
   'ar':('البحر ينشقّ!','قصة النبي موسى عليه السلام','rtl'),
   'en':('The Sea Splits!','Prophet Moses','ltr'),
   'fr':("La mer s'ouvre !",'Le prophète Moïse','ltr')}
for k,(a,b,d) in T.items():
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); dr=ImageDraw.Draw(im)
    for y,txt,sz,col in [(150,a,92,(255,214,90,255)),(270,b,58,(255,255,255,255))]:
        f=ImageFont.truetype(F,sz)
        w=dr.textlength(txt,font=f,direction=d)
        dr.text(((1080-w)/2,y),txt,font=f,fill=col,stroke_width=8,stroke_fill=(20,20,60,255),direction=d)
    f=ImageFont.truetype(F,44); txt='@BelovedOfAllahKids'
    w=dr.textlength(txt,font=f)
    dr.rounded_rectangle(((1080-w)/2-30,1700,(1080+w)/2+30,1780),radius=40,fill=(20,20,60,170))
    dr.text(((1080-w)/2,1712),txt,font=f,fill=(255,255,255,255))
    im.save(f'ov_{k}.png')
