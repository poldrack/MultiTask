import glob
import os

setcode='sc2'
basedir='/scratch/01329/poldrack/MultiTask/%s/DICOM'%setcode
outbase='/scratch/01329/poldrack/MultiTask/%s/nii'%setcode
#outbase='/data/01329/poldrack/MultiTask/nii'
#outbase=basedir.replace('DICOM','nii')
assert outbase != basedir
if not os.path.exists(outbase):
    os.mkdir(outbase)

dcmdirs=glob.glob(os.path.join(basedir,'s*'))
sing_cmd='singularity exec -e /work/01329/poldrack/stampede2/singularity_images/nipy_heudiconv-2017-09-17-de6d3b1c7930.img '
sing_cmd=''
for d in dcmdirs:
    outdir=os.path.join(outbase,os.path.basename(d))
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    cmd="%sdcm2niix -f '%%f_%%p_%%t_%%s' -b y -o %s %s"%(sing_cmd,outdir,d)
    print(cmd)
