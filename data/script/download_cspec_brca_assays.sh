#!/bin/bash
set -e
set -o pipefail
set -o verbose

helpFunction()
{
   echo ""
   echo "Usage: $0 -p path -n foldername -t tools_path -g genomes -y pythonpath"
   echo "This script installs CSpec brca assays"
   echo -e "\t-p Where should the new data be stored"
   echo -e "\t-t Paths of tools. Always key=value pairs."
   echo -e "\t-g Paths of genomes. Always key=value pairs."
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
if [ -z "$basedir" ] || [ -z "$ngsbits" ] || [ -z "$dbconverter_splicing" ] || [ -z "$db_cspec_merge" ] || [ -z "$dbconverter_functional" ] || [ -z "$foldername" ] || [ -z "$venv" ] || [ -z "$grch38" ]
then
   echo "Installation path and ngsbits, dbconverter path and filename are required.";
   helpFunction
fi



# Begin script in case all parameters are correct
echo "Installing BRCA exchange to $basedir..."


source $venv/bin/activate


### originally download CSpec BRCA Assays from https://cspec.genome.network/cspec/File/id/d9047945-dc87-407a-93a0-36b2ebe7e1bf/data and convert tables 
# Classification scheme: https://cspec.genome.network/cspec/ui/svi/doc/GN092
mkdir -p $basedir/$foldername
cd $basedir/$foldername

#foldername=CSpec_BRCA_Assays

wget -O assays.xlsx https://cspec.genome.network/cspec/File/id/d9047945-dc87-407a-93a0-36b2ebe7e1bf/data


# splicing assays
s_assays=splicing_assays
xlsx2csv -i -d '|' -s 3 assays.xlsx $s_assays.csv

python3 $dbconverter_splicing -i $s_assays.csv -o $s_assays.process.csv
mv $s_assays.process.csv $s_assays.csv

$ngsbits/HgvsToVcf -in $s_assays.csv -ref $grch38 -out $s_assays.vcf
#Warning: NM_000059:c.7397C>T skipped: couldn't transform it to valid VCF: Invalid reference sequence of variant 'chr13:32355250-32355250 C>T': Variant reference sequence is 'C', but the genome sequence is 'T'


$ngsbits/VcfLeftNormalize -in $s_assays.vcf -ref $grch38 -out $s_assays.process.vcf
mv $s_assays.process.vcf $s_assays.vcf
$ngsbits/VcfSort -in $s_assays.vcf -out $s_assays.sorted.vcf
mv $s_assays.sorted.vcf $s_assays.vcf

$ngsbits/VcfCheck -in $s_assays.vcf -ref $grch38 -lines 0

python3 $db_cspec_merge -i $s_assays.vcf -o $s_assays.process.vcf -c splicing_assay
mv $s_assays.process.vcf $s_assays.vcf

bgzip $s_assays.vcf
tabix -p vcf $s_assays.vcf.gz

# functional assays
f_assays=functional_assays
xlsx2csv -i -d '|' -s 4 assays.xlsx $f_assays.csv

python3 $dbconverter_functional -i $f_assays.csv -o $f_assays.process.csv
mv $f_assays.process.csv $f_assays.csv

$ngsbits/HgvsToVcf -in $f_assays.csv -ref $grch38 -out $f_assays.vcf
#Warning: NM_007294:c.[5359T>A;5363G>A] skipped: couldn't transform it to valid VCF: Unsupported cDNA change '[5359T>A;5363G>A]'.
#Warning: NM_007294:c.4884G>H skipped: couldn't transform it to valid VCF: Could not convert base 'H' to complement!
#Warning: NM_000059:c.7397C>T skipped: couldn't transform it to valid VCF: Invalid reference sequence of variant 'chr13:32355250-32355250 C>T': Variant reference sequence is 'C', but the genome sequence is 'T'
#Warning: NM_007294:c.[922A>G;923G>C] skipped: couldn't transform it to valid VCF: Unsupported cDNA change '[922A>G;923G>C]'.


$ngsbits/VcfLeftNormalize -in $f_assays.vcf -ref $grch38 -out $f_assays.process.vcf
mv $f_assays.process.vcf $f_assays.vcf
$ngsbits/VcfSort -in $f_assays.vcf -out $f_assays.sorted.vcf
mv $f_assays.sorted.vcf $f_assays.vcf

$ngsbits/VcfCheck -in $f_assays.vcf -ref $grch38 -lines 0

python3 $db_cspec_merge -i $f_assays.vcf -o $f_assays.process.vcf -c functional_assay
mv $f_assays.process.vcf $f_assays.vcf

bgzip $f_assays.vcf
tabix -p vcf $f_assays.vcf.gz



