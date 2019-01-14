import os
import json
from Smarch.smarch import count, read_constraints, get_var, read_dimacs, checkSAT
import itertools


def get_commmon(dimacs_, cdir_, configs_, include_=True):
    common = list()
    init = True

    # check if config dir exists
    if not os.path.exists(cdir_):
        print("config not found")
        return

    # get features and clauses
    _features, _clauses, _vars = read_dimacs(dimacs_)
    _names = [i[1] for i in _features]

    # iterate over each randconfig configurations
    for file in os.listdir(cdir_):
        if file.endswith('.config'):
            if (include_ and (file in configs_)) or (not include_ and (file not in configs_)) or (len(configs_) == 0):
                with open(cdir_ + "/" + file, 'r') as f:
                    # print(file)
                    _existing = set()

                    sol = list()
                    for line in f:
                        # line: # FEATURE is not set
                        if line.startswith('#'):
                            line = line[0:len(line) - 1]
                            data = line.split()
                            if len(data) > 4:
                                # if data[1] == 'UCLIBC_HAS_ARGP': #HTTP_HAS_AUTHORIZATION
                                #     print(str(include_) + " " + file + " unselected")

                                if data[1] in _names:
                                    i = _names.index(data[1])
                                    _existing.add(data[1])
                                    if i != -1:
                                        sol.append('-' + _features[i][1])
                                else:
                                    print(data)
                        # line: FEATURE=y or FEATURE="nonbool value"
                        else:
                            line = line[0:len(line) - 1]
                            data = line.split('=')
                            if len(data) > 1:
                                if data[0] in _names:
                                    # if data[0] == 'UCLIBC_HAS_ARGP':
                                    #     print(str(include_) + " " + file + " selected")
                                    i = _names.index(data[0])
                                    _existing.add(data[0])
                                    # FEATURE=y
                                    if data[1] == 'y':
                                        sol.append(str(_features[i][1]))
                                    # FEATURE=empty string or 0
                                    elif data[1] == '\"\"' or data[1] == '0':
                                        if _features[i][3] != '\"\"' and _features[i][3] != '0':
                                            sol.append('-' + _features[i][1])
                                    # FEATURE='nonbool value'
                                    else:
                                        sol.append(str(_features[i][1]))
                                else:
                                    print(data)
                    # if '-CONFIG_DATE' in sol:
                    #     print(file)

                    if init:
                        common = sol
                        init = False
                    else:
                        for s in common:
                            if s not in sol:
                                common.remove(s)

    return common


def filter_common(dimacs_, cdir_, configs_):
    print()
    common_fail = get_commmon(dimacs_, cdir_, configs_, True)
    print("Common across failed configs: " + str(common_fail))
    print()
    common_pass = get_commmon(dimacs_, cdir_, configs_, False)
    print("Common across passed configs: " + str(common_pass))
    print()

    common = list()

    print("Only in failed configs: ", end='')
    for s in common_fail:
        if s not in common_pass:
            print(s, end=',')
            common.append(s)
    print()
    print()

    print("Only in passed configs: ", end='')
    for s in common_pass:
        if s not in common_fail:
            print(s, end=',')
            common.append(s)
    print()
    print()
    return common


def check_ratio(dimacs_, constraints_, check_):
    _features, _clauses, _vcount = read_dimacs(dimacs_)
    total = count(dimacs_, constraints_)
    vars = get_var(check_, _features)
    varlist = [vars[i:i + 1] for i in range(0, len(vars))]

    print("Checking for conjunctions")
    for i in range(1, len(varlist)+1):
        for comb in itertools.combinations(varlist, i):
            temp = constraints_ + list(comb)
            if checkSAT(dimacs_, temp):
                part = count(dimacs_, temp)
                ratio = part / total
                print(str(ratio) + ": ", end="")
            else:
                print("0.0: ", end="")

            for c in comb:
                i = varlist.index(c)
                print(check_[i], end=",")

            print()
    print()

    print("Checking for disjunctions")
    for i in range(1, len(vars)+1):
        for comb in itertools.combinations(vars, i):
            temp = constraints_.copy()
            temp.append(list(comb))
            if checkSAT(dimacs_, temp):
                part = count(dimacs_, temp)
                ratio = part / total
                print(str(ratio) + ": ", end="")
            else:
                print("0.0: ", end="")

            for c in comb:
                i = vars.index(c)
                print(check_[i], end=",")

            print()


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


def check_bias(dimacs_, constraints_, check_, cdir_):
    _features, _clauses, _vcount = read_dimacs(dimacs_)
    total = count(dimacs_, constraints_)
    vars = get_var(check_, _features)

    for v in vars:
        i = vars.index(v)
        print(check_[i], end=": ")
        l = list()
        l.append(int(v))
        temp = constraints_.copy()
        temp.append(l)
        part = count(dimacs_, temp)
        ratio = part / total
        print("Poputlation = " + str(ratio) + " / ", end="")

        hit = 0
        samples = 0
        for file in os.listdir(cdir_):
            if file.endswith('.config'):
                if check_contains(cdir_ + "/" + file, check_[i]):
                    hit += 1
                samples += 1

        ratio = hit / samples
        print("Samples = " + str(ratio))
    print()


def analyze_cpp(dimacs_, cdir_, listfile_):
    configs = list()

    # get list of configurations
    if os.path.exists(listfile_):
        with open(listfile_, 'r') as f:
            for line in f:
                raw = line.split('/')
                configs.append(raw[1])
    else:
        print("checking with no config list")

        common = filter_common(dimacs_, cdir_, configs)
        print(common)


def analyze_cpp_paul(dimacs_, cdir_, reportfile_):
    with open(reportfile_, 'r') as f:
        for line in f:
            #print(line)
            raw = line.split(',')

            if raw[0].startswith('set'):
                names = raw[1].split()
                print(raw[0] + ": ", end='')
                configs = [name + '.config' for name in names]

                common = filter_common(dimacs_, cdir_, configs)
                print(common)


def analyze_infer(dimacs_, cdir_, jsonfile_):
    # read json file
    with open(jsonfile_) as f:
        rawdata = json.load(f)

    i = 1
    for datum in rawdata:
        # get list of configurations
        configs = datum['configs']

        print("(" + str(i) + "/" + str(len(rawdata)) + ") " + datum['key'] + ":" + str(datum['line']) + " (" + str(len(configs)) + "): ", end='')

        # get filtered config list
        filtered = list()
        for c in configs:
            slash = c.split('/')
            name = slash[1].split('_')
            filtered.append(name[1])

        # find common features
        common = filter_common(dimacs_, cdir_, filtered)
        #print(common)

        i += 1


def analyze_clang(dimacs_, cdir_, jsonfile_):
    # read json file
    with open(jsonfile_) as f:
        rawdata = json.load(f)

    i = 1
    for datum in rawdata:
        # get list of configurations
        cf = datum['configurations']
        configs = cf['__value__']
        #print(len(configs))

        if 'investigation' in datum:
            inv = datum["investigation"]
            res = inv["result"]

            if res == "true":
                cset = set()
                for ci in configs:
                    c = str(ci)
                    if '.config' in c:
                        cset.add(c)
                    else:
                        cset.add(c + '.config')

                print("(" + str(i) + "/" + str(len(rawdata)) + ") " + datum['file'] + ":" + str(datum['location']) + " (" + str(len(cset)) + "): ", end='')

                # get filtered config list
                # filtered = list()
                # #for c in configs:
                #     #slash = c.split('/')
                #     #name = slash[1].split('_')
                #     filtered.append(name[1])

                # find common features
                #if datum['source_file'] == 'auto/jdb_tbuf_show.cc':
                common = filter_common(dimacs_, cdir_, cset)
                print(common)

                i += 1

        else:
            cset = set()
            for ci in configs:
                c = str(ci)
                if '.config' in c:
                    cset.add(c)
                else:
                    cset.add(c + '.config')

            print("(" + str(i) + "/" + str(len(rawdata)) + ") " + datum['hash'] + ":" + str(
                datum['source_file']) + "," + str(datum['location']) + " (" + str(len(cset)) + "/" + str(len(configs))  + "): ", end='')

            common = filter_common(dimacs_, cdir_, cset)

            # if datum['hash'] == 'e260e94feabb02f22ed397b00a425c63':
            #     common = filter_common(dimacs_, cdir_, cset)
            # print()

            i += 1


def analyze_build(dimacs_, cdir_, configlist_):
    configs = list()

    i = 0
    # read return codes
    with open(configlist_) as f:
        for line in f:
            if not '0' in line:
                configs.append(str(i) + ".config")

            i += 1

    print("Number of failed configs: " + str(len(configs)))

    common = filter_common(dimacs_, cdir_, configs)
    # print(common)

    return common


def jsonLineChange(inFile, outFile):
    if os.path.exists(inFile):
        with open(inFile) as f:
            data = json.load(f)

    i = 1
    for datum in data:
        cf = datum['configurations']
        configs = cf#['__value__']
        lc = datum['location']

        # if '@function' in lc:
        #     symbol = lc['@function']
        # else:
        #     symbol = ""
        #
        # file = lc['@file']
        # line = lc['@line']
        #
        # print("" + str(i) + "/" + str(len(data)) + "," + file + "," + symbol + "," + line + "," + str(
        #     len(configs)))

        print("(" + str(i) + "/" + str(len(data)) + ") " + str(lc) + " (" + str(len(configs)) + "): ")

        i += 1

    with open(outFile, 'w') as outfile:
        json.dump(data, outfile, indent=1)


def createCSV(inFile, outFile):
    if os.path.exists(inFile):
        with open(inFile) as f:
            data = json.load(f)

    i = 1
    for datum in data:
        cf = datum['configurations']
        configs = cf#['__value__']
        lc = datum['location']
        inv = datum["investigation"]

        # if '@function' in lc:
        #     symbol = lc['@function']
        # else:
        #     symbol = ""
        #
        # file = lc['@file']
        # line = lc['@line']
        #
        # print("" + str(i) + "/" + str(len(data)) + "," + file + "," + symbol + "," + line + "," + str(
        #     len(configs)))

        print(datum['hash'], end=",")
        print(datum['category'], end=",")
        print(datum['file'], end=",")
        print(lc['line'], end=",")
        print("\"" + datum['description'] + "\"", end=",")
        print(inv["result"], end=",")
        print("\"" + inv["notes"] + "\"", end=",")
        print()
        i += 1

    with open(outFile, 'w') as outfile:
        json.dump(data, outfile, indent=1)

target = "fiasco_17_10"
dimacs = "/home/jeho-lab/git/kconfig_case_studies/cases/" + target + "/build/kconfig.dimacs"

cdir = "/home/jeho-lab/git/kconfig_case_studies/cases/" + target + "/bugs/configs"
# #cdir = "/home/jeho/kmax/kconfig_case_studies/cases/" + target + "/build/e260/A_D_H"

# inferfile = "/home/jeho/kmax/kconfig_case_studies/bugs/infer/axtls/mapping.json"
# analyze_infer(dimacs, cdir, inferfile)

# clangfile = "/home/jeho/kmax/kconfig_case_studies/bugs/clang-4.0/axtls/unique.json.results.filtered"#axtls_clang-4.0_unique.json"
# # clangfile = "/home/jeho/Downloads/Jeho/A_D_H/axtls_2_1_4/clang-4.0_results/unique.json.results.filtered"
# analyze_clang(dimacs, cdir, clangfile)

# cppfile = "/home/jeho/kmax/kconfig_case_studies/bugs/toybox_bug_report/config_occurrence_lists/configs_with_bugs.txt"
# cppfile_paul = "/home/jeho/kmax/kconfig_case_studies/bugs/cppcheck/busybox_bug_report/busybox_report_unique.txt"
# analyze_cpp_paul(dimacs, cdir, cppfile_paul)

# inFile = "/home/jeho/kmax/kconfig_case_studies/bugs/clang-4.0/busybox/picked.json"
# outFile = "/home/jeho/kmax/kconfig_case_studies/bugs/clang-4.0/busybox/picked_linewrap.json"
# jsonLineChange(clangfile, clangfile + "csv")
# createCSV(clangfile, clangfile + "csv")

target = "fiasco_17_10"
configlist = "/home/jeho-lab/git/kconfig_case_studies/cases/" + target + "/build/configs/return_codes.txt"
cdir = "/home/jeho-lab/kmax/kconfig_case_studies/cases/" + target + "/build/configs"

constfile = os.path.dirname(dimacs) + "/constraints.txt"
features, clauses, vcount = read_dimacs(dimacs)
const = read_constraints(constfile, features)

check = analyze_build(dimacs, cdir, configlist)

check_bias(dimacs, const, check, cdir)
check_ratio(dimacs, const, check)
