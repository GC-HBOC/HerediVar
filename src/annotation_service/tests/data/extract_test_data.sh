#!/bin/bash


root=/mnt/users/ahdoebm1/HerediVar
tools=$root/src/tools
datadir=$root/data/dbs
testdir=$root/src/annotation_service/tests
testdatadir=$testdir/data/testdbs

# prepare folder
mkdir -p $testdatadir


# get dbsnp
zcat $datadir/dbSNP/dbSNP_v155.vcf.gz | head -n 100 > $testdatadir/dbSNP.vcf
#chr1    10001   rs1570391677    T       A       .       .       RS=1570391677;dbSNPBuildID=154;SSR=0;PSEUDOGENEINFO=DDX11L1:100287102;VC=SNV;R5;GNO;FREQ=KOREAN:0.9891,0.0109,.|SGDP_PRJ:0,1,.|dbGaP_PopFreq:1,.,0;COMMON
echo "chr1	10304277	rs149267056	T	C	.	.	RS=149267056" >> $testdatadir/dbSNP.vcf
bgzip -f $testdatadir/dbSNP.vcf
tabix -fp vcf $testdatadir/dbSNP.vcf.gz


# get revel
zcat $datadir/REVEL/revel_grch38_all_chromosomes.vcf.gz | head -n 100 > $testdatadir/revel.vcf
#chr1	35142	.	G	A	.	.	REVEL=0.027
bgzip -f $testdatadir/revel.vcf
tabix -fp vcf $testdatadir/revel.vcf.gz


# get cadd
zcat $datadir/CADD/CADD_SNVs_1.6_GRCh38.vcf.gz | head -n 100 > $testdatadir/CADD.vcf
#chr1    10009   .       A       T       .       .       CADD=8.518
bgzip -f $testdatadir/CADD.vcf
tabix -fp vcf $testdatadir/CADD.vcf.gz


# get gnomad
zcat $datadir/gnomAD/gnomAD_genome_v3.1.2_GRCh38.vcf.gz | head -n 100 > $testdatadir/gnomAD.vcf
#chr1	10037	.	T	C	.	AS_VQSR	AF=2.60139e-05;AC=2;hom=0;popmax=eas;AC_popmax=1;AN_popmax=2456;AF_popmax=0.000407166;het=2
bgzip -f $testdatadir/gnomAD.vcf
tabix -fp vcf $testdatadir/gnomAD.vcf.gz

zcat $datadir/gnomAD/gnomAD_genome_v3.1.mito_GRCh38.vcf.gz | head -n 100 > $testdatadir/gnomAD_mito.vcf
#chr1	10037	.	T	C	.	AS_VQSR	AF=2.60139e-05;AC=2;hom=0;popmax=eas;AC_popmax=1;AN_popmax=2456;AF_popmax=0.000407166;het=2
bgzip -f $testdatadir/gnomAD_mito.vcf
tabix -fp vcf $testdatadir/gnomAD_mito.vcf.gz


# get BRCA exchange
zcat $datadir/BRCA_exchange/BRCA_exchange_02-22-22.vcf.gz | head -n 100 > $testdatadir/BRCA_exchange.vcf
#chr13   32315226        .       G       A       .       .       clin_sig_detail=Benign(ENIGMA),_Benign_(ClinVar);clin_sig_short=Benign_/_Little_Clinical_Significance
bgzip -f $testdatadir/BRCA_exchange.vcf
tabix -fp vcf $testdatadir/BRCA_exchange.vcf.gz


# get flossies
zcat $datadir/FLOSSIES/FLOSSIES_25-03-2022.vcf.gz | grep -v "^##contig" | head -n 100 > $testdatadir/FLOSSIES.vcf
#chr2	17753961	.	G	C	.	.	num_eur=1;num_afr=0
bgzip -f $testdatadir/FLOSSIES.vcf
tabix -fp vcf $testdatadir/FLOSSIES.vcf.gz


# get cancerhotspots
zcat $datadir/cancerhotspots/cancerhotspots.v2.final.vcf.gz | grep -v "^##contig" | head -n 100 > $testdatadir/cancerhotspots.vcf
#chr1	939434	.	A	AT	.	.	cancertypes=Colorectal_Adenocarcinoma:bowel|Invasive_Breast_Carcinoma:breast|Cutaneous_Melanoma:skin|Low-Grade_Glioma:cnsbrain;AC=4;AF=0.00016503692701241903
bgzip -f $testdatadir/cancerhotspots.vcf
tabix -fp vcf $testdatadir/cancerhotspots.vcf.gz


# get arup brca classifications
zcat $datadir/ARUP/ARUP_BRCA_2022_04_01.vcf.gz | grep -v "^##contig" | head -n 100 > $testdatadir/ARUP_BRCA.vcf
#chr13	32316453	.	AGGTAAAAATGCCTATT	A	.	.	HGVSc=ENST00000380152:c.-5_11del;classification=5
bgzip -f $testdatadir/ARUP_BRCA.vcf
tabix -fp vcf $testdatadir/ARUP_BRCA.vcf.gz


#get tp53 db
zcat $datadir/TP53_database/GermlineDownload_r20.normalized.vcf.gz | grep -v "^##contig" | head -n 100 > $testdatadir/TP53_database.vcf
#chr17	7670613	.	A	C	.	.	class=FH;bayes_del=0.1186;transactivation_class=functional;DNE_LOF_class=notDNE_notLOF;DNE_class=No;domain_function=Regulation;pubmed=12672316&18511570
bgzip -f $testdatadir/TP53_database.vcf
tabix -fp vcf $testdatadir/TP53_database.vcf.gz


# get clinvar
zcat $datadir/ClinVar/clinvar_20220320_converted_GRCh38.vcf.gz | head -n 100 > $testdatadir/ClinVar.vcf
#chr1	925952	1019397	G	A	.	.	inpret=Uncertain_significance;revstat=criteria_provided,_single_submitter;varid=1019397;submissions=1019397|Uncertain_significance|2020-07-03|criteria_provided\_single_submitter|CN517202:not_provided|Invitae|description:_This_sequence_change_replaces_glycine_with_glutamic_acid_at_codon_4_of_the_SAMD11_protein_(p.Gly4Glu)._The_glycine_residue_is_weakly_conserved_and_there_is_a_moderate_physicochemical_difference_between_glycine_and_glutamic_acid._This_variant_is_not_present_in_population_databases_(ExAC_no_frequency)._This_variant_has_not_been_reported_in_the_literature_in_individuals_with_SAMD11-related_conditions._Algorithms_developed_to_predict_the_effect_of_missense_changes_on_protein_structure_and_function_are_either_unavailable_or_do_not_agree_on_the_potential_impact_of_this_missense_change_(SIFT:_Deleterious&_PolyPhen-2:_Probably_Damaging&_Align-GVGD:_Class_C0)._In_summary\_the_available_evidence_is_currently_insufficient_to_determine_the_role_of_this_variant_in_disease._Therefore\_it_has_been_classified_as_a_Variant_of_Uncertain_Significance.
bgzip -f $testdatadir/ClinVar.vcf
tabix -fp vcf $testdatadir/ClinVar.vcf.gz


zcat $datadir/ClinVar/submission_summary_preprocessed.txt.gz | head -n 1 > $testdatadir/ClinVar.txt
zcat $datadir/ClinVar/submission_summary_preprocessed.txt.gz | grep "^1019397" >> $testdatadir/ClinVar.txt
#1019397	Uncertain significance	Jul 03, 2020	This sequence change replaces glycine with glutamic acid at codon 4 of the SAMD11 protein (p.Gly4Glu). The glycine residue is weakly conserved and there is a moderate physicochemical difference between glycine and glutamic acid. This variant is not present in population databases (ExAC no frequency). This variant has not been reported in the literature in individuals with SAMD11-related conditions. Algorithms developed to predict the effect of missense changes on protein structure and function are either unavailable or do not agree on the potential impact of this missense change (SIFT: Deleterious; PolyPhen-2: Probably Damaging; Align-GVGD: Class C0). In summary, the available evidence is currently insufficient to determine the role of this variant in disease. Therefore, it has been classified as a Variant of Uncertain Significance.	MedGen:CN517202	CN517202:not provided	criteria provided, single submitter	clinical testing	germline:na	Invitae	SCV001509541.1	SAMD11	-
bgzip -f $testdatadir/ClinVar.txt

# get spliceai
zcat $datadir/SpliceAI/spliceai_scores_2022_02_09_GRCh38.vcf.gz | head -n 100 > $testdatadir/SpliceAI.vcf
#chr1	69092	.	T	C	.	.	SpliceAI=C|OR4F5|0.01|0.00|0.09|0.01|41|42|1|23
bgzip -f $testdatadir/SpliceAI.vcf
tabix -fp vcf $testdatadir/SpliceAI.vcf.gz


# get HCI_priors
zcat $datadir/HCI_priors/priors.vcf.gz | grep "^#" > $testdatadir/HCI_priors.vcf
zcat $datadir/HCI_priors/priors.vcf.gz | grep "43095845" >> $testdatadir/HCI_priors.vcf
#chr17	43095845	.	C	G	.	.	HCI_prior=0.5
bgzip -f $testdatadir/HCI_priors.vcf
tabix -fp vcf $testdatadir/HCI_priors.vcf.gz