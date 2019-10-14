#!/bin/bash

logfile=$1
while IFS='' read -r line || [[ -n "$line" ]]; do
    configs=$line
    if [[ "$line" == *"INVALID"* ]]; then
        continue
    fi
    if [[ "$line" == *"---"* ]]; then
	echo "--- ---"
        continue
    fi
    #echo $configs
    #echo $configs
    num=`echo $configs | cut -d "." -f 1`
    num=$((num+1))
    #echo $num
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
    #echo "$num ${f}f ${d}d ${ld}ld ${fcall}fcall ${dcall}dcall"
    echo "[$num, $((f+fcall)), $((d+dcall)), $((ld))]"
done < $logfile
