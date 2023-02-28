#!/bin/bash -l

#SBATCH --job-name=castep
#SBATCH --time=00:20:00
#SBATCH --nodes=4
#SBATCH --tasks-per-node=64
#SBATCH --cpus-per-task=2
#SBATCH --array=1-1
#SBATCH --account=e89-camm
#SBATCH --partition=standard
#SBATCH --qos=short

# --------------------------------------------------

source /work/e89/e89/shj29/.bashrc
#module load PrgEnv-gnu
#module load castep/22.11


# set variables

workdir="${SLURM_SUBMIT_DIR}"
jobid="${SLURM_ARRAY_JOB_ID}"
taskid="${SLURM_ARRAY_TASK_ID}"
jids="${jobid}.${taskid}"
prefix=".spawnpids"

cmdline='castep'
program='castep'
mpinp='256'
export OMP_NUM_THREADS=1

t_submit='2023-02-27 18:21:36'
t_start="$(date +%Y-%m-%d\ %H:%M:%S)"
tsec_start=$(date +%s)

# launch program

echo "--------------------${jids}"                       > ${prefix}.${jids}
echo "program:            ${program}"                   >> ${prefix}.${jids}
echo "command:            ${cmdline}"                   >> ${prefix}.${jids}
echo "jobid:              ${jobid}"                     >> ${prefix}.${jids}
echo "mpinp:              ${mpinp}"                     >> ${prefix}.${jids}
echo "submit_time:        ${t_submit}"                  >> ${prefix}.${jids}
echo "start_time:         ${t_start}"                   >> ${prefix}.${jids}

seed='LiNiO2'
for i in {1..3}
do
    srun --distribution=block:block --hint=nomultithread castep.mpi $seed
    cp $seed.cell $seed-${i}.cell
    cp $seed-out.cell $seed-out-${i}.cell
    new_cell $seed
done


t_end=$(date +%Y-%m-%d\ %H:%M:%S)
echo "end_time:           ${t_end}"                     >> ${prefix}.${jids}

sleep 5

touch DONE_${jobid}
exit 0
