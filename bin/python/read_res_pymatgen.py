#!/usr/bin/env python
import json
from pymatgen.io.res import AirssProvider

# Load the Res file
res = AirssProvider.from_file("LMO-Imma-conv.res")

# Print some basic information about the Res file
#print("Res file contains {} structures".format(len(res.structure)))
#print("First structure:")
print(res.structure)

# Convert the Res object to a dictionary
res_dict = res.as_dict()

#print(res_dict)

for key, value in res_dict.items():
    print(key, value,"\n")

for key, value in res_dict['res'].items():
    print(key, value,"\n")

for key, value in res_dict['res']['SFAC'].items():
    print(key, value,"\n")

for key, value in res_dict['res']['SFAC']['ions'].items():
    print(key, value,"\n")
