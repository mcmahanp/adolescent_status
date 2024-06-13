from OrderEstimator.OrderEstimator import OrderEstimator
import igraph as ig
import scipy as sp
import numpy as np
import os, sys, time
import re
from collections import Counter
from pathlib import Path

graph_dir = Path('anonSchoolGraphs/')
trace_dir = Path('output/gradetrace/')
trace_dir.mkdir(parents = True, exist_ok = True)


if __name__ == '__main__':
    numProcesses = 20
    minGradeSize=40
    maxGradeSize=195

    # find appropriate schools
    schoolNums = []
    for fn in os.listdir(graph_dir):
        mtches = re.findall(r'comm_(\d+)\.graphml', fn)
        if mtches:
            commId = int(mtches[0])
            g = ig.Graph.Read_GraphML(str(graph_dir / fn))
            try:
                grades = g.vs()['grade']
            except KeyError:
                continue
            gradeCounts = Counter([g for g in grades if not np.isnan(g)])
            bigEnough = np.all([v>=minGradeSize for (g,v) in gradeCounts.items() if g>6])
            smallEnough = np.all([v<=maxGradeSize for (g,v) in gradeCounts.items() if g>6])
            if bigEnough and smallEnough:
                schoolNums.append(commId)


    #collect grades as adjacency matrices
    amList = []
    for fileNum in schoolNums:
        g = ig.Graph.Read_GraphML(str(graph_dir / f'comm_{fileNum}.graphml'))
        for gradeNum in range(7,13):
            h = g.induced_subgraph(g.vs().select(grade_eq=gradeNum))
            thisAm = np.array([[int(i) for i in j] for j in h.get_adjacency()])
            if thisAm.shape[0]>=50:
                amList.append((fileNum,gradeNum,thisAm))

    # skip schools that we already have traces for
    existingFiles = os.listdir(trace_dir)
    existingPairs = set()
    for fn in existingFiles:
        # super cludgey
        if  fn[-7:] != '.sqlite':
            continue
        sn = int(re.findall(r'school(\d+)\_',fn)[0])
        gn = int(re.findall(r'grade(\d+)\_',fn)[0])
        existingPairs.add((sn,gn))

    # estimate
    estimators = {}
    logFileName = trace_dir / 'log.txt'
    for fileNum,gradeNum,am in amList:
        print('starting school %d grade %d (%d students)' % (fileNum,gradeNum,am.shape[0]))
        if (fileNum,gradeNum) in existingPairs:
            print('  (trace file already exists: skipping)')
            continue
        db = trace_dir / f'gradetrace_order_school{fileNum}_grade{gradeNum}_{int(time.time())}.sqlite'
        oe = OrderEstimator(am,pAlpha=1.05)
        estimators[(fileNum,gradeNum)] = oe
        oe.sample_mcmc_parallel(10000,1000,4000,thin=20,updateEvery=60,hist_size=80,nChains=20,db=db,verbose=True,record_throughout=True,logFileName=logFileName)


