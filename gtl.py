from googletrans import Translator
import os
import sys
import csv
import pickle
from io import StringIO
# coding: utf8

subst=[
    "[P]",
    "[P姓]",
    "[P名]",
    "[P名前]",
    "[Pあだ名]",
    "[H]",
    "[H姓]",
    "[H名]",
    "[H名前]",
    "[Hあだ名]"
]

limit=2000
pad=10

keys=[]
lines=[]
comments=[]

tr=Translator()

trcache={}
try:
    trcache=pickle.load(open('cache.p','rb'))
except:
    pass

def flush():
    if len(lines) == 0: return

    totri=[]
    totr=[]
    flines={}
    for i in range(0,len(lines)):
        if lines[i] in trcache:
            flines[i] = trcache[lines[i]]
        else:
            totri.append(i)
            totr.append(lines[i].replace("\r","").replace("\n","THENEWLINE"))

    if len(totr)>0:
        line="\n".join(totr)

        for i in range(0,len(subst)):
            line = line.replace(subst[i], "SUBST%s" % chr(ord('A')+i))
        trline = tr.translate(line,src="ja",dest="en").text
        for i in range(0,len(subst)):
            trline = trline.replace("SUBST%s" % chr(ord('A')+i), subst[i])

        trlines = trline.split("\n")
        assert(len(trlines) == len(totr))

        for i in range(0,len(totri)):
            flines[totri[i]] = trlines[i].replace("THENEWLINE","\n")

    for i in range(0,len(lines)):
        trcache[lines[i]]=flines[i]
        outf.writerow([keys[i],lines[i],flines[i],comments[i]])
    pickle.dump(trcache, open("cache.p_","wb"))
    try:
        os.remove("cache.p")
    except:
        pass
    os.rename("cache.p_","cache.p")
    del keys[:]
    del lines[:]
    del comments[:]

suff=""
for root, dir, files in os.walk(sys.argv[1]):
    for f in files:
        if not f.endswith('csv'): continue
        inbuf=open(root +"/"+ f,"r",encoding='utf8').read()
        outf=csv.writer(open(root +"/"+ f + suff,"w",encoding='utf8'))
        llen=0
        for row in csv.reader(StringIO(inbuf),delimiter=",",quotechar='"'):
            if row[0] == "key":
                outf.writerow(["key","jp","en","comment"])
                continue
            llen += len(row[1]) + pad
            keys.append(row[0])
            lines.append(row[1].replace('♪',''))
            comments.append(row[3])
            if llen > limit:
                flush()
                llen=0
        flush()
        print(f)
        sys.stdout.flush()


