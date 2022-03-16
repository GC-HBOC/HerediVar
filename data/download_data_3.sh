#!/bin/bash
set -e
set -o pipefail
set -o verbose

###
# This script provides a wrapper for all data download needed to run HerediVar annotation scripts
###

root="$(dirname `pwd`)"
tools=$root/src/tools
data=$root/data
dbs=$data/dbs
ngsbits=$tools/ngs-bits/bin
genome=$data/genomes/GRCh38.fa

mkdir -p $dbs


# download phyloP conservation scores (https://www.ensembl.org/info/docs/tools/vep/script/vep_example.html#gerp)
cd $dbs
mkdir -p phyloP
cd phyloP
wget http://hgdownload.soe.ucsc.edu/goldenPath/hg38/phyloP100way/hg38.phyloP100way.bw