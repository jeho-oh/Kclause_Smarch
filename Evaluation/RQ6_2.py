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
            if check + "=y" in line:
                if neg:
                    return False
                else:
                    return True
            elif check + " " in line:
                if neg:
                    return True
                else:
                    return False

            # if check in line:
            #     if line.startswith('#'):
            #         if neg:
            #             return True
            #         else:
            #             return False
            #     else:
            #         if neg:
            #             return False
            #         else:
            #             return True
        return False
        #print("ERROR: Feature not found")


def sample_rdiff(dimacs_, smdir_, randir_):
    features, clauses, vcount = read_dimacs(dimacs)

    total = count(dimacs_, [])

    for f in features:
        if f[2] != 'nonbool':
            fv = [f[0]]

            if checkSAT(dimacs_, [fv]):
                tp = count(dimacs_, [fv])
                #print(tp)
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

                #print(str(tr) + " " + str(sr) + " " + str(rr))
                print(str(abs(sr - tr)) + " " + str(abs(rr - tr)))


def samples_contain(feature_, randir_):
    for file in os.listdir(randir_):
        if file.endswith('.config'):
            if check_contains(randir_ + "/" + file, feature_):
                print(file)


target = "uClibc-ng_1_0_29"
n = 1000

dimacs = os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + ".dimacs"

smdir = os.path.dirname(os.path.realpath(__file__)) + "/Configs/" + target + "/" + str(n) + "/smarch/"
randir = os.path.dirname(os.path.realpath(__file__)) + "/Configs/" + target + "/" + str(n) + "/randconfig/"

sample_rdiff(dimacs, smdir, randir)




