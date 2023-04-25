#!/usr/bin/env python

from mp_api.client import MPRester

api_key = "d7BCat3ve9lYksDLTojHg3AceBOcN5B9"
mpr = MPRester(api_key)

def mp_fields():
    print("List of available fields")
    list_of_available_fields = mpr.summary.available_fields
    print(list_of_available_fields)

def mp_example():
    docs = mpr.summary.search(material_ids=["mp-1"])
    print(docs[0])

# get mpids

def get_mpids_formula(formula):
    #docs = mpr.summary.search(formula=formula, fields=["material_id"])
    #docs = mpr.summary.search(formula=formula, is_stable=True, fields=["material_id"])
    docs = mpr.summary.search(formula=formula, theoretical=False, fields=["material_id"])
    return [doc.material_id for doc in docs]
    
def get_mpids_elements(elements):
    #docs = mpr.summary.search(elements=elements, fields=["material_id"])
    docs = mpr.summary.search(elements=elements, is_stable=True, fields=["material_id"])
    #docs = mpr.summary.search(elements=elements, theoretical=False, fields=["material_id"])
    return [doc.material_id for doc in docs]


# to query summary data with Materials Project IDs

def get_structures(mpids):

    docs = mpr.summary.search(material_ids=mpids,
                              fields=["material_id", "formula_pretty", "nsites", "structure", "symmetry"])

    for doc in docs:
        mpid = doc.material_id
        formula = doc.formula_pretty
        nsites = doc.nsites
        sg = doc.symmetry.symbol
        sg = sg.replace("/","").replace("_","")
        structure = doc.structure

        fmt = 'cif'
        filename = formula + "-" + str(nsites) + "-" + sg + "-"  + mpid + "." + fmt
        print(filename)
        #print(structure)
        structure.to(filename = filename, fmt = fmt)


#############################
# Main
#############################

mp_fields()
mp_example()
get_structures(get_mpids_formula(["Ni"]))
