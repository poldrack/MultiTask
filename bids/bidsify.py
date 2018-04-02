"""
convert multitask data to BIDS
"""

import os,sys,shutil
import glob
import json
import datetime

if os.path.exists('bids_commands.sh'):
    os.remove('bids_commands.sh')

def saveCommand(cmd,outfile='bids_commands.sh'):
    with open(outfile,'a') as f:
        f.write(cmd+'\n')

def getSeriesNumbers(setcode,subcode,sesscode):
    seriesNumbers=json.load(open('seriesNumbers.json'))
    return(seriesNumbers[setcode][subcode][sesscode])

if len(sys.argv)>1:
    basedir=sys.argv[1]
else:
    basedir='/scratch/01329/poldrack/MultiTask'
    #basedir='/Users/poldrack/data_unsynced/multitask'

verbose=False

datainfo={}

def getFileInfo(niifile,bidsbase,setcode,
                makedirs=True,verbose=False):
    """
    get info and set up bids directory structures
    """

    fname=os.path.basename(niifile)
    fname_s=fname.split('.nii')[0].split('_')
    fdir=os.path.dirname(niifile)
    fileinfo={}
    fileinfo['subcode']=os.path.basename(fdir)
    fileinfo['subnum']=int(os.path.basename(fdir).split('_')[0].replace('s',''))
    fileinfo['sessnum']=int(os.path.basename(fdir).split('_')[1])
    fileinfo['seriesnum']=fname_s[-1]
    fileinfo['bidssub']='sub-%02d'%fileinfo['subnum']
    fileinfo['bidssubdir']=os.path.join(bidsbase,fileinfo['bidssub'])
    fileinfo['bidssess']='ses-%d'%fileinfo['sessnum']
    fileinfo['bidssubdir']=os.path.join(bidsbase,fileinfo['bidssub'])
    fileinfo['bidssessdir']=os.path.join(fileinfo['bidssubdir'],fileinfo['bidssess'])
    if makedirs:
        if not os.path.exists(fileinfo['bidssubdir']):
            os.mkdir(fileinfo['bidssubdir'])
        if not os.path.exists(fileinfo['bidssessdir']):
            os.mkdir(fileinfo['bidssessdir'])
    # skip equalized files
    if fname.find('Eq_1')>-1:
        print('skipping equalized file')
        fileinfo['filetype']='unknown'
        sd=None
    elif fname_s[2]=='gre':
        fileinfo['filetype']='fmap'
        sd=os.path.join(fileinfo['bidssessdir'],'fmap')
        dcmhdr=json.load(open(niifile.replace('nii.gz','json')))
        fileinfo['echoTime']=dcmhdr['EchoTime']
        if dcmhdr['ImageType'][2]=='P':
            fileinfo['fmaptype']='phasediff'
        else:
            if dcmhdr['EchoTime']<0.005:
                fileinfo['fmaptype']='magnitude1'
            else:
                fileinfo['fmaptype']='magnitude2'
        fileinfo['bidsfilestem']=os.path.join(sd,
                    '%s_%s_%s'%(fileinfo['bidssub'],
                        fileinfo['bidssess'],
                        fileinfo['fmaptype']))

    elif fname_s[2]=='mprage':
        fileinfo['filetype']='anat'
        sd=os.path.join(fileinfo['bidssessdir'],'anat')
        fileinfo['bidsfilestem']=os.path.join(sd,
                    '%s_%s_T1w'%(fileinfo['bidssub'],
                        fileinfo['bidssess']))
    elif fname_s[2]=='t2':
        fileinfo['filetype']='anat'
        sd=os.path.join(fileinfo['bidssessdir'],'anat')
        fileinfo['bidsfilestem']=os.path.join(sd,
                    '%s_%s_T2w'%(fileinfo['bidssub'],
                        fileinfo['bidssess']))

    elif fname_s[2]=='ep':
        fileinfo['filetype']='func'
        sd=os.path.join(fileinfo['bidssessdir'],'func')
        seriesnums=getSeriesNumbers(setcode,'s%02d'%fileinfo['subnum'],
                                    '%s'%fileinfo['sessnum'])
        if verbose:
            print(fileinfo['seriesnum'])
            print(seriesnums)
        seriesmatch=[i for i,x in enumerate(seriesnums) if int(x) == int(fileinfo['seriesnum'])]
        if len(seriesmatch)==0:
            if verbose:
                print('no match found')
        else:
            if verbose:
                print(seriesmatch)
            assert len(seriesmatch)==1
            fileinfo['bidsfilestem']=os.path.join(sd,
                                    '%s_%s_task-%d_bold'%(fileinfo['bidssub'],
                                                        fileinfo['bidssess'],
                                                        seriesmatch[0]+1))
    else:
        fileinfo['filetype']='unknown'
        sd=None
    if sd is not None:
        if not os.path.exists(sd):
            os.mkdir(sd)

    return fileinfo

for setcode in ['SC1','SC2']:
    setdir=os.path.join(basedir,setcode.lower())
    niidir=os.path.join(setdir,'nii')
    bidsbase=os.path.join(setdir,'BIDS')
    if not os.path.exists(bidsbase):
        os.mkdir(bidsbase)
    if not setcode in datainfo:
        datainfo[setcode]={}
    subdirs=glob.glob(os.path.join(niidir,'s*'))
    subdirs.sort()
    for sd in subdirs:
        niifiles=glob.glob(os.path.join(sd,'*.nii.gz'))
        niifiles.sort()
        if verbose:
            print(sd)
        for niifile in niifiles:
            if verbose:
                print(niifile)
            fileinfo=getFileInfo(niifile,bidsbase,setcode,verbose=verbose)
            datainfo[niifile]=fileinfo
            if verbose:
                print(fileinfo)
            if not 'bidsfilestem' in fileinfo:
                print('skipping bids commands')
                continue
            niifilestem=niifile.replace('.nii.gz','')
            for ft in ['.nii.gz','.json']:
                cmd='cp %s%s %s%s'%(niifilestem,ft,
                                    fileinfo['bidsfilestem'],ft)
                saveCommand(cmd)
