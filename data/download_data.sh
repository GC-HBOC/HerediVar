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

# download GRCH38 genome
: '
cd $data
chmod 755 ./download_GRCh38.sh
./download_GRCh38.sh
'

# download HGNC
: '
cd $dbs
mkdir HGNC
cd HGNC
wget -O - http://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/tsv/hgnc_complete_set.txt > hgnc_complete_set.tsv
'

# download gnomAD genome data
cd $dbs
mkdir -p gnomAD
cd gnomAD
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr1.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py --header > gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr2.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr3.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr4.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr5.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr6.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr7.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr8.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr9.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr10.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr11.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr12.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr13.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr14.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr15.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr16.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr17.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr18.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr19.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr20.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr21.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr22.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chrX.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chrY.vcf.bgz | gunzip  | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
#python3 $tools/db_filter_gnomad.py -i gnomAD_genome_v3.1.1_GRCh38_unprocessed.vcf --header # > gnomAD_genome_v3.1.1_GRCh38.vcf
bgzip gnomAD_genome_v3.1.2_GRCh38.vcf
tabix -p vcf gnomAD_genome_v3.1.2_GRCh38.vcf.gz

wget -O - https://gnomad-public-us-east-1.s3.amazonaws.com/release/3.1/vcf/genomes/gnomad.genomes.v3.1.sites.chrM.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | python3 $tools/db_filter_gnomad.py > gnomAD_genome_v3.1.mito_GRCh38.vcf
bgzip gnomAD_genome_v3.1.mito_GRCh38.vcf
tabix -p vcf gnomAD_genome_v3.1.mito_GRCh38.vcf.gz