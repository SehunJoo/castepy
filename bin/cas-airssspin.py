#!/usr/bin/env python

import sys
from cell import Cell


#===============================================================================
# Main
#==============================================================================

if __name__ == "__main__":

    filename = sys.argv[1]
    cell = Cell.from_file(filename)
    cell.set_spin('mp')
    cell.to_file()
