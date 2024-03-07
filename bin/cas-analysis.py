#!/usr/bin/env python

import os
import argparse
from cell import Cell
from param import Param


#===============================================================================
# Arguments
#==============================================================================

def get_args():
    """
    Parse arguments
    """

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Retrieve structures from Materials Project database",
        epilog="examples:\n"
               "    mp_query.py -el Li,Ni,O\n"
               "    mp_query.py -el Li,Ni,O -in 20\n"
    )
    parser.add_argument('-s', '--seed', type=str, dest='seed',
                        default=None,
                        help='seed')
    parser.add_argument('-m', '--mode', type=str, dest='mode',
                        default='airss_spin',
                        help='Nmode')

    args = parser.parse_args()


    # banner

    banner = [
        f"",
        f"     {os.path.basename(__file__)}",
        f"",
        f"       Author: Se Hun Joo (shj29@cam.ac.uk)",
        f"",
        f"       Summary of arguments",
        f""
    ]

    banner += [
        f"         {attr:<20}: {getattr(args, attr)}"
        for attr in dir(args)
        if not attr.startswith('_')
    ]

    print("\n".join(banner) + "\n")

    return args

#===============================================================================
# Funcitons
#==============================================================================


def calc_thickness(seed):
    echo "$f"                                                                                                           
    lattc=$(awk '/CELL/{print $5}' "$f")                                                                                
    echo "lattice parameter c: $lattc Angstrom"                                                                         
                                                                                                                        
    # Extract fifth column of data                                                                                      
    fracposz=$(awk '/SFAC/,/END/ {if ($0 !~ /SFAC|END/) print $5}' "$f")                                                
                                                                                                                        
    diff=$(echo "$fracposz" | sort -nr | awk 'NR==1{max=$1} END{printf "%.13f", max - $1}')                             
                                                                                                                        
    thickness=$(echo "$diff $lattc" | awk '{printf "%.13f", $1 * $2 / 10}')                                             
    echo -e "thickness : $thickness nm   

def show initial magnetic(castep):
    sed -n '/Initial magnetic/,/xx/p' $file | tail -n 1                                                                 
    sed -n '/Initial magnetic/,/xx/p' $file        

def show scf(castep):
for file in `ls *.castep`; do                                                                                           
    echo $file                                                                                                          
    grep "<-- SCF" $file | head -n 4                                                                                    
    grep "<-- SCF" $file | tail -n 1                                                                                    
done     

#===============================================================================
# Main
#==============================================================================

if __name__ == "__main__":

    args = get_args()

    seed = args.seed
    mode = args.mode

    if args.mode == "airss_spin":
        airss_spin(seed)

    elif args.mode == "ms_surface":
        ms_surface(seed)

    #test_geom_tol(seed)
    #test_set_restart(seed)
    
    #param_gen_gencell()


