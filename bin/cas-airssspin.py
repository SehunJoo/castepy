#!/usr/bin/env python

import sys
from cell import Cell
from param import Param


#===============================================================================
# Main
#==============================================================================

if __name__ == "__main__":

    filename = sys.argv[1]
    cell = Cell.from_file(filename)
    param = Param.from_file(filename.replace('.cell','.param'))
    if param.param['spin_polarized'] == 'true':
        cell.set_spin('mp')
        print("set initial spin for spin-polarized calculation")
    else:
        print("spin-unpolarized calculation")
    cell.to_file()
