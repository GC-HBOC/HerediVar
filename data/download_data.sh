#!/bin/bash
set -e
set -o pipefail
set -o verbose

###
# This script provides a wrapper for all data download needed to run HerediVar annotation scripts
###

root=`pwd`
folder=$root/dbs/
tools=$root/tools/

