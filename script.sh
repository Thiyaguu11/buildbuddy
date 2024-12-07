#!/bin/bash

VER="$1"
CUSTOMER="$2"
SPECIFIC="$3"
SCALING_NAME="$4"

echo "====================="
echo "VER: $VER"
echo "CUSTOMER: $CUSTOMER"
echo "====================="


if [ -z "$SCALING_NAME" ]
then
    if [ -z "$SPECIFIC" ]
    then
        echo "4"
        sleep 100
    else
        echo "2"
        sleep 100
    fi
else
    if [ -z "$SPECIFIC" ]
    then
        echo "3"
        sleep 100
    else
        echo "1"
        sleep 100
    fi
fi

echo "Copying package files"  | tee -a ${BUILD_LOG_FILE}

echo "Build complete" | tee -a ${BUILD_LOG_FILE}
