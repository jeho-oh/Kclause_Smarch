import os
from anytree import AnyNode
from anytree.importer import JsonImporter
from subprocess import getoutput, check_call
from kconfigIO import read_dimacs, read_config_kmax, is_int
from smarch import gen_dimacs, SHARPSAT


# select a cube based on given  number
def traverse_cube(current_, sol_, number_):
    _precision = -1

    for node in current_.children:
        cube = list(map(int, node.cube))
        if all(x in sol_ for x in cube):
            current_ = node
            if len(node.children) == 0:
                _precision = node.count
            else:
                _precision = 0
            break
        else:
            number_ += node.count

    return current_, _precision, number_


def get_rank(dimacs_, dir_):
    # read dimacs file for feature list
    _features, _clauses, _vars = read_dimacs(dimacs_)

    # read tree structure from file
    _treefile = os.path.dirname(dimacs_) + '/smarch/tree.json'
    # node = AnyNode(count=-1, cube=[])

    if os.path.exists(_treefile):
        with open(_treefile, 'r') as file:
            data = file.read()
            importer = JsonImporter()
            _root = importer.import_(data)
            total = _root.count
    else:
        print("ERROR: tree file not found!")
        return

    _cdir = dir_
    for file in os.listdir(_cdir):
        if file.endswith('.config'):
            # convert config file into variable list
            sol = read_config_kmax(_features, _cdir + "/" + file)

            # traverse tree based on solution
            _node = _root
            _precision = 0
            _number = 0
            while _precision == 0:
                _node, _precision, _number = traverse_cube(_node, sol, _number)

            if _precision > 0:
                print(str(_number) + "," + str(_precision))
            else:
                print("ERROR: tree traverse failure")


def get_rank_kcr(dimacs_, solset_):

    # read tree structure from file
    _treefile = os.path.dirname(dimacs_) + '/smarch/tree.json'
    # node = AnyNode(count=-1, cube=[])

    if os.path.exists(_treefile):
        with open(_treefile, 'r') as file:
            data = file.read()
            importer = JsonImporter()
            _root = importer.import_(data)
            total = _root.count
    else:
        print("ERROR: tree file not found!")
        return

    for sol in solset_:
        # traverse tree based on solution
        _node = _root
        _precision = 0
        _number = 0
        while _precision == 0:
            _node, _precision, _number = traverse_cube(_node, sol, _number)

        if _precision > 0:
            print(str(_number/total) + "," + str(_precision/total))
        else:
            print("ERROR: tree traverse failure")


def get_rank_unigen(dimacs_, sampleFile_):
    # read dimacs file for feature list
    _features, _clauses, _vars = read_dimacs(dimacs_)

    # read tree structure from file
    _treefile = os.path.dirname(dimacs_) + '/smarch/tree.json'
    # node = AnyNode(count=-1, cube=[])

    if os.path.exists(_treefile):
        with open(_treefile, 'r') as file:
            data = file.read()
            importer = JsonImporter()
            _root = importer.import_(data)
            total = _root.count
    else:
        print("ERROR: tree file not found!")
        return

    with open(sampleFile_, 'r') as f:
        i = 1
        for line in f:
            line = line[1:len(line)]
            raw = line.split()
            if len(raw) != 0:
                sol = raw[1:len(raw)-1]
                #print(sol)
                # traverse tree based on solution
                _node = _root
                _precision = 0
                _number = 0

                _cdir = os.path.dirname(dimacs_) + '/'
                sdimacs = _cdir + "/sample.dimacs"
                ssol = _cdir + "/" + "sample.sol"
                gen_dimacs(_vars, _clauses, sol, sdimacs)
                getoutput("minisat " + sdimacs + " " + ssol)

                _outfile = os.path.dirname(sampleFile_) + '/validCheck.dimacs'
                gen_dimacs(_vars, _clauses, sol, _outfile)
                res = getoutput(SHARPSAT + ' -q ' + _outfile)

                fsol = list()
                with open(ssol, 'r') as f:
                    fsol = f.read().split()
                    del fsol[0]

                if is_int(res):
                    print(res, end=',')
                    while _precision == 0:
                        _node, _precision, _number = traverse_cube(_node, fsol, _number)

                    if _precision > 0:
                        print(str(_number/total) + "," + str(_precision/total))
                    else:
                        print("ERROR: tree traverse failure")
                else:
                    print("ERROR: sample invalid")
            i += 1
