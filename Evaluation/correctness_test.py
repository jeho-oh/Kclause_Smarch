import os
from subprocess import getoutput, check_call
from smarch import gen_dimacs, SHARPSAT
from kconfigIO import read_dimacs, is_int

CONFIG = 'bash /home/jeho/kmax/kconfig_case_studies/checkSamples.sh'


def test_kbuild(target_, configs_):
    # run vagrant for config check
    if target_ == 'fiasco_17_10':
        check_call(CONFIG + " " + target_ + " " + configs_ + " " + target_ + "/src/kernel/fiasco", shell=True)
    else:
        check_call(CONFIG + " " + target_ + " " + configs_ + " " + target_, shell=True)


def get_commmon(dimacs_, cdir_, configlist_, include_=True):
    common = list()
    configs = list()
    init = True

    # check if config dir exists
    if not os.path.exists(cdir_):
        print("randconfig not found")
        return

    # get list of configurations
    if os.path.exists(configlist_):
        with open(configlist_, 'r') as f:
            for line in f:
                raw = line.split('/')
                configs.append(raw[1])
    else:
        print("checking with no config list")

    # get features and clauses
    _features, _clauses, _vars = read_dimacs(dimacs_)
    _names = [i[1] for i in _features]

    # iterate over each randconfig configurations
    for file in os.listdir(cdir_):
        if (include_ and (file in configs)) or (not include_ and (file not in configs)) or (len(configs) == 0):
            with open(cdir_ + "/" + file, 'r') as f:
                print(file)
                _existing = set()

                sol = list()
                for line in f:
                    # line: # FEATURE is not set
                    if line.startswith('#'):
                        line = line[0:len(line) - 1]
                        data = line.split()
                        if len(data) > 4:
                            if data[1] in _names:
                                i = _names.index(data[1])
                                _existing.add(data[1])
                                if i != -1:
                                    sol.append('-' + _features[i][1])
                    # line: FEATURE=y or FEATURE="nonbool value"
                    else:
                        line = line[0:len(line) - 1]
                        data = line.split('=')
                        if len(data) > 1:
                            if data[0] in _names:
                                i = _names.index(data[0])
                                _existing.add(data[0])
                                # FEATURE=y
                                if data[1] == 'y':
                                    sol.append(str(_features[i][1]))
                                    if 'SMACK' in _features[i][1]:
                                        print("yes!")
                                # FEATURE=empty string or 0
                                elif data[1] == '\"\"' or data[1] == '0':
                                    if _features[i][3] != '\"\"' and _features[i][3] != '0':
                                        sol.append('-' + _features[i][1])
                                # FEATURE='nonbool value'
                                else:
                                    sol.append(str(_features[i][1]))

                if init:
                    common = sol
                    init = False
                else:
                    for s in common:
                        if s not in sol:
                            common.remove(s)

    return common


def test_randconfig_kmax(dimacs_):
    passed = 0
    common = list()
    init = True

    # check if randconfig exists
    cdir = os.path.dirname(dimacs_) + "/correctness/randconfigs/"
    if not os.path.exists(cdir):
        print("randconfig not found")
        return

    # get features and clauses
    _features, _clauses, _vars = read_dimacs(dimacs_)
    _names = [i[1] for i in _features]

    # iterate over each randconfig configurations
    for file in os.listdir(cdir):
        if file.endswith('.config'):
            with open(cdir + "/" + file, 'r') as f:
                _existing = set()

                sol = list()
                for line in f:
                    # line: # FEATURE is not set
                    if line.startswith('#'):
                        line = line[0:len(line) - 1]
                        data = line.split()
                        if len(data) > 4:
                            if data[1] in _names:
                                i = _names.index(data[1])
                                _existing.add(data[1])
                                if i != -1:
                                    sol.append('-' + _features[i][0])
                    # line: FEATURE=y or FEATURE="nonbool value"
                    else:
                        line = line[0:len(line) - 1]
                        data = line.split('=')
                        if len(data) > 1:
                            if data[0] in _names:
                                i = _names.index(data[0])
                                _existing.add(data[0])
                                if data[1] == 'y':
                                    sol.append(str(_features[i][0]))
                                    #print(_features[i][0])
                                elif data[1] == '\"\"' or data[1] == '0':
                                    if _features[i][3] != '\"\"' and _features[i][3] != '0':
                                        sol.append('-' + _features[i][0])
                                        #print('-' + _features[i][0])
                                    # else:
                                    #     #print(_features[i][1])
                                else:
                                    sol.append(str(_features[i][0]))
                                    #print(str(_features[i][0]))

                    outfile = cdir + '/check.dimacs'
                    gen_dimacs(_vars, _clauses, sol, outfile)
                    res = getoutput(SHARPSAT + ' -q ' + outfile)
                    print(line + ": " + str(res))
                    if not is_int(res):
                        print(file + " failed")
                        return

                # set all nonexistent variables to false
                # for f in _features:
                #     if f[1] not in _existing:
                #         sol.append('-' + str(f[0]))

                # sol.append('-55')
                # sol.append('-109')

                outfile = cdir + '/check.dimacs'

                gen_dimacs(_vars, _clauses, sol, outfile)
                res = getoutput(SHARPSAT + ' -q ' + outfile)

                if is_int(res):
                    if res != '1':
                        print(file + ": " + str(res))
                    else:
                        passed += 1
                else:
                    print(file + ": " + str(res))
                    if init:
                        common = sol
                        init = False
                    else:
                        for s in common:
                            if s not in sol:
                                common.remove(s)

    print("Passed:" + str(passed))
    print(common)


def test_randconfig_kcr(dimacs_, target_):
    # check if randconfig exists
    cdir = os.path.dirname(dimacs_) + "/randconfigs"
    if not os.path.exists(cdir):
        print("randconfig not found")
        return

    # get features and clauses
    _features, _clauses, _vars = read_dimacs(dimacs_)
    kf, kc, kv = read_dimacs("/home/jeho/kmax/kconfig_case_studies/cases/" + target_ + "/kconfig.dimacs")
    _names = list()
    kn = [i[1] for i in kf]

    prefix = False

    for f in _features:
        if len(f) > 2:
            name = f[1]
            for i in range(2, len(f)):
                name = name + ' ' + f[i]
            if not name.startswith('CONFIG_') and prefix:
                name = 'CONFIG_' + name
            _names.append(name)
        else:
            name = f[1]
            if not name.startswith('CONFIG_') and prefix:
                name = 'CONFIG_' + name
            _names.append(name)

    # iterate over each randconfig configurations
    for file in os.listdir(cdir):
        if file.endswith('.config'):
            with open(cdir + "/" + file, 'r') as f:
                sol = set()
                ambig = set()
                for line in f:
                    if line.startswith('#'):
                        line = line[0:len(line) - 1]
                        data = line.split()
                        if len(data) > 4:
                            if data[1] in _names:
                                i = _names.index(data[1])
                                if i != -1:
                                    sol.add('-' + _features[i][0])
                            # else:
                            #     print(line)
                    else:
                        line = line[0:len(line) - 1]
                        data = line.split('=')
                        if len(data) > 1:
                            if data[1] == 'y':
                                if data[0] in _names:
                                    i = _names.index(data[0])
                                    sol.add(str(_features[i][0]))
                                # else:
                                #     print('y: '+data[0])
                            elif data[1] == '\"\"' or data[1] == '0':
                                if data[0] in kn:
                                    k = kn.index(data[0])
                                    if kf[k][3] != '\"\"' and kf[k][3] != '0':
                                        feature = data[0] + '=n'
                                        if feature in _names:
                                            i = _names.index(feature)
                                            sol.add(str(_features[i][0]))
                                        # else:
                                        #     print("Not in dimacs: " + feature)
                                    else:
                                        # print('n: ' + line)
                                        ambig.add(data[0])
                                        # feature = data[0] + '=n'
                                        # if feature in _names:
                                        #     i = _names.index(feature)
                                        #     sol.add(str(_features[i][0]))
                            else:
                                temp = line.replace('\"', '')
                                feature = temp.replace('\\\\', '\\')
                                if feature in _names:
                                    i = _names.index(feature)
                                    sol.add(str(_features[i][0]))
                                else:
                                    if data[0] in kn:
                                        k = kn.index(data[0])
                                        dv = kf[k][3].replace('\"', '')
                                        dv = dv.replace('\\\\', '\\')
                                        feature = data[0] + '=' + dv
                                        if feature in _names:
                                            i = _names.index(feature)
                                            sol.add(str(_features[i][0]))
                                        # else:
                                        #     print("Not in dimacs: " + feature)
                                    else:
                                        for ft in kn:
                                            print(ft)
                                        print('nb: ' + line + "," + feature)

                    # outfile = cdir + '/check.dimacs'
                    # gen_dimacs(_vars, _clauses, sol, outfile)
                    # res = getoutput(SHARPSAT + ' -q ' + outfile)
                    # print(line + ": " + str(res))
                    # print(sol)
                    # if not is_int(res):
                    #     print(file + " failed")
                    #     return

                outfile = cdir + '/check.dimacs'
                gen_dimacs(_vars, _clauses, sol, outfile)
                res = getoutput(SHARPSAT + ' -q ' + outfile)

                if is_int(res):
                    print(file + "," + str(len(_features) - len(sol)) + "," + str(len(ambig)) + "," + str(res) + "," + str(ambig))
                else:
                    print(file + "," + str(len(_features) - len(sol)) + "," + str(len(ambig)) + ",0")


