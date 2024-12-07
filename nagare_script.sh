#!/bin/bash

VER="$1"
CUSTOMER="$2"
SPECIFIC="$3"

echo "====================="
echo "VER: $VER"
echo "CUSTOMER: $CUSTOMER"
echo "====================="


if [ -z "$SPECIFIC" ]
then
    echo "3"
    sleep 100
else
    echo "2"
    sleep 100
fi
