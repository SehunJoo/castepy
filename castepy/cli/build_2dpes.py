#!/usr/bin/env python

import os
import sys
import numpy as np

from ase import Atoms
from ase.io import read, iread, write
from pymatgen.io.res import ResIO



class pescalc2D:
    """class for calculating 2D potential energy surface"""
    """
    parameters:

    struct: Atoms object
    atom_indices: list
            a list of indices for atoms to apply displacement vectors
    atom_symbols: list
            a list of element symbols to applyl idsplacement vectors.
            This overwrite the atom_indices
    ia: integer
        Range: from (0, 0) to ($ia, $ib) (# points: ($ia+1)*($ib+1))
    ib: integer
        Range: from (0, 0) to ($ia, $ib) (# points: ($ia+1)*($ib+1))
    na: integer
        subdivisions along the lattice vector a
    nb: integer
        subdivisions along the lattice vector b
    """
    # Translate from (0, 0) to (ia/na, ib/nb)
    # The range of translation can be set by ia/na and ib/nb
    # The solution can be set by na and nb

    def __init__(self,
        seed: str,
        atoms: Atoms,
        indices: list[int] | None = None,
        symbols: list[str] | None = None,
        posfrac_c: tuple[int] | None = None,
        ia=16, ib=16, na=16, nb=16
    ):

        self.seed = seed
        self.root = seed.split('-')[0]
        self.atoms = atoms
        self.latvec_a, self.latvec_b, self.latvec_c = atoms.get_cell()
        print(self)

        # initialize a group of atoms

        self.group = None
        self.set_group(indices, symbols, posfrac_c)
        print()

        # initialize the displacement grid in fractional coordinate

        self.disp_grid_points = None
        self.set_disp_grid(ia, ib)


        # Trajectory of displaced structures
        self.traj = []



    def __str__(self):
        string = [
            f'lattice vector a : {self.latvec_a}',
            f'lattice vector b : {self.latvec_b}',
            f'lattice vector c : {self.latvec_c}',
            ""
        ]
        atoms_symbol = self.atoms.get_chemical_symbols()
        atoms_posfrac = self.atoms.get_scaled_positions()
        for i in range(len(self.atoms)):
            string += [f"{i} {atoms_symbol[i]} {atoms_posfrac[i]})"]

        return "\n".join(string) + "\n"


    def set_group(self,
        indices: list[int] | None = None,
        symbols: list[str] | None = None,
        posfrac_z: tuple[float] | None = None
    ):
        """
        Set a group of atoms to move/translate/displace
        """

        print(f"indices: {indices}")
        print(f"symbols: {symbols}")
        print(f"posfrac_z: {posfrac_z}")

        if indices is None:
            indices = list(range(len(self.atoms)))

        atoms_posfrac = self.atoms.get_scaled_positions()
        atoms_symbol = self.atoms.get_chemical_symbols()

        indices_group = []

        # get indices for target atoms
        for i in indices:

            # filter symbols
            if symbols is not None and atoms_symbol[i] not in symbols:
                continue

            # filter fractional z(c) coordinate
            if posfrac_z is not None and not (posfrac_z[0] <= atoms_posfrac[i][2] <= posfrac_z[1]):
                continue

            indices_group.append(i)

        print("Group of atoms to move\n")

        for i in indices_group:
            print(i, atoms_symbol[i], atoms_posfrac[i])

        self.group = indices_group

        return indices_group


    def set_disp_grid(self,
        na: int = 16, 
        nb: int = 16,
        rangea: tuple | None = None,
        rangeb: tuple | None = None
    ):
        """
        grid in lattice vectors a & b space in fractional coordinate
        """
        if rangea is None:
            rangea = (0, na)
        if rangeb is None:
            rangeb = (0, nb)

        print("set grid for displacements...")
        print(f"grid size: ({na}, {nb})")
        print(f"grid range: {rangea}, {rangeb}")

        disp_grid_points = []

        # generate grid points in fractional coordinate

        disp_grid_points_a = np.linspace(0, 1, na)
        disp_grid_points_b = np.linspace(0, 1, nb)

        # get specified range of grid points

        disp_grid_points_a = disp_grid_points_a[rangea[0]:rangea[1]]
        disp_grid_points_b = disp_grid_points_b[rangeb[0]:rangeb[1]]

        # generate grid points as a list

        print("Grid for scanning potential energy surface")
        print()
        cnt = 0
        for db in disp_grid_points_b:
            for da in disp_grid_points_a:
                disp_grid_points.append((da, db))
                cnt += 1
                print(f"{cnt:5d}\t{da:10.5f}\t{db:10.5f}")

        # update instance variable

        self.disp_grid_points = disp_grid_points
        self.disp_grid_points_abs = self.get_disp_grid_points_abs()

        return disp_grid_points


    def get_disp_grid_points_abs(self):

        disp_grid_points_abs = []

        print("Grid for scanning potential energy surface (in Angstrom)")
        cnt = 0
        for pt in self.disp_grid_points:
            cnt += 1
            dispvec_a_mag = pt[0] * np.linalg.norm(self.latvec_a)
            dispvec_b_mag = pt[1] * np.linalg.norm(self.latvec_b)
            disp_grid_points_abs.append((dispvec_a_mag, dispvec_b_mag))
            print(f"{cnt:5d}\t{pt[0]:10.5f}\t{pt[1]:10.5f}\t{dispvec_a_mag:10.5f}\t{dispvec_b_mag:10.5f}")

        return disp_grid_points_abs


    def set_spin(self):
        """
        Initialize spin (magnetic moment) of atoms
        """
        for atom in self.atoms:
            if atom.symbol in ["Ni"]:
                atom.magmom = 5.0
            else:
                atom.magmom = 0.6
        
    ## build / generate structures        

    def generate_displaced_structures(self):
        """
        Build / Generate structures
        """
        dirname = 'hopper_2dpes'
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        else:
            print(f"Warning: {dirname} already exists")

        for point in self.disp_grid_points:
            da, db = point
            atoms_displaced = self.atoms.copy()
            dvec_a = da * self.latvec_a
            dvec_b = db * self.latvec_b

            for i, atom in enumerate(atoms_displaced):
                if i in self.group:
                    atom.position += dvec_a + dvec_b

            seed_displaced = f"{self.root}-disp_{1000*da:04.0f}_{1000*db:04.0f}"
            #self.atoms_to_cell(atoms_displaced, seed_displaced)
            self.atoms_to_res(atoms_displaced, seed_displaced, dirpath=dirname)

            self.traj.append(atoms_displaced)

        write(f"displaced_structures.xyze", self.traj, format='extxyz')


    ## output

    def atoms_to_cell(self, atoms: Atoms, seed: str):
        """
        Save ASE Atoms to CASTEP cell file
        """

        write(f"{seed}.cell", atoms, format='castep-cell', magnetic_moments='initial')


    def atoms_to_res(self, atoms: Atoms, seed: str, dirpath: str | None = None):
        """
        Save ASE Atoms to a res file.
        """

        from pymatgen.io.ase import AseAtomsAdaptor
        from pymatgen.entries.computed_entries import ComputedStructureEntry

        # Convert from Atoms to ComputedStructureEntry

        adaptor = AseAtomsAdaptor()
        structure = adaptor.get_structure(atoms)
        entry = ComputedStructureEntry(structure, energy=0)

        # TITL: add seed to entry.data

        entry.data.update({"seed": seed})

        # TITL: add pressure to entry.data

        entry.data.update({"pressure": 0})

        # TITL: add isd/iasd to entry.data - spin density

        isd = 0
        iasd = 0
        for site in entry.structure:
            if 'magmom' in site.properties:
                 isd += site.properties['magmom']
                 iasd += abs(site.properties['magmom'])

        entry.data.update({"isd": 0})
        entry.data.update({"iasd": 0})

        # Save to a res file

        filename= entry.data.get("seed", "") + ".res"
        if dirpath is not None:
            filename = dirpath + "/" + filename
        ResIO.entry_to_file(entry, filename)






###################################################################################################
# MAIN
###################################################################################################

def main():
    
    if len(sys.argv) < 4:
        print("2dpes.py <seed> <zmin> <zmax>")
        print("<seed> seed name")
        print("<task> gen  : generate displaced structures")
        print("       plot : plot 2D potential enerty surface")
        sys.exit(1)
    
    
    # Input parameters
    seed = sys.argv[1]
    zmin = float(sys.argv[2])
    zmax = float(sys.argv[3])
    print('seed :', seed)
    print()

    
    # Load the .res file
    if os.path.isfile(seed+".cell"):
        structure = read(seed+".cell", format='castep-cell')
    elif os.path.isfile(seed+".res"):
        structure = read(seed+".res", format='res')
    else:
        print("The file does not exist.")
    
    # Generate displaced structures
    pescalc = pescalc2D(seed, structure, posfrac_c=(zmin, zmax))
    pescalc.set_spin()
    pescalc.generate_displaced_structures()
    
    #print("Plotting 2D potential energy surface")
    #pesplot = pesplot2D()
    #pesplot.cryan2dat()
    #print("Generating scatter plot")
    #pesplot.plot_scatter()
    #print("Generating contour plot")
    #pesplot.plot_contourf()


if __name__ == '__main__':
    main()
