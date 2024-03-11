

seed = 'Ni-surf_556_3L-slab'


class Param:

    def __init__(self, seed, param):
        self.seed = seed
        self.filename = seed + ".param"
        self.param = param


    def __str__(self):
        return "\n".join([
            f"{k:30s} : {v}" for k, v in self.param.items()
        ]) + "\n"


    @ classmethod
    def from_file(cls, filename: str):
        """
        Reads parameters from a file and returns them as a dictionary.

        This function opens a file with the given filename, reads each line,
        and for lines that do not start with a '#', it extracts a key-value pair.
        The key is the string before the colon ':' and the value is the first
        string after the colon, ignoring any leading or trailing whitespace.

        Parameters:
        - filename (str): The name of the file (without the '.param' extension)
                          from which to read the parameters.

        Returns:
        - dict: A dictionary where each key is a parameter name and the associated
                value is the parameter's value.
        """
        seed = filename.replace('.param', '')
        param = {}
        with open(f"{seed}.param", 'r') as f:
            for line in f:
                if not line.strip() or line.strip().startswith('#') or ':' not in line:
                    continue
                keyword, value = line.split(':', 1)
                value = value.split()[0] if value.split() else ''
                param[keyword.strip().lower()] = value.strip().lower()

        return cls(seed, param=param)


    @ classmethod
    def from_seed(cls, seed: str):
        return cls.from_file(f"{seed}.param")

    @ classmethod
    def from_gencell(cls):
        param = {
            'task': 'geometryoptimization',
            'xc_functional': 'PBE',
            'spin_polarized': 'false',
            'fix_occupancy': 'false',
            'metals_method': 'dm',
            'mixing_scheme': 'pulay',
            'max_scf_cycles': '1000',
            'cut_off_energy': '340',
            'opt_strategy': 'speed',
            'page_wvfns': '0',
            'num_dump_cycles': '0',
            'backup_interval': '0',
            'geom_method': 'LBFGS',
            'geom_max_iter': '20',
            'mix_history_length': '20',
            'finite_basis_corr': '0',
            'fixed_npw': 'true',
            'write_cell_structure': 'true',
            'write_checkpoint': 'none',
            'write_bib': 'false',
            'write_otfg': 'false',
            'write_cst_esp': 'false',
            'write_bands': 'false',
            'write_geom': 'false',
            'bs_write_eigenvalues': 'false',
            'calculate_stress': 'true',
        }
        return cls(seed='gencell', param=param)

    def copy_to_md5(self):
        import hashlib
        with open(f"{self.seed}.param", 'rb') as fin:
            bytes = fin.read()
            hash = hashlib.md5(bytes).hexdigest()
            with open(f"{self.seed}.param.{hash[:8]}", 'wb') as fout:
                fout.write(bytes)

    def to_str(self, keys: list[str] = None):
        if keys is None:
            keys = self.param.keys()

        return "\n".join([
            f"{k:30s} : {v}" for k, v in self.param.items() if k in keys
        ]) + "\n"


    def to_file(self):
        with open(f"{self.seed}.param", "w") as f:
            f.write(str(self))

    def as_dict(self):
        return self.param


    def set_scf_mixing(self,
        quality: str = 'normal'
    ):
        """
        If SCF convergence truns out to be very slow or failed,
        If the convergence failed, please try this
        The optimal mixing parameters depends very much on the system.
        For metals, thie parameter usually has to be rather small, e.g. 0.02
        """

        if quality == "default-castep":
            self.param.update({
                'metals_method': 'dm',
                'mix_charge_amp': 0.8,
                'mix_spin_amp': 2.0
            })
        elif quality == "default-ms":
            self.param.update({
                'metals_method': 'dm',
                'mix_charge_amp': 0.5,
                'mix_spin_amp': 2.0
            })
        elif quality == "default-vasp":
            # AMIX, AMIX_MAG
            self.param.update({
                'metals_method': 'dm',
                'mix_charge_amp': 0.4,
                'mix_spin_amp': 1.6
            })
        elif quality == "normal":
            self.param.update({
                'metals_method': 'dm',
                'mix_charge_amp': 0.2,
                'mix_spin_amp': 0.8
            })
        elif quality == "edft":
            self.param.update({'metals_method', 'edft'})
        elif quality == "improve":

            mix_charge_amp = float(self.param['mix_charge_amp'])
            mix_spin_amp = float(self.param['mix_spin_amp'])

            if mix_charge_amp > 0.1:
                 self.param.update({'mix_charge_amp': max(mix_charge_amp/2, 0.1)})

            if mix_spin_amp > 0.4:
                 self.param.update({'mix_spin_amp': max(mix_spin_amp/2, 0.4)})



    def set_scf_tol(self,
        quality: str = 'default'
    ):
        """
        CASTEP default is same as MS-coarse
        """
        self.param.update({'max_scf_cycles': 200})

        elec_tol_set = {
            'default_castep': {
                'elec_energy_tol': 1.0e-05
            },
            'coarse': {
                'elec_energy_tol': 1.0e-05
            },
            'medium': {
                'elec_energy_tol': 2.0e-06
            },
            'fine': {
                'elec_energy_tol': 1.0e-06
            },
            'ultrafine':{
                'elec_energy_tol': 5.0e-07
            }
        }

        if quality in elec_tol_set:
            self.param.update(elec_tol_set[quality])

        elif quality in ["looser", "tighter"]:
            elec_tol = {key: float(self.param[key]) for key in [
                'elec_energy_tol'
            ]}

            if quality == 'tighter':
                for q in ['coarse', 'medium', 'fine', 'ultrafine']:
                    if all(elec_tol_set[q][k] < elec_tol[k] for k in elec_tol):
                        self.param.update(elec_tol_set[q])
                        print(f"elec_energy_tol increased/tightened to: {q}")
                        break

            elif quality == 'looser':
                for q in ['ultrafine', 'fine', 'medium', 'coarse']:
                    if all(elec_tol[k] < elec_tol_set[q][k] for k in elec_tol):
                        self.param.update(elec_tol_set[q])
                        print(f"elec_energy_tol reduced/loosened to: {q}")
                        break
        else:
            raise ValueError(f"{quality} is not supported")


    def set_geom_tol(self,
        quality: str = 'medium'
    ):
        """
        CASTEP default is almost same as MS-medium
        """
        self.param.update({'max_scf_cycles': 200})


        # param set
        geom_tol_set = {
            'default_castep': {
                'geom_energy_tol': 2.0e-5,
                'geom_force_tol': 0.05,
                'geom_stress_tol': 0.1,
                'geom_disp_tol': 0.001
            },
            'default_vasp': {
                'geom_energy_tol': 0.001,
                'geom_force_tol': 100,
                'geom_stress_tol': 100,
                'geom_disp_tol': 100
            },
            'coarse': {
                'geom_energy_tol': 5.0e-5,
                'geom_force_tol': 0.1,
                'geom_stress_tol': 0.2,
                'geom_disp_tol': 0.005
            },
            'medium': {
                'geom_energy_tol': 2.0e-5,
                'geom_force_tol': 0.05,
                'geom_stress_tol': 0.1,
                'geom_disp_tol': 0.002
            },
            'fine': {
                'geom_energy_tol': 1.0e-5,
                'geom_force_tol': 0.03,
                'geom_stress_tol': 0.05,
                'geom_disp_tol': 0.001
            },
            'ultrafine': {
                'geom_energy_tol': 5.0e-6,
                'geom_force_tol': 0.01,
                'geom_stress_tol': 0.02,
                'geom_disp_tol': 5.0e-4
            }
        }

        if quality in geom_tol_set:
            self.param.update(geom_tol_set[quality])

        elif quality in ["looser", "tighter"]:
            geom_tol = {key: float(self.param[key]) for key in [
                'geom_energy_tol', 'geom_force_tol',
                'geom_stress_tol', 'geom_disp_tol'
            ]}

            if quality == 'tighter':
                for q in ['coarse', 'medium', 'fine', 'ultrafine']:
                    if all(geom_tol_set[q][k] < geom_tol[k] for k in geom_tol):
                        self.param.update(geom_tol_set[q])
                        print(f"geom_tol increased/tightened to: {q}")
                        break

            elif quality == 'looser':
                for q in ['ultrafine', 'fine', 'medium', 'coarse']:
                    if all(geom_tol[k] < geom_tol_set[q][k] for k in geom_tol):
                        self.param.update(geom_tol_set[q])
                        print(f"geom_tol reduced/loosened to: {q}")
                        break
        else:
            raise ValueError(f"{quality} is not supported")


    def set_restart(self, option: str | None = None):
        """
        A reuse run is essentially a new calculation that tries to reuse as
        much as possible from an earlier calculation.
        """

        self.param.pop('reuse', None)
        self.param.pop('continuation', None)

        if option == 'reuse':
            self.param.update({'reuse': 'default'})
        elif option == 'continuation':
            self.param.update({'continuation': 'default'})

    def set_write(self, option: str | None = None):
        
        if option == "restart":
            self.param.update({
                'backup_interval': 600,
                'write_cell_structure': 'true',
                'write_checkpoint': 'all',
                'write_bib': 'false',
                'write_otfg': 'false',
                'write_cst_esp': 'false',
                'write_bands': 'false',
                'write_geom': 'false',
                'bs_write_eigenvalues': 'false'
            })
        else:
            self.param.update({
                'backup_interval': 0,
                'write_cell_structure': 'true',
                'write_checkpoint': 'none',
                'write_bib': 'false',
                'write_otfg': 'false',
                'write_cst_esp': 'false',
                'write_bands': 'false',
                'write_geom': 'false',
                'bs_write_eigenvalues': 'false'
            })


    def set_spin_fix(self, option: str):
        """
        Default:
        The total spin is held constant for SPIN_FIX SCF cycles
        (or less if electronic convergence criteria met with the fixed spin) and then allowed to relax.
        """
        spin_fix_set = {
            'default_castep': {
                'spin_fix': 10,
                'geom_spin_fix': 0
            },
            'fix': {
                'spin_fix': -1,
                'geom_spin_fix': -1
            }
        }

        if option in set_spin_fix:
            self.param.update(spin_fix_set[option])


    def set_extra_bands(self, perc: int = 20):
        self.param.pop('nextra_bands', None)
        self.param.update({'perc_extra_bands': perc})

    def compare(self, param):
        same = {}
        diff = {}
        other = {}

        for key in param:
            key = key.lower()
            if key in self.param:
                if str(self.param[key]).lower() == str(param[key]).lower():
                    same[key] = str(param[key]).lower()
                else:
                    diff[key] = str(param[key]).lower()
            else:
                other[key] = str(param[key]).lower()

        print("# diff\n")
        print("\n".join([
            f"{key:30s} : {self.param[key]} # {diff[key]}" for key in diff
        ]) + "\n")

        print("# add\n")
        print("\n".join([
            f"{key:30s} : {other[key]}" for key in other
        ]) + "\n")

