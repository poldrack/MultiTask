#!/bin/bash
#
# Simple SLURM script for submitting multiple serial
# jobs (e.g. parametric studies) using a script wrapper
# to launch the jobs.
#
# To use, build the launcher executable and your
# serial application(s) and place them in your WORKDIR
# directory.  Then, edit the CONTROL_FILE to specify 
# each executable per process.
#-------------------------------------------------------
#-------------------------------------------------------
# 
#         <------ Setup Parameters ------>
#
#SBATCH -J bidscopy
#SBATCH -N 1
#SBATCH -p normal
#SBATCH -o bidscopy.o%j
#SBATCH --ntasks-per-node 16
#SBATCH -t 24:00:00
#          <------ Account String ----->
# <--- (Use this ONLY if you have MULTIPLE accounts) --->
##SBATCH -A
#------------------------------------------------------
#export LAUNCHER_PPN=16

export LAUNCHER_PLUGIN_DIR=$LAUNCHER_DIR/plugins
export LAUNCHER_RMI=SLURM
export LAUNCHER_JOB_FILE=bids_commands.sh
 
$LAUNCHER_DIR/paramrun

