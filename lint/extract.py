import re,sys
s=open(sys.argv[1]).read()
scs=re.findall(r'<script(?![^>]*src)[^>]*>(.*?)</script>',s,re.S)
open(sys.argv[2],'w').write('\n;\n'.join(scs))
