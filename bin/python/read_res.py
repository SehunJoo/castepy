#!/usr/bin/env python

import spglib as spg
import os
import numpy as np
import pandas as pd
from collections import defaultdict
import glob
import json

seed = 'NiCo2O4-9266-3506-9'

## define funcitons

#!/usr/bin/env python

import read_resdef read_res(filename):

    # Create an empty dictionary to store the parsed data
    data = {}

    with open(filename, 'r') as f:

        lines = f.readlines()

        # Find the index of the line starting with 'TITL'
        try:
            titl_index = next(i for i, line in enumerate(lines) if line.startswith('TITL'))
        except StopIteration:
            print("Could not find 'TITL' line")
            return None


        # Parse the data using split
        tokens = lines[titl_index].strip().split()

        # Update the dictionary with parsed data
        data = { 
            'seed': [tokens[1]],
            'pressure': [tokens[2]],
            'volume': [tokens[3]],
            'enthalpy': [tokens[4]],
            'spin': [tokens[5]],
            'modspin': [tokens[6]],
            'delec': [tokens[7] if len(tokens) == 13 else None],
            'nat': [tokens[8]] if len(tokens) == 13 else [tokens[7]],
            'sym': [tokens[9]] if len(tokns) == 13 lese [tokens[8]],
        }

        # Find the indices of the lines starting with 'SFAC' and 'END'
        sfac_index = None
        end_index = None
        for i, line in enumerate(lines):
            if line.startswith('SFAC'):
                sfac_index = i
            elif line.startswith('END'):
                end_index = i
                break

        if sfac_index is None or end_index is None:
            # Handle case where 'SFAC' and/or 'END' line is not found
            print("Could not find 'SFAC' and/or 'END' lines")
            return None

        # Extract the atomic symbols and atomic information
        elements = lines[sfac_index].strip().split()[1:]
        atoms = [line.strip().split() + ['0.0'] * (7-len(line.strip().split())) for line in lines[sfac_index+1:end_index]]

        # Update the dictionary 'data'
        data.update({
            'elements': [elements],
            'atoms': [atoms],
        })

        # Convert the 'atoms' list to a Pandas DataFrame
        df = pd.DataFrame(atoms, columns=['element', 'element_id', 'x', 'y', 'z', 'occ', 'spin']).astype({'spin': float})
        spin = df['spin'].mean()
        modspin = df['spin'].abs().mean()
        elements_spin = df.groupby('element')['spin'].mean().to_dict()
        elements_modspin = df.groupby('element')['spin'].apply(lambda x: x.abs().mean()).to_dict()

        # Update the dictionary 'data' with spin and modspin values for each element
        data.update({f'spin_{key}': [val] for key, val in elements_spin.items()})
        data.update({f'modspin_{key}': [val] for key, val in elements_modspin.items()})
        
    return data

        
        ## Calculate mean spin and absolute mean spin for Co octahedral and tetrahedral sites, if present
        #co_oct = df.loc[df['element'] == 'Co'].iloc[0:4]
        #if not co_oct.empty:
        #    elements_spin['Co_oct'] = co_oct['spin'].mean()
        #    elements_modspin['Co_oct'] = co_oct['spin'].abs().mean()
        #
        #co_tet = df.loc[df['element'] == 'Co'].iloc[4:9]
        #if not co_tet.empty:
        #    elements_spin['Co_tet'] = co_tet['spin'].mean()
        #    elements_modspin['Co_tet'] = co_tet['spin'].abs().mean()

    


def pretty_print_dict(dictionary):
    """
    Prints the given dictionary in a pretty format.
    """
    print(json.dumps(dictionary, indent=4))

##################
# MAIN
##################

listres = glob.glob("*.res")
nres = len(listres)


data = defaultdict(list)
for i, resfile in enumerate(listres):

    print(str(i) + "/" + str(nres), end="\r", flush=True)
    pretty_print_dict(read_res(resfile))

    exit()

    
df_mag = pd.DataFrame.from_dict(data)
print(df_mag)
df_mag.to_csv('df_mag.csv', index=False)


exit()


def divline():
    print("="*100,"\n")

