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
   echo -e "\t-v Put the date when you downloaded it: eg 1.3."
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
if [ -z "$basedir" ] || [ -z "$ngsbits" ] || [ -z "$dbconverter" ] || [ -z "$foldername" ] || [ -z "$version" ] || [ -z "$venv" ] || [ -z "$grch38" ] || [ -z "$zhead" ]
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



# download REVEL (https://sites.google.com/site/revelgenomics/downloads) https://download.imgag.de/ahdoebm1/revel_grch38_all_chromosomes.vcf.gz

source $zhead
#old url: wget https://rothsj06.u.hpc.mssm.edu/revel-v1.3_all_chromosomes.zip 
wget https://rothsj06.dmz.hpc.mssm.edu/revel-v${version}_all_chromosomes.zip
unzip -p revel-v${version}_all_chromosomes.zip | tr ',' '\t' | sed '1s/.*/#&/' | bgzip > revel_tmp.tsv.gz
zhead revel_tmp.tsv.gz 1 > h
zgrep -h -v '^#chr' revel_tmp.tsv.gz | $ngsbits/TsvFilter -numeric -v -filter '3 is .' | egrep -v '^#\s' | sort -k1,1 -k3,3n - | cat h - > revel_grch38_all_chromosomes.tsv
python3 $dbconverter -i revel_grch38_all_chromosomes.tsv | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | bgzip -c > revel_grch38_all_chromosomes.vcf.gz
tabix -f -p vcf revel_grch38_all_chromosomes.vcf.gz
rm -f revel_tmp.tsv.gz h revel_grch38_all_chromosomes.tsv
$ngsbits/VcfCheck -in revel_grch38_all_chromosomes.vcf.gz -ref $grch38 -lines 0









