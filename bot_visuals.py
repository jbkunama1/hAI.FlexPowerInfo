import struct,zlib

def chart_png(rows):
    rows=rows[:96]
    if not rows:raise ValueError('Keine Preisintervalle')
    w,h=800,300;left,right,top,bottom=35,785,20,275
    values=[float(x['price']['gross_ct']) for x in rows]
    lo=min(0,min(values));hi=max(0,max(values))
    if hi==lo:hi=lo+1
    span=hi-lo;lo-=span*.08;hi+=span*.08
    pixels=bytearray(bytes((15,23,42))*(w*h))
    def rect(x0,y0,x1,y1,color):
        for y in range(max(0,y0),min(h,y1)):
            a=(y*w+max(0,x0))*3;b=(y*w+min(w,x1))*3
            if b>a:pixels[a:b]=bytes(color)*((b-a)//3)
    def ypos(v):return round(bottom-(v-lo)/(hi-lo)*(bottom-top))
    for i in range(5):
        y=top+round((bottom-top)*i/4);rect(left,y,right,y+1,(45,60,82))
    zero=ypos(0);rect(left,zero,right,zero+2,(210,220,235))
    start=rows[0]['start'];end=max(x['end'] for x in rows);duration=max(1,end-start)
    for x,v in zip(rows,values):
        a=left+round((x['start']-start)/duration*(right-left));b=left+round((x['end']-start)/duration*(right-left))
        y=ypos(v);rect(a,min(y,zero),max(a+1,b-1),max(y,zero)+1,(96,221,181) if v>=0 else (187,135,250))
    raw=b''.join(b'\0'+pixels[y*w*3:(y+1)*w*3] for y in range(h))
    def chunk(t,d):return struct.pack('!I',len(d))+t+d+struct.pack('!I',zlib.crc32(t+d)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')
