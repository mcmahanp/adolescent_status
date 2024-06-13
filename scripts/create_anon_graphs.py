import igraph as ig 
import csv
import sqlite3
from collections import Counter,defaultdict
import os

# path to INSCHOOL.CSV
inschoolPath=''
# path to allwave1.csv
inhomePath = ''
# path to sfriend.csv
sfriendPath = ''

# output directory
outputPattern = 'anonSchoolGraphs/comm%d.graphml'


if __name__ == '__main__':
    # ID maps
    sqidAidMap = {}
    aidSchoolidMap = {}
    schoolidAidMap = {}
    with open(inschoolPath,'r') as f:
        reader = csv.reader(f)
        header = reader.next()
        for row in reader:
            try:
                sqId,aId,schoolId = [int(c) for c in row[:3]]
            except ValueError:
                continue
            sqidAidMap[sqId] = aId
            aidSchoolidMap[aId] = schoolId
            schoolidAidMap[schoolId] = aId

    # grab all the edges
    edges = []  # (schoolId, egoId, alterId)
    excludedIds = set(['',77777777,88888888,99959995,99999999])
    with open(sfriendPath,'r') as f:
        reader = csv.reader(f)
        header = reader.next()
        for row in reader:
            sqId = int(row[0])
            try:
                egoId = sqidAidMap[sqId]
                schoolId = aidSchoolidMap[egoId]
            except KeyError:
                continue
            for alterIdString in row[1:]:
                try:
                    alterId = int(alterIdString)
                except ValueError:
                    continue
                if egoId not in excludedIds and alterId not in excludedIds:
                    edges.append((schoolId,egoId,alterId))


    # get all school pairs
    schoolPairs = set()
    with open(inhomePath,'r') as f:
        reader = csv.reader(f)
        header = reader.next()
        for row in reader:
            try:
                scid,sscid = [int(c) for c in row[4:6]]
            except ValueError:
                continue
            if scid != 999:
                schoolPairs.add(tuple(sorted(((scid,sscid)))))

    # build anonymized graphs and save to disk, along with key
    realToFake = {}
    for pair in schoolPairs:
        pel = []
        for sid,ego,alter in edges:
            if sid not in pair:
                continue
            if ego not in realToFake:
                realToFake[ego] = os.urandom(8).hex()
            if alter not in realToFake:
                realToFake[alter] = os.urandom(8).hex()
            egoFake = realToFake[ego]
            alterFake = realToFake[alter]

            pel.append((egoFake,alterFake))
        g = ig.Graph.TupleList(pel,directed=True)
        with open(outputPattern % min(pair),'w') as f:
            g.write(f)
    with open(os.path.split(outputPattern)[0]+'/key.csv','w') as f:
        f.write('realId,fakeId\n')
        for mp in realToFake.iteritems():
            f.write('%d,%d\n' % mp)
















