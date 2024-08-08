#!/usr/bin/env python
#
import sys
import argparse
import random
import time
import subprocess



def usage():
    parser = argparse.ArgumentParser(description='Run many castep/repose/ramble computations')
    parser.add_argument('-exec', type=str, help='Use this executable')
    parser.add_argument('-launch', type=str, help='Use this parallel launcher')
    parser.add_argument('-mpinp', type=int, default=0, help='Number of cores per mpi Castep')
    parser.add_argument('-keep', action='store_true', help='Keep all output files')
    parser.add_argument('-nostop', action='store_true', help='Keep the script running')
    parser.add_argument('-cycle', action='store_true', help='Retry failed runs')
    parser.add_argument('-pack', action='store_true', help='Run with packed data')
    parser.add_argument('-num', type=int, default=1000, help='Max number to unpack')
    parser.add_argument('-workdir', type=str, default='.', help='Work directory')
    parser.add_argument('-h', '--help', action='store_true', help='Show this help message and exit')

    args = parser.parse_args()

    if args.help:
        parser.print_help()
        sys.exit()

    return args



def main():

    time.sleep(random.random())

    # make work directory

    os.makedirs(opt_workdir, exist_ok=True)

    # list files with .res extension in the hopper directory

    try:
        files = subprocess.check_output(
            f"ls -U hopper | head -{args.num} | grep '\.res\$' | grep '-' | shuf", shell=True
        ).decode('utf-8').split()

    except subprocess.CalledProcessError:
        pass


    if len(files) == 0:
        time.sleep(random.random())
        if args.nostop == False:
            exit()

    # get one of the files in the hopper directory

    gotfile = False
    f = ""

    for f in files:
        hopper_path = os.path.join("hopper", f)
        workdir_path = os.path.join(args.workdir, f)
        if not os.path.isfile(workdir_path):
            try:
                shutil.move(hopper_path, workdir_path)
                if os.path.isfile(workdir_path):
                    gotfile = True
                    break
            except Exception as e:
                print(f"Error moving file {f}: {e}")

    # prepare input files

    if gotfile == True:

        # remove './' from file paths

        f = f.lstrip('./')

        # parse root and seed

        tmp = file.split('.cell')
        seed = tmp[0]
        tmp = seed.split('-')
        root = tmp[0]

        # executables
        executable = 'castep'
        if args.exec:
            executable = args.exec

        if args.mpinp > 0:
            launcher = 'mprun -np '
            if args.launch:
                launcher = args.launch
            executable = f"{opt_launch}{opt_mpinp} {executable}"




if __name__ == "__main__":
    args = usage()

