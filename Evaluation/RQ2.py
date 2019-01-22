import os
from operator import itemgetter

from Smarch.smarch import read_dimacs, read_constraints, sample, checkSAT
from Evaluation.kconfigIO import read_config_kmax, gen_configs_kcr, convert_kcr_to_kmax
from Evaluation.search import Searcher, BN
from Evaluation.randomness_test import get_rank, get_rank_kcr


target = "uClibc-ng_1_0_29"
dimacs = os.path.dirname(os.path.realpath(__file__)) + "/FM/kcr/" + target + ".dimacs"
kmax = os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + ".dimacs"
constfile = os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + ".const"
wdir = os.path.dirname(dimacs) + "/smarch"
cdir = "/home/jeho/kmax/kconfig_case_studies/cases/" + target + "/build/kcr/configs"

eval = BN(target, dimacs, cdir, True)

features, clauses, vcount = read_dimacs(dimacs)
const = read_constraints(constfile, features)

if checkSAT(dimacs, const):
    samples = sample(vcount, clauses, 1000, wdir, const, False, 1)
    solset = convert_kcr_to_kmax(dimacs, kmax, samples)
    get_rank_kcr(kmax, solset)
else:
    print("Constraint not satisfiable")