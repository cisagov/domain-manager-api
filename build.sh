#!/usr/bin/env bash

set -o nounset
set -o errexit
set -o pipefail

###
# Define the name of the Lambda zip file being produced.
###
ZIP_FILE=skeleton-aws-lambda.zip

###
# Set up the Python virtual environment.
# We use --system-site-packages so the venv has access to the packages already
# installed in the container to avoid duplicating what will be available in the
# lambda environment on AWS.
###
VENV_DIR=/venv
python -m venv --system-site-packages $VENV_DIR

# Here shellcheck complains because it can't follow the dynamic path.
# The path doesn't even exist until runtime, so we must disable that
# check.
#
# shellcheck disable=1090
source $VENV_DIR/bin/activate

###
# Upgrade pip.
###
pip install --upgrade pip

###
# Install local example AWS lambda (eal) and requirements.
###
pip install --requirement requirements.txt

###
# Leave the Python virtual environment.
#
# Note that we have to turn off nounset before running deactivate,
# since otherwise we get an error that states "/venv/bin/activate:
# line 31: $1: unbound variable".
###
set +o nounset
deactivate
set -o nounset

###
# Set up the build directory.
###
BUILD_DIR=/build

###
# Copy all packages, including any hidden dotfiles. Also copy the
# local eal package and the lambda handler.
###
cp -rT $VENV_DIR/lib/python3.8/site-packages/ $BUILD_DIR
cp -rT $VENV_DIR/lib64/python3.8/site-packages/ $BUILD_DIR
cp -r eal $BUILD_DIR
cp lambda_handler.py $BUILD_DIR

###
# Zip it all up.
###
OUTPUT_DIR=/output
if [ ! -d $OUTPUT_DIR ]
then
    mkdir $OUTPUT_DIR
fi

if [ -e $OUTPUT_DIR/$ZIP_FILE ]
then
    rm $OUTPUT_DIR/$ZIP_FILE
fi

cd $BUILD_DIR
zip -rq9 $OUTPUT_DIR/$ZIP_FILE .
