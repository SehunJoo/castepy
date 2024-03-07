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

def airss_spin(seed):
    cell = Cell.from_seed(seed)
    #cell.copy_to_md5()
    cell.set_spin('mp')
    cell.to_file()


def ms_surface(seed):

    cell = Cell.from_seed(seed)
    cell.copy_to_md5()

    cell.set_spin('mp')
    cell.set_kpoints(0.05)
    cell.set_symmetry('on')
    cell.set_cell_constraints('geomopt')
    cell.set_ionic_constraints(None)
    cell.set_efield('off')
    cell.set_pressure('off')
    cell.set_species_mass('off')
    cell.set_pseudopot('C19')
    cell.set_species_lcao_states('off')

    cell.to_file()

    param = Param.from_seed(seed)
    param.copy_to_md5() 

    param.set_scf_mixing('default-vasp')
    param.set_scf_tol('medium')
    param.set_geom_tol('medium')
    param.set_restart('reuse')
    param.set_write('restart')
    param.set_extra_bands(20)

    param.compare(Param.from_gencell().as_dict())

    param.to_file()

    

def run_geomopt(seed, quality_initial = 'medium', mode = 'tighter'):

    cell = Cell.from_seed(seed)
    cell.copy_to_md5()

    param = Param.from_seed(seed)
    param.copy_to_md5()

    param.set_scf_tol(quality_initial)
    param.set_restart('reuse')
    param.set_write('restart')

    # run

    # check err (counting *.err file(


def test_mixing(seed):

    # If SCF convergence failed
    print("Test mixing")
    keys_mixing = ['mix_charge_amp','mix_spin_amp']
    param.set_scf_mixing(quality='improve')
    print(param.to_str(keys=keys_mixing))
    param.set_scf_mixing(quality='improve')
    print(param.to_str(keys=keys_mixing))
    param.set_scf_mixing(quality='improve')
    print(param.to_str(keys=keys_mixing))

def test_elec_tol(seed):

    param = Param.from_file(seed)

    print("-"*100)
    print("Test tolerance")
    print("-"*100)

    keys_scf_tol = ['elec_energy_tol']

    param.set_scf_tol(quality='default_castep')
    print(param.to_str(keys=keys_scf_tol))

    param.set_scf_tol(quality='looser')
    print(param.to_str(keys=keys_scf_tol))
    param.set_scf_tol(quality='looser')
    print(param.to_str(keys=keys_scf_tol))
    param.set_scf_tol(quality='looser')
    print(param.to_str(keys=keys_scf_tol))
    param.set_scf_tol(quality='tighter')
    print(param.to_str(keys=keys_scf_tol))
    param.set_scf_tol(quality='tighter')
    print(param.to_str(keys=keys_scf_tol))


def test_geom_tol(seed):

    param = Param.from_file(seed)

    print("-"*100)
    print("Test tolerance")
    print("-"*100)

    keys = [
        'geom_energy_tol', 'geom_force_tol',
        'geom_stress_tol', 'geom_disp_tol'
    ]

    param.set_geom_tol(quality='default_castep')
    print(param.to_str(keys=keys))

    param.set_geom_tol(quality='looser')
    print(param.to_str(keys=keys))
    param.set_geom_tol(quality='looser')
    print(param.to_str(keys=keys))
    param.set_geom_tol(quality='looser')
    print(param.to_str(keys=keys))
    param.set_geom_tol(quality='tighter')
    print(param.to_str(keys=keys))
    param.set_geom_tol(quality='tighter')
    print(param.to_str(keys=keys))
    param.set_geom_tol(quality='tighter')
    print(param.to_str(keys=keys))
    param.set_geom_tol(quality='tighter')
    print(param.to_str(keys=keys))

def test_set_restart(seed):

    param = Param.from_file(seed)

    print("-"*100)
    print("Test restart")
    print("-"*100)

    keys = [
        'reuse', 'continuation'
    ]
    param.set_restart(None)
    print(param.to_str(keys=keys))
    param.set_restart('reuse')
    print(param.to_str(keys=keys))
    param.set_restart('continuation')
    print(param.to_str(keys=keys))


def param_gen_gencell():
    param = Param.from_gencell()
    print(param)
    param.to_file()


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


