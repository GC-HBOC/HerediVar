#!/bin/bash
set -e
set -o pipefail
set -o verbose

helpFunction()
{
   echo ""
   echo "Usage: $0 -p path -n foldername -t tools_path -g genomes -y pythonpath"
   echo "This script installs the grch38 reference genome"
   echo -e "\t-p Where should the new data be stored"
   echo -e "\t-t Paths of tools. Always key=value pairs."
   echo -e "\t-g Paths of genomes. Always key=value pairs."
   echo -e "\t-v Put the date when you downloaded it: eg 155."
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
if [ -z "$basedir" ] || [ -z "$ngsbits" ] || [ -z "$dbconverter" ] || [ -z "$foldername" ] || [ -z "$venv" ] || [ -z "$grch38" ]
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



### download TP53 database (https://tp53.isb-cgc.org/get_tp53data#get_annot)

# this assumes that the first line is the header line. If this is not the case remove the sed
tp_db=GermlineDownload_r20
wget -O - https://storage.googleapis.com/tp53-static-files/data/$tp_db.csv | sed -e "1s/^/#/" | python3 $dbconverter > $tp_db.vcf

$ngsbits/VcfSort -in $tp_db.vcf -out $tp_db.vcf
cat $tp_db.vcf | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort > $tp_db.normalized.vcf
bgzip -f -c $tp_db.normalized.vcf > $tp_db.normalized.vcf.gz
tabix -p vcf $tp_db.normalized.vcf.gz

$ngsbits/VcfCheck -in $tp_db.normalized.vcf.gz -ref $grch38
rm -f $tp_db.vcf





