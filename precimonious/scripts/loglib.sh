#!/bin/bash

# ###################################
# Shell script to create llvm bitcode files
# Use: ./compile.sh
# ####################################

loggingPath=$CORVETTE_PATH"/logging"

clang -emit-llvm -c $loggingPath/cov_checker.c -o $loggingPath/cov_checker.bc
clang -emit-llvm -c $loggingPath/timers.c -o $loggingPath/timers.bc
clang -emit-llvm -c $loggingPath/cov_serializer.c -o $loggingPath/cov_serializer.bc
clang -emit-llvm -c $loggingPath/cov_log.c -o $loggingPath/cov_log.bc
clang -emit-llvm -c $loggingPath/cov_rand.c -o $loggingPath/cov_rand.bc
llvm-link -o $loggingPath/loglib.bc $loggingPath/cov_checker.bc $loggingPath/cov_serializer.bc $loggingPath/cov_log.bc $loggingPath/cov_rand.bc $loggingPath/timers.bc

