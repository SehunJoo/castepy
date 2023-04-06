#!/bin/bash -l

#$ -N castep
#$ -ac allow=A
#$ -pe mpi 120
#$ -t 1-1
#$ -l mem=4G
#$ -l h_rt=48:00:00
#$ -A Faraday_FCAT
#$ -P Gold
#$ -cwd
#$ -S /bin/bash
#$ -M shj29@cam.ac.uk
#$ -m beas
##$ -m n

# --------------------------------------------------

source ~/.bashrc

# set variables

workdir="${SGE_O_WORKDIR}"
jobid="${JOB_ID}"
taskid="${SGE_TASK_ID}"
jids="${jobid}.${taskid}"
prefix=".spawnpids"

cmdline='castep'
program='castep'
mpinp=$NSLOTS # number of cores : $NSLOTS, number of nodes : $NHOSTS
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

task=$(sed -n '/^task/p' $seed.param  | awk '{print $3}')

# =================================================================================================
# task : singlepoint
# =================================================================================================

# when failure
# *Warning* max. SCF cycles performed but system has not reached the groundstate.
# Warning: electronic minimisation did not converge when finding ground state.
# no Total time
if [[ $task == "singlepoint" ]]; then

    stat='none'
    tol='default'
    elec_method='dm-normal'

    param-spin
    param-tol $tol
    param-scf $elec_method
    param-restart continuation

    for (( i = 1; i <= 10; i++ ))
    do

        # if this is not the first run
        if [[ $stat == 'failure' ]]; then

            tol='default'
            param-tol $tol

            [[ $elec_method == 'dm-fast'   ]] && elec_method='dm-normal'
            [[ $elec_method == 'dm-normal' ]] && elec_method='dm-slow'
            [[ $elec_method == 'dm-slow'   ]] && elec_method='dm-veryslow'
            param-scf $elec_method

            param-restart continuation

        elif [[ $stat == 'success' ]] && [[ $tol == 'default' ]]; then

            tol='ultrafine'
            param-tol $tol

            param-restart continuation

        elif [[ $stat == 'success' ]] && [[ $tol == 'ultrafine' ]]; then

            break;

        fi


        # run

        mpirun -n $mpinp castep.mpi $seed

        # check status

        temp=$(tail -20 $seed.castep | grep "Total time          = " | awk '{print $1}')
        if [[ $temp == 'Total' ]]; then
            stat='success'
        else
            stat='failure'
        fi

        # backup

        seedrun=$(echo $seed $i | awk '{printf "%s-run-%02d", $1, $2}')
        cp $seed.cell     $seedrun.cell
        cp $seed-out.cell $seedrun-out.cell
        [[ $(ls $seed.*.err 2>/dev/null | wc -l) -gt 0 ]] && cat $seed.*.err  > $seedrun.err && rm -rf $seed.*.err

        # if success
        # update input for new run
        [[ $stat == 'success' ]] && new_cell $seed
    done
fi 

# =================================================================================================
# task : geometryoptimization
# =================================================================================================
if [[ $task == "geometryoptimization" ]]; then

    tol='ultrafine'

    param-spin
    param-tol $tol
    param-restart continuation

    stat='none'
    nsuccess=0

    for (( i = 1; i <= 10; i++ ))
    do

        # if this is not the first run

        if [[ $stat == 'failure' ]]; then

            param-restart continuation
            nsuccess=0

        elif [[ $stat == 'success' ]] && [[ $nsuccess -lt 3 ]]; then
            
            param-restart continuation
            nsuccess=$(( nsuccess + 1 ))

        elif [[ $stat == 'success' ]] && [[ $nsuccess -ge 3 ]]; then

            break;

        fi

        # run 

        mpirun -n $mpinp castep.mpi $seed

        # check status

        temp=$(tail -20 $seed.castep | grep "Total time          = " | awk '{print $1}')
        if [[ $temp == 'Total' ]]; then
            stat='success'
        else
            stat='failure'
        fi

        # backup

        seedrun=$(echo $seed $i | awk '{printf "%s-run-%02d", $1, $2}')
        cp $seed.cell     $seedrun.cell
        cp $seed-out.cell $seedrun-out.cell
        [[ $(ls $seed.*.err 2>/dev/null | wc -l) -gt 0 ]] && cat $seed.*.err  > $seedrun.err && rm -rf $seed.*.err
    
        # if success
        # update input for new run
        [[ $stat == 'success' ]] && new_cell $seed
    done
fi


t_end=$(date +%Y-%m-%d\ %H:%M:%S)
echo "end_time:           ${t_end}"                     >> ${prefix}.${jids}

sleep 5

touch DONE_${jobid}
exit 0
