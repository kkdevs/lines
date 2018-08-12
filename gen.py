import csv
import sys
import os
import pickle
import gtl
def wrow(f,row):
    if len(row)==2:
        row = [""] + row
    def quot(v):
        nv = v.replace('"','""')
        if (nv != v) or (',' in v) or ("\n" in v):
            nv = '"' + nv + '"'
        return nv
    f.write("%s,%s,%s\n" % (row[0], quot(row[1]), quot(row[2])))
target = sys.argv[1]
def tran(key,line,comment=""):
    return [key,line,"TRANSLATEME",comment]


def dictreader(data):
    header=None
    rowidx=0
    for row in data:
        if not header:
            header=list(row)
            continue
        rowidx+=1
        dr={}
        for i in range(0,len(row)):
            if i==len(header):
                dr[header[-1]] = [dr[header[-1]]]
            if i>=len(header):
                dr[header[-1]].append(row[i])
            else:
                dr[header[i]] = row[i]
        dr['rowidx'] = rowidx
        yield dr

def walk(path, mask, asdict=False):
    for root, dir, files in os.walk(path):
        for f in files:
            if f.startswith(mask):
                if f.endswith("csv"):
                    c=csv.reader(open(root +"/"+ f,"r",encoding='utf8'),delimiter=",",quotechar='"')
                    yield root,f,asdict and dictreader(c) or c
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
                    db[pers][voice]=line.replace("\r","").replace("\n"," ").strip()
    try:
        os.makedirs(target+"/h")
    except:
        pass
    for pers,voices in db.items():
        #print(pers)
        sys.stdout.flush()
        f=open(target+"/h/"+pers+".csv",'w',encoding='utf8')
        for line in gtl.trans(sorted(voices.items())):
            wrow(f,line)
            #f.write("%s|%s=%s\n" %(line[0],line[1],line[2]))
        f.close()

def make_talklines():
    climit=999
    try:
        os.makedirs(target+"/talk")
    except:
        pass
    prev = None
    db={}
    linekey={}
#    mc=set()
    db={}
    lines=set()
    for _,fn, data in walk("!base/communication", "communication_"):
        fn=fn.split('.')[0].split('_')[-1]
        idx=0
        db[fn]={}
        for row in data:
            idx+=1
            if idx < 9: continue
            if len(row) < 16: continue
            lid = row[1]
            cond = row[9]
            ab = row[13]
            ass = row[14]
            line = row[15]
            if line == "": continue
            line = line.replace("\r","").replace("\n", " ").strip()
            lines.add(line)
            db[fn][idx] = line

    comm=None
    if climit != 999:
        comm=open(target+"/talk/common.csv",'w',encoding='utf8')
    commd=set()
    counts={}

    for fn, lines in db.items():
        for idx,line in lines.items():
            #print(fn,idx,line)
            if not line in counts:
                counts[line] = 0
            counts[line] += 1

    for fn, lines in db.items():
        f=open(target+"/talk/"+fn+".csv",'w',encoding='utf8')
        tdb=gtl.trans(sorted(lines.items()))
        #print(len(tdb),len(lines))
        for item in tdb:
            if counts[item[1]] < climit:
                item[0] = ':'+str(item[0])
                #f.write("%s|%s=%s\n"%(item[0],item[1],item[2]))
                wrow(f,item)
            elif item[1] not in commd:
                wrow(comm,item[1:])
                #comm.write("%s=%s\n"%(item[1],item[2]))
                commd.add(item[1])
        f.close()
    if comm:
        comm.close()

def make_adv():
    try:
        os.makedirs(target+"/adv")
    except:
        pass
    prev=None
    fout=None
    db={}
    for dname, fn, data in walk("!base/adv/scenario", "", True):
        scdir=dname.split('/')[-2]
        scid=fn.split('.')[0]
        if not scdir in db:
            db[scdir]={}
        for dr in data:
            if not '_args' in dr:
                continue
            _cmd = dr['_command']
            _h = dr['_hash']
            _args = dr['_args']
            if _cmd == "Text":
                ll=_args[-1].replace("\r","").replace("\n", " ").strip()
                if ll == "………………": continue
                if ll == "…………": continue
                if ll == "……": continue
                db[scdir]["%s:%03d"%(scid,dr['rowidx'])] = ll
    counts={}
    for pers in db:
        tl=gtl.trans(sorted(db[pers].items()))
        for row in tl:
            ln=row[1]
            if not ln in counts:
                counts[ln]=0
            counts[ln]+=1
        db[pers]=tl
    climit=999
    if climit != 999:
        comm=open(target+"/adv/common.csv",'w',encoding='utf8')

    for pers in db:
        f=open(target+"/adv/"+pers+".csv",'w',encoding='utf8')
        for row in db[pers]:
            ln=row[1]
            if counts[ln] < climit: 
                if counts[ln] != -1:
                    wrow(f,row)
                    #f.write("%s|%s=%s\n"%tuple(row))
            else:
                #comm.write("%s=%s\n"%(row[1],row[2]))
                wrow(comm,row[1:])
                counts[ln]=-1
        f.close()


def make_generic(outfn,indir,inpfx,jprow,keyrow,skip=True):
    db=[]
    known=set()
    for _,fn, data in walk("!base/"+indir, inpfx):
        skipped=False
        for row in data:
            if skip and (not skipped):
                if row[0] == "": continue
                skipped=True
                continue
            if jprow >= len(row) or (keyrow >= len(row) and keyrow != -1): continue
            jp=row[jprow].replace("\r","").replace("\n", " ").strip()
            key=row[keyrow]
            if jp=="": continue
            if key in known: continue
            known.add(key)
            db.append([key,jp])

    transdb(db,outfn)

def transdb(db,outfn):
    ofn=target+"/"+outfn+".csv"
    try:
        os.makedirs(os.path.dirname(ofn))
    except:
        pass
    f=open(ofn,'w',encoding='utf8')
    for line in gtl.trans(db):
        wrow(f,line)
    f.close()

def make_characustom():
    db=[]
    for _,fn, data in walk("!base/list/characustom", "", True):
        cat = fn.split("_")[0]
        for row in data:
            if 'Name' in row:
                db.append([cat + '+' + row['ID'], row['Name']])
    transdb(db, "cat/characustom")

make_hlines()
make_talklines()
make_adv()

make_characustom()

make_generic("cat/map","map/list/mapinfo","",0,3)
make_generic("cat/itemlist","studio","itemlist_",3,6)
make_generic("cat/voicegroup","studio","voicegroup_",1,0)
make_generic("cat/itemgroup","studio","itemgroup_",1,0)
make_generic("cat/itemcategory","studio","itemcategory_",1,0)
make_generic("cat/voicecategory","studio","voicecategory_",1,0)
make_generic("cat/filter","studio","filter_",1,3)
make_generic("cat/bone","studio","bone_",2,1)
make_generic("cat/bgm","studio","bgm_",1,3)
make_generic("cat/animegroup","studio","animegroup_",1,0)
make_generic("cat/animecategory","studio","animecategory_",1,0)
make_generic("cat/accessorypointgroup","studio","accessorypointgroup_",1,0)
make_generic("cat/accessorypoint","studio","accessorypoint_",3,2)
make_generic("cat/anime","studio","anime_",3,6)
make_generic("cat/hanime","studio","hanime_",3,8)
make_generic("cat/animationinfo","h/list","animationinfo_",0,1)

