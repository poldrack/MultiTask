"""
fix various metadata issues

"""


import os,sys,glob
import json


from bids.grabbids import BIDSLayout

#project_root = '/Users/poldrack/data_unsynced/multitask/sc1/BIDS'
project_root='/scratch/01329/poldrack/MultiTask/sc2/BIDS'
layout = BIDSLayout(project_root)


for sub in layout.get_subjects():
    for sess in layout.get_sessions(subject=sub):
        print(sub,sess)
        # first fix fieldmap metadata
        # need to add echo times to phasediff

        m1=layout.get(subject=sub,session=sess,
            type='magnitude1',extensions='.json')
        assert len(m1)<=1
        if len(m1)==0:
            print('no fieldmap - skipping')
        else:
            m2=layout.get(subject=sub,session=sess,
                type='magnitude2',extensions='.json')
            assert len(m2)==1
            pd=layout.get(subject=sub,session=sess,
                            type='phasediff',extensions='.json')
            assert len(pd)==1
            pd_metadata=layout.get_metadata(pd[0].filename)
            if 'EchoTime' in pd_metadata:
                pd_metadata['EchoTime1']=layout.get_metadata(m1[0].filename)['EchoTime']
                pd_metadata['EchoTime2']=layout.get_metadata(m2[0].filename)['EchoTime']
                del pd_metadata['EchoTime']
                json.dump(pd_metadata,open(pd[0].filename,'w'),
                                sort_keys=True,indent=4)

        boldruns=layout.get(subject=sub,session=sess,
                    type='bold',extensions='.json')
        for b in boldruns:
            br_metadata=layout.get_metadata(b.filename)
            if not 'TaskName' in br_metadata:
                br_metadata['TaskName']='MultiTask'
                json.dump(br_metadata,open(b.filename,'w'),
                            sort_keys=True,indent=4)
