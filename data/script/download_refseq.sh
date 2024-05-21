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



# download refseq transcripts release 110
basename=refseq_transcripts_$version
full_refseq_gff=$basename.gff
wget -O - https://ftp.ncbi.nlm.nih.gov/genomes/refseq/vertebrate_mammalian/Homo_sapiens/annotation_releases/$version/GCF_000001405.40_GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.gff.gz | gunzip > $full_refseq_gff


# activate virtual environment
source $venv/bin/activate

# install refseq gff3 for vcfannotateconsequence
wget -O $tools/add_utrs_to_gff.py https://ftp.ncbi.nlm.nih.gov/genomes/TOOLS/add_utrs_to_gff/add_utrs_to_gff.py
python3 $tools/add_utrs_to_gff.py $full_refseq_gff > $basename.utrs.gff

python3 $refseq2ensemblaccession -i $basename.utrs.gff -o $basename.filtered.gff

sed 's/ID=gene-/ID=gene:/g' $basename.filtered.gff > $basename.converted.gff
sed -i 's/Parent=gene-/Parent=gene:/g' $basename.converted.gff

sed -i 's/ID=rna-/ID=transcript:/g' $basename.converted.gff
sed -i 's/Parent=rna-/Parent=transcript:/g' $basename.converted.gff

sed -i 's/ID=exon-/ID=exon:/g' $basename.converted.gff
sed -i 's/ID=cds-/ID=CDS:/g' $basename.converted.gff
sed -i 's/ID=id-/ID=id:/g' $basename.converted.gff

# delete mi-rna entries
sed -i '/ID=transcript:MIR/d' $basename.converted.gff
sed -i '/Parent=transcript:MIR/d' $basename.converted.gff
sed -i '/ID=transcript:TR/d' $basename.converted.gff
sed -i '/Parent=transcript:TR/d' $basename.converted.gff

sed -i '/ID=transcript:(RNR1|RNR2|ND1|ND2|COX1|COX2|ATP8|ATP6|COX3|ND3|ND4L|ND4|ND5|ND6|CYTB)/d' $basename.converted.gff
sed -i '/Parent=transcript:(RNR1|RNR2|ND1|ND2|COX1|COX2|ATP8|ATP6|COX3|ND3|ND4L|ND4|ND5|ND6|CYTB)/d' $basename.converted.gff




sed -i '/ID=gene:/i \
###' $basename.converted.gff

python3 $refseq2ensemblgff -i $basename.converted.gff -o $basename.final.gff

