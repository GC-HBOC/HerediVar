#!/bin/bash
set -e
set -o pipefail
set -o verbose

#General description:
#  https://wiki.dnanexus.com/scientific-notes/human-genome
#Description of decoy sequences:
#  ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/reference/phase2_reference_assembly_sequence/README_human_reference_20110707

root="$(dirname `pwd`)"
samtools=$root/src/tools/samtools-1.11/samtools

mkdir -p `pwd`/genomes/
genome=`pwd`/genomes
cd $genome

wget https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/reference/phase2_reference_assembly_sequence/hs37d5.fa.gz
(gunzip -c hs37d5.fa.gz | sed -r 's/>/>chr/g' > GRCh37.fa) || true
rm hs37d5.fa.gz

# build indexy
$samtools faidx GRCh37.fa


# download GRCh37 to GRCh38 chain file for liftover (version date: 2013-12-31 23:08  222K)
wget http://hgdownload.soe.ucsc.edu/goldenPath/hg19/liftOver/hg19ToHg38.over.chain.gz
(gunzip -c hg19ToHg38.over.chain.gz | sed -r 's/chrM/chrMT/g' | bgzip > hg19ToHg38.fixed.over.chain.gz) || true
rm hg19ToHg38.over.chain.gz
# alternatively use the chain file from ensembl download: wget http://ftp.ensembl.org/pub/assembly_mapping/homo_sapiens/GRCh37_to_GRCh38.chain.gz