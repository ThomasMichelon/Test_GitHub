#!/bin/bash

for cpu in /sys/devices/system/cpu/cpu[1-9]*; do
    if [ -e "$cpu/topology/thread_siblings_list" ]; then
        sibling=$(awk -F '[^0-9]' '{ print $2 }' $cpu/topology/thread_siblings_list)
        if [ ! -z $sibling ]; then
            echo 0 | sudo tee "/sys/devices/system/cpu/cpu$sibling/online" > /dev/null
        fi
    fi
done
