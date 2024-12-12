#!/bin/bash

VER="$1"
CUSTOMER="$2"
SPECIFIC="$3"

echo "====================="
echo "VER: $VER"
echo "CUSTOMER: $CUSTOMER"
echo "====================="
echo "PROGRESS:0"

if [ -z "$SPECIFIC" ]
then
    echo "PROGRESS:10"
    sleep 1
    echo "PROGRESS:20"
    sleep 1
    echo "PROGRESS:30"
    sleep 1
    echo "PROGRESS:40"
    sleep 1
    echo "PROGRESS:50"
    sleep 1
    echo "PROGRESS:60"
    sleep 1
    echo "PROGRESS:70"
    sleep 1
    echo "PROGRESS:80"
    sleep 1
    echo "PROGRESS:90"
    sleep 1
    echo "PROGRESS:100"
else
    for i in {1..100}
    do
        sleep 1
        echo "PROGRESS:99"
    done
fi
echo "Build complete"
echo "PROGRESS:100"