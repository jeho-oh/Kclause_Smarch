import os

from Smarch.smarch import read_dimacs, read_constraints, sample
from Evaluation.kconfigIO import read_config_kmax, gen_configs_kcr
from Evaluation.search import BN


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

target = "uClibc-ng_1_0_29"
dimacs = os.path.dirname(os.path.realpath(__file__)) + "/FM/kcr/" + target + ".dimacs"
constfile = os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + ".const"
wdir = os.path.dirname(dimacs) + "/smarch"
cdir = "/home/jeho/kmax/kconfig_case_studies/cases/" + target + "/build/kcrconfigs"
eval = BN(target, dimacs, cdir)

features, clauses, vcount = read_dimacs(dimacs)
const = read_constraints(constfile, features)
samples = sample(vcount, clauses, 10, wdir, const, False, 1)
gen_configs_kcr(target, dimacs, samples, cdir)

