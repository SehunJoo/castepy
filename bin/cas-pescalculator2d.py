from ase.io import read, iread, write
from ase import Atoms
import numpy as np
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

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

    def __init__(self, atoms: Atoms,
        atom_indices: list[int] | None = None,
        atom_symbols: list[str] | None = None,
        frac_c: tuple[int] | None = None,
        ia=16, ib=16, na=16, nb=16
    ):

        self.atoms = atoms

        indices = [i for i in range(len(struct))]

        fracpos = atoms.get_scaled_positions()
        symbols = atoms.get_chemical_symbols()

        if idx, (symbol, fracpos) = enumerate(zip(sym

        if atom_indices is not None:
            self.atom_indices = atom_indices

        if self.atom_indices is None:
            self.atom_indices = [i for i in range(len(struct))]

        if frac_c is not None:
            minc = frac_c[0]
            maxc = frac_c[1]
        
            fractional_coords = atoms.get_scaled_positions()
        selected_indices = [i for i, coord in enumerate(fractional_coords) if min_val <= coord[2] <= max_val]


        # Define the atom indices for elements B and N
        self.atom_indices = [i for i, atom in enumerate(struct) if atom.symbol in atom_symbols]


        # Initialize the lattice vectors
        self.latvec_a, self.latvec_b, self.latvec_c = struct.get_cell()

        # Initialize the displacement grid in fractional coordinate
        self.dispgrid_frac_a = np.linspace(0, 1, na + 1) * (ia / na)
        self.dispgrid_frac_b = np.linspace(0, 1, nb + 1) * (ib / nb)
        self.dispvec_a = [da * self.latvec_a for da in self.dispgrid_frac_a ]
        self.dispvec_b = [db * self.latvec_b for db in self.dispgrid_frac_b ]

        # Trajectory of displaced structures
        self.traj = []

    def print_structure(self):

        print(self.struct)
        print()
        for atom in self.struct:
            print(atom)
        print()

    def print_lattice_vectors(self):

        print('lattice vector a :', self.latvec_a)
        print('lattice vector b :', self.latvec_b)
        print('lattice vector c :', self.latvec_c)
        print()

    def print_displacement_grid(self):

        print('displacement along lattice vector a (in fractional coordinate) :', self.dispgrid_frac_a)
        print('displacement along lattice vector b (in fractional coordinate) :', self.dispgrid_frac_b)
        print()

    def print_displacement_vectors(self):

        print('displacement along lattice vector a (in fractional coordinate) :', self.dispvec_a)
        print('displacement along lattice vector b (in fractional coordinate) :', self.dispvec_b)
        print()

    def generate_displaced_structures(self):

        # Create the output directory if it doesn't exist
        os.makedirs('displaced', exist_ok=True)

        for da in self.dispgrid_frac_a:
            for db in self.dispgrid_frac_b:

                displaced_struct = self.struct.copy()
                dvec_a = da * self.latvec_a
                dvec_b = db * self.latvec_b

                for atom in displaced_struct:
                    if atom.index in self.atom_indices:
                        atom.position += dvec_a + dvec_b
                        atom.magmom = 0.0
                    else:
                        atom.magmom = 2.0
                
                self.traj.append(displaced_struct)
                write(f"displaced/{seed}_{1000*da:04.0f}_{1000*db:04.0f}.cell", displaced_struct, format='castep-cell', magnetic_moments='initial')

        write(f"displaced_structures.xyze", self.traj, format='extxyz')


class pesplot2D:

    def __init__(self):
        self.filename = '2D_PES'
        # empty
        pass

    def cryan2dat(self):

        datafile = '2D_PES.dat'

        if not os.path.isfile(datafile):
            print(f"    generating {datafile} ...")
            os.system(f"ca -l -nr -r 1>./{datafile} 2>/dev/null")
        else:
            print(f"    {datafile} found ...")
    
        print("Done\n")

    
    def read_data(self):
        
        datafile = '2D_PES.dat'
        a = []
        b = []
        energy = []
    
        with open(datafile, "r") as file:
            for line in file:
                values = line.split()
                a.append(float(values[0].split("_")[-2])/1000)
                b.append(float(values[0].split("_")[-1])/1000)
                energy.append(float(values[3]) * float(values[6]))
    
        d = {}
        d['a'] = a
        d['b'] = b
        d['E(eV)'] = energy
    
        df = pd.DataFrame(d)
        df = df.sort_values(by=['a', 'b'])
        df['dE(eV)'] = df['E(eV)'] - df['E(eV)'].min()
        print(df)

        return df
    
    
    def plot_scatter(self):

        df = self.read_data()

        x = df['a']
        y = df['b']
        de = df['dE(eV)']

        fig, ax = plt.subplots() 
        scatter = ax.scatter(x, y, c=de, cmap='viridis')
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label(r'$\Delta$E (eV)', rotation=270, labelpad=20)
        cbar.ax.title.set_rotation(90)
        plt.xlabel('Displacement along a')
        plt.ylabel('Displacement along b')
        plt.savefig('2D_PES_plot_scatter.png')
        plt.close(fig)
        #plt.show()
    
    def plot_contourf(self):

        df = self.read_data()

        x = df['a']
        y = df['b']
        de = df['dE(eV)']
    
        X = df['a'].unique()
        Y = df['b'].unique()
        de_2d = de.values.reshape((len(Y), len(X)))
    
        fig, ax = plt.subplots()
        contour = ax.contourf(X, Y, de_2d.T, levels=10, cmap='viridis')
        cbar = plt.colorbar(contour, ax=ax)
        cbar.set_label(r'$\Delta$E (eV)', rotation=270, labelpad=20)
        plt.xlabel('Displacement along a')
        plt.ylabel('Displacement along b')
        plt.savefig('2D_PES_plot_contourf.png')
        #plt.show()
        plt.close(fig)
    


                
                

###################################################################################################
# MAIN
###################################################################################################
        

if len(sys.argv) < 3:
    print("2dpes.py <seed> <task>")
    print("<seed> seed name")
    print("<task> gen  : generate displaced structures")
    print("       plot : plot 2D potential enerty surface")
    sys.exit(1)


# Input parameters
seed = sys.argv[1]
task = sys.argv[2]
print('seed :', seed)
print('task :', task)

if task == 'gen':
    # Load the .res file
    if os.path.isfile(seed+".cell"):
        structure = read(seed+".cell", format='castep-cell')
    elif os.path.isfile(seed+".res"):
        structure = read(seed+".res", format='res')
    else:
        print("The file does not exist.")

    # Generate displaced structures    
    pescalc = pescalc2D(structure, atom_symbols=['B','N'])
    pescalc.print_structure()
    pescalc.print_lattice_vectors()
    pescalc.print_displacement_grid()
    pescalc.print_displacement_vectors()
    pescalc.generate_displaced_structures()

elif task == 'plot':
    print("Plotting 2D potential energy surface") 
    pesplot = pesplot2D()
    pesplot.cryan2dat()
    print("Generating scatter plot")
    pesplot.plot_scatter()
    print("Generating contour plot")
    pesplot.plot_contourf()


