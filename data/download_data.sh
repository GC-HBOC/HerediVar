#!/bin/bash
set -e
set -o pipefail
set -o verbose

###
# This script provides a wrapper for all data download needed to run HerediVar annotation scripts
###

root=`pwd`
tools=$root/tools/
dbs=$root/dbs/

mkdir $dbs

cd $dbs
mkdir HGNC
cd HGNC
wget -O - http://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/tsv/hgnc_complete_set.txt > hgnc_complete_set.tsv