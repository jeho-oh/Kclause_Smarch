import os
import time

from smarch import sample, read_dimacs, read_constraints
from operator import itemgetter
from scipy.stats import ttest_ind, pearsonr
from evaluation import GT, BN


# find noteworthy features from benchmarked samples
def get_noteworthy(measurements, obj):
    noteworthy = list()

    # sort by objective
    sortedlist = sorted(measurements, key=itemgetter(obj), reverse=False)

    # find common features from best two measurements
    common = list(set(sortedlist[0][0]).intersection(sortedlist[1][0]))

    # check noteworthiness of common features
    for c in common:
        in_measure = list()
        ex_measure = list()

        for m in measurements:
            if c in m[0]:
                in_measure.append(m[obj])
            else:
                ex_measure.append(m[obj])

        if len(in_measure) > 1 and len(ex_measure) > 1:
            stat, pvalue = ttest_ind(in_measure, ex_measure, equal_var=False)

            if stat < 0 and pvalue < 0.05:
                const = list()
                const.append(c)
                noteworthy.append(const)

    return noteworthy


class Searcher:
    features = list()
    clauses = list()
    vcount = list()
    const = list()
    eval = list()
    wdir = ''

    def __init__(self, target_, eval_):
        dimacs = "/home/jeho/MOO/FM/" + target + ".dimacs"
        constfile = "/home/jeho/MOO/FM/" + target + ".const"
        self.wdir = os.path.dirname(dimacs) + "/smarch"

        self.features, self.clauses, self.vcount = read_dimacs(dimacs)
        self.const = read_constraints(constfile, self.features)

        self.eval = eval_

    # one recursion of sampling, benchmarking, and finding noteworthy features
    def _recurse(self, n_, obj_, constraints):
        # sample configurations with constraints
        _samples = sample(self.vcount, self.clauses, n_, self.wdir, constraints, False, 1)

        # evaluate configurations
        eval_time = time.time()
        _measurements = self.eval.evaluate(_samples)
        print("Evaluation time: " + str(time.time() - eval_time))

        # deduce noteworthy features
        _noteworthy = get_noteworthy(_measurements, obj_)

        # determine termination
        if len(_noteworthy) != 0:
            return True, _noteworthy, _measurements
        else:
            return False, _noteworthy, _measurements

    # SearchExtreme
    def sx(self, n, objs, rmax=-1):
        popl = set()

        if len(objs) > 1:
            # sample initial configurations with constraints
            initsamples = sample(self.vcount, self.clauses, n, self.wdir, self.const, False, 1)

            # benchmark configurations
            measurements = self.eval.evaluate(initsamples)

            # collect measurements
            for m in measurements:
                m[0] = tuple(m[0])
                # t = tuple(tuple(v) for v in m)
                popl.add(tuple(m))

            tobj = objs.copy()
            # check correlation between objectives for grouping
            for i in range(0, len(objs)):
                for j in range(i+1, len(objs)):
                    x = [j[i] for j in measurements]
                    y = [k[j] for k in measurements]
                    corr, pvalue = pearsonr(x, y)

                    # group objectives if correlation is larger than 0.8
                    if corr > 0.8:
                        tobj.remove(y)
            objs = tobj.copy()

        for o in objs:
            rec = True
            ntwf = self.const.copy()
            r = 0

            while rec and (rmax == -1 or r < rmax):
                print(">> Recursion: " + str(r))
                rec, ntw, measurements = self._recurse(n, o, ntwf)
                ntwf = ntwf + ntw
                print("Added noteworthy features: " + str(ntw))

                # collect measurements
                for m in measurements:
                    m[0] = tuple(m[0])
                    # t = tuple(tuple(v) for v in m)
                    popl.add(tuple(m))

                sortedlist = sorted(popl, key=itemgetter(1), reverse=False)
                print("Recursion " + str(r) + " best: " + str(sortedlist[0][1:]))
                print(str(sortedlist[0][0]))
                r += 1

        return popl

    # SearchRegion
    def sr(self, poi):
        print(poi)


# run script
if __name__ == "__main__":
    target = "fiasco_17_10"
    n = 20
    obj = [1]

    eval = BN(target)
    searcher = Searcher(target, eval)

    result = searcher.sx(n, [1], -1)

    print()
    print("<<Search results>>")
    print("N: " + str(len(result)))
    sortedlist = sorted(result, key=itemgetter(1), reverse=False)
    print("Best: " + str(sortedlist[0][1:]))
    print(str(sortedlist[0][0]))
    #rank = eval.get_rank(sortedlist[0][1], 1)
    #print("Rank: " + str(rank))
