"""
convert original task data files into BIDS format

Description from Maedbh:


Within each of these subject folders, there are 17 dat files with the following
format: <study>_<subj>_<taskName>.dat (i.e. sc1_s02_stroop.dat).

Task-specific dat files Each of these task-specific dat files contains all of
the information needed to run a given task in addition to the behavioural
results of that task. Each row always corresponds to an event that occurred
within that task and there are also columns labelled 'startTimeReal',
'startTRreal' and 'runNum' for each run that indicate event timings within each
task (between 0-30 seconds) and TR onsets (between 0-601 TR's). Behavioural runs
(pre-scan training) and scanning runs (for both sessions within a study) are
included. The runs that correspond to the scanning runs are always labelled
51-66 (16 runs across two scanning sessions).

General dat file There is an 18th dat file within each of these subject folders
with the following format: <study>_<subj>.dat (i.e. sc1_s02.dat). This is an
overall dat file that contains information about all of the tasks that occur
within each run. There are always columns labelled 'realStartTime', 'TRreal',
and 'runNum'  that indicate the onset of the tasks as they occur within each
run. Runs corresponding to scanning runs (51-66) always contain 17 tasks. Each
of these 17 tasks is executed for 30 seconds and there is always a 5 second
instruction period preceding the beginning of each task. The first 6 TR's (TR=1
second) of each functional run are "dummy scans" so the first task of each
scanning run starts at 6 seconds.

I have also attached a file: 'sc1_sc2_taskConds_GLM.txt', which details how each
of the these tasks was subdivided into task conditions (29 for sc1 and 32 for
sc2). For example, the affective processing task is subdivided into two
conditions - 'unpleasant scenes' and 'pleasant scenes'. I'm not sure whether
this is of use to you at the moment (I imagine not) but might be in future when
you are building the design matrix. We can perhaps discuss these task conditions
on Tuesday.

"""

import os,sys,glob
import pandas

TR=1 # confirmed that TR=1 for all functional datasets in sc1 and sc2

subcodes=['s04']
setcodes=['sc1']

for setcode in setcodes:
    basedir='/Users/poldrack/data_unsynced/multitask/%s/data'%setcode
    outdir='/Users/poldrack/data_unsynced/multitask/%s/BIDSevents'%setcode
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    for sc in subcodes:
        subdir=os.path.join(basedir,sc)
        gendatfile=os.path.join(subdir,'%s_%s.dat'%(setcode,sc))
        gendat=pandas.read_csv(gendatfile,sep='\t')
        gendat['boldRun']=gendat.runNum-51
        gendat=gendat.query('boldRun >= 0')
        taskfiles=glob.glob(os.path.join(subdir,'%s_%s_*.dat'%(setcode,sc)))
        taskfiles.sort()
        assert len(taskfiles)==17
        taskdata={}
        for tf in taskfiles:
            taskname=os.path.basename(tf).split('.')[0].split('_')[-1]
            tmpdata=pandas.read_csv(tf,sep='\t')
            tmpdata['boldRun']=tmpdata.runNum-51
            taskdata[taskname]=tmpdata.query('boldRun >= 0')
        # group everything into runs
        runs=gendat.boldRun.unique()
        rundata={}
        suboutdir=os.path.join(outdir,sc)
        if not os.path.exists(suboutdir):
            os.mkdir(suboutdir)
        cols_to_drop=['B', 'G', 'R','colour','digit1',
            'digit2', 'digit3', 'digit4', 'digit5', 'digit6', 'endNav', 'falseID',
            'hand', 'imgDir', 'imgFile', 'interval', 'letter', 'movFile',
            'possCorr', 'possFalse', 'possFalseID',
            'question', 'resp1', 'resp2', 'resp3', 'resp4', 'resp5', 'resp6',
            'rotateDistractor','seqCorr', 'setSize',
            'startNav','story','tmp1', 'tmp2', 'tmp3', 'tmp4', 'tmp5',
            'word', 'wordnum']
        for r in runs:
            rundata[r]=None
            for task in taskdata.keys():
                if rundata[r] is None:
                    rundata[r]=taskdata[task].query('boldRun==%d'%r)
                else:
                    rundata[r]=rundata[r].append(taskdata[task].query('boldRun==%d'%r))
            rundata[r]=rundata[r].drop(cols_to_drop,axis=1).sort_values('startTRreal')
            print('run %d: found %d trials'%(r,rundata[r].shape[0]))
            rnum=r+1
            setnum=1
            if rnum>8:
                rnum=rnum-8
                setnum=2

            outfile=os.path.join(suboutdir,'%s_%d_run%d_events.tsv'%(sc,
                                    setnum,rnum))
            rundata[r].to_csv(outfile,sep='\t',index=False)
