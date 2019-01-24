import os
from operator import itemgetter
from pathlib import Path

from Smarch.smarch import read_dimacs, read_constraints, sample, checkSAT
from Evaluation.search import Searcher, BN
from Evaluation.randomness_test import get_rank
from Evaluation.kconfigIO import gen_configs_kmax

home = str(Path.home())

target = "busybox_1_28_0"
dimacs = os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + ".dimacs"
constfile = "" # os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + ".const"
wdir = os.path.dirname(dimacs) + "/smarch"
cdir = home + "/kmax/kconfig_case_studies/cases/" + target + "/correctness/configs"
eval = BN(target, dimacs, cdir)

if not os.path.exists(cdir):
    os.makedirs(cdir)

# sample configurations
features, clauses, vcount = read_dimacs(dimacs)
const = read_constraints(constfile, features)

if checkSAT(dimacs, const):
    samples = sample(vcount, clauses, 100, wdir, const, False, 1)

    gen_configs_kmax(dimacs, samples, cdir)
    #get_rank(dimacs, cdir)

    # measure build sizes
    #measurements = eval.evaluate(samples)
    #sortedlist = sorted(measurements, key=itemgetter(1), reverse=False)

    #measurements = eval.evaluate_existing()

    # print measurements
    # print("<<Build sizes from 1000 URS samples>>")
    # for m in measurements:
    #     print(m)

else:
    print("Constraint not satisfiable")


# # search for configuration with minimum buildsize as possible
# n = 15
# obj = [1]
#
# searcher = Searcher(dimacs, constfile, eval)
# result = searcher.srs(n, [1], -1, True)
#
# print()
# print("<<Search results>>")
# print("N: " + str(len(result)))
# sortedlist = sorted(result, key=itemgetter(1), reverse=False)
# print("Best: " + str(sortedlist[0][1:]))
# print(str(sortedlist[0][0]))
