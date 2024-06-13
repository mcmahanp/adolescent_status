import igraph as ig 
import numpy as np
import sqlite3, glob, re, sys, csv
from collections import Counter,defaultdict
from pathlib import Path


trace_dir = Path('output/gradetrace/')
friend_dir = Path('anonSchoolGraphs')
statusDAG_dir = Path('output/statusDAGs')
out_path_node = Path('output/nodeData.csv')
out_path_grade = Path('output/gradeData.csv')
burnin = 5000

def transitiveReduction(g):
    '''transitive recuction of a DAG g'''
    res = g.copy()
    n = res.vcount()
    for j in range(n):
        res[j,j] = False
        for i in range(n):
            if res[i,j]:
                for k in range(n):
                    if res[j,k]:
                        res[i,k] = False
    return(res)

def transitiveClosure(g):
    '''Transitive closure of a DAG g
    (removes all vertex/edge/graph attributes)'''
    reachable = np.array(g.shortest_paths()) < np.inf 
    h = ig.Graph.Adjacency([[int(c) for c in r] for r in reachable])
    h.simplify()
    return(h)


def loadTraces(fn,burnin,ignoreStuckChains=True):
    '''load an sqlite3 trace of an addHealth status model'''
    con = sqlite3.connect(fn)
    cur = con.cursor()
    # get number of samples and chains
    cur.execute('select max(iter),max(chain)+1 from deviance')
    niter,nchains = cur.fetchone()
    if niter <= burnin:
        raise ValueError('Max interations (%d) not larger than burnin (%d) in %s' % (niter,burnin,fn))

    # find stuck chains
    stuckChains = set()
    if ignoreStuckChains:
        dProbsTraces = defaultdict(list)
        cur.execute('select * from dProbs where iter>%d' % burnin)
        for chain,it,pBase,pLow,pHigh in cur:
            dProbsTraces[chain].append((pBase,pLow,pHigh))

        for chain,trace in dProbsTraces.items():
            dProbsTraces[chain] = np.array(dProbsTraces[chain])
            if np.var(dProbsTraces[chain][:,0]) <= 0.0000000000001:
                stuckChains.add(chain)
        print('dropping %d/%d chains due to stuckness' % (len(stuckChains),nchains))

    # grab all the traces
    q = '''select perm.*, p.pBase, p.pLow, p.pHigh, d.deviance
        from perm, dProbs as p, deviance as d
        where perm.iter=p.iter and perm.chain=p.chain
            and perm.iter=d.iter and perm.chain=d.chain
            and perm.iter>%d and perm.chain not in (%s)'''
    q %= (burnin,','.join([str(c) for c in stuckChains]))

    traces = {'perm':[],'dProbs':[],'deviance':[]}
    cur.execute(q)
    for row in cur:
        traces['perm'].append(row[2:-4])
        traces['dProbs'].append(row[-4:-1])
        traces['deviance'].append([row[-1]])
    # make them into arrays
    for k,v in traces.items():
        traces[k] = np.array(v)

    return(traces)

def edgeCertainties(orderTrace):
    '''convert trace of statusOrder to a matrix
    of edge certainties'''
    n = orderTrace.shape[1]
    mat = np.zeros((n,n),dtype='float')
    for i in range(n-1):
        for j in range(i+1,n):
            p = (orderTrace[:,i]>orderTrace[:,j]).mean()
            mat[i,j] = p
            mat[j,i] = 1 - p
    return(mat)

def statusDAGFromTraces(orderTrace,cutoff):
    am = edgeCertainties(orderTrace) >= cutoff
    g = ig.Graph.Adjacency([[int(c) for c in row] for row in am],mode=ig.ADJ_DIRECTED)
    h = transitiveReduction(g)
    return(h)

def loadFriendshipGraph(schoolNum,gradeNum):
    g = ig.Graph.Read_GraphML('anonSchoolGraphs/comm_%d.graphml' % schoolNum)
    h = g.induced_subgraph(g.vs().select(grade_eq=gradeNum))
    return(h)


def schoolRows(school_num, grade_nums):
    friend_path = friend_dir / f'comm_{school_num}.graphml'
    friend_net = ig.Graph.Read_GraphML(str(friend_path))

# statFunctions is a dictionary of functions
# that take a graph and return an iterable of 
# vertex statistics for that graph.
statFunctions = [
    ('upDegree', (lambda g: g.degree(g.vs(),mode=ig.IN))),
    ('downDegree', (lambda g: g.degree(g.vs(),mode=ig.OUT))),
    ('hSize', (lambda g: g.neighborhood_size(order=g.vcount(),mode=ig.ALL))),
    ('hSizeCalc', (lambda g: [x1+x2 for (x1,x2) in zip(g.neighborhood_size(order=g.vcount(),mode=ig.IN),g.neighborhood_size(order=g.vcount(),mode=ig.OUT))])),
    ('hNumAbove', (lambda g: g.neighborhood_size(order=g.vcount(),mode=ig.IN))),
    ('hNumBelow', (lambda g: g.neighborhood_size(order=g.vcount(),mode=ig.OUT))),
]

if __name__ == '__main__':


    trace_paths = sorted(trace_dir.glob("gradetrace*.sqlite"))
    school_grades = defaultdict(list)
    for fn in trace_paths:
        school_num, grade_num = [int(x) for x in re.findall(r'_school(\d+)_grade(\d+)_',str(fn))[0]]
        school_grades[school_num].append(grade_num)


    grade_rows = []
    data_rows = []
    for school_num, grade_nums in school_grades.items():
        for grade_num in sorted(grade_nums):
            print(f"school {school_num}; grade {grade_num}")
            grade_path = next(trace_dir.glob(f"gradetrace_order_school{school_num}_grade{grade_num}_*.sqlite"))

            try:
                traces = loadTraces(grade_path,burnin,True)
            except ValueError:
                continue

            order_trace = traces['perm']

            friendship_graph = loadFriendshipGraph(school_num,grade_num)

            for cutoff in [.6,.75,.8,.9,.95]:
                sys.stdout.write(' . %.2f' % cutoff)
                sys.stdout.flush()
                statusDAG = statusDAGFromTraces(order_trace,cutoff)

                statusDAG.vs()['vid'] = [v.index for v in statusDAG.vs()]

                statusDAG.write_graphml(str(statusDAG_dir / f"school{school_num}_grade_{grade_num}_{int(cutoff*100)}.graphml"))

                # grade stats
                # (schoolNum,gradeNum,grade_size,cutoff)
                grade_row = [school_num,grade_num,statusDAG.vcount(),cutoff]
                # race
                raceCounts = [np.nansum(friendshipGraph.vs()[rc]) for rc in ['white','black','asian','hispanic','aIndian','otherRace']]
                # propWhite
                grade_row.append(raceCounts[0]/float(sum(raceCounts)))
                # propBlack
                grade_row.append(raceCounts[1]/float(sum(raceCounts)))
                # propAsian
                grade_row.append(raceCounts[2]/float(sum(raceCounts)))
                # propHispanic
                grade_row.append(raceCounts[3]/float(sum(raceCounts)))
                # propAIndian
                grade_row.append(raceCounts[4]/float(sum(raceCounts)))
                # propOther
                grade_row.append(raceCounts[5]/float(sum(raceCounts)))
                # (propFemale)
                isFemale = [s=='f' for s in friendshipGraph.vs()['sex']]
                grade_row.append(np.mean(isFemale))
                # append
                grade_rows.append(tuple(grade_row))
            sys.stdout.write('\n')

            # make rows for students
            columns = [
                friendshipGraph.vs()['name'     ],
                [school_num] * friendshipGraph.vcount(),
                friendshipGraph.vs()['grade'    ],
                friendshipGraph.vs()['sex'     ],
                friendshipGraph.vs()['hispanic' ],
                friendshipGraph.vs()['aIndian'  ],
                friendshipGraph.vs()['black'    ],
                friendshipGraph.vs()['asian'    ],
                friendshipGraph.vs()['white'    ],
                friendshipGraph.vs()['otherRace'],
                order_trace.mean(0), # mean status
                np.median(order_trace,0), # median status
                friendshipGraph.evcent(), # eigenvector centrality
                friendshipGraph.degree(mode=ig.IN), #Degree
                friendshipGraph.degree(mode=ig.OUT)
            ]
            columns.extend([f(statusDAG) for (_,f) in statFunctions])
            rows = zip(*columns)
            data_rows.extend(rows)


    # write it all to disk
    with open(out_path_node,'w') as f:
        # header
        f.write('fakeId,schoolId,grade,sex,hispanic,aIndian,black,asian,white,otherRace,meanStatus,medianStatus,friend_evcent,friend_indegree,friend_outdegree,')
        f.write(','.join([sName for (sName,_) in statFunctions]))
        f.write('\n')
        writer = csv.writer(f)
        writer.writerows(data_rows)
    with open(out_path_grade,'w') as f:
        f.write('schoolNum,gradeNum,gradeSize,cutoff,propWhite,propBlack,propAsian,propHispanic,propAIndian,propOther,propFemale\n')
        writer = csv.writer(f)
        writer.writerows(grade_rows)
        for row in grade_rows:
            f.write('%d,%d,%d,%.2f,%d,%.8f,%8f,%8f,%.8f,%8f,%.8f,%d,%.8f\n' % row)
