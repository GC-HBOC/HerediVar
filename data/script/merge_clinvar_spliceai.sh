basedir=/mnt/storage2/users/ahdoebm1/HerediVar

root=$basedir
tools=$root/tools
data=$root/data
dbs=$data/dbs
ngsbits=$tools/ngs-bits/bin
grch38=$data/genomes/GRCh38.fa


clinvar_dat=$tools/herediclass/databases/Clinvar/clinvar_snv.vcf.gz
spliceai_snv_dat=$dbs/SpliceAI/spliceai_scores.masked.snv.hg38.vcf.gz
spliceai_indel_dat=$dbs/SpliceAI/spliceai_scores.masked.indel.hg38.vcf.gz


cd $root
source .venv/bin/activate


cd $dbs
mkdir -p clinvar_merge_spliceai
cd clinvar_merge_spliceai


#gunzip -c $clinvar_dat > clinvar.vcf
#clinvar_dat=clinvar.vcf
#gunzip -c $spliceai_snv_dat > spliceai_snv.vcf
#spliceai_snv_dat=spliceai_snv.vcf
#gunzip -c $spliceai_indel_dat > spliceai_indel.vcf
#spliceai_indel_dat=spliceai_indel.vcf
#
#$ngsbits/VcfSubstract -in clinvar.vcf -in2 spliceai_snv.vcf -out clinvar_no_spliceai_snv.vcf
#$ngsbits/VcfSubstract -in clinvar_no_spliceai_snv.vcf -in2 spliceai_indel.vcf -out clinvar_no_spliceai_snv_indel.vcf



$ngsbits/VcfAnnotateFromVcf -in $clinvar_dat -source $spliceai_snv_dat -threads 5 -info_keys SpliceAI -out clinvar_annotated_snv.vcf
$ngsbits/VcfAnnotateFromVcf -in clinvar_annotated_snv.vcf -source $spliceai_indel_dat -threads 5 -info_keys SpliceAI -out clinvar_annotated_snv_indel.vcf


egrep "^#|;SpliceAI=" clinvar_annotated_snv_indel.vcf > clinvar_only_annotated.vcf
$ngsbits/VcfSubstract -in clinvar_annotated_snv_indel.vcf -in2 clinvar_only_annotated.vcf -out variants_missing_annotation.vcf


bgzip -f variants_missing_annotation.vcf
tabix -f -p vcf variants_missing_annotation.vcf.gz
spliceai -I variants_missing_annotation.vcf.gz -O variants_added_annotation.vcf -R $grch38 -A grch38 -M 1


$ngsbits/VcfAdd -in variants_added_annotation.vcf -in2 clinvar_only_annotated.vcf -out clinvar_spliceai_all.vcf

$ngsbits/VcfSort -in clinvar_spliceai_all.vcf -out clinvar_spliceai_all_sorted.vcf

bgzip clinvar_spliceai_all_sorted.vcf
