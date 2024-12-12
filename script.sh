#!/bin/bash

set -x
VER="$1"
CUSTOMER="$2"
SPECIFIC="$3"
SCALING_NAME="$4"


echo "====================="
echo "VER: $VER"
echo "CUSTOMER: $CUSTOMER"

if [ ! -z $SPECIFIC ]
then
    echo "SPECIFIC: $SPECIFIC"
fi
if [ ! -z $SCALING_NAME ]
then
    echo "SCALING_NAME: $SCALING_NAME"
fi
echo "====================="

# Your existing script logic here


script_dir=`pwd`
echo $script_dir

cd /jidoka_build/
# Get latest version of jt.devops
if [ ! -d jt.devops ]
then 
    echo "Getting jt.devops"
    git clone --progress git@git_devops:jidoka-tech/jt.devops
else 
    pushd jt.devops
    echo "Pulling latest version of jt.devops"
    git pull
    popd
fi

BUILD_DATE=`TZ=UTC-5:30 date +%Y%m%d%H%M`
BUILD_LOG_FILE=/jidoka_deploy/build_logs/build_log_${VER}_${CUSTOMER}_${BUILD_DATE}.txt
BINARY_DIR=/mnt/srv1/Customer/${CUSTOMER}/Binary/${VER}

# Remove model folder if present (clean up)
if [ -d models ]
then
    echo "Removing models directory from previous build"
    rm -r models
fi

# Remove testdata folder if present (clean up)
if [ -d testdata ]
then
    echo "Removing testdata directory from previous build"
    rm -r testdata
fi

if [ -z "$SCALING_NAME" ]
then
    SEMVER_FILE=./jt.devops/customer/${CUSTOMER}/${CUSTOMER}_${VER}.json
    if [ ! -f "$SEMVER_FILE" ] 
    then 
        echo "SEMVER configuration file $SEMVER_FILE doesn't exist. Exiting" | tee -a ${BUILD_LOG_FILE}
        exit 1
    fi
else
    SEMVER_FILE=./jt.devops/customer/${SCALING_NAME}/${CUSTOMER}/${CUSTOMER}_${VER}.json
    if [ ! -f "$SEMVER_FILE" ] 
    then 
        echo "SEMVER configuration file doesn't exist. Exiting"
        exit 1
    fi
fi

# Define storage location for binaries 
STORAGE_MOUNT_PATH=`cat $SEMVER_FILE | jq '."project_mount_path"' | tr -d '"'`
STORAGE_LOCATION=`cat $SEMVER_FILE | jq '."project_storage_location"' | tr -d '"'`
BINARY_PATH="Binary/"
DOCKER_PATH="Docker_Repository/"

if [[ "$STORAGE_MOUNT_PATH" == "null" || "$STORAGE_LOCATION" == "null" || "$BINARY_PATH" == "null" ]]
then
    STORAGE_MOUNT_PATH=/mnt/srv1/Customer/
    BINARY_DIR=/mnt/srv1/Customer/${CUSTOMER}/Binary/${VER}
    DOCKER_REPOSITORY=/mnt/srv1/Customer/${CUSTOMER}/Docker_Repository/
    echo "No specific storage specified for binary folder. Defaulting to $BINARY_DIR" | tee -a ${BUILD_LOG_FILE}
else
    BINARY_DIR=${STORAGE_MOUNT_PATH}${STORAGE_LOCATION}${BINARY_PATH}/${VER}
    DOCKER_REPOSITORY=${STORAGE_MOUNT_PATH}${STORAGE_LOCATION}${DOCKER_PATH}
    echo "Saving binaires to $BINARY_DIR" | tee -a ${BUILD_LOG_FILE}
fi

if [ -z "$SCALING_NAME" ]
then
    if [ -z "$SPECIFIC" ]
    then
        ./jt.devops/build/build_all_v3.sh ${VER} ${CUSTOMER} --clean --package --ci --sanity --slack | tee -a ${BUILD_LOG_FILE}
    else
        ./jt.devops/build/build_all_v3.sh ${VER} ${CUSTOMER} ${SPECIFIC} --clean --package --ci --sanity --slack | tee -a ${BUILD_LOG_FILE}
    fi
else
    if [ -z "$SPECIFIC" ]
    then
        ./jt.devops/build/build_all_v3.sh ${VER} ${CUSTOMER} ${SPECIFIC} --scaling-build=${SCALING_NAME} --clean --package --ci --sanity --slack | tee -a ${BUILD_LOG_FILE}
    else
        ./jt.devops/build/build_all_v3.sh ${VER} ${CUSTOMER} ${SPECIFIC} --scaling-build=${SCALING_NAME} --clean --package --ci --sanity --slack | tee -a ${BUILD_LOG_FILE}
    fi
fi

echo "Copying package files"  | tee -a ${BUILD_LOG_FILE}
mkdir -p ${BINARY_DIR}
mkdir -p ${DOCKER_PATH}
mv /jidoka/*.tar ${DOCKER_PATH}/ 2>/dev/null
mv /jidoka_build/*install.sh ${BINARY_DIR}/

echo "Build complete" | tee -a ${BUILD_LOG_FILE}
