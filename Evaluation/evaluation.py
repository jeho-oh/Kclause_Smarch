from kconfigIO import gen_configs_kmax, build_samples

# text purpose
from smarch import sample, read_dimacs, read_constraints


def unselected_features(sample):
    value = 0

    for f in sample:
        if f < 0:
            value += 1

    return value


class GT:
    """Evaluation for ground truth systems"""
    configs = list()
    values = list()

    def __init__(self, target_, features_):
        names = [i[1] for i in features_]

        file = "/home/jeho/MOO/Data/" + target_ + ".csv"
        with open(file, 'r') as f:
            for line in f:
                data = line.split("\"")

                config = data[1].split(',')
                c = set()
                for n in names:
                    if n in config:
                        c.add(names.index(n)+1)
                    else:
                        c.add((names.index(n)+1) * -1)

                v = data[2][1:len(data[2]) - 1].split(',')

                self.configs.append(c)
                self.values.append(list(map(float, v)))

    def evaluate(self, samples):
        # create measurements
        measurements = list()
        for s in samples:
            i = self.configs.index(s)
            m = list()
            m.append(s)

            val = self.values[i]
            for v in val:
                m.append(v)

            measurements.append(m)
        return measurements

    def get_rank(self, value_, obj_):
        r = 0
        for v in self.values:
            if value_ > v[obj_-1]:
                r += 1
        return r / len(self.values)


class PM:
    values = list()

    def __init__(self, target, features):

        file = "/home/jeho/MOO/Data/" + target + ".txt"

        with open(file, 'r') as f:
            for line in f:
                if not line.startswith('#'):
                    data = line.split(" ")
                    self.values.append(data)

    def evaluate(self, samples):
        # create measurements
        measurements = list()

        for s in samples:
            m = [None] * (len(self.values[0]) + 2)
            m[0] = s

            for i in range(1, len(self.values[0])):
                m[i] = 0
                for f in s:
                    if f > 0:
                        m[i] += self.values[f][i]

            m[5] = unselected_features(s)
            measurements.append(m)

        return measurements


class BN:
    wdir = ""
    dimacs = ""
    target = ""

    def __init__(self, target_):
        self.target = target_
        self.wdir = "/home/jeho/kmax/kconfig_case_studies/cases/" + target_ + "/build/configs"
        self.dimacs = "/home/jeho/kmax/kconfig_case_studies/cases/" + target_ + "/build/kconfig.dimacs"

        # check vagrant is up

    def evaluate(self, samples):
        # create .config files
        gen_configs_kmax(self.dimacs, samples, self.wdir, )

        # build samples
        build_samples(self.target, 'build/configs')

        # read build size reports
        file = self.wdir + "/binary_sizes.txt"
        buildsizes = list()
        with open(file, 'r') as f:
            for line in f:
                data = line.split(' ')

                if data[0] == 'binary':
                    buildsizes.append(int(data[4]))

        # create measurement set
        measurements = list()
        i = 0
        for s in samples:
            m = list()

            m.append(s)
            m.append(buildsizes[i])
            m.append(unselected_features(s))

            measurements.append(m)
            i += 1

        return measurements


# test script
if __name__ == "__main__":
    target = "axtls_2_1_4"
    dimacs = "/home/jeho/MOO/FM/" + target + ".dimacs"
    wdir = "/home/jeho/MOO/FM/smarch"
    features, clauses, vcount = read_dimacs(dimacs)
    constfile = "/home/jeho/kmax/kconfig_case_studies/cases/" + target + "/build/constraints.txt"
    constraints = read_constraints(constfile, features)

    # gt = GT()
    # gt.setup(target, features)

    bn = BN(target)
    samples = sample(vcount, clauses, 5, wdir, constraints, False, 1)

    results = bn.evaluate(samples)
    for r in results:
        print(r)
    print(len(results))
