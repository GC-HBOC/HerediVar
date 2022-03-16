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

# download dbSNP
cd dbs
mkdir -p dbSNP
cd dbSNP
wget -O - https://ftp.ncbi.nih.gov/snp/latest_release/VCF/GCF_000001405.39.gz | gunzip | python3 $tools/vcf_refseq_to_chrnum.py | $ngsbits/VcfBreakMulti | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort > dbSNP_v155.vcf
bgzip dbSNP_v155.vcf
tabix -p vcf dbSNP_v155.vcf.gz

