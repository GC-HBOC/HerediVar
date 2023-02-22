#!/bin/bash

###
# This script provides a wrapper for all installations needed to run HerediVar annotation scripts
###

root="$(dirname `pwd`)"
tools=$root/src/tools/


# download xpath
# sudo apt-get install libxml-xpath-perl

#download and build VEP
#cd $tools
#chmod 755 ./download_tools_vep.sh
#./download_tools_vep.sh

#download and build ngs-bits

cd $tools 
git clone --recursive https://github.com/imgag/ngs-bits.git
cd ngs-bits
##git checkout 2021_12 && git submodule update --recursive --init ## select stable version once project is finished!
make build_3rdparty build_libs_release build_tools_release



#download and build samtools

cd $tools
wget https://github.com/samtools/samtools/releases/download/1.11/samtools-1.11.tar.bz2
tar xjf samtools-1.11.tar.bz2
rm samtools-1.11.tar.bz2
cd samtools-1.11
make
cd ..
mv samtools-1.11 samtools


# download and build htslib

cd $tools
wget https://github.com/samtools/htslib/releases/download/1.16/htslib-1.16.tar.bz2
tar -vxjf htslib-1.16.tar.bz2
cd htslib-1.16
make
rm -f htslib-1.16.tar.bz2




# python setup
# create venv and download packages
: '
cd $root
python3 -m venv .venv
source .venv/bin/activate

python3 -m pip install --upgrade pip
pip install wheel
pip install setuptools
python3 -m pip install --upgrade setuptools wheel

pip install flask flask-session flask-paginate
#pip install Flask-OIDC
pip install authlib
pip install mysql-connector


pip install spliceai tensorflow
pip install CrossMap



pip install blinker
pip install lxml


pip install celery redis

pip install reportlab

pip install python-dotenv


pip install biopython



pip install jsonschema

pip install pytest
'

#### previous click version: 8.0.4 (before celery installation)


# install keycloak
cd $tools
wget https://github.com/keycloak/keycloak/releases/download/18.0.0/keycloak-18.0.0.zip
unzip keycloak-18.0.0.zip
rm keycloak-18.0.0.zip