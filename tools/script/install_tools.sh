#!/bin/bash
set -e
set -o pipefail
set -o verbose


# CONFIGURE YOUR PATH HERE!
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
root=$(dirname $(dirname $(dirname $SCRIPT_DIR)))




# set relative paths
tools=$root/tools
js_packages=$root/src/frontend_celery/webapp/static/packages


# install system requirements
sudo apt-get update
sudo apt-get install autoconf automake make gcc perl zlib1g-dev libbz2-dev liblzma-dev libcurl4-gnutls-dev libssl-dev libncurses5-dev libncursesw5-dev
sudo apt-get install g++ libqt5xmlpatterns5-dev libqt5sql5-mysql libcurl4 libcurl4-openssl-dev
sudo apt-get install qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools
sudo apt-get install -y mariadb-server
sudo apt-get install default-jdk -y
sudo apt install genometools
sudo apt install libpq-dev


# prepare python venv & install packages
# python must be installed already
$tools/script/install_python.sh -p $root/


# prepare htslisb
$tools/script/install_htslib.sh -p $tools/ -v 1.16

# prepare keycloak
$tools/script/install_keycloak.sh -p $tools/ -v 18.0.0

# prepare redis
$tools/script/install_redis.sh -p $tools/


# prepare samtools
$tools/script/install_samtools.sh -p $tools/ -v 1.11

# prepare vep
$tools/script/install_vep.sh -p $tools/

# prepare ngs bits
$tools/script/install_ngs_bits.sh -p $tools/ -v 2022_10

# prepare automatic classification algorithm
$tools/script/install_automatic_classification.sh -p $tools



# install bootstrap
$tools/script/install_bootstrap.sh -p $js_packages -v 5.2.3

# install igv
$tools/script/install_igv_js.sh -p $js_packages -v 2.13.9
# download csp conform version from: https://download.imgag.de/ahdoebm1/igv/

# install jquery
$tools/script/install_jquery.sh -p $js_packages -v 3.6.3


# install datatables
$tools/script/install_datatables.sh -p $js_packages -v 1.13.4