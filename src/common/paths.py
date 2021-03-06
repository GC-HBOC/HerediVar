import os

# workdir
workdir = "/mnt/users/ahdoebm1/HerediVar/"
datadir = workdir + "data/dbs/"

# tools
vep_path = "/mnt/storage2/GRCh38/share/opt/ensembl-vep-release-104.3"
#ngs_bits_path = "/mnt/storage1/share/opt/ngs-bits-hg38-2022_04-70-g53bce65c/"
ngs_bits_path = workdir + "src/tools/ngs-bits/bin/"


# data
ref_genome_name = "GRCh38"
ref_genome_path = workdir + "data/genomes/GRCh38.fa"
ref_genome_path_grch37 = workdir + "data/genomes/GRCh37.fa"
chainfile_path = workdir + "data/genomes/hg19ToHg38.fixed.over.chain.gz"

#metadata
gnomad_path = datadir + "gnomAD/gnomAD_genome_v3.1.2_GRCh38.vcf.gz"
gnomad_m_path  = datadir + "gnomAD/gnomAD_genome_v3.1.mito_GRCh38.vcf.gz"
phylop_file_path = datadir + "phyloP/hg38.phyloP100way.bw"
dbsnp_path = datadir + "dbSNP/dbSNP_v155.vcf.gz"
revel_path = datadir + "REVEL/revel_grch38_all_chromosomes.vcf.gz"
spliceai_path = datadir + "SpliceAI/spliceai_scores_2022_02_09_GRCh38.vcf.gz"
#spliceai_path = datadir + "SpliceAI/spliceai_test.vcf.gz"
cadd_snvs_path = datadir + "CADD/CADD_SNVs_1.6_GRCh38.vcf.gz"
#cadd_snvs_path = datadir + "CADD/CADD_SNVs_1.6_test.vcf.gz"
cadd_indels_path = datadir + "CADD/CADD_InDels_1.6_GRCh38.vcf.gz"
clinvar_path = datadir + "ClinVar/clinvar_20220320_converted_GRCh38.vcf.gz"
submission_summary_path = datadir + "ClinVar/submission_summary_preprocessed.txt.gz"
BRCA_exchange_path = datadir + "BRCA_exchange/BRCA_exchange_02-22-22.vcf.gz"
FLOSSIES_path = datadir + "FLOSSIES/FLOSSIES_25-03-2022.vcf.gz"
cancerhotspots_path = datadir + "cancerhotspots/cancerhotspots.v2.final.vcf.gz"
arup_brca_path = datadir + "ARUP/ARUP_BRCA_2022_04_01.vcf.gz"
tp53_db = datadir + "TP53_database/GermlineDownload_r20.normalized.vcf.gz"

# data for init_db
hgnc_path = datadir + "HGNC/hgnc_complete_set.tsv"
ensembl_transcript_path = datadir + "ensembl/Homo_sapiens.GRCh38.105.gff3"
MANE_path = datadir + "MANE/MANE.GRCh38.v1.0.ensembl_genomic.gff"
ensembl_canonical_path = datadir + "ensembl/Homo_sapiens.GRCh38.105.canonical.tsv"
pfam_id_mapping_path = datadir + "PFAM/pfam_id_mapping.tsv"
pfam_legacy_path = datadir + "PFAM/pfam_legacy.tsv"
refseq_transcript_path = datadir + "RefSeq/refseq_transcripts_110.gff.gz"
omim_path = datadir + "OMIM/mim2gene.txt"
orphanet_path = datadir + "OrphaNet/en_product6.xml"
task_force_protein_domains_path = datadir + "task-force_protein_domains/Proteindom??nen VUS-Task-Force_2022_final.tsv"

# further data
parsing_refseq_ensembl = datadir + "mapping_tables/hg38_ensembl_transcript_matches.tsv"
gene_to_ensembl_transcript_path = datadir + "mapping_tables/gene_to_ensembl_transcript.tsv"

