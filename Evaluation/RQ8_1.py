import os

from Smarch.smarch import count, read_dimacs, get_var, checkSAT


def kmax_kcr_rdiff(target_, kmax_, kcr_):
    mf, mc, mv = read_dimacs(kmax_)
    cf, cc, cv = read_dimacs(kcr_)

    mtotal = count(kmax_, [])
    ctotal = count(kcr_, [])

    mfnames = list(i[1] for i in mf)
    kfnames = list(i[1] for i in cf)

    if target_ in ('fiasco_17_10', 'busybox_1_28_0'):
        kfnames = ['CONFIG_' + s for s in kfnames]

    for f in mfnames:
        if f in kfnames:
            mvar = get_var([f], mf)

            if checkSAT(kmax_, [mvar]):
                mp = count(kmax_, [mvar])
                mr = mp/mtotal

                newf = f
                if target_ in ('fiasco_17_10', 'busybox_1_28_0'):
                    newf = f[7:]

                print(f, end="")

                cvar = get_var([newf], cf)

                if checkSAT(kcr_, [cvar]):
                    cp = count(kcr_, [cvar])
                    cr = cp / ctotal

                    print(": " + str(cr - mr))

target = "uClibc-ng_1_0_29"
kmax = os.path.dirname(os.path.realpath(__file__)) + "/FM/" + target + ".dimacs"
kcr = os.path.dirname(os.path.realpath(__file__)) + "/FM/kcr/" + target + ".dimacs"

kmax_kcr_rdiff(target, kmax, kcr)




