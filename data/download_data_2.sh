#!/bin/bash
set -e
set -o pipefail
set -o verbose

###
# This script provides a wrapper for all data download needed to run HerediVar annotation scripts
###

root="$(dirname `pwd`)"
tools=$root/src/tools
data=$root/data
dbs=$data/dbs
ngsbits=$tools/ngs-bits/bin
genome=$data/genomes/GRCh38.fa

mkdir -p $dbs

# download dbSNP
: '
cd dbs
mkdir -p dbSNP
cd dbSNP
wget -O - https://ftp.ncbi.nih.gov/snp/latest_release/VCF/GCF_000001405.39.gz | gunzip | python3 $tools/vcf_refseq_to_chrnum.py | $ngsbits/VcfBreakMulti | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort > dbSNP_v155.vcf
bgzip dbSNP_v155.vcf
tabix -p vcf dbSNP_v155.vcf.gz
'


# download phyloP conservation scores (https://www.ensembl.org/info/docs/tools/vep/script/vep_example.html#gerp)
: '
cd $dbs
mkdir -p phyloP
cd phyloP
wget http://hgdownload.soe.ucsc.edu/goldenPath/hg38/phyloP100way/hg38.phyloP100way.bw
'


# Install CADD - http://cadd.gs.washington.edu/download
: '
cd $dbs
mkdir -p CADD
cd CADD
wget -O - http://kircherlab.bihealth.org/download/CADD/v1.6/GRCh38/whole_genome_SNVs.tsv.gz > CADD_SNVs_1.6_GRCh38.tsv.gz
zcat CADD_SNVs_1.6_GRCh38.tsv.gz | python3 $tools/db_converter_cadd.py | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | bgzip > CADD_SNVs_1.6_GRCh38.vcf.gz
tabix -f -p vcf CADD_SNVs_1.6_GRCh38.vcf.gz
rm -f CADD_SNVs_1.6_GRCh38.tsv.gz
$ngsbits/VcfCheck -in CADD_SNVs_1.6_GRCh38.vcf.gz -ref $genome -lines 0

wget -O - https://kircherlab.bihealth.org/download/CADD/v1.6/GRCh38/gnomad.genomes.r3.0.indel.tsv.gz > CADD_InDels_1.6_GRCh38.tsv.gz
zcat CADD_InDels_1.6_GRCh38.tsv.gz | python3 $tools/db_converter_cadd.py | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | bgzip > CADD_InDels_1.6_GRCh38.vcf.gz
tabix -f -p vcf CADD_InDels_1.6_GRCh38.vcf.gz
rm -f CADD_InDels_1.6_GRCh38.tsv.gz
$ngsbits/VcfCheck -in CADD_InDels_1.6_GRCh38.vcf.gz -ref $genome -lines 0
: '


# download REVEL (https://sites.google.com/site/revelgenomics/downloads)
#cd $dbs
#mkdir -p REVEL
#cd REVEL
#source $tools/zhead.sh
#wget https://rothsj06.u.hpc.mssm.edu/revel-v1.3_all_chromosomes.zip
#unzip -p revel-v1.3_all_chromosomes.zip | tr ',' '\t' | sed '1s/.*/#&/' | bgzip > revel_tmp.tsv.gz
#zhead revel_tmp.tsv.gz 1 > h
#zgrep -h -v '^#chr' revel_tmp.tsv.gz | $ngsbits/TsvFilter -numeric -v -filter '3 is .' | egrep -v '^#\s' | sort -k1,1 -k3,3n - | cat h - | cut -f1-8 > revel_grch38_all_chromosomes.tsv
#python3 $tools/db_converter_revel.py -i revel_grch38_all_chromosomes.tsv | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | bgzip -c > revel_grch38_all_chromosomes.vcf.gz
#tabix -f -p vcf revel_grch38_all_chromosomes.vcf.gz
#rm -f revel_tmp.tsv.gz h revel_grch38_all_chromosomes.tsv
#$ngsbits/VcfCheck -in revel_grch38_all_chromosomes.vcf.gz -ref $genome -lines 0


# download annotation file for SpliceAI
: '
cd $dbs
mkdir -p SpliceAI
cd SpliceAI
wget https://download.imgag.de/ahsturm1/spliceai_scores_2022_02_09_GRCh38.vcf.gz
tabix -p vcf spliceai_scores_2022_02_09_GRCh38.vcf.gz
'


# download ClinVar (https://www.ncbi.nlm.nih.gov/clinvar/)
cd $dbs
mkdir -p ClinVar
cd ClinVar

# submissions table for 'Submitted interpretations and evidence' table from website
#wget https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/submission_summary.txt.gz
#ncomment_lines=$(zgrep '^#' submission_summary.txt.gz | wc -l)
##source $tools/zhead.sh
#zhead submission_summary.txt.gz $ncomment_lines | tail -1 | cut -c 2- > h # nochmal auf die encoding schauen (SâˆšÂ°nchez-GutiâˆšÂ©rrez_2002_PMID:12417303; Sebastio_1991_PMID:18)
#zgrep -v '^#' submission_summary.txt.gz | cat h - | bgzip > submission_summary_preprocessed.txt.gz

#most recent release: https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz
#wget https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar_20220320.vcf.gz 
gunzip -c clinvar_20220320.vcf.gz  | python3 $tools/db_converter_clinvar.py --submissions submission_summary_preprocessed.txt.gz | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | bgzip > clinvar_20220320_converted_GRCh38.vcf.gz
tabix -p vcf clinvar_20220320_converted_GRCh38.vcf.gz

#CNVs
#wget -O - http://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/archive/variant_summary_2021-12.txt.gz | gunzip > variant_summary_2021-12.txt
#cat variant_summary_2021-12.txt | php $src/Tools/db_converter_clinvar_cnvs.php 5 "Pathogenic/Likely pathogenic" | sort | uniq > clinvar_cnvs_2021-12.bed
#$ngsbits/BedSort -with_name -in clinvar_cnvs_2021-12.bed -out clinvar_cnvs_2021-12.bed











# clinvar_variant_annotation table
# - ID (column): variation ID
# - CLNSIG + CLNSIGCONF: interpretation
# - CLNREVSTAT: review status


# clinvar_interpretations table
# - interpretation: ClinicalSignificance column
# - last_evaluated: DateLastEvaluated column
# - review_status: ReviewStatus column
# (- assertion_criteria: CollectionMethod column)
# - condition: SubmittedPhenotypeInfo column
# (- inheritance: OriginCounts column)
# - submitter: Submitter column
# - supporting_information: ExplanationOfInterpretation / description