import os,glob
import dicom
import json


basedir='/scratch/01329/poldrack/MultiTask/sc1/nii'

fmapfiles=glob.glob(os.path.join(basedir,'*/*gre*.json'))

te=[]
for f in fmapfiles:
    j=json.load(open(f))
    te.append(j['EchoTime'])
