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


# Install CADD - http://cadd.gs.washington.edu/download
cd $dbs
mkdir CADD
cd CADD
wget -O - http://kircherlab.bihealth.org/download/CADD/v1.6/GRCh38/whole_genome_SNVs.tsv.gz > CADD_SNVs_1.6_GRCh38.tsv.gz
zcat CADD_SNVs_1.6_GRCh38.tsv.gz | php $src/Tools/db_converter_cadd.php -build GRCh38 -in - -out - | $ngsbits/VcfStreamSort | bgzip > CADD_SNVs_1.6_GRCh38.vcf.gz
tabix -f -p vcf CADD_SNVs_1.6_GRCh38.vcf.gz
$ngsbits/VcfCheck -in CADD_SNVs_1.6_GRCh38.vcf.gz -lines 0 –ref $genome

wget -O - https://kircherlab.bihealth.org/download/CADD/v1.6/GRCh38/gnomad.genomes.r3.0.indel.tsv.gz > CADD_InDels_1.6_GRCh38.tsv.gz
zcat CADD_InDels_1.6_GRCh38.tsv.gz | php $src/Tools/db_converter_cadd.php -build GRCh38 -in - -out - | $ngsbits/VcfStreamSort | bgzip > CADD_InDels_1.6_GRCh38.vcf.gz
tabix -f -p vcf CADD_InDels_1.6_GRCh38.vcf.gz
$ngsbits/VcfCheck -in CADD_InDels_1.6_GRCh38.vcf.gz -lines 0 –ref $genome
