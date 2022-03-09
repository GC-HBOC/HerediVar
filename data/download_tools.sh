#!/bin/bash

###
# This script provides a wrapper for all installations needed to run HerediVar annotation scripts
###

root=`pwd`
folder=$root/tools/


#download and build VEP
cd $root
chmod 755 ./download_tools_vep.sh
./download_tools_vep.sh