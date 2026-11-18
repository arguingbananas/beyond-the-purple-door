import sys
src, ips, out = sys.argv[1:4]
img = bytearray(open(src,"rb").read()); p = open(ips,"rb").read()
assert p[:5]==b"PATCH"; i=5
while p[i:i+3]!=b"EOF":
    off=int.from_bytes(p[i:i+3],"big"); n=int.from_bytes(p[i+3:i+5],"big"); i+=5
    if n==0:
        r=int.from_bytes(p[i:i+2],"big"); b=p[i+2:i+3]; i+=3; img[off:off+r]=b*r
    else:
        img[off:off+n]=p[i:i+n]; i+=n
open(out,"wb").write(img)
