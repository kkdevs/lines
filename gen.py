import csv
import sys
import os
import pickle
target = sys.argv[1]
def tran(key,line,comment=""):
    return [key,line,"TRANSLATEME",comment]

def walk(path, mask):
    for root, dir, files in os.walk(path):
        for f in files:
            if f.startswith(mask):
                if f.endswith("csv"):
                   yield root,f, csv.reader(open(root +"/"+ f,"r",encoding='utf8'),delimiter=",",quotechar='"')
                elif f.endswith("lst"):
                   yield root,f, csv.reader(open(root +"/"+ f,"r",encoding='utf8'),delimiter="\t")

def make_hlines():
    blen=23
    count=4
    skip=3
    db={}

    for _,_, data in walk("!base/h/list", "personality_voice_"):
        for row in data:
            for i in range(0,blen*count,blen):
                voice,line=row[i+skip], row[i+skip+1]
                if voice != "" and voice != "0" and line != "" and line != "0":
                    parts = voice.split('_')
                    pers = parts[2]
                    if not pers in db:
                        db[pers] = {}
                    db[pers][voice]=line
    try:
        os.makedirs(target+"/h")
    except:
        pass
    for pers,voices in db.items():
        f=open(target+"/h/"+pers+".csv",'w',newline='',encoding='utf8')
        outf=csv.writer(f)
        outf.writerow(['key','jp','en','comment'])
        for voice in sorted(voices):
            outf.writerow(tran(voice,voices[voice]))
        f.close()

def make_talklines():
    climit=7
    try:
        os.makedirs(target+"/talk")
    except:
        pass
    prev = None
    db={}
    common={}
    linekey={}
#    mc=set()
    for _,_, data in walk("!base/communication", "communication_"):
        for row in data:
            if len(row) < 16: continue
            lid = row[1]
            cond = row[9]
            ab = row[13]
            ass = row[14]
            line = row[15]
            if ab.endswith('.unity3d'):
                if not ass.startswith("com"): continue
                pers = ass.split('_')[2]
                if pers not in db:
                    db[pers]={}
                db[pers][ass] = line
                continue
            if cond == "": continue
            if ab == "" and line != "" and int(cond) > 0:
                if not line in common:
                    common[line] = set()
                common[line].add(pers)
                db[pers]["talk%03d/%02d"%(int(cond),int(pers))] = line
                linekey[line]="talk%03d"%int(cond)


    for pers,voices in db.items():
        f=open(target+"/talk/"+pers+".csv",'w',newline='',encoding='utf8')
        outf=csv.writer(f)
        outf.writerow(['key','jp','en','comment'])
        for voice in sorted(voices):
            line=voices[voice]
            #if (line in common) and (len(common[line])>climit): continue
            outf.writerow(tran(voice.split(',')[0],line))
        f.close()

    if False:
        outf=csv.writer(open(target+"/talk/common.csv",'w',newline='',encoding='utf8'))
        rt=[]
        for line in common:
            if len(common[line]) <= climit: continue
            rt.append(tran(linekey[line],line))
        outf.writerow(['key','jp','en','comment'])
        for r in sorted(rt):
            outf.writerow(r)

def make_adv():
    try:
        os.makedirs(target+"/adv")
    except:
        pass
    prev=None
    fout=None
    for dname, fn, data in walk("!base/adv/scenario", ""):
        scdir=dname.split('/')[-2]
        if scdir != prev:
            outf=csv.writer(open(target+"/adv/"+scdir+".csv",'w',newline='',encoding='utf8'))
            outf.writerow(['key','jp','en','comment'])
            prev=scdir
        header=None
        for row in data:
            if not header:
                header=list(row)
                continue
            dr={}
            for i in range(0,len(row)):
                if i==len(header):
                    dr[header[-1]] = [dr[header[-1]]]
                if i>=len(header):
                    dr[header[-1]].append(row[i])
                else:
                    dr[header[i]] = row[i]
            if not '_args' in dr:
                continue
            _cmd = dr['_command']
            _h = dr['_hash']
            _args = dr['_args']
            if _cmd == "Voice":
                currvoice = _args[-1]
            elif _cmd == "Text":
                outf.writerow(tran(_h,_args[-1],"%s %s" % (_args[-2],currvoice)))


make_hlines()
make_talklines()
make_adv()

