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


# download BRCA exchange (https://brcaexchange.org/releases)
: '
cd $dbs
mkdir -p BRCA_exchange
cd BRCA_exchange
wget https://brcaexchange.org/backend/downloads/releases/release-02-22-22/release-02-22-22.tar.gz
tar -xf release-02-22-22.tar.gz
mv -f output/release/built_with_change_types.tsv .
rm -rf output/
python3 $tools/db_converter_brca_exchange.py -i built_with_change_types.tsv | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | bgzip > BRCA_exchange_02-22-22.vcf.gz
tabix -p vcf BRCA_exchange_02-22-22.vcf.gz
'


# download ensembl transcripts (http://ftp.ensembl.org/pub/current_gff3/homo_sapiens/)
: '
cd $dbs
mkdir -p ensembl
cd ensembl
wget http://ftp.ensembl.org/pub/current_gff3/homo_sapiens/Homo_sapiens.GRCh38.105.gff3.gz
'


#download GRCH37 reference_genome
: '
cd $data
chmod 755 ./download_GRCh37.sh
./download_GRCh37.sh
'



# download FLOSSIES (https://whi.color.com/about) there is no versioning so the date specified in the filename equals the date when the database was accessed
cd $dbs
mkdir -p FLOSSIES
cd FLOSSIES
flossies_file=FLOSSIES_25-03-2022.vcf
cat $data/FLOSSIES_data_uris.txt | python3 $tools/data_uri_to_blob.py --header | python3 $tools/db_converter_flossies.py > $flossies_file
$ngsbits/VcfSort -in $flossies_file -out $flossies_file
$ngsbits/VcfLeftNormalize -in $flossies_file -stream -ref $data/genomes/GRCh37.fa -out $flossies_file.2
$ngsbits/VcfStreamSort -in $flossies_file.2 -out $flossies_file
awk -v OFS="\t" '!/##/ {$9=$10=""}1' $flossies_file |sed 's/^\s\+//g' > $flossies_file.2 # remove SAMPLE and FORMAT columns from vcf as they are added by vcfsort
mv -f $flossies_file.2 $flossies_file
bgzip $flossies_file

$ngsbits/VcfCheck -in $flossies_file.gz -ref $data/genomes/GRCh37.fa

# crossmap to lift from GRCh37 to GRCh37
CrossMap.py vcf $data/genomes/hg19ToHg38.over.chain.gz $flossies_file.gz $genome $flossies_file.2
cat $flossies_file.2 | $ngsbits/VcfLeftNormalize -stream -ref $data/genomes/GRCh37.fa | $ngsbits/VcfStreamSort | bgzip > $flossies_file.gz
tabix -p vcf $flossies_file.gz
rm -f $flossies_file.2

$ngsbits/VcfCheck -in $flossies_file.gz -ref $genome
