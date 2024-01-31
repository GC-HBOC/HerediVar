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
if [ -z "$basedir" ] || [ -z "$ngsbits" ] || [ -z "$dbconverter" ] || [ -z "$foldername" ] || [ -z "$venv" ] || [ -z "$grch38" ] || [ -z "$grch37" ] || [ -z "$chainfile" ]
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



## download CancerHotspots.org (version date: 2017-12-15 corresponds to the release date of the publication: Accelerating Discovery of Functional Mutant Alleles in Cancer, Chang et al. (PMCID: PMC5809279 ))

oncotree_name=oncotree_2021_11_02.json
wget -O - http://oncotree.mskcc.org/api/tumorTypes?version=oncotree_2021_11_02 > $oncotree_name

cancerhotspotsfile=cancerhotspots.v2
wget -O $cancerhotspotsfile.maf.gz http://download.cbioportal.org/cancerhotspots/cancerhotspots.v2.maf.gz
gunzip $cancerhotspotsfile.maf.gz
(head -n 2  $cancerhotspotsfile.maf && tail -n +3  $cancerhotspotsfile.maf | sort -t$'\t' -f -k5,5V -k6,6n -k11,11 -k13,13) >  $cancerhotspotsfile.sorted.maf

cancerhotspotssamples=$(awk -F '\t' '{print $16}' $cancerhotspotsfile.sorted.maf | sort | uniq -c | wc -l)
python3 $dbconverter -i $cancerhotspotsfile.sorted.maf --samples $cancerhotspotssamples --oncotree $oncotree_name -o $cancerhotspotsfile.vcf
$ngsbits/VcfSort -in $cancerhotspotsfile.vcf -out $cancerhotspotsfile.vcf
cat $cancerhotspotsfile.vcf | $ngsbits/VcfLeftNormalize -stream -ref $grch37 | $ngsbits/VcfStreamSort > $cancerhotspotsfile.final.vcf
awk -v OFS="\t" '!/##/ {$9=$10=""}1' $cancerhotspotsfile.final.vcf | sed 's/^\s\+//g' > $cancerhotspotsfile.final.vcf.2 # remove SAMPLE and FORMAT columns from vcf as they are added by vcfsort
mv -f $cancerhotspotsfile.final.vcf.2 $cancerhotspotsfile.final.vcf
bgzip -f $cancerhotspotsfile.final.vcf

$ngsbits/VcfCheck -in $cancerhotspotsfile.final.vcf.gz -ref $grch37

# crossmap to lift from GRCh37 to GRCh37
CrossMap.py vcf $chainfile $cancerhotspotsfile.final.vcf.gz $grch38 $cancerhotspotsfile.final.vcf
cat $cancerhotspotsfile.final.vcf | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | bgzip > $cancerhotspotsfile.final.vcf.gz
rm -f $cancerhotspotsfile.final.vcf
rm -f $cancerhotspotsfile.vcf
rm -f $cancerhotspotsfile.maf
rm -f $cancerhotspotsfile.sorted.maf

$ngsbits/VcfCheck -in $cancerhotspotsfile.final.vcf.gz -ref $grch38

tabix -p vcf $cancerhotspotsfile.final.vcf.gz





## download oncotree (version: oncotree_2021_11_02, downloaded from: http://oncotree.mskcc.org/#/home?tab=api) FOR Cancerhotspots
#cd $dbs
#mkdir -p cancerhotspots
#cd cancerhotspots
#oncotree_name=oncotree_2021_11_02.json
#wget -O - http://oncotree.mskcc.org/api/tumorTypes?version=oncotree_2021_11_02 > $oncotree_name

## download CancerHotspots.org (version date: 2017-12-15 corresponds to the release date of the publication: Accelerating Discovery of Functional Mutant Alleles in Cancer, Chang et al. (PMCID: PMC5809279 ))
#cd $dbs
#mkdir -p cancerhotspots
#cd cancerhotspots
#
#cancerhotspotsfile=cancerhotspots.v2
#wget -O $cancerhotspotsfile.maf.gz http://download.cbioportal.org/cancerhotspots/cancerhotspots.v2.maf.gz
#gunzip $cancerhotspotsfile.maf.gz
#(head -n 2  $cancerhotspotsfile.maf && tail -n +3  $cancerhotspotsfile.maf | sort -t$'\t' -f -k5,5V -k6,6n -k11,11 -k13,13) >  $cancerhotspotsfile.sorted.maf
#
#cancerhotspotssamples=$(awk -F '\t' '{print $16}' $cancerhotspotsfile.sorted.maf | sort | uniq -c | wc -l)
#python3 $data/script/db_converter_cancerhotspots.py -i $cancerhotspotsfile.sorted.maf --samples $cancerhotspotssamples --oncotree $oncotree_name -o $cancerhotspotsfile.vcf
#$ngsbits/VcfSort -in $cancerhotspotsfile.vcf -out $cancerhotspotsfile.vcf
#cat $cancerhotspotsfile.vcf | $ngsbits/VcfLeftNormalize -stream -ref $grch37 | $ngsbits/VcfStreamSort > $cancerhotspotsfile.final.vcf
#awk -v OFS="\t" '!/##/ {$9=$10=""}1' $cancerhotspotsfile.final.vcf | sed 's/^\s\+//g' > $cancerhotspotsfile.final.vcf.2 # remove SAMPLE and FORMAT columns from vcf as they are added by vcfsort
#mv -f $cancerhotspotsfile.final.vcf.2 $cancerhotspotsfile.final.vcf
#bgzip -f $cancerhotspotsfile.final.vcf
#$ngsbits/VcfCheck -in $cancerhotspotsfile.final.vcf.gz -ref $grch37
#
## crossmap to lift from GRCh37 to GRCh38
#CrossMap.py vcf $chainfile $cancerhotspotsfile.final.vcf.gz $grch38 $cancerhotspotsfile.final.vcf
#cat $cancerhotspotsfile.final.vcf | $ngsbits/VcfLeftNormalize -stream -ref $grch38 | $ngsbits/VcfStreamSort | bgzip > $cancerhotspotsfile.final.vcf.gz
#rm -f $cancerhotspotsfile.final.vcf
#rm -f $cancerhotspotsfile.vcf
#rm -f $cancerhotspotsfile.maf
#rm -f $cancerhotspotsfile.sorted.maf
#
#$ngsbits/VcfCheck -in $cancerhotspotsfile.final.vcf.gz -ref $grch38
#
#tabix -p vcf $cancerhotspotsfile.final.vcf.gz


