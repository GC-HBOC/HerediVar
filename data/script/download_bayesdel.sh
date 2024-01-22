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
   echo -e "\t-v Put the date when you downloaded it: eg 4.4. This is the dbnsfp version"
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




# install bayesDEL from dbNSFP
# http://database.liulab.science/dbNSFP#database

wget https://dbnsfp.s3.amazonaws.com/dbNSFP${version}a.zip
unzip dbNSFP${version}a.zip -d dbNSFP${version}a
mv dbNSFP${version}a dbNSFP${version}a_full
mkdir -p dbNSFP${version}a
mv dbNSFP${version}a_full/*variant* dbNSFP${version}a
rm -r dbNSFP${version}a_full

bayesdel_file=bayesdel
python3 $dbconverter -i dbNSFP${version}a -o $bayesdel_file.vcf
$ngsbits/VcfSort -in $bayesdel_file.vcf -out $bayesdel_file.vcf
$ngsbits/VcfLeftNormalize -stream -ref $grch38 -in $bayesdel_file.vcf -out $bayesdel_file.vcf.2
mv $bayesdel_file.vcf.2 $bayesdel_file.vcf
# IDONT KNOW IF THIS IS ENOUGH TO MAKE IT UNIQUE! -> maybe there is a more sophisticated method required!
awk '!seen[$0]++' $bayesdel_file.vcf > $bayesdel_file.uniq.vcf
mv $bayesdel_file.uniq.vcf $bayesdel_file.vcf
bgzip $bayesdel_file.vcf
#$ngsbits/VcfCheck -lines 0 -in $bayesdel_file.vcf.gz -ref $grch38

tabix -p vcf $bayesdel_file.vcf.gz

rm dbNSFP${version}a.zip










