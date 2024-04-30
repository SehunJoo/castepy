#!/usr/bin/env python


class Cell():

    def __init__(self, seed, cell):
        self.seed = seed
        self.cell = cell

    def __str__(self):
        lines = []
        for k, v in self.cell.items():
            if isinstance(v, list):
                lines.append("\n".join(
                    [f"%BLOCK {k.upper()}", *v, f"%ENDBLOCK {k.upper()}"]
                ))
            else:
                if k in ['fix_all_cell', 'fix_vol', 'fix_com']:
                    lines.append(f"{k.upper()} : {v}")
                else:
                    lines.append(f"{k.upper()} {v}")
            lines.append("")
        return "\n".join(lines)


    @ classmethod
    def from_file(cls, filename):
        seed = filename.replace('.cell', '')
        cell = {}
        with open(filename, 'r') as f:
            lines = iter(f.readlines())

            # covert to lowercase except elements
            for line in lines:
                temp = line.strip()

                # skip comments
                if not temp or temp.startswith('#'):
                    continue

                if temp.lower().startswith('%block'):
                    keyword = line.lower().split()[1]
                    cell[keyword] = []

                    for line in lines:
                        temp = line.strip()
                        if temp.lower().startswith('%endblock'):
                            break
                        else:
                            cell[keyword].append(temp)
                else:
                    temp = temp.lower()
                    tokens = temp.split(':', maxsplit=1)
                    print(tokens)
                    if len(tokens) > 1:
                        key = tokens[0].strip()
                        value = tokens[1].strip()
                    else:
                        tokens = temp.split()
                        key = tokens[0].strip()
                        value = tokens[1:].strip() if len(tokens) > 1 else ""
                    cell[key] = value

        return cls(seed=seed, cell=cell)

    @ classmethod
    def from_seed(cls, seed):
        return cls.from_file(f"{seed}.cell")

    def copy_to_md5(self):
        import hashlib
        with open(f"{self.seed}.cell", 'rb') as fin:
            bytes = fin.read()
            hash = hashlib.md5(bytes).hexdigest()
            with open(f"{self.seed}.cell.{hash[:8]}", 'wb') as fout:
                fout.write(bytes)


    def to_file(self, filename: str | None = None):
        if filename == None:
            filename = f"{self.seed}.cell"
        with open(filename, 'w') as f:
            f.write(str(self))

    def as_dict(self):
        return self.cell


    def set_ionic_constraints(self, option: str = 'off'):
        """
        Default: false
        set true if present
        """
        if option == 'default':
            self.cell.pop('ionic_constraints', None)
            self.cell.pop('fix_all_ions', None)
            self.cell.pop('fix_com', None)
        elif option == 'off':
            self.cell.pop('ionic_constraints', None)
            self.cell.pop('fix_all_ions', None)
            self.cell.pop('fix_com', None)
        else:
            self.cell.pop('fix_com', None)



    def set_cell_constraints(self, option: str = 'cellopt'):
        """
        Default: false
        set true if present
        """
        if option == 'default':
            self.cell.pop('cell_constaints', None)
            self.cell.pop('fix_all_cell', None)
            self.cell.pop('fix_vol', None)
        elif option == "off":
            self.cell.pop('cell_constaints', None)
            self.cell.pop('fix_all_cell', None)
            self.cell.pop('fix_vol', None)
        elif option == "geomopt":
            self.cell.pop('cell_constaints', None)
            self.cell.update({'fix_all_cell': 'true'})
        elif option == "cellopt":
            self.cell.pop('cell_constaints', None)
            self.cell.pop('fix_all_cell', None)
            self.cell.pop('fix_vol', None)



    def set_hubbardu(self, option: str = 'off'):
        if option == 'off':
            self.cell.pop('hubbard_u', None)

    def set_kpoints(self, spacing: float | None = None):
        if isinstance(spacing, float):
            self.cell.pop('kpoints_list', None)
            self.cell.update({'kpoints_mp_spacing': spacing})

    def set_pseudopot(self, pot: str = "C19"):
        if pot == 'off':
            self.cell.pop('species_pot')
        else:
            self.cell.update({'species_pot': [pot]})

    def set_symmetry(self, option: str = 'on'):
        if option == 'off':
            self.cell.pop('symmetry_ops', None)
            self.cell.pop('symmetry_generate', None)
            self.cell.pop('snap_to_symmetry', None)
        elif option == 'on':
            self.cell.pop('symmetry_ops', None)
            self.cell.update({'symmetry_generate': ''})
            self.cell.update({'snap_to_symmetry': ''})

    def set_pressure(self, pressure: float | None = None):
        if pressure == None:
            self.cell.pop('external_pressure', None)
        elif pressure == 'off':
            self.cell.pop('external_pressure', None)
        else:
            self.cell.update({
                'external_pressure': [f"{pressure} 0 0 ", f"{pressure} 0", f"{pressure}"]
            })

    def set_efield(self, efield: list[float] | None = None):
        if efield == None:
            self.cell.pop('external_efield', None)
        elif efield == 'off':
            self.cell.pop('external_efield', None)
        else:
            self.cell.update({
                'external_efield': [f"{efield[0]} {efield[1]} {efield[2]}"]
            })

    def set_species_mass(self, option: str = 'off'):
        if option == 'off':
            self.cell.pop('species_mass', None)

    def set_species_lcao_states(self, option: str = 'off'):
        if option == 'off':
            self.cell.pop('species_lcao_states', None)

    def set_spin(self, option='mp'):
        d_block_3d = ['Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn']
        d_block_4d = ['Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd']
        d_block_5d = ['La','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg']
        d_block = d_block_3d + d_block_4d + d_block_5d

        for i, atom in enumerate(self.cell['positions_frac']):
            tokens = atom.split()
            element = tokens[0]

            if option == 'mp':
                if element in d_block:
                    spin = 5.0
                else:
                    spin = 0.6

            if not 'SPIN' in atom:
                self.cell['positions_frac'][i] = atom + f' SPIN={spin}'
            else:
                atom_wospin = atom.split(' SPIN')[0]
                self.cell['positions_frac'][i] = atom_wospin + f' SPIN={spin}'

