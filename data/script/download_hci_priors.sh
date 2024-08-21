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



## download HCI prior probabilities of pathogenicity (http://priors.hci.utah.edu/PRIORS/index.php)
cd $dbs
mkdir -p HCI_priors
cd HCI_priors

python3 $dbconverter -g BRCA1 -e exon2 --header > priors_hg19.vcf
python3 $dbconverter -g BRCA2 -e exon2 >> priors_hg19.vcf

$ngsbits/VcfCheck -in priors_hg19.vcf -ref $grch37 -lines 0 > vcferrors_hg19.txt
$ngsbits/VcfSort -in priors_hg19.vcf -out priors_hg19.vcf
bgzip -f -c priors_hg19.vcf > priors_hg19.vcf.gz
tabix -p vcf priors_hg19.vcf.gz


## crossmap to lift from GRCh37 to GRCh38
CrossMap vcf $data/genomes/hg19ToHg38.fixed.over.chain.gz priors_hg19.vcf.gz $grch38 priors.vcf
rm priors_hg19.vcf.gz
rm priors_hg19.vcf.gz.tbi


python3 $dbconverter -g MLH1 -e exon1 >> priors.vcf

##### STILL MISSING:
python3 $dbconverter -g MSH2 -e exon1 > priors_msh2.vcf
python3 $dbconverter -g MSH6 -e exon1 >> priors.vcf

$ngsbits/VcfSort -in priors.vcf -out priors.vcf

cat priors.vcf | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort > priors.normalized.vcf
rm priors.vcf
mv priors.normalized.vcf priors.vcf

bgzip -f -c priors.vcf > priors.vcf.gz
tabix -p vcf priors.vcf.gz
$ngsbits/VcfCheck -in priors.vcf.gz -ref $grch38 > vcferrors.txt










