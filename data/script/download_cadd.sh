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
   echo -e "\t-v Put the date when you downloaded it: eg 1.6."
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
if [ -z "$basedir" ] || [ -z "$ngsbits" ] || [ -z "$dbconverter" ] || [ -z "$foldername" ] || [ -z "$version" ] || [ -z "$venv" ] || [ -z "$grch38" ]
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



# Install CADD - http://cadd.gs.washington.edu/download

wget -O - http://kircherlab.bihealth.org/download/CADD/v$version/GRCh38/whole_genome_SNVs.tsv.gz > CADD_SNVs_GRCh38.tsv.gz
zcat CADD_SNVs_GRCh38.tsv.gz | python3 $dbconverter | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | bgzip > CADD_SNVs_GRCh38.vcf.gz
tabix -f -p vcf CADD_SNVs_GRCh38.vcf.gz
rm -f CADD_SNVs_GRCh38.tsv.gz
$ngsbits/VcfCheck -in CADD_SNVs_GRCh38.vcf.gz -ref $grch38 #-lines 0


wget -O - https://kircherlab.bihealth.org/download/CADD/v$version/GRCh38/gnomad.genomes.r3.0.indel.tsv.gz > CADD_InDels_GRCh38.tsv.gz
zcat CADD_InDels_GRCh38.tsv.gz | python3 $dbconverter | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | bgzip > CADD_InDels_GRCh38.vcf.gz
tabix -f -p vcf CADD_InDels_GRCh38.vcf.gz
rm -f CADD_InDels_GRCh38.tsv.gz
$ngsbits/VcfCheck -in CADD_InDels_GRCh38.vcf.gz -ref $grch38 #-lines 0
