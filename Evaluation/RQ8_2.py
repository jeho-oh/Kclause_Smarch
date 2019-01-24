import os

from Smarch.smarch import count, read_dimacs, get_var, checkSAT


def check_contains(config_, feature_):
    if feature_.startswith('-'):
        neg = True
        check = feature_[1:]
    else:
        neg = False
        check = feature_

    with open(config_, 'r') as f:
        for line in f:
            if check in line:
                if line.startswith('#'):
                    if neg:
                        return True
                    else:
                        return False
                else:
                    if neg:
                        return False
                    else:
                        return True

        print("ERROR: Feature not found")


def sample_rdiff(dimacs_, smdir_, randir_):
    features, clauses, vcount = read_dimacs(dimacs)

    total = count(dimacs_, [])

    for f in features:
        if f[2] != 'nonbool':
            fv = [f[0]]

            if checkSAT(dimacs_, [fv]):
                tp = count(dimacs_, [fv])
                tr = tp/total
                print(f[1] + ": ", end="")

                hit = 0
                samples = 0
                for file in os.listdir(smdir_):
                    if file.endswith('.config'):
                        if check_contains(smdir_ + "/" + file, f[1]):
                            hit += 1
                        samples += 1

                sr = hit / samples

                hit = 0
                samples = 0
                for file in os.listdir(randir_):
                    if file.endswith('.config'):
                        if check_contains(randir_ + "/" + file, f[1]):
                            hit += 1
                        samples += 1

                rr = hit / samples

                # print(str(tr) + " " + str(sr) + " " + str(rr))
                print(str(abs(sr - tr)) + " " + str(abs(rr - tr)))


target = "toybox_0_7_5"
n = 1000

dimacs = os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + ".dimacs"

smdir = os.path.dirname(os.path.realpath(__file__)) + "/Configs/Smarch/" + target + "/" + str(n) + "/"
randir = os.path.dirname(os.path.realpath(__file__)) + "/Configs/randconfig/" + target + "/" + str(n) + "/"

sample_rdiff(dimacs, smdir, randir)




