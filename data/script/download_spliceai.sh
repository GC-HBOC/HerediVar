#!/bin/bash
set -e
set -o pipefail
set -o verbose

helpFunction()
{
   echo ""
   echo "Usage: $0 -p path -n foldername -t tools_path -g genomes"
   echo "This script installs the grch38 reference genome"
   echo -e "\t-p Where should the new data be stored"
   echo -e "\t-t Paths of tools. Always key=value pairs."
   echo -e "\t-g Paths of genomes. Always key=value pairs."
   echo -e "\t-v Put the date when you downloaded it: eg 155."
   exit 1 # Exit script after printing help
}

while getopts "p:n:v:t:g:" opt
do
   case "$opt" in
      p ) basedir="$OPTARG" ;;
      t ) tools="$OPTARG" ;;
      g ) genomes="$OPTARG" ;;
      n ) foldername="$OPTARG" ;;
      v ) version="$OPTARG" ;;
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
if [ -z "$basedir" ] || [ -z "$foldername" ]
then
   echo "Installation path and ngsbits, dbconverter path and filename are required.";
   helpFunction
fi



# Begin script in case all parameters are correct
echo "Installing BRCA exchange to $basedir..."



# init folder structure
mkdir -p $basedir/$foldername
cd $basedir/$foldername



# download annotation file for SpliceAI. Download from: https://basespace.illumina.com/s/otSPW8hnhaZR
wget https://download.molgeniscloud.org/downloads/vip/resources/GRCh38/spliceai_scores.masked.indel.hg38.vcf.gz
wget https://download.molgeniscloud.org/downloads/vip/resources/GRCh38/spliceai_scores.masked.indel.hg38.vcf.gz.tbi
wget https://download.molgeniscloud.org/downloads/vip/resources/GRCh38/spliceai_scores.masked.snv.hg38.vcf.gz
wget https://download.molgeniscloud.org/downloads/vip/resources/GRCh38/spliceai_scores.masked.snv.hg38.vcf.gz.tbi











