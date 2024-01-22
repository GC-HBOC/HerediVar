#!/bin/bash
set -e
set -o pipefail
set -o verbose

helpFunction()
{
   echo ""
   echo "Usage: $0 -p path -n foldername -v version -t tools_path -g genomes"
   echo "This script installs the grch38 reference genome"
   echo -e "\t-p Where should the new data be stored"
   echo -e "\t-t Paths of tools. Always key=value pairs."
   echo -e "\t-g Paths of genomes. Always key=value pairs."
   echo -e "\t-v Put the date when you downloaded it: eg 1.3."
   exit 1 # Exit script after printing help
}

while getopts "p:n:v:t:g:" opt
do
   case "$opt" in
      p ) basedir="$OPTARG" ;;
      t ) tools="$OPTARG" ;;
      g ) genomes="$OPTARG" ;;
      n ) foldername="$OPTARG" ;;
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
if [ -z "$basedir" ] || [ -z "$foldername" ] || [ -z "$version" ] 
then
   echo "Installation path and ngsbits, dbconverter path and filename are required.";
   helpFunction
fi



# Begin script in case all parameters are correct
echo "Installing BRCA exchange to $basedir..."


# init folder structure
mkdir -p $basedir/$foldername
cd $basedir/$foldername



## download mane select (https://ftp.ncbi.nlm.nih.gov/refseq/MANE/)
wget -O - https://ftp.ncbi.nlm.nih.gov/refseq/MANE/MANE_human/release_$version/MANE.GRCh38.v$version.ensembl_genomic.gff.gz | gunzip > MANE.GRCh38.v$version.ensembl_genomic.gff










