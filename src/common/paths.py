import os
from os import path
import sys

def joinpaths(path, *paths):
    result = path.rstrip('/')
    for p in paths:
        p = p.strip().strip('/')
        if p != '':
            p = '/' + p
            result += p
    return result


ref_genome_name = "GRCh38"


webapp_env = os.environ.get('WEBAPP_ENV', None)


if webapp_env == 'dev':
    """ configuration for the development environment """
    
    # general paths
    workdir = "/mnt/storage2/users/ahdoebm1/HerediVar/"
    datadir = joinpaths(workdir, "data/dbs")
    toolsdir = joinpaths(workdir, "tools")
    resources_dir = joinpaths(workdir, 'resources')
    logs_dir = joinpaths(workdir, 'logs')
    classified_variants_dir = joinpaths(workdir, 'classified_variants')
    #report_dir = joinpaths(workdir, "") #'downloads/consensus_classification_reports/'

    # webapp logs path
    webapp_log_dir = joinpaths(logs_dir, "webapp")
    webapp_log = joinpaths(webapp_log_dir, "webapp.log")

    #tools
    vep_path = joinpaths(toolsdir, "ensembl-vep")
    vep_cache_dir = joinpaths(toolsdir, "ensembl-vep/data/cache")
    #ngs_bits_path = "/mnt/storage1/share/opt/ngs-bits-hg38-2022_10-1-gcb80a2dd/"
    ngs_bits_path = joinpaths(toolsdir, "ngs-bits/bin")
    htslib_path = joinpaths(toolsdir, "htslib")
    automatic_classification_path = joinpaths(toolsdir, "variant_classification")

    # data
    ref_genome_dir = joinpaths(workdir, "data/genomes")
    ref_genome_path = joinpaths(ref_genome_dir, "GRCh38.fa")
    ref_genome_path_grch37 = joinpaths(ref_genome_dir, "GRCh37.fa")
    chainfile_path = joinpaths(ref_genome_dir, "hg19ToHg38.fixed.over.chain.gz")
    
    #metadata
    gnomad_path = joinpaths(datadir, "gnomAD/gnomAD_genome_v3.1.2_GRCh38.vcf.gz")
    gnomad_m_path = joinpaths(datadir, "gnomAD/gnomad_m.vcf.gz")
    phylop_file_path = joinpaths(datadir, "phyloP/hg38.phyloP100way.bw")
    dbsnp_path = joinpaths(datadir, "dbSNP/dbSNP_v155.vcf.gz")
    revel_path = joinpaths(datadir, "REVEL/revel_grch38_all_chromosomes.vcf.gz")
    spliceai_snv_path = joinpaths(datadir, "SpliceAI/spliceai_scores.masked.snv.hg38.vcf.gz")
    spliceai_indel_path = joinpaths(datadir, "SpliceAI/spliceai_scores.masked.indel.hg38.vcf.gz")
    #spliceai_path = joinpaths(datadir, "SpliceAI/spliceai_scores_2022_02_09_GRCh38.vcf.gz")
    #spliceai_path = joinpaths(datadir, "SpliceAI/spliceai_test.vcf.gz")
    cadd_snvs_path = joinpaths(datadir, "CADD/CADD_SNVs_1.6_GRCh38.vcf.gz")
    #cadd_snvs_path = joinpaths(datadir, "CADD/CADD_SNVs_1.6_test.vcf.gz")
    cadd_indels_path = joinpaths(datadir, "CADD/CADD_InDels_1.6_GRCh38.vcf.gz")
    clinvar_path = joinpaths(datadir, "ClinVar/clinvar_converted_GRCh38.vcf.gz")
    submission_summary_path = joinpaths(datadir, "ClinVar/submission_summary_preprocessed.txt.gz")
    BRCA_exchange_path = joinpaths(datadir, "BRCA_exchange/BRCA_exchange_02-22-22.vcf.gz")
    FLOSSIES_path = joinpaths(datadir, "FLOSSIES/FLOSSIES_25-03-2022.vcf.gz")
    cancerhotspots_path = joinpaths(datadir, "cancerhotspots/cancerhotspots.v2.final.vcf.gz")
    arup_brca_path = joinpaths(datadir, "ARUP/ARUP_BRCA_2022_04_01.vcf.gz")
    tp53_db = joinpaths(datadir, "TP53_database/GermlineDownload_r20.normalized.vcf.gz")
    hci_priors = joinpaths(datadir, "HCI_priors/priors.vcf.gz")
    bayesdel = joinpaths(datadir, "BayesDEL/bayesdel_4.4.vcf.gz")
    cosmic = joinpaths(datadir, "COSMIC/cosmic_cmc.vcf.gz")

    # data for init_db
    hgnc_path = joinpaths(datadir, "HGNC/hgnc_complete_set.tsv")
    ensembl_transcript_path = joinpaths(datadir, "ensembl/Homo_sapiens.GRCh38.110.gff3")
    MANE_path = joinpaths(datadir, "MANE/MANE.GRCh38.v1.3.ensembl_genomic.gff")
    ensembl_canonical_path = joinpaths(datadir, "ensembl/Homo_sapiens.GRCh38.105.canonical.tsv")
    pfam_id_mapping_path = joinpaths(datadir, "PFAM/pfam_id_mapping.tsv")
    pfam_legacy_path = joinpaths(datadir, "PFAM/pfam_legacy.tsv")
    refseq_transcript_path = joinpaths(datadir, "RefSeq/refseq_transcripts_110.gff.gz")
    omim_path = joinpaths(datadir, "OMIM/mim2gene.txt")
    orphanet_path = joinpaths(datadir, "OrphaNet/en_product6.xml")
    task_force_protein_domains_path = joinpaths(datadir, "task-force_protein_domains/domains_task_force_27_11_2023.tsv")

    # further data
    parsing_refseq_ensembl = joinpaths(datadir, "mapping_tables/hg38_ensembl_transcript_matches.tsv")
    gene_to_ensembl_transcript_path = joinpaths(datadir, "mapping_tables/gene_to_ensembl_transcript.tsv")


    # IGV data
    igv_data_path = joinpaths(workdir, "src/frontend_celery/webapp/static/packages/igv/data")

    # clinvar submission
    clinvar_submission_schema = joinpaths(resources_dir, "clinvar_submission_schemas/clinvar_submission_schema_18_10_23.json")


elif webapp_env == 'localtest':
    """ configuration when the tests are run locally and not through github actions """

    # general paths
    workdir = "/mnt/storage2/users/ahdoebm1/HerediVar/"
    datadir = joinpaths(workdir, "src/annotation_service/tests/data/testdbs/")
    toolsdir = joinpaths(workdir, "tools")
    resources_dir = joinpaths(workdir, 'resources')
    logs_dir = joinpaths(workdir, 'logs')
    classified_variants_dir = joinpaths(workdir, 'classified_variants')
    #report_dir = joinpaths(workdir, "") #'downloads/consensus_classification_reports/'

    # webapp logs path
    webapp_log_dir = joinpaths(logs_dir, "test")
    webapp_log = joinpaths(webapp_log_dir, "webapp.log")

    
    #tools
    #vep_path = "/mnt/storage2/GRCh38/share/opt/ensembl-vep-release-104.3"
    #vep_cache_dir = "/mnt/storage2/GRCh38/share/data/dbs/ensembl-vep-104/cache"
    vep_path = joinpaths(toolsdir, "ensembl-vep")
    vep_cache_dir = joinpaths(toolsdir, "ensembl-vep/data/cache")
    #ngs_bits_path = "/mnt/storage1/share/opt/ngs-bits-hg38-2022_04-70-g53bce65c/"
    ngs_bits_path = joinpaths(toolsdir, "ngs-bits/bin/")
    htslib_path = joinpaths(toolsdir, "htslib/")


    # data
    ref_genome_path = workdir + "data/genomes/GRCh38.fa"
    ref_genome_path_grch37 = workdir + "data/genomes/GRCh37.fa"
    chainfile_path = workdir + "data/genomes/hg19ToHg38.fixed.over.chain.gz"

    
    #metadata
    gnomad_path = datadir + "gnomAD.vcf.gz"
    gnomad_m_path  = datadir + "gnomAD_mito.vcf.gz"
    phylop_file_path = "/mnt/users/ahdoebm1/HerediVar/data/dbs/phyloP/hg38.phyloP100way.bw"#"https://download.imgag.de/public/dbs/phyloP/hg38_phyloP100way_vertebrate.bw"
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
    hci_priors = datadir + "HCI_priors.vcf.gz"

    # IGV data
    igv_data_path = joinpaths(workdir, "src/frontend_celery/webapp/static/packages/igv/data")

    # clinvar submission
    clinvar_submission_schema = joinpaths(resources_dir, "clinvar_submission_schemas/clinvar_submission_schema_18_10_23.json")

elif webapp_env == 'githubtest':   
    """ configuration for the testing environment on github actions """

    workdir = "/home/runner/work/HerediVar/HerediVar/"
    datadir =  joinpaths(workdir, "src/annotation_service/tests/data/testdbs/")
    toolsdir = joinpaths(workdir, "tools")
    resources_dir = joinpaths(workdir, 'resources')
    logs_dir = joinpaths(workdir, 'logs')
    classified_variants_dir = joinpaths(workdir, 'classified_variants')
    #datadir = "/data/"

    # tools
    # vep not used atm
    ngs_bits_path = "" # added to path variable
    htslib_path = "" # added to path variable


    # data
    #ref_genome_path = "https://download.imgag.de/public/genomes/GRCh38.fa"
    ref_genome_path = workdir + "GRCh38.fa" # used for spliceai
    ref_genome_path_grch37 = workdir + "GRCh37.fa"
    chainfile_path =  workdir + "hg19ToHg38.fixed.over.chain.gz"

    
    #metadata
    gnomad_path = datadir + "gnomAD.vcf.gz"
    gnomad_m_path  = datadir + "gnomAD_mito.vcf.gz"
    phylop_file_path = workdir + "hg38.phyloP100way.bw"
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
    hci_priors = datadir + "HCI_priors.vcf.gz"

    # IGV data
    igv_data_path = joinpaths(workdir, "src/frontend_celery/webapp/static/packages/igv/data")

    # clinvar submission
    clinvar_submission_schema = joinpaths(resources_dir, "clinvar_submission_schemas/clinvar_submission_schema_18_10_23.json")



elif webapp_env == 'prod':
    """ configuration for the production environment """


    # general paths
    workdir = "/mnt/storage1/HerediVar"
    datadir = joinpaths(workdir, "data/dbs")
    toolsdir = joinpaths(workdir, "tools")
    resources_dir = joinpaths(workdir, 'resources')
    logs_dir = joinpaths(workdir, 'logs')
    classified_variants_dir = joinpaths(workdir, 'classified_variants')
    #report_dir = joinpaths(workdir, "") #'downloads/consensus_classification_reports/'

    # webapp logs path
    webapp_log_dir = joinpaths(logs_dir, "webapp")
    webapp_log = joinpaths(webapp_log_dir, "webapp.log")



    #tools
    vep_path = joinpaths(toolsdir, "ensembl-vep")
    vep_cache_dir = joinpaths(vep_path, "data/cache")
    os.environ['PERL5LIB'] = vep_path + "/Bio/:" + vep_path + "/cpan/lib/perl5/:" + os.environ.get('PERL5LIB', '')
    #ngs_bits_path = "/mnt/storage1/share/opt/ngs-bits-hg38-2022_04-70-g53bce65c/"
    ngs_bits_path = joinpaths(toolsdir, "ngs-bits/bin")
    htslib_path = joinpaths(toolsdir, "htslib-1.16")



    # data
    ref_genome_dir = joinpaths(workdir, "data/genomes")
    ref_genome_path = joinpaths(ref_genome_dir, "GRCh38.fa")
    ref_genome_path_grch37 = joinpaths(ref_genome_dir, "GRCh37.fa")
    chainfile_path = joinpaths(ref_genome_dir, "hg19ToHg38.fixed.over.chain.gz")

    ensembl_transcript_path = joinpaths(datadir, "ensembl/Homo_sapiens.GRCh38.110.gff3")

    
    #metadata
    gnomad_path = joinpaths(datadir, "gnomAD/gnomAD_genome_v3.1.2_GRCh38.vcf.gz")
    gnomad_m_path  = joinpaths(datadir, "gnomAD/gnomAD_genome_v3.1.mito_GRCh38.vcf.gz")
    phylop_file_path = joinpaths(datadir, "phyloP/hg38.phyloP100way.bw")
    dbsnp_path = joinpaths(datadir, "dbSNP/dbSNP_v155.vcf.gz")
    revel_path = joinpaths(datadir, "REVEL/revel_grch38_all_chromosomes.vcf.gz")
    spliceai_snv_path = joinpaths(datadir, "SpliceAI/spliceai_scores.masked.snv.hg38.vcf.gz")
    spliceai_indel_path = joinpaths(datadir, "SpliceAI/spliceai_scores.masked.indel.hg38.vcf.gz")
    #spliceai_path = joinpaths(datadir, "SpliceAI/spliceai_scores_2022_02_09_GRCh38.vcf.gz")
    cadd_snvs_path = joinpaths(datadir, "CADD/CADD_SNVs_1.6_GRCh38.vcf.gz")
    cadd_indels_path = joinpaths(datadir, "CADD/CADD_InDels_1.6_GRCh38.vcf.gz")
    clinvar_path = joinpaths(datadir, "ClinVar/clinvar_converted_GRCh38.vcf.gz")
    submission_summary_path = joinpaths(datadir, "ClinVar/submission_summary_preprocessed.txt.gz")
    BRCA_exchange_path = joinpaths(datadir, "BRCA_exchange/BRCA_exchange_02-22-22.vcf.gz")
    FLOSSIES_path = joinpaths(datadir, "FLOSSIES/FLOSSIES_25-03-2022.vcf.gz")
    cancerhotspots_path = joinpaths(datadir, "cancerhotspots/cancerhotspots.v2.final.vcf.gz")
    arup_brca_path = joinpaths(datadir, "ARUP/ARUP_BRCA_2022_04_01.vcf.gz")
    tp53_db = joinpaths(datadir, "TP53_database/GermlineDownload_r20.normalized.vcf.gz")
    hci_priors = joinpaths(datadir, "HCI_priors/priors.vcf.gz")
    bayesdel = joinpaths(datadir, "BayesDEL/bayesdel_4.4.vcf.gz")
    cosmic = joinpaths(datadir, "COSMIC/cosmic_cmc.vcf.gz")

    # IGV data
    igv_data_path = joinpaths(workdir, "src/frontend_celery/webapp/static/packages/igv/data")

    # clinvar submission
    clinvar_submission_schema = joinpaths(resources_dir, "clinvar_submission_schemas/clinvar_submission_schema_18_10_23.json")