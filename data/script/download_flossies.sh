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
   echo -e "\t-v Put the date when you downloaded it: eg 25-03-2022."
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
if [ -z "$basedir" ] || [ -z "$ngsbits" ] || [ -z "$dbconverter" ] || [ -z "$foldername" ] || [ -z "$version" ] || [ -z "$venv" ] || [ -z "$grch38" ] || [ -z "$grch37" ] || [ -z "$chainfile" ] || [ -z "$flossiesdatauris"]
then
   echo "Installation path and ngsbits, dbconverter path and filename are required.";
   helpFunction
fi



# Begin script in case all parameters are correct
echo "Installing BRCA exchange to $basedir..."


source $venv/bin/activate


### download FLOSSIES (https://whi.color.com/about) there is no versioning so the date specified in the filename equals the date when the database was accessed
mkdir -p $basedir/$foldername
cd $basedir/$foldername




flossies_file=FLOSSIES_$version.vcf
cat $flossiesdatauris | python3 $datauri2blob --header | python3 $dbconverter > $flossies_file
$ngsbits/VcfSort -in $flossies_file -out $flossies_file
$ngsbits/VcfLeftNormalize -in $flossies_file -stream -ref $grch37 -out $flossies_file.2
$ngsbits/VcfStreamSort -in $flossies_file.2 -out $flossies_file
awk -v OFS="\t" '!/##/ {$9=$10=""}1' $flossies_file |sed 's/^\s\+//g' > $flossies_file.2 # remove SAMPLE and FORMAT columns from vcf as they are added by vcfsort
mv -f $flossies_file.2 $flossies_file
bgzip $flossies_file
$ngsbits/VcfCheck -in $flossies_file.gz -ref $grch37


## crossmap to lift from GRCh37 to GRCh38
CrossMap.py vcf $chainfile $flossies_file.gz $grch38 $flossies_file.2
cat $flossies_file.2 | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | bgzip > $flossies_file.gz
tabix -p vcf $flossies_file.gz
rm -f $flossies_file.2
$ngsbits/VcfCheck -in $flossies_file.gz -ref $grch38











