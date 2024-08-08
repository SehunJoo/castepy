#!/usr/bin/env python

import numpy as np

from ase import Atoms
from ase.io import read, write
from ase.constraints import FixAtoms


def slab_vacuum(atoms: Atoms, thickness: float = 15):
    """
    Vacuum slab is added in lattice-c direction
    currently can be applied to
        orthorhombic lattice
        tetragonal lattice
        cubic lattice
    """

    print("Adjusting the thickness of vacuum slab ...\n")

    # get atomic positions and lattice parameters
 
    posabs = atoms.get_positions()
    latcart = atoms.get_cell()

    #print(latcart)
    #print(latcart[:])

    # check if the lattice is orthorhombic, tetragonal or cubic

    if not (latcart[2,0] == 0 and latcart[2,1] == 0):
        print("Warning: cell is not orthorhombic, tetragonal or cubic")

    # calculate the slab thickness

    max_z = max(posabs[:,2])
    min_z = min(posabs[:,2])
    diff_z = max_z - min_z
    vac_z = latcart[2,2] - diff_z

    print("from")
    print(f'Thickness (materials): {diff_z:.3f} Ang')
    print(f'Thickness (vacuum): {vac_z:.3f} Ang')
    print(f'Lattice parameter c: {latcart[2,2]:.3f} Ang')
    print()

    # calculate the lattice parameter c

    latleng_c = diff_z + 15

    print("to")
    print(f'Thickness (materials): {diff_z:.3f} Ang')
    print(f'Thickness (vacuum): {thickness:.3f} Ang')
    print(f'Lattice parameter c: {latleng_c:.3f} Ang')
    print()


    # update cell parameters

    latcart[2,2] = latleng_c
    atoms.set_cell(latcart)



def slab_center(atoms: Atoms):


    print("Adjusting centroid ...\n")

    cell_center_z = atoms.cell[2, 2] / 2

    centroid_z = np.mean(atoms.positions[:, 2])

    print("from")
    print(f"center of cell: {cell_center_z:.3f} Ang")
    print(f"centroid: {centroid_z:.3f} Ang")
    print()

    disp_vec_z = cell_center_z - centroid_z
    atoms.positions[:,2] += disp_vec_z

    centroid_z = np.mean(atoms.positions[:, 2])

    print("to")
    print(f"center of cell: {cell_center_z:.3f} Ang")
    print(f"centroid: {centroid_z:.3f} Ang")
    print()




def slab_constraints(atoms: Atoms):


    c = FixAtoms(indices=[atom.index for atom in atoms if atom.symbol == 'Ni'])
    atoms.set_constraint(c)
    print(atoms.constraints)


def cell_to_res(seed):
    import subprocess

    try:
        command_string = f'cabal cell res < {seed}.cell > {seed}.res && rm -f {seed}.cell'
        result = subprocess.run(command_string, shell=True, capture_output=True, text=True, check=True)
        
    except subprocess.CalledProcessError as e:
        print("오류 발생:", e)
        print(e.stderr)


def check_structure(atoms: Atoms):

    print()
    print("-"*72)
    print("Cell lengths:", atoms.cell.lengths())
    print("Cell angles:", atoms.cell.angles())
    print()
    for atom in atoms:
        print(atom)
    print("-"*72)
    print()



def main():
    import sys

    if len(sys.argv) < 2:                                                                                               
        print("2dpes.py <seed>")                                                                                 
        sys.exit(1)                                                                                                     
                                                                                                                        
                                                                                                                        
    # Input parameters                                                                                                  
    seed = sys.argv[1]                                                                                                  
    print('seed :', seed)                                                                                               
    print()                                                                                                             
                                                                                                                        
    st = read(seed+".res", format='res')
   
    print() 
    print("Reading structure ...\n")
    check_structure(st)
    
    slab_vacuum(st)
    #check_structure(st)

    slab_center(st)
    #check_structure(st)

    slab_constraints(st)
    #check_structure(st)

    check_structure(st)

    print("Writing structure ...\n")
    write(f"{seed}.cell", st,
        format='castep-cell',
        positions_frac = True,
        precision = 13,
        magnetic_moments='initial'
    )                                  

    cell_to_res(seed)



if __name__ == '__main__':
    main()

