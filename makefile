ROOT := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
TOOLS := $(ROOT)/tools
DATA := $(ROOT)/data
DBS := $(DATA)/dbs
GENOMES := $(DATA)/genomes
HARDCODEDDBS := $(DATA)/dbs_hardcoded



_TEXTCOL_RED := "\033[31m%s\033[0m %s\n"

## all	:	Install all tools, Download all databases and initialize the HerediVar database
.PHONY: test
test: ask_confirmation
	@echo ${ROOT}
	@echo ${TOOLS}
	@echo ${DATA}
	@echo ${DBS}

## ask_confirmation	:	Asks the user on the command line for confirmation -- use with another target
ask_confirmation:
	@read -p "Are you sure? [y/N] " ans && ans=$${ans:-N} ; \
	if [ $${ans} != y ] && [ $${ans} != Y ]; then \
		printf ${_TEXTCOL_RED} "Execution aborted!" ; \
		exit 1; \
	fi

folders:
	mkdir -p ${DBS}
	mkdir -p ${TOOLS}



#### INSTALL TOOLS















tools: python venv htslib keycloak redis vep ngs_bits samtools herediclass

## python
PYTHONPATH := $(ROOT)
PYTHONNAME := .localpython
PYTHONVERSION := 3.12.4 #3.8.10
PYTHON := $(PYTHONPATH)/$(PYTHONNAME)
python:
	if [ ! -d "${PYTHON}" ]; then \
		printf ${_TEXTCOL_RED} "Installing python $(PYTHONVERSION)" ; \
		${TOOLS}/script/install_python.sh -p ${PYTHONPATH} -n ${PYTHONNAME} -v ${PYTHONVERSION} ; \
	fi

python_clean: venv_clean
	rm -rf ${PYTHON}
	rm -rf ${PYTHONPATH}/Python-*
	

python_update: python_clean python venv


VENVPATH := $(ROOT)
VENVNAME := .venv
VENV := $(VENVPATH)/$(VENVNAME)
venv:
	if [ ! -d "${VENV}" ]; then \
		printf ${_TEXTCOL_RED} "Installing venv" ; \
		${TOOLS}/script/install_venv.sh -p ${VENVPATH} -n ${VENVNAME} -y ${PYTHON}/bin/python3 ; \
	fi

venv_clean:
	rm -rf ${VENV}

venv_update: venv_clean venv

## HTSLIB
HTSLIBPATH := $(TOOLS)
HTSLIBNAME := htslib
HTSLIB := $(HTSLIBPATH)/$(HTSLIBNAME)
HTSLIBVERSION := 1.16
htslib:
	if [ ! -d "${HTSLIB}" ]; then \
		printf ${_TEXTCOL_RED} "Installing htslib $(HTSLIBVERSION)" ; \
		${TOOLS}/script/install_htslib.sh -p ${HTSLIBPATH} -n ${HTSLIBNAME} -v ${HTSLIBVERSION} ; \
	fi

htslib_clean:
	rm -rf ${HTSLIB}

htslib_update: htslib_clean htslib


## keycloak
KEYCLOAKPATH := $(TOOLS)
KEYCLOAKNAME := keycloak
KEYCLOAK := $(KEYCLOAKPATH)/$(KEYCLOAKNAME)
KEYCLOAKVERSION := 18.0.0
keycloak:
	if [ ! -d "${KEYCLOAK}" ]; then \
		printf ${_TEXTCOL_RED} "Installing keycloak $(KEYCLOAKVERSION)" ; \
		${TOOLS}/script/install_keycloak.sh -p ${KEYCLOAKPATH} -n ${KEYCLOAKNAME} -v ${KEYCLOAKVERSION} ; \
	fi

keycloak_clean:
	rm -rf ${KEYCLOAK}

keycloak_update: keycloak_clean keycloak


## REDIS
REDISPATH := $(TOOLS)
REDISNAME := redis-stable
REDIS := $(REDISPATH)/$(REDISNAME)
redis:
	if [ ! -d "${REDIS}" ]; then \
		printf ${_TEXTCOL_RED} "Installing redis" ; \
		${TOOLS}/script/install_redis.sh -p ${REDISPATH} -n ${REDISNAME} ; \
	fi

redis_clean:
	rm -rf ${REDIS}

redis_update: redis_clean redis


## VEP
VEPPATH := $(TOOLS)
VEPNAME := ensembl-vep
VEP := $(VEPPATH)/$(VEPNAME)
VEPVERSION := 110
VEPMINORVERSION := 0
vep:
	if [ ! -d "${VEP}" ]; then \
		printf ${_TEXTCOL_RED} "Installing vep ${VEPVERSION}.${VEPMINORVERSION}" ; \
		${TOOLS}/script/install_vep.sh -p ${VEPPATH} -v ${VEPVERSION} -m ${VEPMINORVERSION} -n ${VEPNAME} ; \
	fi

vep_clean:
	rm -rf ${VEP}

vep_update: vep_clean vep

## NGS-BITS
NGSBITSPATH := $(TOOLS)
NGSBITSNAME := ngs-bits
NGSBITS := $(NGSBITSPATH)/$(NGSBITSNAME)
NGSBITSVERSION := 2022_10
ngs_bits:
	if [ ! -d "${NGSBITS}" ]; then \
		printf ${_TEXTCOL_RED} "Installing ngs-bits ${NGSBITSVERSION}" ; \
		${TOOLS}/script/install_ngs_bits.sh -p ${NGSBITSPATH} -n ${NGSBITSNAME} -v ${NGSBITSVERSION} ; \
	fi

ngs_bits_clean:
	rm -rf ${NGSBITS}

ngs_bits_update: ngs_bits_clean ngs_bits

## SAMTOOLS
SAMTOOLS := $(TOOLS)/samtools
SAMTOOLS_VERSION := 1.11
SAMTOOLSNAME := samtools
samtools:
	if [ ! -d "$(SAMTOOLS)" ]; then \
		printf ${_TEXTCOL_RED} "Installing samtools" ; \
		${TOOLS}/script/install_samtools.sh -p ${SAMTOOLSPATH} -v ${SAMTOOLSVERSION} -n ${SAMTOOLSNAME} ; \
	fi
	
samtools_clean:
	rm -rf ${SAMTOOLS}

samtools_update: samtools_clean samtools


## AUTOMATIC CLASSIFICATION HEREDICLASS
HEREDICLASSPATH := $(TOOLS)
HEREDICLASSNAME := herediclass
HEREDICLASS := $(HEREDICLASSPATH)/$(HEREDICLASSNAME)
herediclass:
	if [ ! -d "${HEREDICLASS}" ]; then \
		printf ${_TEXTCOL_RED} "Installing the automatic classification algorithm" ; \
		${TOOLS}/script/install_herediclass.sh -p ${HEREDICLASSPATH} -n ${HEREDICLASSNAME} ; \
		${TOOLS}/script/install_herediclass_config.sh -p ${HEREDICLASSPATH} -n ${HEREDICLASSNAME} ; \
	fi

herediclass_clean:
	rm -rf ${HEREDICLASS}

herediclass_update: herediclass_clean herediclass

herediclass_update_soft:
	cd ${HEREDICLASS}
	git pull

herediclass_update_config:
	${TOOLS}/script/install_herediclass_config.sh -p ${HEREDICLASSPATH} -n ${HEREDICLASSNAME} ; \




#### INSTALL JS LIBRARIES
js_libs: bootstrap igv jquery datatables

## BOOTSTRAP
BOOTSTRAPPATH := $(TOOLS)
BOOTSTRAPNAME := bootstrap
BOOTSTRAP := $(BOOTSTRAPPATH)/$(BOOTSTRAPNAME)
BOOTSTRAPVERSION := 5.2.3
bootstrap:
	if [ ! -f "${BOOTSTRAP}" ]; then \
		printf ${_TEXTCOL_RED} "Installing the automatic classification algorithm" ; \
		${TOOLS}/script/install_bootstrap.sh -p ${BOOTSTRAPPATH} -n ${BOOTSTRAPNAME} -v ${BOOTSTRAPVERSION} ; \
	fi

bootstrap_clean:
	rm -rf ${BOOTSTRAP}

bootstrap_update: bootstrap_clean bootstrap

## IGV
# download csp conform version from: https://download.imgag.de/ahdoebm1/igv/
IGVPATH := $(TOOLS)
IGVNAME := igv
IGV := $(IGVPATH)/$(IGVNAME)
IGVVERSION := 2.15.0
igv:
	if [ ! -d "${IGV}" ]; then \
		printf ${_TEXTCOL_RED} "Installing the automatic classification algorithm" ; \
		${TOOLS}/script/install_igv.sh -p ${IGVPATH} -n ${IGVNAME} -v ${IGVVERSION} ; \
	fi

igv_clean:
	rm -rf ${IGV}

igv_update: igv_clean igv

## JQUERY
JQUERYNAME := $(TOOLS)
JQUERYPATH := jquery
JQUERY := $(JQUERYPATH)/$(JQUERYNAME)
JQUERYVERSION := 3.6.3
jquery:
	if [ ! -f "${JQUERY}" ]; then \
		printf ${_TEXTCOL_RED} "Installing the automatic classification algorithm" ; \
		${TOOLS}/script/install_jquery.sh -p ${JQUERYPATH} -n ${JQUERYNAME} -v ${JQUERYVERSION} ; \
	fi

jquery_clean:
	rm -rf ${JQUERY}

jquery_update: jquery_clean jquery

## DATATABLES
DATATABLESNAME := $(TOOLS)
DATATABLESPATH := datatables
DATATABLES := $(DATATABLESPATH)/$(DATATABLESNAME)
DATATABLESVERSION := 1.13.4
datatables:
	if [ ! -f "${DATATABLES}" ]; then \
		printf ${_TEXTCOL_RED} "Installing the automatic classification algorithm" ; \
		${TOOLS}/script/install_datatables.sh -p ${DATATABLESPATH} -n ${DATATABLESNAME} -v ${DATATABLESVERSION} ; \
	fi

datatables_clean:
	rm -rf ${DATATABLES}

datatables_update: datatables_clean datatables







#### DOWNLOAD GENOMES
GRCH38PATH := $(GENOMES)
GRCH38NAME := GRCh38.fa
GRCH38 := $(GRCH38PATH)/$(GRCH38NAME)

GRCH37PATH := $(GENOMES)
GRCH37NAME := GRCh37.fa
GRCH37 := $(GRCH37PATH)/$(GRCH37NAME)

CHAINFILEPATH := $(GENOMES)
CHAINFILENAME := hg19ToHg38.fixed.over.chain.gz
CHAINFILE := $(CHAINFILEPATH)/$(CHAINFILENAME)

genomes: grch37 grch38 chainfile

grch38: samtools
	if [ ! -f "${GRCH38}" ]; then \
		printf ${_TEXTCOL_RED} "Installing grch38 reference genome" ; \
		${DATA}/script/download_GRCh38.sh -p ${GRCH38PATH} -n ${GRCH38NAME} -t samtools=${SAMTOOLS}/samtools ; \
	fi
	
grch37: samtools
	if [ ! -f "${GRCH37}" ]; then \
		printf ${_TEXTCOL_RED} "Installing grch37 reference genome" ; \
		${DATA}/script/download_GRCh37.sh -p ${GRCH37PATH} -n ${GRCH37NAME} -t samtools=${SAMTOOLS}/samtools ; \
	fi

chainfile:
	if [ ! -f "${CHAINFILE}" ]; then \
		printf ${_TEXTCOL_RED} "Installing the grch37 to grch38 chainfile" ; \
		${DATA}/script/download_chainfile.sh -p ${CHAINFILEPATH} -n ${CHAINFILENAME} ; \
	fi







#### DOWNLOAD DATA FOR INITIALIZATION OF HEREDIVAR
initialization_data: omim mapping_tables pfam mane refseq ensembl orphanet hgnc

## hgnc
HGNCPATH := $(DBS)
HGNCNAME := HGNC
HGNC := $(HGNCPATH)/$(HGNCNAME)
hgnc:
	if [ ! -d "${HGNC}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading HGNC..." ; \
		${DATA}/script/download_hgnc.sh -p ${HGNCPATH} -n ${HGNCNAME} ; \
	fi

hgnc_clean:
	rm -rf ${HGNC}

hgnc_update: hgnc_clean hgnc

## orphanet
ORPHANETPATH := $(DBS)
ORPHANETNAME := OrphaNet
ORPHANET := $(ORPHANETPATH)/$(ORPHANETNAME)
orphanet:
	if [ ! -d "${ORPHANET}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading orphanet..." ; \
		${DATA}/script/download_orphanet.sh -p ${ORPHANETPATH} -n ${ORPHANETNAME} ; \
	fi

orphanet_clean:
	rm -rf ${ORPHANET}

orphanet_update: orphanet_clean orphanet

#ensembl
ENSEMBLPATH = $(DBS)
ENSEMBLNAME = ensembl
ENSEMBLVERSION = 110
ENSEMBL= $(ENSEMBLPATH)/$(ENSEMBLNAME)
ensembl: 
	if [ ! -d "${ENSEMBL}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading ensembl ${ENSEMBLVERSION}..." ; \
		${DATA}/script/download_ensembl.sh -p ${ENSEMBLPATH} -n ${ENSEMBLNAME} -v ${ENSEMBLVERSION} ; \
	fi

ensembl_clean:
	rm -rf ${ENSEMBL}

ensembl_update: ensembl_clean ensembl

#refseq
REFSEQPATH = $(DBS)
REFSEQNAME = RefSeq
REFSEQVERSION = 110
REFSEQ= $(REFSEQPATH)/$(REFSEQNAME)
refseq: 
	if [ ! -d "${REFSEQ}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading refseq ${REFSEQVERSION}..." ; \
		${DATA}/script/download_refseq.sh -p ${REFSEQPATH} -n ${REFSEQNAME} -v ${REFSEQVERSION} -y ${VENV} -t "refseq2ensemblaccession=${TOOLS}/vcf_refseq_to_chrnum.py tools=${TOOLS} refseq2ensemblgff=${TOOLS}/refseq2ensemblgff.py"; \
	fi

refseq_clean:
	rm -rf ${REFSEQ}

refseq_update: refseq_clean refseq

#mane
MANEPATH = $(DBS)
MANENAME = MANE
MANEVERSION = 1.3
MANE= $(MANEPATH)/$(MANENAME)
mane:
	if [ ! -d "${MANE}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading mane ${MANEVERSION}..." ; \
		${DATA}/script/download_mane.sh -p ${MANEPATH} -n ${MANENAME} -v ${MANEVERSION} ; \
	fi

mane_clean:
	rm -rf ${MANE}

mane_update: mane_clean mane

## pfam protein domains
PFAMPATH = $(DBS)
PFAMNAME = PFAM
PFAMVERSION = 35.0
PFAM= $(PFAMPATH)/$(PFAMNAME)
pfam:
	if [ ! -d "${PFAM}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading pfam protein domains..." ; \
		${DATA}/script/download_pfam.sh -p ${PFAMPATH} -n ${PFAMNAME} -v ${PFAMVERSION} -y ${VENV} -t "dbconverter=${TOOLS}/db_converter_pfam.py" ; \
	fi

pfam_clean:
	rm -rf ${PFAM}

pfam_update: pfam_clean pfam

## mapping_tables
MAPPINGTABLESPATH = $(DBS)
MAPPINGTABLESNAME = mapping_tables
MAPPINGTABLES= $(MAPPINGTABLESPATH)/$(MAPPINGTABLESNAME)
mapping_tables:
	if [ ! -d "${MAPPINGTABLES}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading mapping tables..." ; \
		${DATA}/script/download_mapping_tables.sh -p ${MAPPINGTABLESPATH} -n ${MAPPINGTABLESNAME} -v ${MAPPINGTABLESVERSION} -y ${VENV} ; \
	fi

mapping_tables_clean:
	rm -rf ${MAPPINGTABLES}

mapping_tables_update: mapping_tables_clean mapping_tables

## omim
OMIMPATH = $(DBS)
OMIMNAME = OMIM
OMIM= $(OMIMPATH)/$(OMIMNAME)
omim:
	if [ ! -d "${OMIM}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading mapping tables..." ; \
		${DATA}/script/download_omim.sh -p ${OMIMPATH} -n ${OMIMNAME} ; \
	fi

omim_clean:
	rm -rf ${OMIM}

omim_update: omim_clean omim



#### DOWNLOAD ANNOTATION DATABASES
annotation_data: brca_exchange flossies dbsnp phylop cadd revel cancerhotspots tp53 gnomad hci_priors spliceai bayesdel clinvar coldspot cspecassays 

## brca exchange
BRCAEXCHANGEPATH = $(DBS)
BRCAEXCHANGENAME = BRCA_exchange
BRCAEXCHANGEVERSION = 02-22-22
BRCAEXCHANGE= $(BRCAEXCHANGEPATH)/$(BRCAEXCHANGENAME)
brca_exchange: grch38 venv ngs_bits
	if [ ! -d "${BRCAEXCHANGE}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading brca exchange..." ; \
		${DATA}/script/download_brca_exchange.sh -p ${BRCAEXCHANGEPATH} -n ${BRCAEXCHANGENAME} -v ${BRCAEXCHANGEVERSION} -y ${VENV} -t "dbconverter=${TOOLS}/db_converter_brca_exchange.py ngsbits=${NGSBITS}/bin" -g "grch38=${GRCH38}" ; \
	fi

brca_exchange_clean:
	rm -rf ${BRCAEXCHANGE}

brca_exchange_update: brca_exchange_clean brca_exchange

## flossies
FLOSSIESPATH = $(DBS)
FLOSSIESNAME = FLOSSIES
FLOSSIESVERSION = 25-03-2022
FLOSSIES= $(FLOSSIESPATH)/$(FLOSSIESNAME)
flossies: genomes venv ngs_bits
	if [ ! -d "${FLOSSIES}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading flossies $(FLOSSIESVERSION)..." ; \
		${DATA}/script/download_flossies.sh -p ${FLOSSIESPATH} -n ${FLOSSIESNAME} -v ${FLOSSIESVERSION} -y ${VENV} -t "dbconverter=${TOOLS}/db_converter_flossies.py ngsbits=${NGSBITS}/bin datauri2blob=${TOOLS}/data_uri_to_blob.py flossiesdatauris=${HARDCODEDDBS}/FLOSSIES/FLOSSIES_data_uris.txt" -g "grch38=${GRCH38} grch37=${GRCH37} chainfile=$(CHAINFILE)" ; \
	fi

flossies_clean:
	rm -rf ${FLOSSIES}

flossies_update: flossies_clean flossies

## dbsnp
DBSNPPATH = $(DBS)
DBSNPNAME = dbSNP
DBSNPVERSION = 155
DBSNP= $(DBSNPPATH)/$(DBSNPNAME)
dbsnp:
	if [ ! -d "${DBSNP}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading dbsnp $(DBSNPVERSION)..." ; \
		${DATA}/script/download_dbsnp.sh -p ${DBSNPPATH} -n ${DBSNPNAME} -v ${DBSNPVERSION} -y ${VENV} -t "dbconverter=${TOOLS}/vcf_refseq_to_chrnum.py ngsbits=${NGSBITS}/bin" -g "grch38=${GRCH38} grch37=${GRCH37} chainfile=$(CHAINFILE)" ; \
	fi

dbsnp_clean:
	rm -rf ${DBSNP}

dbsnp_update: dbsnp_clean dbsnp

## phylop
PHYLOPPATH = $(DBS)
PHYLOPNAME = phyloP
PHYLOP= $(PHYLOPPATH)/$(PHYLOPNAME)
phylop: genomes venv ngs_bits
	if [ ! -d "${PHYLOP}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading phyloP $(PHYLOPVERSION)..." ; \
		${DATA}/script/download_phylop.sh -p ${PHYLOPPATH} -n ${PHYLOPNAME} ; \
	fi

phylop_clean:
	rm -rf ${PHYLOP}

phylop_update: phylop_clean phylop

## cadd
CADDPATH = $(DBS)
CADDNAME = CADD
CADDVERSION = 1.6
CADD= $(CADDPATH)/$(CADDNAME)
cadd: genomes venv ngs_bits
	if [ ! -d "${CADD}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading cadd $(CADDVERSION)..." ; \
		${DATA}/script/download_cadd.sh -p ${CADDPATH} -n ${CADDNAME} -v ${CADDVERSION} -y ${VENV} -t "dbconverter=${TOOLS}/db_converter_cadd.py ngsbits=${NGSBITS}/bin" -g "grch38=${GRCH38} grch37=${GRCH37} chainfile=$(CHAINFILE)" ; \
	fi

cadd_clean:
	rm -rf ${CADD}

cadd_update: cadd_clean cadd

## revel
REVELPATH = $(DBS)
REVELNAME = REVEL
REVELVERSION = 1.3
REVEL= $(REVELPATH)/$(REVELNAME)
revel: genomes venv ngs_bits
	if [ ! -d "${REVEL}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading revel $(REVELVERSION)..." ; \
		${DATA}/script/download_revel.sh -p ${REVELPATH} -n ${REVELNAME} -v ${REVELVERSION} -y ${VENV} -t "dbconverter=${TOOLS}/db_converter_revel.py ngsbits=${NGSBITS}/bin zhead=${TOOLS}/zhead.sh" -g "grch38=${GRCH38} grch37=${GRCH37} chainfile=$(CHAINFILE)" ; \
	fi

revel_clean:
	rm -rf ${REVEL}

revel_update: revel_clean revel

## cancerhotspots
CANCERHOTSPOTSPATH = $(DBS)
CANCERHOTSPOTSNAME = cancerhotspots
CANCERHOTSPOTS= $(CANCERHOTSPOTSPATH)/$(CANCERHOTSPOTSNAME)
cancerhotspots: genomes venv ngs_bits
	if [ ! -d "${CANCERHOTSPOTS}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading cancerhotspots ..." ; \
		${DATA}/script/download_cancerhotspots.sh -p ${CANCERHOTSPOTSPATH} -n ${CANCERHOTSPOTSNAME} -y ${VENV} -t "dbconverter=${TOOLS}/db_converter_cancerhotspots.py merge_duplicated=${TOOLS}/db_converter_cancerhotspots_merge_duplicated.py ngsbits=${NGSBITS}/bin" -g "grch38=${GRCH38} grch37=${GRCH37} chainfile=$(CHAINFILE)" ; \
	fi

cancerhotspots_clean:
	rm -rf ${CANCERHOTSPOTS}

cancerhotspots_update: cancerhotspots_clean cancerhotspots


### arup brca
#ARUPPATH = $(DBS)
#ARUPNAME = ARUP
#ARUP= $(ARUPPATH)/$(ARUPNAME)
#arup: genomes venv ngs_bits
#	if [ ! -d "${ARUP}" ]; then \
#		printf ${_TEXTCOL_RED} "Downloading arup brca $(ARUPVERSION)..." ; \
#		${DATA}/script/download_arup.sh -p ${ARUPPATH} -n ${ARUPNAME} -y ${VENV} -t "dbconverter=${TOOLS}/db_converter_arup.py ngsbits=${NGSBITS}/bin" -g "grch38=${GRCH38} grch37=${GRCH37} chainfile=$(CHAINFILE)" ; \
#	fi
#
#arup_clean:
#	rm -rf ${ARUP}
#
#arup_update: arup_clean arup



## tp53
TP53PATH = $(DBS)
TP53NAME = TP53_database
TP53= $(TP53PATH)/$(TP53NAME)
tp53: genomes venv ngs_bits
	if [ ! -d "${TP53}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading tp53_db $(TP53VERSION)..." ; \
		${DATA}/script/download_tp53.sh -p ${TP53PATH} -n ${TP53NAME} -y ${VENV} -t "dbconverter=${TOOLS}/db_converter_TP53_database.py ngsbits=${NGSBITS}/bin zhead=${TOOLS}/zhead.sh" -g "grch38=${GRCH38} grch37=${GRCH37} chainfile=$(CHAINFILE)" ; \
	fi

tp53_clean:
	rm -rf ${TP53}

tp53_update: tp53_clean tp53

## gnomad
GNOMADPATH = $(DBS)
GNOMADNAME = gnomAD
GNOMADVERSION = 3.1.2
GNOMADMITOVERSION = 3.1
GNOMAD= $(GNOMADPATH)/$(GNOMADNAME)
gnomad: genomes venv ngs_bits
	if [ ! -d "${GNOMAD}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading gnomad $(GNOMADVERSION)..." ; \
		${DATA}/script/download_gnomad.sh -p ${GNOMADPATH} -n ${GNOMADNAME} -v ${GNOMADVERSION} -y ${VENV} -t "mito_version=${GNOMADMITOVERSION} dbconverter=${TOOLS}/db_filter_gnomad.py ngsbits=${NGSBITS}/bin" -g "grch38=${GRCH38} grch37=${GRCH37} chainfile=$(CHAINFILE)" ; \
	fi

gnomad_clean:
	rm -rf ${GNOMAD}

gnomad_update: gnomad_clean gnomad



## hci_priors
HCIPRIORSPATH = $(DBS)
HCIPRIORSNAME = HCI_priors
HCIPRIORS= $(HCIPRIORSPATH)/$(HCIPRIORSNAME)
hci_priors: genomes venv ngs_bits
	if [ ! -d "${HCIPRIORS}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading hci_priors..." ; \
		${DATA}/script/download_hci_priors.sh -p ${HCIPRIORSPATH} -n ${HCIPRIORSNAME} -y ${VENV} -t "dbconverter=${TOOLS}/priors_crawler.py ngsbits=${NGSBITS}/bin" -g "grch38=${GRCH38} grch37=${GRCH37} chainfile=$(CHAINFILE)" ; \
	fi

hci_priors_clean:
	rm -rf ${HCIPRIORS}

hci_priors_update: hci_priors_clean hci_priors


## spliceai
SPLICEAIPATH = $(DBS)
SPLICEAINAME = SpliceAI
SPLICEAI= $(SPLICEAIPATH)/$(SPLICEAINAME)
spliceai: genomes venv ngs_bits
	if [ ! -d "${SPLICEAI}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading spliceai $(SPLICEAIVERSION)..." ; \
		${DATA}/script/download_spliceai.sh -p ${SPLICEAIPATH} -n ${SPLICEAINAME} -y ${VENV} -t "dbconverter=${TOOLS}/db_filter_spliceai.py ngsbits=${NGSBITS}/bin" -g "grch38=${GRCH38} grch37=${GRCH37} chainfile=$(CHAINFILE)" ; \
	fi

spliceai_clean:
	rm -rf ${SPLICEAI}

spliceai_update: spliceai_clean spliceai


## bayesdel
BAYESDELPATH = $(DBS)
BAYESDELNAME = BayesDEL
BAYESDELVERSION = 4.4
BAYESDEL= $(BAYESDELPATH)/$(BAYESDELNAME)
bayesdel: genomes venv ngs_bits
	if [ ! -d "${BAYESDEL}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading bayesdel $(BAYESDELVERSION)..." ; \
		${DATA}/script/download_bayesdel.sh -p ${BAYESDELPATH} -n ${BAYESDELNAME} -v ${BAYESDELVERSION} -y ${VENV} -t "dbconverter=${TOOLS}/db_converter_bayesdel.py ngsbits=${NGSBITS}/bin" -g "grch38=${GRCH38} grch37=${GRCH37} chainfile=$(CHAINFILE)" ; \
	fi

bayesdel_clean:
	rm -rf ${BAYESDEL}

bayesdel_update: bayesdel_clean bayesdel


## clinvar
# version used atm: clinvar_20240107.vcf.gz
# always downloads the most recent release
CLINVARPATH = $(DBS)
CLINVARNAME = ClinVar
CLINVAR= $(CLINVARPATH)/$(CLINVARNAME)
clinvar: genomes venv ngs_bits
	if [ ! -d "${CLINVAR}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading most recent release of clinvar..." ; \
		${DATA}/script/download_clinvar.sh -p ${CLINVARPATH} -n ${CLINVARNAME} -y ${VENV} -t "dbconverter=${TOOLS}/db_converter_clinvar.py ngsbits=${NGSBITS}/bin" -g "grch38=${GRCH38} grch37=${GRCH37} chainfile=$(CHAINFILE)" ; \
	fi

clinvar_clean:
	rm -rf ${CLINVAR}

clinvar_update: clinvar_clean clinvar



## cosmic cmc Cancer Mutation Census
COSMICPATH = $(DBS)
COSMICNAME = COSMIC
COSMIC= $(COSMICPATH)/$(COSMICNAME)
cosmic: genomes venv ngs_bits
	if [ ! -d "${COSMIC}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading most recent release of cosmic..." ; \
		${DATA}/script/download_cosmic.sh -p ${COSMICPATH} -n ${COSMICNAME} -y ${VENV} -t "dbconverter=${TOOLS}/db_converter_cosmic.py ngsbits=${NGSBITS}/bin" -g "grch38=${GRCH38} grch37=${GRCH37} chainfile=$(CHAINFILE)" ; \
	fi

cosmic_clean:
	rm -rf ${COSMIC}

cosmic_update: cosmic_clean cosmic



## coldspot list
COLDSPOTPATH = $(DBS)
COLDSPOTNAME = coldspots
COLDSPOT= $(COLDSPOTPATH)/$(COLDSPOTNAME)
coldspot: genomes venv ngs_bits
	if [ ! -d "${COLDSPOT}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading most recent release of coldspot..." ; \
		${DATA}/script/download_coldspot.sh -p ${COLDSPOTPATH} -n ${COLDSPOTNAME} ; \
	fi

coldspot_clean:
	rm -rf ${COLDSPOT}

coldspot_update: coldspot_clean coldspot



## assays CSpec
CSPECASSAYSPATH = $(DBS)
CSPECASSAYSNAME = CSpec_BRCA_assays
CSPECASSAYS= $(CSPECASSAYSPATH)/$(CSPECASSAYSNAME)
cspecassays: genomes venv ngs_bits
	if [ ! -d "${CSPECASSAYS}" ]; then \
		printf ${_TEXTCOL_RED} "Downloading CSpec BRCA assays..." ; \
		${DATA}/script/download_cspec_brca_assays.sh -p ${CSPECASSAYSPATH} -n ${CSPECASSAYSNAME} -y ${VENV} -t "dbconverter_splicing=${TOOLS}/db_converter_CSpec_splicing_assays.py dbconverter_functional=${TOOLS}/db_converter_CSpec_functional_assays.py db_cspec_merge=${TOOLS}/db_converter_CSpec_merge.py ngsbits=${NGSBITS}/bin" -g "grch38=${GRCH38}" ; \
	fi

cspecassays_clean:
	rm -rf ${CSPECASSAYS}

cspecassays_update: cspecassays_clean cspecassays






