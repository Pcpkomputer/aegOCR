import cv2
import numpy as np
from PIL import Image
import os
import time
import os
import re
import math
import pytesseract
import subprocess
from glob import glob

class setting:
    txt=''
    default='Dialogue: 0,{},{},Default,,0,0,0,,\n'
    ffmpeg=''
    videofile=''
    _filter=re.compile(r'\d+\s+[^\/]+')
    _filter_time=re.compile(r'\d+')
    path='temp.txt'
    def __init__(self):
        with open('SETTING.ini', 'r', encoding='utf-8') as t:
            text=t.read()
            self.ffmpeg=re.search(r"ffmpeg='(.*)'",str(text)).group(1)
            self.videofile=re.search(r"videofile='(.*)'",str(text)).group(1)
            t.close()
            
    class _720p:
        #SETTING 720p
        MARGIN_TOP=31
        MARGIN_LEFT=280
        MARGIN_RIGHT=550
    class _490p:
        #SETTING 480p
        MARGIN_TOP=31
        MARGIN_LEFT=280
        MARGIN_RIGHT=550
    class _360p:
        #SETTING 360p
        MARGIN_TOP=31
        MARGIN_LEFT=280
        MARGIN_RIGHT=550
    
    

def template(x):
    with open('template.yudha', 'r', encoding='utf-8') as template:
        isi=template.read()
        for a,b in x:
            isi+=setting.default.format(a,b)
        return isi
    
def sentuhanakhir_timecode(zipfile, milisec):
    t_awal=[]
    t_akhir=[]
    milisec_awal=[]
    milisec_akhir=[]

    fix1=[]
    fix2=[]
    
    for timecode_awal, timecode_akhir in zipfile:
        a=re.search(r'.(.:..:..)',str(timecode_awal)).group(1)
        t_awal.append(a)
        b=re.search(r'.(.:..:..)',str(timecode_akhir)).group(1)
        t_akhir.append(b)
    for mili_awal, mili_akhir in milisec:
        milisec_awal.append('.'+mili_awal)
        milisec_akhir.append('.'+mili_akhir)
    for x in zip(t_awal,milisec_awal):
        n=''.join(x)
        fix1.append(n)
    for y in zip(t_akhir,milisec_akhir):
        m=''.join(y)
        fix2.append(m)
    return zip(fix1,fix2)
        

def parser(x):
    fm_aw_encoded=[]
    fm_ak_encoded=[]
    yparser=[]
    xparser=[]
    for frame_awal,frame_akhir in x:
        _val=int(frame_awal)/float(framerate)
        _milisec=re.search(r'...(..)',str(_val)).group(1)
        yparser.append(_milisec)
        _val_rounded=math.floor(_val)
        _timecode_awal=time.strftime('%H:%M:%S', time.gmtime(_val_rounded))

        fm_aw_encoded.append(_timecode_awal)

        val_=int(frame_akhir)/float(framerate)
        milisec_=re.search(r'...(..)',str(val_)).group(1)
        xparser.append(milisec_)
        val_rounded_=math.floor(val_)
        timecode_akhir_=time.strftime('%H:%M:%S', time.gmtime(val_rounded_))

        fm_ak_encoded.append(timecode_akhir_)
        
    return zip(fm_aw_encoded,fm_ak_encoded),zip(yparser,xparser)
    
def framerate(videofile):
    val=subprocess.run([setting.ffmpeg,'-i',videofile],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    var=re.search(r'(\d+.\d+) fps',str(val.stderr)).group(1)
    return var

def init_(__init__):
    awal=0
    #akhir=int(len(__init__))-1
    arr=[]
    for x in __init__:
        _x=re.findall(setting._filter_time,str(x))
        arr.append((_x[awal],_x[len(_x)-1]))
    return arr

def groupby(FILES):
    with open(FILES, 'r', encoding='utf-8') as text:
        isi=text.read()
        frame=re.findall(setting._filter,str(isi))
        return frame
        
def _720p(video):
    print('720p')

def _480p(video):
    print('480p')

def _360p(video):
    init=0
    vid=cv2.VideoCapture(video)
    while vid.isOpened():
        print(setting.txt)
        switch=False
        init+=1
        ret, frame=vid.read()
        y,x,l=frame.shape
        print('Ini adalah frame ke - {}'.format(init))
        for q in range(x-int(setting._360p.MARGIN_RIGHT)):
            if(frame[y-int(setting._360p.MARGIN_TOP),q+int(setting._360p.MARGIN_LEFT)][1]==0):
                switch=True
                
            frame[y-int(setting._360p.MARGIN_TOP),q+int(setting._360p.MARGIN_LEFT)]=[255,0,0]
            
        cv2.imshow('window',frame)
        if switch==True:
            setting.txt+=str(init)+' '
        else:
            setting.txt+='/ ' 
        #time.sleep(1)
        if cv2.waitKey(1) & 0xFF==ord('q'):
                break
    ext=open('temp.txt', 'w', encoding='utf-9')
    ext.write(setting.txt)
    vid.release()
    cv2.destroyAllWindows()

def bacadialog():
    cap=cv2.VideoCapture(setting.videofile)
    for frameawal, frameakhir in obj:
        cap.set(1,int(frameawal))
        ret,frame=cap.read()
        cv2.imwrite('images/im_'+str(frameawal)+'.jpg',frame)
    cap.release()

def ocr():
    file=glob('images/*')
    for w in file:
        images=cv2.imread(x)
        p,o,i=images.shape
        z=Image.open(w)
        imz=z.crop((0,p-100,o,p))
        im=np.array(imz)
        cv2.imshow("cropped", im)
        cv2.waitKey(0)
        print(pytesseract.image_to_string(imz))

if __name__=='__main__':
    setting=setting()
    #print(setting.path)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'
    #_360p()
    if len(os.listdir('images'))>0:
        for x in glob('images/*'):
            os.remove(x)
    f=groupby(setting.path)
    obj=init_(f)
    framerate=framerate(setting.videofile)
    zipfile,last=parser(obj)
    timecode=sentuhanakhir_timecode(zipfile, last)
    template=template(timecode)
    #print(template)
    bacadialog()
    with open('final.ass','w',encoding='utf-8') as final:
        final.write(template)
        final.close()
    ocr()
    
          

