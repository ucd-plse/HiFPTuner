#!/bin/bash

TAIL=$1
if [ "$TAIL" == "" ]; then
    TAIL=1
fi
#ls | grep "time.txt" | sed "s/^/cat /" | sh +x
#echo "---"
ls | grep "log.dd" | sed -e "s/^/cat /" -e "s/$/ \| wc -l/" | sh +x
echo "---"
ls | grep "time.txt" | sed -e "s/^/sed -n '3p' /" -e "s/$/ \| cut -d ':' -f 2/" | sh +x
echo "----"
odds=`ls | grep "time.txt" | sed -e "s/^/sed -n '2p' /" | sh +x`
echo $odds
cmp=`echo $odds | grep "/"`
if [ "$cmp" != "" ]; then
    mod=`echo $odds | cut -d "/" -f 1 | sed "s/ //g"`
    ori=`echo $odds | cut -d "/" -f 2 | sed "s/ //g"`
    imp=`echo "scale=6; ($ori-$mod)*100/$ori" | bc`
    echo $imp%    
fi
echo "----"
logs=`ls | grep "log.dd"`
for log in $logs; do
    configs=`tail -$TAIL $log | sed -n "1p"`
    echo $configs
    f=0
    d=0
    ld=0
    fcall=0
    dcall=0
    for config in $configs; do
        index=`expr index "$config" ':'`
        if [ $index -eq 0 ] || [ $index -eq 1 ]; then
            continue
        fi
        type=`echo $config | cut -d ":" -f 2`
        case $type in
            "f") f=$((f+1)) ;;
            "d") d=$((d+1)) ;;
            "ld") ld=$((ld+1)) ;;
            *)
               i=$((${#type}-1))
               fc=${type:$i:1}
               if [ "$fc" == "f" ]; then
                   fcall=$((fcall+1))
               else
                   dcall=$((dcall+1))
               fi ;;
        esac        
    done
    echo "${f}f ${d}d ${ld}ld ${fcall}fcall ${dcall}dcall"
done
