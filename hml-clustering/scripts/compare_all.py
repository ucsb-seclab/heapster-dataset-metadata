import sys
import glob
import itertools
import subprocess
import multiprocessing
from helpers import *
import time

BINDIFF   = '/opt/bindiff/bindiff'

def bindiff(primary, secondary):
    primary, secondary = sorted([primary, secondary])
    if get_db(primary, secondary) is not None:
        return

    subprocess.check_call([BINDIFF, "--nologo",
                           "--output_dir", CACHEDIR,
                           "--primary",   primary + ".BinExport",
                           "--secondary", secondary + ".BinExport"])

def main():
    targets = get_targets()
    pool  = multiprocessing.Pool(processes=10)
    combs = sorted(list(itertools.combinations(targets, 2)))
    print('Total number of combinations: %d' % len(combs))
    sys.stdout.flush()

    for i, (primary, secondary) in enumerate(combs):
        res = pool.apply_async(bindiff, (primary, secondary))

    pool.close()
    pool.join()

if __name__ == "__main__":
    main()
