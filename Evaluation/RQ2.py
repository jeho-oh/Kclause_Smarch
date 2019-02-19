import os
from operator import itemgetter

from Smarch.smarch import read_dimacs, read_constraints, sample, checkSAT
from Evaluation.kconfigIO import read_config_kmax, gen_configs_kcr, convert_kcr_to_kmax
from Evaluation.randomness_test import get_rank, get_rank_kcr


target = "axtls_2_1_4"
dimacs = os.path.dirname(os.path.realpath(__file__)) + "/FM/kcr/" + target + ".dimacs"
kmax = os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + ".dimacs"
constfile = os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + ".const"
wdir = os.path.dirname(dimacs) + "/smarch"
jsonfile = os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + "_build.json"

features, clauses, vcount = read_dimacs(dimacs)
const = read_constraints(constfile, features)

if checkSAT(dimacs, const):
    samples = sample(vcount, clauses, 100, wdir, const, False, 1)
    solset = convert_kcr_to_kmax(dimacs, kmax, samples)
    get_rank_kcr(kmax, solset, jsonfile)
else:
    print("Constraint not satisfiable")
