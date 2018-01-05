import os,glob
import dicom
import json


basedir='/Users/poldrack/data_unsynced/multitask/sc1/nii'

fmapfiles=glob.glob(os.path.join(basedir,'*/*gre*.json'))

te=[]
for f in fmapfiles:
    j=json.load(open(f))
    te.append(j['EchoTime'])
