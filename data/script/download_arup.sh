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



### download ARUP BRCA1 & BRCA2 (https://arup.utah.edu/database/BRCA/Variants/BRCA1.php and https://arup.utah.edu/database/BRCA/Variants/BRCA2.php)
### Database was accessed at 01.04.2022. As there is no versioning this date was used instead of an actual version number

wget -O - https://arup.utah.edu/database/BRCA/Variants/BRCA1.php | python3 $dbconverter --reference NM_007294.3 > ARUP_BRCA.tsv
# IMPORTANT NOTE: The ARUP website sais that their variants for BRCA2 are on the transcript "NM_000059.3". 
# For conversion of hgvs to vcf it is required that this transcript is contained in the NGSD database which is not the case for NM_000059.3. 
# Thus, I searched for the corresponding ensembl transcript: ENST00000380152 (see: https://www.ensembl.org/Homo_sapiens/Gene/Summary?g=ENSG00000139618;r=13:32315086-32400268)
wget -O - https://arup.utah.edu/database/BRCA/Variants/BRCA2.php | python3 $dbconverter --reference ENST00000380152 >> ARUP_BRCA.tsv
# working hgvstovcf on server: /mnt/storage1/share/opt/ngs-bits-hg38-2022_04-38-gd5054098/HgvsToVcf
$ngsbits/HgvsToVcf -in ARUP_BRCA.tsv -ref $grch38 -out ARUP_BRCA.vcf
$ngsbits/VcfSort -in ARUP_BRCA.vcf -out ARUP_BRCA.vcf
cat ARUP_BRCA.vcf | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | bgzip > ARUP_BRCA.vcf.gz
tabix -p vcf ARUP_BRCA.vcf.gz

$ngsbits/VcfCheck -in ARUP_BRCA.vcf.gz -ref $grch38 -lines 0








