## Extracting Kconfig Constraints

Build the Kconfig parser:

    make

Here is an example of converting Kconfig constraints to a dimacs file:

    cd ~/src/busybox
    check_dep --dimacs Config.in | tee kconfig.kmax | python dimacs.py -d --include-nonvisible-bool-defaults --remove-orphaned-nonvisibles | tee kconfig.dimacs

`check_dep` using the Linux Kconfig tool to extract constraints into
an intermediate format (the `kconfig.kmax` file).  `dimacs.py`
translates these constraints uses our model of Kconfig semantcs in
conjunctive normal form (CNF) and produces a dimacs file (the
`kconfig.dimacs` file).

## Information about the Linux Kconfig Implementation

The Kconfig parser in this directory has been copied from the
linux-4.12.8/scripts/kconfig directory.  `zconf.hash.c_shipped` has
been copied to `zconf.hash.c`.  The following minor changes have been
made:

1. In `expr.c`, the `static` keyword has been removed from
   `expr_compare_type` so it can be used by `check_dep.c`.

2. In `expr.h`, `struct symbol` is given two more fields:

        bool searched;
        bool depends;
3. 	In `expr.h`, `struct_property` is given an extra field in order to
       save a select's original dependency `if` dependency, if any.

        struct expr *original_expr;

    This is used in conjunction with a change in `menu.c` that saves
    the original original after parsing the select line.
    
          if (P_SELECT == type) {
            // hang on to the original for kmax
            prop->original_expr = prop->visible.expr;
          }

    The reason this is done is to avoid clause blowup in dimacs due to
    a config's entire dependencies between conjoined with select's
    `if` dependencies.  Our Boolean formulae already account for
    dependencies and don't need them on the select.
