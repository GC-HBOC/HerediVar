#!/bin/bash
set -e
set -o pipefail
set -o verbose

###
# This script provides a wrapper for the conversion of HerediCare imports
###

root="$(dirname `pwd`)"
tools=$root/src/tools
data=$root/data
dbs=$data/dbs
ngsbits=$tools/ngs-bits/bin
genome=$data/genomes/GRCh38.fa

mkdir -p $dbs



cd $dbs
mkdir -p HerediCare
cd HerediCare

: ' 
python3 $tools/db_converter_heredicare.py -i heredicare_variants_11.05.22.tsv > heredicare_variants_11.05.22.vcf

# initial sorting, probably unneccessary here
$ngsbits/VcfSort -in heredicare_variants_11.05.22.vcf -out heredicare_variants_11.05.22.vcf

# check
bgzip -f -c heredicare_variants_11.05.22.vcf > heredicare_variants_11.05.22.vcf.gz
$ngsbits/VcfCheck -in heredicare_variants_11.05.22.vcf.gz -ref $data/genomes/GRCh37.fa > vcfcheck_errors.txt

# liftover to hg38
CrossMap.py vcf $data/genomes/hg19ToHg38.fixed.over.chain.gz heredicare_variants_11.05.22.vcf.gz $genome heredicare_variants_11.05.22_lifted.vcf

# add variants which lack a vcf information but have hgvs annotation
$ngsbits/HgvsToVcf -in hgvs.tsv -ref $genome -out hgvs_recovered.vcf 2> hgvstovcf_errors.txt
grep "^[^#]" hgvs_recovered.vcf >> heredicare_variants_11.05.22_lifted.vcf

# leftnormalize & sorting
$ngsbits/VcfSort -in heredicare_variants_11.05.22_lifted.vcf -out heredicare_variants_11.05.22_lifted.vcf
cat heredicare_variants_11.05.22_lifted.vcf | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | bgzip > heredicare_variants_11.05.22_lifted.vcf.gz


$ngsbits/VcfCheck -in heredicare_variants_11.05.22_lifted.vcf.gz -ref $genome >> vcfcheck_errors.txt
'

#cut -f2 heredicare_variants_11.05.22.tsv | grep "^[^#]" | $ngsbits/GenesToApproved | grep "REPLACED" | awk '!seen[$0]++' > legacy_gene_names.tsv

python3 $tools/collect_new_heredicare.py --tsv heredicare_variants_11.05.22.tsv --vcfworked heredicare_variants_11.05.22_lifted.vcf -o heredicare_variants_11.05.22_ANNOTATED.tsv



#tabix -p vcf heredicare_variants_11.05.22.vcf.gz