import random
import os
from subprocess import check_call

from smarch import read_dimacs

BUILD = 'bash /home/jeho/kmax/kconfig_case_studies/buildSamples.sh'


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


# def gen_configs_kmax(dimacs_, cdir_):
#     sdir = os.path.dirname(dimacs_) + "/smarch/samples"
#     if not os.path.exists(sdir):
#         print("ERROR: sample folder does not exist")
#         return
#
#     features, clauses, vars = read_dimacs(dimacs_)
#
#     # generate .config files from samples
#     for file in os.listdir(sdir):
#         if file.endswith('.sol'):
#             with open(sdir + "/" + file, 'r') as f:
#                 name = file.split('.')[0]
#                 data = f.read().split()
#                 del data[0]
#                 config = ""
#                 for sel in data:
#                     val = int(sel)
#                     feature = features[abs(val) - 1]
#
#                     if val > 0:
#                         if feature[2] == 'nonbool':
#                             config = config + feature[1] + "=" + feature[3] + "\n"
#                         else:
#                             config = config + feature[1] + "=y\n"
#
#                     elif val < 0:
#                         if feature[2] == 'nonbool':
#                             if is_int(feature[3]):
#                                 config = config + feature[1] + "=0\n"
#                             else:
#                                 config = config + feature[1] + "=\"\"\n"
#                         else:
#                             config = config + "# " + feature[1] + " is not set\n"
#
#                 with open(cdir_ + "/" + name + ".config", 'w') as outfile:
#                     outfile.write(config)
#                     outfile.close()
#
#     print("Configs generated")


def gen_configs_kmax(dimacs_, samples_, cdir_):
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


def gen_configs_kcr(dimacs_):
    cdir = os.path.dirname(dimacs_) + "/configs"
    if not os.path.exists(cdir):
        os.makedirs(cdir)
    sdir = os.path.dirname(dimacs_) + "/smarch/samples"
    if not os.path.exists(sdir):
        print("ERROR: sample folder does not exist")
        return

    flist = set()
    with open(os.path.dirname(dimacs_) + '/output.features') as file:
        for line in file:
            flist.add(line[0:len(line) - 1])

    features, clauses, vars = read_dimacs(dimacs_)
    _indexes = [i[0] for i in features]

    # generate .config files from samples
    for file in os.listdir(sdir):
        if file.endswith('.sol'):
            with open(sdir + "/" + file, 'r') as f:
                name = file.split('.')[0]
                data = f.read().split()
                del data[0]
                config = ""
                for sel in data:
                    val = int(sel)
                    if str(abs(val)) in _indexes:
                        i = _indexes.index(str(abs(val)))
                        feature = features[i][1]
                        if not feature.startswith('CONFIG_'):
                            feature = 'CONFIG_' + feature

                        if feature in flist:
                            flist.remove(feature)
                        #print(flist)

                        if feature != 'MODULES' and feature != 'CONFIG_MODULES' and 'CHOICE_' not in feature:
                            if val > 0:
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
                            elif val < 0:
                                if '=' not in feature:
                                    config = config + "# " + feature + " is not set\n"

                for fv in flist:
                    r = random.random()
                    if r < 0.5:
                        config = config + "# " + fv + " is not set\n"
                    else:
                        config = config + fv + "=y\n"

                with open(cdir + "/" + name + ".config", 'w') as outfile:
                    outfile.write(config)
                    outfile.close()


def convert_kcr_to_kmax(kcr_, kmax_):
    sdir = os.path.dirname(kcr_) + "/smarch/samples"
    if not os.path.exists(sdir):
        print("ERROR: sample folder does not exist")
        return

    solset = list()

    kcrf, kcrc, kcrv = read_dimacs(kcr_)
    kmaxf, kamxc, kmaxv = read_dimacs(kmax_)

    _kcri = [i[0] for i in kcrf]

    # generate .config files from samples
    for file in os.listdir(sdir):
        if file.endswith('.sol'):
            with open(sdir + "/" + file, 'r') as f:
                name = file.split('.')[0]
                data = f.read().split()
                del data[0]
                config = set()
                sol = set()

                for sel in data:
                    val = int(sel)
                    if str(abs(val)) in _kcri:
                        i = _kcri.index(str(abs(val)))
                        feature = kcrf[i][1]
                        if not feature.startswith('CONFIG_'):
                            feature = 'CONFIG_' + feature

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
                    if kf[1] in config:
                        sol.add(kf[0])
                    elif ('-'+kf[1]) in config:
                        sol.add('-' + kf[0])
                    else:
                        r = random.random()
                        if r < 0.5:
                            sol.add(kf[0])
                        else:
                            sol.add('-' + kf[0])

                solset.append(sol)

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
                            sol.append('-' + features_[i][0])
            # line: FEATURE=y or FEATURE="nonbool value"
            else:
                line = line[0:len(line) - 1]
                data = line.split('=')
                if len(data) > 1:
                    if data[0] in _names:
                        i = _names.index(data[0])
                        _existing.add(data[0])
                        if data[1] == 'y':
                            sol.append(str(features_[i][0]))
                        elif data[1] == '\"\"' or data[1] == '0':
                            if features_[i][3] != '\"\"' and features_[i][3] != '0':
                                sol.append('-' + features_[i][0])
                            else:
                                sol.append(features_[i][0])
                                # r = random.random()
                                # sol.append('-' + features_[i][0])
                                # if r < 0.5:
                                #     sol.append(features_[i][0])
                                # else:
                                #     sol.append('-' + features_[i][0])
                        else:
                            sol.append(str(features_[i][0]))

    # set all nonexistent variables to false
    for f in features_:
        if f[1] not in _existing:
            sol.append('-' + str(f[0]))

    return sol


def benchmark_PM(configs_, fvfile_, fifile_):
    fvlist = dict()
    filist = dict()

    with open(fvfile_, 'r') as f:
        for line in f:
            raw = line.split(': ')
            fvlist[raw[0]] = raw[1]

    with open(fifile_, 'r') as f:
        for line in f:
            raw = line.split(': ')
            filist[raw[0]] = raw[1]

    for file in os.listdir(configs_):
        if file.endswith('.config'):
            with open(configs_ + "/" + file, 'r') as f:
                selected = set()
                perf = 0.0
                for line in f:
                    if not(line.startswith('#')):
                        line = line[0:len(line) - 1]
                        data = line.split('=')
                        if len(data) > 1:
                            if data[0] in fvlist:
                                perf = perf + float(fvlist[data[0]])
                        selected.add(data[0])

                for fi in filist:
                    fif = fi.split('#')
                    if all(x in selected for x in fif):
                        perf = perf + float(filist[fi])

                print(file + "," + str(perf))


def build_samples(target_, configs_):
    # run vagrant for build
    if target_ == 'fiasco_17_10':
        check_call(BUILD + " " + target_ + " " + configs_ + " " + target_ + "/src/kernel/fiasco", shell=True)
    else:
        check_call(BUILD + " " + target_ + " " + configs_ + " " + target_, shell=True)
