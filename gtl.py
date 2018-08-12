# coding: utf8
from googletrans import Translator
import os
import sys
import csv
import pickle
from io import StringIO

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

# input: [(key,line),(key,line)...]
# ouput: [(key,line,en),(key,line,en)...]
def trans(db):
    lines=[]
    keys=[]
    res=[]
    def flush():
        if len(lines) == 0: return
        totri=[]
        totr=[]
        flines={}
        for i in range(0,len(lines)):
            if lines[i] in trcache:
                flines[i] = trcache[lines[i]].replace('\n',' ')
            else:
                totri.append(i)
                totr.append(lines[i].replace("\r","").replace("\n"," "))

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
                flines[totri[i]] = trlines[i]

        for i in range(0,len(lines)):
            trcache[lines[i]]=flines[i]
            res.append([keys[i],lines[i],flines[i]])

        if len(totr)>0:
            pickle.dump(trcache, open("cache.p_","wb"))
            try:
                os.remove("cache.p")
            except:
                pass
            os.rename("cache.p_","cache.p")
        del lines[:]
        del keys[:]
    llen=0
    for item in db:
        keys.append(item[0])
        lines.append(item[1])
        llen += len(item[1]) + pad
        if llen > limit:
            flush()
            llen=0
    flush()
    return res
