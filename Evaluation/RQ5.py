import os
from operator import itemgetter

from Smarch.smarch import read_dimacs, read_constraints, sample, checkSAT
from Evaluation.kconfigIO import read_config_kmax, gen_configs_kcr, convert_kcr_to_kmax
from Evaluation.randomness_test import get_rank


target = "uClibc-ng_1_0_29"
n = 1000

dimacs = os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + ".dimacs"
jsonfile = os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + ".json"

randir = os.path.dirname(os.path.realpath(__file__)) + "/Configs/randconfig/" + target + "/" + str(n) + "/"

# check randconfig randomness
get_rank(dimacs, randir, jsonfile)

