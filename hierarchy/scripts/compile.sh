#!/bin/bash

##Usage: Script {test}.bc

my_dir="$(dirname "$0")"
source $my_dir/env.sh

test=`echo $1 | sed 's/\(.*\).bc/\1/'`

#clang -c -emit-llvm $test.c -o temp_$test.bc
#llvm-link -o $test.bc temp_$test.bc $auto_tuning/utils/doProfiling.bc $auto_tuning/utils/jsoncpp.bc
#rm temp_$test.bc

llvm-link -o json_$test.bc $test.bc $auto_tuning/utils/doProfiling.bc $auto_tuning/utils/jsoncpp.bc
