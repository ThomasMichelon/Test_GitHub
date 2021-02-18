#!/bin/bash

set -e

VOLUME_DIR="/home/nabla/tmp"

printf "Volume dir: ${VOLUME_DIR}\n\n"
printf "Simulation type: ${SIMULATION_TYPE}\n\n"

SRC="/home/nabla/OpenFoam"

# Copy the OpenFoam folder to the execution volume
rm -rf $VOLUME_DIR/*
mkdir -p $VOLUME_DIR
mkdir -p $VOLUME_DIR/OpenFoam
cp -r $SRC/* $VOLUME_DIR/OpenFoam

# Replace the OpenFoam variables
node replace.js

# Copy the model to the simulation folder on S3
aws s3 cp $MODEL_URL $SIMULATION_URL

# Download the model from the simulation folder on S3
aws s3 cp $SIMULATION_URL $VOLUME_DIR/OpenFoam/constant/triSurface/model.stl

# Debug the disk size
#lsblk

# Debug the contents of the VOLUME_DIR
#ls -la $VOLUME_DIR

# Cd the OpenFoam base directory
cd $VOLUME_DIR/OpenFoam

# Prepare stl
./prepModel.py

# Make domain
./autoDomain.py

# Run the simulation
./Allrun

cp log.* log/
echo "Uploading log files to S3"
aws s3 cp $VOLUME_DIR/OpenFoam/log $OUTPUT_URL --recursive

# Postprocessing
echo "Running getValues.py"
./getValues.py
echo "Running plotSlices.py"
./plotSlices.py 'vel' 'X'
./plotSlices.py 'vel' 'Y'
./plotSlices.py 'vel' 'Z'
./plotSlices.py 'vor' 'X'
echo "Running plotPressure.py"
./plotPressure.py
echo "Running plotBins.py"
./plotBinsBackground.py
./plotBins.py

# Upload the simulation output to s3
echo "Uploading output to S3"
aws s3 cp $VOLUME_DIR/OpenFoam/fig $OUTPUT_URL --recursive
