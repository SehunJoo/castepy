#!/bin/bash -l

#SBATCH --job-name=castep
#SBATCH --time=00:20:00
#SBATCH --nodes=4
#SBATCH --tasks-per-node=128
#SBATCH --cpus-per-task=1
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

seed=$(ls *.param)
seed=${seed%.param}

# spe

# geomopt
niter=4
for (( i = 1; i <= $niter; i++ ))
do
    if [[ $i -eq 1 ]]
    then
        echo
        #sed -i 's/^task [[:print:]]*/task                      : singlepoint/' $seed.param
        #sed -i 's/^metals_method [[:print:]]*/metals_method             : edft/' $seed.param
    else
        sed -i 's/^task [[:print:]]*/task                      : geometryoptimization/' $seed.param
        sed -i 's/^metals_method [[:print:]]*/metals_method             : dm/' $seed.param
    fi

    seedrun=$(echo $seed $i | awk '{printf "%s-run-%02d", $1, $2}')
    srun --distribution=block:block --hint=nomultithread --exclusive castep.mpi $seed
    cp $seed.cell     $seedrun.cell
    cp $seed-out.cell $seedrun-out.cell
    [[ $(ls $seed.*.err 2>/dev/null | wc -l) -gt 0 ]] && cat $seed.*.err  > $seedrun.err && rm -rf $seed.*.err

    stat=$(tail -20 $seed.castep | grep "Total time          = " | awk '{print $1}')
    [[ $stat == Total ]] && new_cell $seed
done


t_end=$(date +%Y-%m-%d\ %H:%M:%S)
echo "end_time:           ${t_end}"                     >> ${prefix}.${jids}

sleep 5

touch DONE_${jobid}
exit 0
