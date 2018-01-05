"""
reformat series numbers for python from original matlab code from Maedbh
"""

import os
import sys
import glob
import dicom

lines=[]
subcode=''
seriesNumbers={'SC1':{},'SC2':{}}
with open('seriesNumbers.py') as f:
    for l in f.readlines():
        l=l.strip()
        if len(l)==0:
            continue
        if l.find("func_seriesNum['SC2']")>-1:
            print('found SC2')
            set='SC2'
        if l.find('#')==0:
            continue
        l_s=l.split('...')
        seriesnums=l_s[0].lstrip().replace('],',']')
        subcode_last=subcode
        subcode=l_s[1].split('#')[-1].split('_')[0].replace(' ','')
        if not subcode in seriesNumbers[set]:
            seriesNumbers[set][subcode]={}
        if subcode==subcode_last:
            session=2
        else:
            session=1
        if len(l_s[1].split('#')[-1].split('_'))>1:
            assert int(l_s[1].split('#')[-1].split('_')[1].replace(' ',''))==session
        print(l,subcode,session,seriesnums)
        seriesnums=seriesnums.replace('[','').replace(']','')
        if len(seriesnums)>0:
            seriesNumbers[set][subcode][session]=[int(i) for i in seriesnums.split(',')]
        else:
            seriesNumbers[set][subcode][session]=[]
# for the remainder of subjects, reverse engineer the series number
# from the dicom headers

if len(sys.argv)>1:
    basedir=sys.argv[1]
else:
    basedir='/scratch/01329/poldrack/MultiTask'

for setcode in seriesNumbers.keys():

    dicomdir=os.path.join(basedir,setcode.lower(),'DICOM')

    dicomdirs=glob.glob(os.path.join(dicomdir,'s*'))
    for d in dicomdirs:
        try:
            subcode=os.path.basename(d).split('_')[0]
            subnum=int(os.path.basename(d).split('_')[0].replace('s',''))
            runnum=int(os.path.basename(d).split('_')[1])
        except ValueError:
            print('skipping',d)
            continue
        if subnum<23:
            print('skipping type 1 subject')
            continue
        if not subcode in seriesNumbers[setcode]:
            seriesNumbers[setcode][subcode]={}
        print('processing:',subnum,runnum,d)
        dcmruns=glob.glob(os.path.join(d,'000*'))
        dcmruns.sort()
        assert len(dcmruns)==8
        seriesnums=[]
        for i,dcr in enumerate(dcmruns):
            assert int(os.path.basename(dcr))==(i+1)
            dcrfiles=glob.glob(os.path.join(dcr,'*.dcm'))
            if len(dcrfiles)>0:
                dcmdata=dicom.read_file(dcrfiles[0])
                seriesnums.append(dcmdata.SeriesNumber)
        print(setcode,subcode,runnum,seriesnums)
        seriesNumbers[setcode][subcode][runnum]=[int(i) for i in seriesnums]
