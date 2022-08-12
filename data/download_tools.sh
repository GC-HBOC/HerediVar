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
: ' '
git clone --recursive https://github.com/imgag/ngs-bits.git
cd ngs-bits
##git checkout 2021_12 && git submodule update --recursive --init ## select stable version once project is finished!
make build_3rdparty
make build_libs_release
make build_tools_release



#download and build samtools
: '
cd $tools
wget https://github.com/samtools/samtools/releases/download/1.11/samtools-1.11.tar.bz2
tar xjf samtools-1.11.tar.bz2
rm samtools-1.11.tar.bz2
cd samtools-1.11
make
cd ..
mv samtools-1.11 samtools
'

# download python

# create venv and download packages
: '
cd $root
python3 -m venv .venv
source .venv/bin/activate

python3 -m pip install --upgrade pip
pip install wheel
pip install setuptools
python3 -m pip install --upgrade setuptools wheel

pip install mysql-connector
pip install spliceai
pip install tensorflow
pip install flask
pip install flask-mysql

pip3 install CrossMap

pip install biopython
pip install flask-paginate

#pip install Flask-OIDC
pip install authlib
pip install blinker

pip install lxml
'

#### previous click version: 8.0.4 (before celery installation)


#cd $tools
#wget https://github.com/keycloak/keycloak/releases/download/18.0.0/keycloak-18.0.0.zip
#unzip keycloak-18.0.0.zip
#rm keycloak-18.0.0.zip