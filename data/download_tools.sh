#!/bin/bash

###
# This script provides a wrapper for all installations needed to run HerediVar annotation scripts
###

root="$(dirname `pwd`)"
tools=$root/src/tools/


#download and build VEP
cd $tools
#chmod 755 ./download_tools_vep.sh
#./download_tools_vep.sh

#download and build ngs-bits
: '
cd $tools
git clone https://github.com/imgag/ngs-bits.git
cd ngs-bits
git checkout 2021_12 && git submodule update --recursive --init
make build_3rdparty
make build_tools_release
'

#download and build samtools
cd $tools
wget https://github.com/samtools/samtools/releases/download/1.11/samtools-1.11.tar.bz2
tar xjf samtools-1.11.tar.bz2
rm samtools-1.11.tar.bz2
cd samtools-1.11
make
cd ..
mv samtools-1.11 samtools