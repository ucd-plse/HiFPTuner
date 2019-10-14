#!/bin/bash

# ###################################
# Shell script to remove output files
# Use: ./compile.sh driver_name .
# ####################################

scriptPath=$CORVETTE_PATH"/scripts"
#loggingPath=$CORVETTE_PATH"/logging"

#source $scriptPath/loglib.sh
clang -emit-llvm -c -I $GSL_PATH $2/$1.c -o $2/$1.bc #/temp_$1.bc
#llvm-link -o $2/$1.bc $loggingPath/loglib.bc $2/temp_$1.bc

#rm $2/temp_$1.bc 
