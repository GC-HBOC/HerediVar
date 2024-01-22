#!/bin/bash
set -e
set -o pipefail
set -o verbose

helpFunction()
{
   echo ""
   echo "Usage: $0 -p path -n foldername -v version -t tools_path -g genomes -y pythonpath"
   echo "This script installs the grch38 reference genome"
   echo -e "\t-p Where should the new data be stored"
   echo -e "\t-t Paths of tools. Always key=value pairs."
   echo -e "\t-g Paths of genomes. Always key=value pairs."
   echo -e "\t-v Put the date when you downloaded it: eg 3.1.2."
   echo -e "\t-y Path to the virtual environment"
   exit 1 # Exit script after printing help
}

while getopts "p:n:v:t:g:y:" opt
do
   case "$opt" in
      p ) basedir="$OPTARG" ;;
      t ) tools="$OPTARG" ;;
      g ) genomes="$OPTARG" ;;
      n ) foldername="$OPTARG" ;;
      v ) version="$OPTARG" ;;
      y ) venv="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

OIFS=$IFS
IFS=' ' read -ra arr <<< "$tools"
for ARGUMENT in "${arr[@]}"; do
    KEY=$(echo $ARGUMENT | cut -f1 -d=)

    KEY_LENGTH=${#KEY}
    VALUE="${ARGUMENT:$KEY_LENGTH+1}"

    export "$KEY"="$VALUE"
done
IFS=' ' read -ra arr <<< "$genomes"
for ARGUMENT in "${arr[@]}"; do
    KEY=$(echo $ARGUMENT | cut -f1 -d=)

    KEY_LENGTH=${#KEY}
    VALUE="${ARGUMENT:$KEY_LENGTH+1}"

    export "$KEY"="$VALUE"
done
IFS=$OIFS

# Print helpFunction in case parameters are empty
if [ -z "$basedir" ] || [ -z "$ngsbits" ] || [ -z "$dbconverter" ] || [ -z "$foldername" ] || [ -z "$version" ] || [ -z "$venv" ] || [ -z "$grch38" ] || [ -z "$mito_version" ]
then
   echo "Installation path and ngsbits, dbconverter path and filename are required.";
   helpFunction
fi



# Begin script in case all parameters are correct
echo "Installing BRCA exchange to $basedir..."


# activate virtual environment
source $venv/bin/activate

# init folder structure
mkdir -p $basedir/$foldername
cd $basedir/$foldername



## download gnomAD genome data
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chr1.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter --header > gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chr2.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chr3.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chr4.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chr5.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chr6.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chr7.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chr8.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chr9.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chr10.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chr11.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chr12.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chr13.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chr14.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chr15.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chr16.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chr17.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chr18.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chr19.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chr20.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chr21.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chr22.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chrX.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/$version/vcf/genomes/gnomad.genomes.v$version.sites.chrY.vcf.bgz | gunzip  | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | python3 $dbconverter >> gnomAD_genome_GRCh38.vcf
bgzip gnomAD_genome_GRCh38.vcf
tabix -p vcf gnomAD_genome_GRCh38.vcf.gz
$ngsbits/VcfCheck -in gnomAD_genome_GRCh38.vcf -ref $grch38 -lines 0

wget -O - https://gnomad-public-us-east-1.s3.amazonaws.com/release/$mito_version/vcf/genomes/gnomad.genomes.v$mito_version.sites.chrM.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | sed 's/chrM/chrMT/g' > gnomAD_mito_GRCh38.vcf
bgzip gnomAD_mito_GRCh38.vcf
tabix -p vcf gnomAD_mito_GRCh38.vcf.gz
$ngsbits/VcfCheck -in gnomAD_mito_GRCh38.vcf -ref $grch38 -lines 0








