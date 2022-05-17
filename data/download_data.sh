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

# download GRCH38 genome
: '
cd $data
chmod 755 ./download_GRCh38.sh
./download_GRCh38.sh
'

# download GRCH37 reference_genome (used for lifting)
: '
cd $data
chmod 755 ./download_GRCh37.sh
./download_GRCh37.sh
'

# download HGNC
: '
cd $dbs
mkdir HGNC
cd HGNC
wget -O - http://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/tsv/hgnc_complete_set.txt > hgnc_complete_set.tsv
'

# download gnomAD genome data
: '
cd $dbs
mkdir -p gnomAD
cd gnomAD
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr1.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py --header > gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr2.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr3.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr4.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr5.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr6.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr7.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr8.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr9.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr10.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr11.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr12.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr13.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr14.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr15.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr16.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr17.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr18.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr19.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr20.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr21.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chr22.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chrX.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
wget -O - https://storage.googleapis.com/gcp-public-data--gnomad/release/3.1.2/vcf/genomes/gnomad.genomes.v3.1.2.sites.chrY.vcf.bgz | gunzip  | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | python3 $tools/db_filter_gnomad.py >> gnomAD_genome_v3.1.2_GRCh38.vcf
bgzip gnomAD_genome_v3.1.2_GRCh38.vcf
tabix -p vcf gnomAD_genome_v3.1.2_GRCh38.vcf.gz
'
#wget -O - https://gnomad-public-us-east-1.s3.amazonaws.com/release/3.1/vcf/genomes/gnomad.genomes.v3.1.sites.chrM.vcf.bgz | gunzip | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | sed 's/chrM/chrMT/g' > gnomAD_genome_v3.1.mito_GRCh38.vcf
#bgzip gnomAD_genome_v3.1.mito_GRCh38.vcf
#tabix -p vcf gnomAD_genome_v3.1.mito_GRCh38.vcf.gz



# download BRCA exchange (https://brcaexchange.org/releases)
: '
cd $dbs
mkdir -p BRCA_exchange
cd BRCA_exchange
wget https://brcaexchange.org/backend/downloads/releases/release-02-22-22/release-02-22-22.tar.gz
tar -xf release-02-22-22.tar.gz
mv -f output/release/built_with_change_types.tsv .
rm -rf output/
python3 $tools/db_converter_brca_exchange.py -i built_with_change_types.tsv | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | bgzip > BRCA_exchange_02-22-22.vcf.gz
tabix -p vcf BRCA_exchange_02-22-22.vcf.gz
'


# download ensembl transcripts (http://ftp.ensembl.org/pub/current_gff3/homo_sapiens/)
: '
cd $dbs
mkdir -p ensembl
cd ensembl
wget http://ftp.ensembl.org/pub/current_gff3/homo_sapiens/Homo_sapiens.GRCh38.105.gff3.gz
gunzip Homo_sapiens.GRCh38.105.gff3.gz
## download ensembl canonical transcripts (http://ftp.ensembl.org/pub/current_tsv/homo_sapiens)
wget -O - http://ftp.ensembl.org/pub/release-105/tsv/homo_sapiens/Homo_sapiens.GRCh38.105.canonical.tsv.gz | gunzip > Homo_sapiens.GRCh38.105.canonical.tsv
'

# download mane select (https://ftp.ncbi.nlm.nih.gov/refseq/MANE/)
: '
cd $dbs
mkdir -p MANE
cd MANE
wget -O - https://ftp.ncbi.nlm.nih.gov/refseq/MANE/MANE_human/release_1.0/MANE.GRCh38.v1.0.ensembl_genomic.gff.gz | gunzip > MANE.GRCh38.v1.0.ensembl_genomic.gff
'




## download FLOSSIES (https://whi.color.com/about) there is no versioning so the date specified in the filename equals the date when the database was accessed
#cd $dbs
#mkdir -p FLOSSIES
#cd FLOSSIES
#flossies_file=FLOSSIES_25-03-2022.vcf
#cat $data/FLOSSIES_data_uris.txt | python3 $tools/data_uri_to_blob.py --header | python3 $tools/db_converter_flossies.py > $flossies_file
#$ngsbits/VcfSort -in $flossies_file -out $flossies_file
#$ngsbits/VcfLeftNormalize -in $flossies_file -stream -ref $data/genomes/GRCh37.fa -out $flossies_file.2
#$ngsbits/VcfStreamSort -in $flossies_file.2 -out $flossies_file
#awk -v OFS="\t" '!/##/ {$9=$10=""}1' $flossies_file |sed 's/^\s\+//g' > $flossies_file.2 # remove SAMPLE and FORMAT columns from vcf as they are added by vcfsort
#mv -f $flossies_file.2 $flossies_file
#bgzip $flossies_file

#$ngsbits/VcfCheck -in $flossies_file.gz -ref $data/genomes/GRCh37.fa

## crossmap to lift from GRCh37 to GRCh37
#CrossMap.py vcf $data/genomes/hg19ToHg38.fixed.over.chain.gz $flossies_file.gz $genome $flossies_file.2
#cat $flossies_file.2 | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | bgzip > $flossies_file.gz
#tabix -p vcf $flossies_file.gz
#rm -f $flossies_file.2

#$ngsbits/VcfCheck -in $flossies_file.gz -ref $genome



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


## download ClinVar (https://www.ncbi.nlm.nih.gov/clinvar/)
#cd $dbs
#mkdir -p ClinVar
#cd ClinVar

## submissions table for 'Submitted interpretations and evidence' table from website
#wget https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/submission_summary.txt.gz
#ncomment_lines=$(zgrep '^#' submission_summary.txt.gz | wc -l)
#source $tools/zhead.sh
#zhead submission_summary.txt.gz $ncomment_lines | tail -1 | cut -c 2- > h # nochmal auf die encoding schauen (SâˆšÂ°nchez-GutiâˆšÂ©rrez_2002_PMID:12417303; Sebastio_1991_PMID:18)
#zgrep -v '^#' submission_summary.txt.gz | cat h - | bgzip > submission_summary_preprocessed.txt.gz

## most recent release: https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz
#wget https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar_20220320.vcf.gz 
#gunzip -c clinvar_20220320.vcf.gz  | python3 $tools/db_converter_clinvar.py --submissions submission_summary_preprocessed.txt.gz | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | bgzip > clinvar_20220320_converted_GRCh38.vcf.gz
#tabix -p vcf clinvar_20220320_converted_GRCh38.vcf.gz

## CNVs - not used atm
#wget -O - http://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/archive/variant_summary_2021-12.txt.gz | gunzip > variant_summary_2021-12.txt
#cat variant_summary_2021-12.txt | php $src/Tools/db_converter_clinvar_cnvs.php 5 "Pathogenic/Likely pathogenic" | sort | uniq > clinvar_cnvs_2021-12.bed
#$ngsbits/BedSort -with_name -in clinvar_cnvs_2021-12.bed -out clinvar_cnvs_2021-12.bed


## download PFAM (last accessed at realease 35.0)
: '
cd $dbs
mkdir -p PFAM
cd PFAM
wget -O - http://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.seed.gz | zcat | iconv -f utf-8 -t utf-8 -c | python3 $tools/db_converter_pfam.py > pfam_id_mapping.tsv
wget -O - ftp://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.dead.gz | zcat | iconv -f utf-8 -t utf-8 -c | python3 $tools/db_converter_pfam.py --deadfile > pfam_legacy.tsv
'


# download oncotree (version: oncotree_2021_11_02, downloaded from: http://oncotree.mskcc.org/#/home?tab=api)
: '
cd $dbs
mkdir -p cancerhotspots
cd cancerhotspots
oncotree_name=oncotree_2021_11_02.json
wget -O - http://oncotree.mskcc.org/api/tumorTypes?version=oncotree_2021_11_02 > $oncotree_name
'

## download CancerHotspots.org (version date: 2017-12-15 corresponds to the release date of the publication: Accelerating Discovery of Functional Mutant Alleles in Cancer, Chang et al. (PMCID: PMC5809279 ))
#cd $dbs
#mkdir -p cancerhotspots
#cd cancerhotspots

#cancerhotspotsfile=cancerhotspots.v2
#wget -O $cancerhotspotsfile.maf.gz http://download.cbioportal.org/cancerhotspots/cancerhotspots.v2.maf.gz
#gunzip $cancerhotspotsfile.maf.gz
#(head -n 2  $cancerhotspotsfile.maf && tail -n +3  $cancerhotspotsfile.maf | sort -t$'\t' -f -k5,5V -k6,6n -k11,11 -k13,13) >  $cancerhotspotsfile.sorted.maf

#cancerhotspotssamples=$(awk -F '\t' '{print $16}' $cancerhotspotsfile.sorted.maf | sort | uniq -c | wc -l)
#python3 $tools/db_converter_cancerhotspots.py -i $cancerhotspotsfile.sorted.maf --samples $cancerhotspotssamples --oncotree $oncotree_name -o $cancerhotspotsfile.vcf
#$ngsbits/VcfSort -in $cancerhotspotsfile.vcf -out $cancerhotspotsfile.vcf
#cat $cancerhotspotsfile.vcf | $ngsbits/VcfLeftNormalize -stream -ref $data/genomes/GRCh37.fa | $ngsbits/VcfStreamSort > $cancerhotspotsfile.final.vcf
#awk -v OFS="\t" '!/##/ {$9=$10=""}1' $cancerhotspotsfile.final.vcf | sed 's/^\s\+//g' > $cancerhotspotsfile.final.vcf.2 # remove SAMPLE and FORMAT columns from vcf as they are added by vcfsort
#mv -f $cancerhotspotsfile.final.vcf.2 $cancerhotspotsfile.final.vcf
#bgzip -f $cancerhotspotsfile.final.vcf

#$ngsbits/VcfCheck -in $cancerhotspotsfile.final.vcf.gz -ref $data/genomes/GRCh37.fa

## crossmap to lift from GRCh37 to GRCh37
#CrossMap.py vcf $data/genomes/hg19ToHg38.fixed.over.chain.gz $cancerhotspotsfile.final.vcf.gz $genome $cancerhotspotsfile.final.vcf
#cat $cancerhotspotsfile.final.vcf | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | bgzip > $cancerhotspotsfile.final.vcf.gz
#rm -f $cancerhotspotsfile.final.vcf
#rm -f $cancerhotspotsfile.vcf
#rm -f $cancerhotspotsfile.maf
#rm -f $cancerhotspotsfile.sorted.maf

#$ngsbits/VcfCheck -in $cancerhotspotsfile.final.vcf.gz -ref $genome

#tabix -p vcf $cancerhotspotsfile.final.vcf.gz



## download refseq transcripts release 110
#cd $dbs
#mkdir -p RefSeq
#cd RefSeq

#wget -O - https://ftp.ncbi.nlm.nih.gov/genomes/refseq/vertebrate_mammalian/Homo_sapiens/annotation_releases/110/GCF_000001405.40_GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.gff.gz > refseq_transcripts_110.gff.gz


## download ensembl refseq transcript id mapping table
#cd $dbs
#mkdir -p mapping_tables
#cd mapping_tables
#wget https://github.com/imgag/ngs-bits/raw/master/src/cppNGS/Resources/hg38_ensembl_transcript_matches.tsv




## download OMIM mapping table (downloaded 02.05.2022)
: '
cd $dbs
mkdir -p OMIM
cd OMIM

wget https://www.omim.org/static/omim/data/mim2gene.txt
'

# download orphanet mapping table (downloaded 02.05.2022)
: '
cd $dbs
mkdir -p OrphaNet
cd OrphaNet

wget http://www.orphadata.org/data/xml/en_product6.xml
'



## download ARUP BRCA1 & BRCA2 (https://arup.utah.edu/database/BRCA/Variants/BRCA1.php and https://arup.utah.edu/database/BRCA/Variants/BRCA2.php)
## Database was accessed at 01.04.2022. As there is no versioning this date was used instead of an actual version number
: '
cd $dbs
mkdir -p ARUP
cd ARUP
wget -O - https://arup.utah.edu/database/BRCA/Variants/BRCA1.php | python3 $tools/db_converter_arup.py --reference NM_007294.3 > ARUP_BRCA_2022_04_01.tsv
# IMPORTANT NOTE: The ARUP website sais that their variants for BRCA2 are on the transcript "NM_000059.3". 
# For conversion of hgvs to vcf it is required that this transcript is contained in the NGSD database which is not the case for NM_000059.3. 
# Thus, I searched for the corresponding ensembl transcript: ENST00000380152 (see: https://www.ensembl.org/Homo_sapiens/Gene/Summary?g=ENSG00000139618;r=13:32315086-32400268)
wget -O - https://arup.utah.edu/database/BRCA/Variants/BRCA2.php | python3 $tools/db_converter_arup.py --reference ENST00000380152 >> ARUP_BRCA_2022_04_01.tsv
# working hgvstovcf on server: /mnt/storage1/share/opt/ngs-bits-hg38-2022_04-38-gd5054098/HgvsToVcf
$ngsbits/HgvsToVcf -in ARUP_BRCA_2022_04_01.tsv -ref $genome -out ARUP_BRCA_2022_04_01.vcf
$ngsbits/VcfSort -in ARUP_BRCA_2022_04_01.vcf -out ARUP_BRCA_2022_04_01.vcf
cat ARUP_BRCA_2022_04_01.vcf | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort | bgzip > ARUP_BRCA_2022_04_01.vcf.gz
tabix -p vcf ARUP_BRCA_2022_04_01.vcf.gz
'



## download TP53 database (https://tp53.isb-cgc.org/get_tp53data#get_annot)
cd $dbs
mkdir -p TP53_database
cd TP53_database

# this assumes that the first line is the header line. If this is not the case remove the sed
tp_db=GermlineDownload_r20
wget -O - https://storage.googleapis.com/tp53-static-files/data/$tp_db.csv | sed -e "1s/^/#/" | python3 $tools/db_converter_TP53_database.py > $tp_db.vcf

$ngsbits/VcfSort -in $tp_db.vcf -out $tp_db.vcf

cat $tp_db.vcf | $ngsbits/VcfLeftNormalize -stream -ref $genome | $ngsbits/VcfStreamSort > $tp_db.normalized.vcf

bgzip -f -c $tp_db.normalized.vcf > $tp_db.normalized.vcf.gz
tabix -p vcf $tp_db.normalized.vcf.gz

$ngsbits/VcfCheck -in $tp_db.normalized.vcf.gz -ref $genome


rm -f $tp_db.vcf



# TODO:
# - Am Ende nochmal überlegen welche referenz genome verwendet werden aktuell: ucsc grch38 + ensembl grch37 + ucsc grch37 chainover grch38

