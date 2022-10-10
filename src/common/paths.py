import os


webapp_env = os.environ.get('WEBAPP_ENV')


ref_genome_name = "GRCh38"

if webapp_env == 'dev':
    """ configuration for the development environment """
    
    # workdir
    workdir = "/mnt/users/ahdoebm1/HerediVar/"
    datadir = workdir + "data/dbs/"

    #tools
    vep_path = "/mnt/storage2/GRCh38/share/opt/ensembl-vep-release-104.3"
    vep_cache_dir = "/mnt/storage2/GRCh38/share/data/dbs/ensembl-vep-104/cache"
    #ngs_bits_path = "/mnt/storage1/share/opt/ngs-bits-hg38-2022_10-1-gcb80a2dd/"
    ngs_bits_path = workdir + "src/tools/ngs-bits/bin/"
    htslib_path = workdir + "src/tools/htslib-1.16/"


    # data
    
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
    task_force_protein_domains_path = datadir + "task-force_protein_domains/Proteindomänen VUS-Task-Force_2022_final.tsv"

    # further data
    parsing_refseq_ensembl = datadir + "mapping_tables/hg38_ensembl_transcript_matches.tsv"
    gene_to_ensembl_transcript_path = datadir + "mapping_tables/gene_to_ensembl_transcript.tsv"

elif webapp_env == 'localtest':
    """ configuration when the tests are run locally and not through github actions """

    workdir = "/mnt/users/ahdoebm1/HerediVar/"
    datadir = workdir + "src/annotation_service/tests/data/testdbs/"

    
    #tools
    vep_path = "/mnt/storage2/GRCh38/share/opt/ensembl-vep-release-104.3"
    vep_cache_dir = "/mnt/storage2/GRCh38/share/data/dbs/ensembl-vep-104/cache"
    #ngs_bits_path = "/mnt/storage1/share/opt/ngs-bits-hg38-2022_04-70-g53bce65c/"
    ngs_bits_path = workdir + "src/tools/ngs-bits/bin/"
    htslib_path = workdir + "src/tools/htslib-1.16/"


    # data
    ref_genome_path = workdir + "data/genomes/GRCh38.fa"
    ref_genome_path_grch37 = workdir + "data/genomes/GRCh37.fa"
    chainfile_path = workdir + "data/genomes/hg19ToHg38.fixed.over.chain.gz"

    
    #metadata
    gnomad_path = datadir + "gnomAD.vcf.gz"
    gnomad_m_path  = datadir + "gnomAD_mito.vcf.gz"
    phylop_file_path = "/mnt/users/ahdoebm1/HerediVar/data/dbs/phyloP/hg38.phyloP100way.bw" #"https://download.imgag.de/public/dbs/phyloP/hg38_phyloP100way_vertebrate.bw"
    dbsnp_path = datadir + "dbSNP.vcf.gz"
    revel_path = datadir + "revel.vcf.gz"
    spliceai_path = datadir + "SpliceAI.vcf.gz"
    cadd_snvs_path = datadir + "CADD.vcf.gz"
    cadd_indels_path = datadir + "CADD_InDels.vcf.gz"
    clinvar_path = datadir + "ClinVar.vcf.gz"
    submission_summary_path = datadir + "ClinVar.txt.gz"
    BRCA_exchange_path = datadir + "BRCA_exchange.vcf.gz"
    FLOSSIES_path = datadir + "FLOSSIES.vcf.gz"
    cancerhotspots_path = datadir + "cancerhotspots.vcf.gz"
    arup_brca_path = datadir + "ARUP_BRCA.vcf.gz"
    tp53_db = datadir + "TP53_database.vcf.gz"


elif webapp_env == 'githubtest':   
    """ configuration for the testing environment on github actions """

    workdir = "/home/runner/work/HerediVar/HerediVar/"
    datadir = workdir + "src/annotation_service/tests/data/testdbs/"
    #datadir = "/data/"

    # tools
    # vep not used atm
    ngs_bits_path = "./" # inside docker container


    # data
    ref_genome_path = "https://download.imgag.de/public/genomes/GRCh38.fa"
    ref_genome_path_local = workdir + "GRCh38.fa" # used for spliceai
    ref_genome_path_grch37 = "https://download.imgag.de/public/genomes/GRCh37.fa"
    chainfile_path = "https://download.imgag.de/public/genomes/hg19ToHg38.over.chain.gz"

    
    #metadata
    gnomad_path = datadir + "gnomAD.vcf.gz"
    gnomad_m_path  = datadir + "gnomAD_mito.vcf.gz"
    phylop_file_path = "https://download.imgag.de/public/dbs/phyloP/hg38_phyloP100way_vertebrate.bw"
    dbsnp_path = datadir + "dbSNP.vcf.gz"
    revel_path = datadir + "revel.vcf.gz"
    spliceai_path = datadir + "SpliceAI.vcf.gz"
    cadd_snvs_path = datadir + "CADD.vcf.gz"
    cadd_indels_path = datadir + "CADD_InDels.vcf.gz"
    clinvar_path = datadir + "ClinVar.vcf.gz"
    submission_summary_path = datadir + "ClinVar.txt.gz"
    BRCA_exchange_path = datadir + "BRCA_exchange.vcf.gz"
    FLOSSIES_path = datadir + "FLOSSIES.vcf.gz"
    cancerhotspots_path = datadir + "cancerhotspots.vcf.gz"
    arup_brca_path = datadir + "ARUP_BRCA.vcf.gz"
    tp53_db = datadir + "TP53_database.vcf.gz"


elif webapp_env == 'production':
    """ configuration for the production environment """
    # TODO





