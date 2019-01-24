import os
from operator import itemgetter
from pathlib import Path

from Smarch.smarch import read_dimacs, read_constraints, sample, checkSAT
from Evaluation.randomness_test import get_rank
from Evaluation.kconfigIO import gen_configs_kmax, build_samples

home = str(Path.home())


def aggregateIfile(dir, n):
    ifiles = set()

    for i in range(0,n-1):
        list = os.listdir(dir + "/" + str(i) + ".config")

        for f in list:
            if f.endswith('.i'):
                ifiles.add(f)

    print(ifiles)


def unique_errors(errorlist):
    elist = set()

    with open(errorlist, 'r') as f:
        for line in f:
            elist.add(line)

    print(len(elist))


target = "axtls_2_1_4"
n = 200
sampling = "smarch"

dimacs = os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + ".dimacs"
constfile = "" # os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + ".const"
wdir = os.path.dirname(dimacs) + "/smarch"
cdir = home + "/kmax/kconfig_case_studies/cases/" + target + "/r83/" + str(n) + "/" + sampling

#sample configurations
features, clauses, vcount = read_dimacs(dimacs)
const = read_constraints(constfile, features)

if checkSAT(dimacs, const):
    samples = sample(vcount, clauses, n, wdir, const, False, 1)

    gen_configs_kmax(dimacs, samples, cdir)

    #build_samples(target, "/r83/" + str(n) + "/" + sampling)
else:
    print("Constraint not satisfiable")


# errors = "/home/jeho/kmax/kconfig_case_studies/cases/" + target + "/r83/" + str(n) + "/" + sampling + "/build_out/errors.txt"
# unique_errors(errors)
#
# sampling = "randconfig"
# errors = "/home/jeho/kmax/kconfig_case_studies/cases/" + target + "/r83/" + str(n) + "/" + sampling + "/build_out/errors.txt"
# unique_errors(errors)


# dir = "/home/jeho/kmax/kconfig_case_studies/preprocess_out/toybox_0_7_5/misc/r6_study/randconfig/100"
# n = 100
#
# aggregateIfile(dir, n)


