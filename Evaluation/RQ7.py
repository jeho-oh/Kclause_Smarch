import os
from operator import itemgetter
from pathlib import Path

from Smarch.smarch import read_dimacs, read_constraints, sample, checkSAT
from Evaluation.kconfigIO import read_config_kmax, gen_configs_kcr, convert_kcr_to_kmax
from Evaluation.search import Searcher, BN
from Evaluation.randomness_test import get_rank

home = str(Path.home())


def count_selected(sol_):
    i = 0
    for s in sol_:
        if s > 0:
            i += 1

    return i


def check_randconfig(dimacs_, cdir_):
    features, clauses, vcount = read_dimacs(dimacs_)

    for file in os.listdir(cdir_):
        if file.endswith('.config'):
            sol = read_config_kmax(features, cdir_ + "/" + file)

            print(count_selected(sol))


# target = "axtls_2_1_4"
# dimacs = os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + ".dimacs"
# constfile = ""#os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + ".const"
# wdir = os.path.dirname(dimacs) + "/smarch"
# cdir = "/home/jeho/kmax/kconfig_case_studies/cases/" + target + "/correctness/randconfigs_500"
# #cdir = "/home/jeho/kmax/kconfig_case_studies/cases/" + target + "/build/configs"
#
# # sample configurations
# features, clauses, vcount = read_dimacs(dimacs)
# const = read_constraints(constfile, features)
# samples = sample(vcount, clauses, 500, wdir, const, False, 1)
# for s in samples:
#     print(count_selected(s))

#check_randconfig(dimacs, cdir)

target = "fiasco_17_10"
dimacs = os.path.dirname(os.path.realpath(__file__)) + "/FM/kcr/" + target + ".dimacs"
constfile = os.path.dirname(os.path.realpath(__file__)) + "/FM/kcr/" + target + ".const"
wdir = os.path.dirname(dimacs) + "/smarch"
cdir = home + "/kmax/kconfig_case_studies/cases/" + target + "/build/configs"

eval = BN(target, dimacs, cdir, True)

# features, clauses, vcount = read_dimacs(dimacs)
# const = read_constraints(constfile, features)
#
# if checkSAT(dimacs, const):
#
#     samples = sample(vcount, clauses, 1000, wdir, const, True, 1)
#
#     gen_configs_kcr(dimacs, samples, cdir)
#     convert_kcr_to_kmax()
#
#     get_rank(dimacs, cdir)
#
#     # measure build sizes
#     #measurements = eval.evaluate(samples)
#     #sortedlist = sorted(measurements, key=itemgetter(1), reverse=False)
#
#
#
#     #measurements = eval.evaluate_existing()
#
#     # print measurements
#     # print("<<Build sizes from 1000 URS samples>>")
#     # for m in measurements:
#     #     print(m)
#
# else:
#     print("Constraint not satisfiable")

# search for configuration with minimum buildsize as possible
n = 150
obj = [1]

searcher = Searcher(dimacs, constfile, eval)
result = searcher.srs(n, [1], 1, True)

print()
print("<<Search results>>")
print("N: " + str(len(result)))
sortedlist = sorted(result, key=itemgetter(1), reverse=False)
print("Best: " + str(sortedlist[0][1:]))
print(str(sortedlist[0][0]))
