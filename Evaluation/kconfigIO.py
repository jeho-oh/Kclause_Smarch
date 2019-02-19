import random
import os
import shutil
from subprocess import check_call
from pathlib import Path

from Smarch.smarch import read_dimacs

home = str(Path.home())
BUILD = 'bash ' + home + '/kmax/kconfig_case_studies/buildSamples.sh'


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def gen_configs_kmax(dimacs_, samples_, cdir_):
    # remove existing contents on the folder
    for f in os.listdir(cdir_):
        file_path = os.path.join(cdir_, f)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)

    # get feature information
    features, clauses, vars = read_dimacs(dimacs_)

    # generate .config files from samples
    i = 0
    for s in samples_:
        config = ""
        for sel in s:
            feature = features[abs(sel) - 1]

            if sel > 0:
                if feature[2] == 'nonbool':
                    config = config + feature[1] + "=" + feature[3] + "\n"
                else:
                    config = config + feature[1] + "=y\n"

            elif sel < 0:
                if feature[2] == 'nonbool':
                    if is_int(feature[3]):
                        config = config + feature[1] + "=0\n"
                    else:
                        config = config + feature[1] + "=\"\"\n"
                else:
                    config = config + "# " + feature[1] + " is not set\n"

        with open(cdir_ + "/" + str(i) + ".config", 'w') as outfile:
            outfile.write(config)
            outfile.close()

        i += 1

    print("Configs generated")


def gen_configs_kcr(target_, dimacs_, samples_, cdir_):
    freevar = set()
    with open(os.path.dirname(dimacs_) + '/' + target_ + '.features') as file:
        for line in file:
            feature = line[0:len(line) - 1]
            if target_ not in ('axtls_2_1_4', 'uClibc-ng_1_0_29'):
                if not feature.startswith('CONFIG_'):
                    feature = 'CONFIG_' + feature
            freevar.add(feature)

    features, clauses, vars = read_dimacs(dimacs_)
    _indexes = [i[0] for i in features]

    # generate .config files from samples
    n = 0
    for s in samples_:
        config = ""
        for sel in s:
            if abs(sel) in _indexes:
                i = _indexes.index(abs(sel))
                feature = features[i][1]

                if target_ not in ('axtls_2_1_4', 'uClibc-ng_1_0_29'):
                    if not feature.startswith('CONFIG_'):
                        feature = 'CONFIG_' + feature

                if feature in freevar:
                    freevar.remove(feature)

                if feature != 'MODULES' and feature != 'CONFIG_MODULES' and 'CHOICE_' not in feature:
                    if sel > 0:
                        if '=' in feature:
                            if '=' in feature:
                                finfo = feature.split('=')
                                if is_int(finfo[1]):
                                    config = config + feature + "\n"
                                else:
                                    if finfo[1] == 'n':
                                        config = config + finfo[0] + '=0\n'
                                    else:
                                        config = config + finfo[0] + '=\"' + finfo[1] + "\"\n"
                        else:
                            config = config + feature + "=y\n"
                    elif sel < 0:
                        if '=' not in feature:
                            config = config + "# " + feature + " is not set\n"
                else:
                    if feature in freevar:
                        freevar.remove(feature)

        for fv in freevar:
            r = random.random()
            if r < 0.5:
                config = config + "# " + fv + " is not set\n"
            else:
                config = config + fv + "=y\n"

        with open(cdir_ + "/" + str(n) + ".config", 'w') as outfile:
            outfile.write(config)
            outfile.close()

        n += 1

    print("Configs generated")


def convert_kcr_to_kmax(kcr_, kmax_, solset_):
    solset = list()

    kcrf, kcrc, kcrv = read_dimacs(kcr_)
    kmaxf, kamxc, kmaxv = read_dimacs(kmax_)

    _kcri = [i[0] for i in kcrf]

    # generate .config files from samples
    for sol in solset_:
        config = set()
        ksol = set()

        for sel in sol:
            val = int(sel)
            if abs(val) in _kcri:
                i = _kcri.index(abs(val))
                feature = kcrf[i][1]
                # if not feature.startswith('CONFIG_'):
                #     feature = 'CONFIG_' + feature

                if feature != 'MODULES' and feature != 'CONFIG_MODULES' and 'CHOICE_' not in feature:
                    if val > 0:
                        if '=' in feature:
                            if '=' in feature:
                                finfo = feature.split('=')
                                if finfo[1] == 'n':
                                    config.add('-' + finfo[0])
                                else:
                                    config.add(finfo[0])
                        else:
                            config.add(feature)
                    elif val < 0:
                        if '=' not in feature:
                            config.add('-' + feature)

        for kf in kmaxf:
            if str(kf[1]) in config:
                ksol.add(kf[0])
            elif ('-' + str(kf[1])) in config:
                ksol.add(-1 * kf[0])
            else:
                r = random.random()
                if r < 0.5:
                    ksol.add(kf[0])
                else:
                    ksol.add(-1 * kf[0])

        solset.append(ksol)

    return solset


def read_config_kmax(features_, config_):
    sol = list()
    _existing = set()
    _names = [i[1] for i in features_]

    with open(config_, 'r') as f:
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
                            sol.append(-1 * features_[i][0])
                    # else:
                    #     print(line)
            # line: FEATURE=y or FEATURE="nonbool value"
            else:
                line = line[0:len(line) - 1]
                data = line.split('=')
                if len(data) > 1:
                    if data[0] in _names:
                        i = _names.index(data[0])
                        _existing.add(data[0])
                        if data[1] == 'y':
                            sol.append(features_[i][0])
                        elif data[1] == '\"\"' or data[1] == '0':
                            if features_[i][3] != '\"\"' and features_[i][3] != '0':
                                sol.append(-1 * features_[i][0])
                            else:
                                sol.append(features_[i][0])
                                # r = random.random()
                                # sol.append('-' + features_[i][0])
                                # if r < 0.5:
                                #     sol.append(features_[i][0])
                                # else:
                                #     sol.append('-' + features_[i][0])
                        else:
                            sol.append(features_[i][0])
                    # else:
                    #     print(line)

    # set all nonexistent variables to false
    for f in features_:
        if f[1] not in _existing:
            sol.append(-1 * f[0])

    return sol


def read_configs_kmax(features_, cdir_):
    samples = list()

    for file in os.listdir(cdir_):
        if file.endswith('.config'):
            # convert config file into variable list
            sol = read_config_kmax(features_, cdir_ + "/" + file)
            samples.append(sol)

    return samples


def build_samples(target_, configs_):
    # run vagrant for build
    if target_ == 'fiasco_17_10':
        check_call(BUILD + " " + target_ + " " + configs_ + " " + target_ + "/src/kernel/fiasco", shell=True)
    else:
        check_call(BUILD + " " + target_ + " " + configs_ + " " + target_, shell=True)
