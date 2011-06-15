import matplotlib
matplotlib.use("Agg") #if run out of ipython do not show any graph
#from procedures import *
from database import *
from multiprocessing import Pool
import util
import pyrHOG2
import VOCpr
import time
#import trainINRIA
import itertools

class config(object):
    pass

def detectWrap(a):
    t=time.time()
    i=a[0]
    imname=a[1]
    bbox=a[2]
    m=a[3]
    cfg=a[4]
    if cfg.show:
        img=util.myimread(imname)
        pylab.figure(10)
        pylab.ioff()
        pylab.clf()
        pylab.axis("off")
        pylab.imshow(img,interpolation="nearest",animated=True) 
    if bbox!=None:
        gtbbox=[{"bbox":x} for x in bbox]   
    else:
        gtbbox=None
    f=pyrHOG2.pyrHOG(imname,interv=10,savedir=cfg.savedir+"/hog/",notload=not(cfg.loadfeat),notsave=not(cfg.savefeat),hallucinate=cfg.hallucinate,cformat=True)
    res=pyrHOG2.detect(f,m,gtbbox,hallucinate=cfg.hallucinate,initr=cfg.initr,ratio=cfg.ratio,deform=cfg.deform,posovr=cfg.posovr,bottomup=cfg.bottomup,usemrf=cfg.usemrf,numneg=cfg.numneg,thr=cfg.thr,inclusion=cfg.inclusion,small=cfg.small,show=cfg.show,usefather=cfg.usefather,useprior=cfg.useprior,nms=cfg.ovr,K=cfg.k)
    if cfg.show:
        pylab.draw()
        pylab.show()
        #raw_input()
    print "Detect Wrap:",time.time()-t
    return res

#cfg.fy=7
#cfg.fx=3
#cfg.lev=3
#cfg.interv=10
#cfg.ovr=0.5
#cfg.sbin=8
#cfg.maxpos=1000#120
#cfg.maxneg=1000#120
#deform=True
#usemrf=True
#initr=1
#ratio=2
#cfg.hallucinate=1
#show=True
#it=6
#sx=0.05 #reduce x dimension of
#testname="./data/test28_10/simpletest"
#testname="./data/test28_10/withoutneg"
#testname="./data/test28_10/hall1"
#testname="./data/test29_10/defnoFatherCache"
#testname="./data/test30_10/highres"
#testname="./data/test30_10/4partsfull"
#testname="./data/test1_8/testfull1000"
#testname="./data/test1_8/fullnodef";it=7
#testname="./data/test2_8/nopneginpos"
#testname="./data/test3_8/Full";it=6
#testname="./data/test11_10/test";it=7
#testname="./data/test3_11/CVPR11";it=5
#testname="./data/test3_11/CVPR11_fullneg";it=7
#testname="./data/test3_11/CVPR11_usefahter";it=9# 93!!!
#testname="./data/test3_11/CVPR11_usefahter";it=6
#testname="./data/INRIA/testTDnoMRFright";it=9
#testname="./data/CVPR/bottomup";it=9
#testname="./data/11_03_16/inria_converg";it=8
testname="./data/INRIA/inria_bothfull";it=6
import sys
if len(sys.argv)>1:
    it=int(sys.argv[1])
#testname="./data/INRIA/testTDnoMRF";it=6
cfg=util.load(testname+".cfg")
cfg.maxtest=1000#100
cfg.numneg=1000
cfg.ovr=0.5
cfg.posovr=0.7
cfg.thr=-2
#cfg.deform=True
cfg.bottomup=True
cfg.loadfeat=False
cfg.savefeat=False
#cfg.usemrf=True#False#True#da togliere
#cfg.ratio=1#datogliere
cfg.multipr=4
cfg.inclusion=False
#cfg.nms=0.4
cfg.dbpath="/home/marcopede/databases/"
#cfg.auxdir="/state/partition1/marcopede/INRIA/"#InriaPosData(basepath="/home/databases/").getStorageDir()
cfg.auxdir=InriaPosData(basepath=cfg.dbpath).getStorageDir()
cfg.show=False
cfg.mythr=-10
cfg.small=False
cfg.useprior=False
cfg.k=1.0
#cfg.usemrf=False
#cfg.maxpostest=1000

#cfg.initr=0
#cfg.ratio=0
#cfg.hallucinate=
#cfg.thr=-2

#trPosImages=InriaPosData(basepath="/home/databases/")
#trNegImages=InriaNegData(basepath="/home/databases/")
#tsImages=InriaTestFullData(basepath="/home/databases/")
#tsImages=DirImages(imagepath="/home/marcopede/Dropbox/Marco/PruebasDemos",ext=".jpg")
#tsImages=getRecord(InriaTestFullData(basepath="/share/ISE/marcopede/database/"),cfg.maxtest)
tsImages=getRecord(InriaTestFullData(basepath=cfg.dbpath),cfg.maxtest)
#tsImages=getRecord(InriaTestData(basepath="/share/ISE/marcopede/database/"),cfg.maxtest)

#svmname="./data/%s.svm"%testname
#lib="libsvm"
#w,r=util.loadSvm(svmname,dir="",lib=lib)
#util.objf(w,r,svmpos,svmneg,pc)
#m=tr.model(w,r,len(m["ww"]),31)

m=util.load("%s%d.model"%(testname,it))
#if cfg.deform:
#    print m["df"]
#    for id,l in enumerate(m["df"]):
#        m["df"][id]=numpy.zeros(l.shape,dtype=numpy.float32)

##############################
####just for the error...
#for id,l in enumerate(m["df"]):
#    m["df"][id][:,:,:2]=numpy.zeros((l.shape[0],l.shape[1],2),dtype=numpy.float32)
#############################

#del m["df"][2]
#del m["ww"][2]
#m["df"][0]=numpy.zeros(m["df"][0].shape,dtype=numpy.float32)
#m["df"][1]=numpy.zeros(m["df"][1].shape,dtype=numpy.float32)
#m["df"][2]=numpy.zeros(m["df"][2].shape,dtype=numpy.float32)

if 0:
    print "Show model"
    pylab.figure(100)
    pylab.clf()
    util.drawModel(m["ww"])
    pylab.figure(101)
    pylab.clf()
    util.drawDeform(m["df"])
    pylab.draw()
    pylab.show()

if cfg.multipr==1:
    numcore=None
else:
    numcore=cfg.multipr

initime=time.time()
print "Test"
detlist=[]
dettime=[]
numhog=0
print "---Test Images----"
arg=[[i,tsImages[i]["name"],None,m,cfg] for i in range(len(tsImages))]
mypool = Pool(numcore)
if not(cfg.multipr):
    itr=itertools.imap(detectWrap,arg)        
else:
    itr=mypool.imap(detectWrap,arg)
for i,im in enumerate(itr):
    print "---- Image %d----"%i
    print "Detections:", len(im[1]) 
    dettime.append(im[2])
    numhog+=im[3]
    print im[3]
    #raw_input()   
    for l in im[1]:
        detlist.append([tsImages[i]["name"].split("/")[-1].split(".")[0],l["scr"],l["bbox"][1],l["bbox"][0],l["bbox"][3],l["bbox"][2]])
del itr
mypool.close()
tp,fp,scr,tot=VOCpr.VOCprRecord(tsImages,detlist,show=False,ovr=0.5)#solved a problem that was giving around 1-2 point less

tplist,fplist,fplist2,fnlist=VOCpr.VOCanalysis(tsImages,detlist,show=False,ovr=0.5)
util.save("%s_anal_%d.dat"%(testname,it),{"tplist":tplist,"fplist":fplist,"fplist2":fplist2,"fnlist":fnlist})

pylab.figure(16)
pylab.clf()
fppi,miss,ap=VOCpr.drawMissRatePerImage(tp,fp,tot,288)
pylab.draw()
pylab.show()
pylab.figure(15)
pylab.clf()
rc,pr,ap=VOCpr.drawPrfast(tp,fp,tot)
pylab.draw()
pylab.show()
#pylab.savefig("%s_ap%d_test.png"%(testname,it))
#pylab.savefig("%s_miss%d_test.png"%(testname,it))
tinit=((time.time()-initime))#/3600.0)
print "Total Time:",numpy.sum(dettime)
print "Average Detection Time:",numpy.mean(dettime)
print "Number of Computed HOGS",numhog
print "AP(it=",it,")=",ap
print "Test Time: %.3fs"%tinit
#rpres.report(testname+".rpt.txt","a","Results")



