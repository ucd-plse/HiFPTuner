#!/bin/bash
echo run benchmark
BcFilePrefix=`echo $1 | sed -n "s/\(.*\).bc.out/\1/p"`
echo $BcFilePrefix

./$BcFilePrefix.bc.out

c=`cat $BcFilePrefix-runtimes`
c=$((c+1))
echo $c >$BcFilePrefix-runtimes
