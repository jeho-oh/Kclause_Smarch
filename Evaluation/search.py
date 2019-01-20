import os, shutil
import time

from Smarch.smarch import sample, read_dimacs, read_constraints
from operator import itemgetter
from scipy.stats import ttest_ind, pearsonr
from Evaluation.kconfigIO import gen_configs_kmax, gen_configs_kcr, build_samples


# find noteworthy features from benchmarked samples
def get_noteworthy(measurements, obj_):
    noteworthy = list()

    # sort by objective
    sortedlist = sorted(measurements, key=itemgetter(obj_), reverse=False)

    # find common features from best two measurements
    common = list(set(sortedlist[0][0]).intersection(sortedlist[1][0]))

    # check noteworthiness of common features
    for c in common:
        in_measure = list()
        ex_measure = list()

        for m in measurements:
            if c in m[0]:
                in_measure.append(m[obj_])
            else:
                ex_measure.append(m[obj_])

        if len(in_measure) > 1 and len(ex_measure) > 1:
            stat, pvalue = ttest_ind(in_measure, ex_measure, equal_var=False)

            if stat < 0 and pvalue < 0.05:
                found = list()
                found.append(c)
                noteworthy.append(found)

    return noteworthy


class BN:
    wdir = ""
    dimacs = ""
    target = ""
    kcr = False

    def __init__(self, target_, dimacs_, wdir_, kcr_=False):
        self.target = target_
        self.wdir = wdir_
        self.dimacs = dimacs_
        self.kcr = kcr_
        # check vagrant is up

    def evaluate(self, samples):

        for file in os.listdir(self.wdir):
            path = os.path.join(self.wdir, file)
            try:
                if os.path.isfile(path):
                    os.unlink(path)
                elif os.path.isdir(path): shutil.rmtree(path)
            except Exception as e:
                print(e)

        # create .config files
        if self.kcr:
            gen_configs_kcr(self.target, self.dimacs, samples, self.wdir)
        else:
            gen_configs_kmax(self.dimacs, samples, self.wdir)

        # build samples
        build_samples(self.target, 'build/configs')

        # check build errors
        i = 0
        file = self.wdir + "/return_codes.txt"
        with open(file) as f:
            for line in f:
                if '0' not in line:
                    i += 1

        print("Number of failed configs: " + str(i))

        # read build size reports
        file = self.wdir + "/binary_sizes.txt"
        buildsizes = list()
        with open(file, 'r') as f:
            for line in f:
                data = line.split(' ')

                if data[0] == 'binary':
                    buildsizes.append(int(data[4]))

        # create measurement set
        measurements = list()
        i = 0
        for s in samples:
            m = list()

            m.append(s)
            m.append(buildsizes[i])

            measurements.append(m)
            i += 1

        return measurements

    def evaluate_existing(self):
        # build samples
        build_samples(self.target, 'build/configs')

        # read build size reports
        file = self.wdir + "/binary_sizes.txt"
        buildsizes = list()
        with open(file, 'r') as f:
            for line in f:
                data = line.split(' ')

                if data[0] == 'binary':
                    buildsizes.append(int(data[4]))

        return buildsizes


class Searcher:
    features = list()
    clauses = list()
    vcount = list()
    const = list()
    eval = list()
    wdir = ''

    def __init__(self, dimacs_, constfile_, eval_):
        self.wdir = os.path.dirname(dimacs_) + "/smarch"

        self.features, self.clauses, self.vcount = read_dimacs(dimacs_)
        self.const = read_constraints(constfile_, self.features)

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

    # recursive search
    def srs(self, n_, objs, rmax=-1, verbose=False):
        popl = set()

        if len(objs) > 1:
            # sample initial configurations with constraints
            initsamples = sample(self.vcount, self.clauses, n_, self.wdir, self.const, False, 1)

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
                rec, ntw, measurements = self._recurse(n_, o, ntwf)
                ntwf = ntwf + ntw

                if verbose:
                    print(">> Recursion: " + str(r))
                    print("Added noteworthy features: " + str(ntw))

                # collect measurements
                for m in measurements:
                    m[0] = tuple(m[0])
                    # t = tuple(tuple(v) for v in m)
                    popl.add(tuple(m))

                sortedlist = sorted(popl, key=itemgetter(1), reverse=False)

                if verbose:
                    print("Recursion " + str(r) + " best: " + str(sortedlist[0][1:]))
                    print(str(sortedlist[0][0]))

                r += 1

        return popl


# run script
if __name__ == "__main__":
    target = "fiasco_17_10"
    n = 20
    obj = [1]

    dimacs = os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + ".dimacs"
    const = os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + ".const"
    wdir = os.path.dirname(dimacs) + "/smarch"

    eval = BN(target, dimacs, wdir)
    searcher = Searcher(dimacs, const, eval)

    result = searcher.srs(n, [1], -1)

    print()
    print("<<Search results>>")
    print("N: " + str(len(result)))
    result = sorted(result, key=itemgetter(1), reverse=False)
    print("Best: " + str(result[0][1:]))
    print(str(result[0][0]))

