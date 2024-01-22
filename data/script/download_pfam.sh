#!/bin/bash
set -e
set -o pipefail
set -o verbose

helpFunction()
{
   echo ""
   echo "Usage: $0 -p path -n foldername -v version -t tools_path -g genomes -y venv"
   echo "This script installs the grch38 reference genome"
   echo -e "\t-p Where should the new data be stored"
   echo -e "\t-t Paths of tools. Always key=value pairs."
   echo -e "\t-g Paths of genomes. Always key=value pairs."
   echo -e "\t-v Put the date when you downloaded it: eg 35.0."
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
if [ -z "$basedir" ] || [ -z "$dbconverter" ] || [ -z "$foldername" ] || [ -z "$version" ]
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



## download PFAM (last accessed at realease 35.0)
wget -O - http://ftp.ebi.ac.uk/pub/databases/Pfam/releases/Pfam$version/Pfam-A.seed.gz | zcat | iconv -f utf-8 -t utf-8 -c | python3 $dbconverter > pfam_id_mapping.tsv
wget -O - http://ftp.ebi.ac.uk/pub/databases/Pfam/releases/Pfam$version/Pfam-A.dead.gz | zcat | iconv -f utf-8 -t utf-8 -c | python3 $dbconverter --deadfile > pfam_legacy.tsv










