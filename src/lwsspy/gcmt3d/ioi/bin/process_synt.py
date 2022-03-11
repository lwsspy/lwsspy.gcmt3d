"""
:Author:
    Lucas Sawade (lsawade-at-princeton.edu)

:Last Modified:
    2022.03.04 11.00
"""
from os import environ
# This is sooo important for parallel processing
# If you don't set this numpy, mkl, etc. will try to use threads
# for processing, but you do not want that, because you want to 
# distribute work to the different cores manually. If this is not 
# set, the different cores will fight for threads!!!!
environ["OMP_NUM_THREADS"] = '1'
environ["OMP_NUM_THREADS"] = '1;

from sys import argv, exit
from ..functions.processing import process_synt


def bin():
    """

    Usage:

        gcmt3d-process-synt eventdir

    This script calls a python function that process the synthetics and saves 
    them in the synt/ folder.

    """

    # Get args or print usage statement 
    if (len(argv) != 2) or (argv[1] == '-h') or (argv[1] == '--help'):
        print(bin.__doc__)
        exit()
    else:
        outdir = argv[1]

    # Run the initializer
    process_synt(outdir)
