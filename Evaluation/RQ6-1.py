import os
from operator import itemgetter
from pathlib import Path

from Smarch.smarch import read_dimacs, read_constraints, sample, checkSAT
from Evaluation.search import Searcher, BN
from Evaluation.randomness_test import get_rank
from Evaluation.kconfigIO import gen_configs_kmax, read_configs_kmax

home = str(Path.home())

target = "uClibc-ng_1_0_29"
n = 1000
sampling = "smarch"

dimacs = os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + ".dimacs"
constfile = os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + ".const"
wdir = os.path.dirname(dimacs) + "/smarch"
cdir = home + "/kmax/kconfig_case_studies/cases/" + target + "/correctness/configs"
eval = BN(target, dimacs, cdir)

if not os.path.exists(cdir):
    os.makedirs(cdir)

# sample configurations
features, clauses, vcount = read_dimacs(dimacs)
const = read_constraints(constfile, features)

if checkSAT(dimacs, const):
    samples = sample(vcount, clauses, n, wdir, const, False, 1)

    gen_configs_kmax(dimacs, samples, cdir)

    #measure build sizes
    measurements = eval.evaluate(samples)
    sortedlist = sorted(measurements, key=itemgetter(1), reverse=False)

    # samples = read_configs_kmax(features, cdir)
    # gen_configs_kmax(dimacs, samples, cdir+'kmax')
    #
    # measurements = eval.evaluate_existing('rbuild/6kmax')

    #print measurements
    print(target)
    for m in measurements:
        print(m)

else:
    print("Constraint not satisfiable")