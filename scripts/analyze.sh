#!/bin/bash

##Usage: Script json_{test}.bc

my_dir="$(dirname "$0")"
source $my_dir/env.sh

test=`echo $1 | sed 's/\(.*\).bc/\1/'`

#instrument the bitcode file
opt -load $auto_tuning/src/varDeps/Passes.so -edge-profiling $1 > i_$1
opt -load $auto_tuning/src/varDeps/Passes.so -print-varDeps $1 > /dev/null

#compile and run the instrumented file
llc i_$test.bc -o i_$test.s
g++ i_$test.s -O2 -lm -llog -L$CORVETTE_PATH/logging -o i_$test.out
rm i_$test.s 

echo "start to run the instrumented file"
start=`date +%s.%N`
time ./i_$test.out
end=`date +%s.%N`
runtime=$(echo "$end - $start" | bc)
echo "instrumented file finished its execution in $runtime seconds" > auto-tuning_analyze_time.txt

#analyze the weighted dependence graph
#start=`date +%s.%N`
#time python -O $auto_tuning/src/graphAnalysis/varDepGraph_pro.py
#end=`date +%s.%N`
#runtime=$(echo "$end - $start" | bc)
#echo "auto-tuning finishes in $runtime seconds" >> auto-tuning_analyze_time.txt
