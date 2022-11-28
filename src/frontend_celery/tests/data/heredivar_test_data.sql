--
-- All Annotation types
--

LOCK TABLES `annotation_type` WRITE;
INSERT INTO `annotation_type` VALUES (3,'rsid','rs-num','The rs-number of a variant from dbSNP (version summary: https://www.ncbi.nlm.nih.gov/projects/SNP/snp_summary.cgi)','text','155','2021-06-16','None'),(4,'phylop_100way','PhyloP-100way','PhyloP 100 vertebrates (100-way) conservation scores. These scores measure evolutionary conservation at individual alignment sites. Interpretations of the scores are compared to the evolution that is expected under neutral drift. Positive scores: Measure conservation, which is slower evolution than expected, at sites that are predicted to be conserved. Negative scores: Measure acceleration, which is faster evolution than expected, at sites that are predicted to be fast-evolving. ','float',NULL,'2013-12-01','Pathogenicity'),(5,'cadd_scaled','CADD','The scaled CADD scores: PHRED-like (-10*log10(rank/total)) scaled C-score ranking a variant relative to all possible substitutions of the human genome (8.6x10^9). These scores range from 1 to 99. A cutoff for deleteriousness can be set to 10-15, but the choice remains arbitrary.','float','v1.6','2020-04-11','Pathogenicity'),(6,'revel','REVEL','The REVEL pathogenicity score of this variant. This score can range from 0 to 1, which reflects the number of trees in the random forest that classified the variant as pathogenic. Thus, higher values represent a more \"certain\" decision. When choosing a cutoff one should keep in mind that higher cutoffs will result in a higher specificity, but lower sensitivity.','float','v1.3','2021-05-03','Pathogenicity'),(7,'spliceai_details','spliceAI','Details about the SpliceAI predictions: These include delta scores (DS) and delta positions (DP) for acceptor gain (AG), acceptor loss (AL), donor gain (DG), and donor loss (DL). Format: GENE|DS_AG|DS_AL|DS_DG|DS_DL|DP_AG|DP_AL|DP_DG|DP_DL','text','v1.3.1','2021-09-07','Splicing'),(8,'spliceai_max_delta','spliceAI max delta','Max of delta scores for acceptor gain, acceptor loss, donor gain and donor loss. A value of 0.5 or more can be assumed to have an impact on splicing.','float','v1.3.1','2021-09-07','Splicing'),(9,'maxentscan_ref','MaxEntScan ref','MaxEntScan reference sequence score. The lower the score, the more difference one would expect the input (ie mutated) sequence is from the reference. Whenever the difference between ref and alt is positive it predicts a functional splice site. A negative difference predicts that this position is not a functional splice site.','float',NULL,'2018-08-29','Splicing'),(10,'maxentscan_alt','MaxEntScan alt','MaxEntScan alternate sequence score calculated though VEP release-104.3 using the MaxEntScan plugin','float',NULL,'2018-08-29','Splicing'),(11,'gnomad_ac','AC','gnomAD alternate allele count for samples','int','v3.1.2','2021-10-22','gnomAD'),(12,'gnomad_af','AF','gnomAD frequency of alternate allele in samples','float','v3.1.2','2021-10-22','gnomAD'),(13,'gnomad_hom','hom','gnomAD number of homozygous individuals in samples','int','v3.1.2','2021-10-22','gnomAD'),(14,'gnomad_hemi','hemi','gnomAD number of hemizygous individuals in samples','int','v3.1.2','2021-10-22','gnomAD'),(15,'gnomad_het','het','gnomAD number of heterozygous individuals in samples','int','v3.1.2','2021-10-22','gnomAD'),(16,'gnomad_popmax','popmax','gnomAD population with maximum allele frequency (AF)','text','v3.1.2','2021-10-22','gnomAD'),(17,'gnomadm_ac_hom','mito AC hom','Allele count restricted to variants with a heteroplasmy level >= 0.95 from the GnomAD mitochondrial genome data. These variants are (almost) homozygous among all mitochondria in an individual','int','v3.1','2020-11-17','gnomAD'),(18,'brca_exchange_clinical_significance','BRCA exchange','Variant pathogenicity as displayed in the Summary view of the BRCA exchange database','text','54','2022-02-22','None'),(19,'flossies_num_afr','num AFR','Number of individuals with this variant in the african american cohort. (n=2559)','int',NULL,'2022-03-25','FLOSSIES'),(20,'flossies_num_eur','num EUR','Number of individuals with this variant in the european american cohort. (n=7325)','int',NULL,'2022-03-25','FLOSSIES'),(21,'arup_classification','ARUP classification','Pathogenicity classification from the ARUP database (1: not pathogenic or of no clinical significance; 2: likely not pathogenic or of little clinical significance; 3: uncertain; 4: likely pathogenic; 5: definitely pathogenic)','int',NULL,'2022-04-01','None'),(22,'cancerhotspots_cancertypes','cancertypes','A | delimited list of all cancertypes associated to this variant according to cancerhotspots. FORMAT: tumortype:tissue','text','v2','2017-12-15','Cancerhotspots'),(23,'cancerhotspots_ac','AC','Number of samples showing the variant from cancerhotspots','int','v2','2017-12-15','Cancerhotspots'),(24,'cancerhotspots_af','AF','Allele Frequency of the variant (AC / num samples cancerhotspots)','float','v2','2017-12-15','Cancerhotspots'),(25,'rsid','rs-num','https://www.ncbi.nlm.nih.gov/projects/SNP/snp_summary.cgi)','text','0','2010-07-01','None'),(26,'rsid','rs-num','atests','text','0','2010-01-01','None'),(27,'tp53db_class','class','Family classification: LFS = strict clinical definition of Li-Fraumeni syndrome, LFL = Li-Fraumeni like for the extended clinical definition of Li-Fraumeni, FH: family history of cancer which does not fulfil LFS or any of the LFL definitions, No FH: no family history of cancer, FH= Family history of cancer (not fulfilling the definition of LFS/LFL),  No= no family history of cancer, ?= unknown','text','r20','2019-07-01','TP53 database'),(29,'tp53db_DNE_LOF_class','DNE LOF class','Functional classification for loss of growth-suppression and dominant-negative activities based on Z-scores','text','r20','2019-07-01','TP53 database'),(30,'tp53db_bayes_del','bayes del','Missense variant functional predictions by BayesDel tool (Feng 2017) used without allele frequency. Score bigger or equal to 0.16: damaging; Score smaller than 0.16: tolerated','float','r20','2019-07-01','TP53 database'),(31,'tp53db_DNE_class','DNE class','Dominant-negative effect on transactivation by wild-type p53. Yes: dominant-negative activity on WAF1 and RGC promoters, Moderate: dominant-negative activity on some but not all promoters, No: no dominant-negative activity on both WAF1 and RGC promoters, or none of the promoters in the large studies.','text','r20','2019-07-01','TP53 database'),(32,'tp53db_domain_function','domain function','Function of the domain in which the mutated residue is located.','text','r20','2019-07-01','TP53 database'),(33,'tp53db_transactivation_class','transactivation class','Functional classification based on the overall transcriptional activity','text','r20','2019-07-01','TP53 database'),(34,'heredicare_cases_count','num cases','Number of cases the variant occurs in','int',NULL,'2022-05-23','HerediCare'),(35,'heredicare_family_count','num failies','Number of families the variant occurs in','int',NULL,'2022-05-23','HerediCare'),(36,'task_force_protein_domain','domain','The description of the protein domain from a hand-crafted table by the VUS-Task-Force.','text',NULL,'2022-06-01','Task-Force protein domains'),(37,'task_force_protein_domain_source','source','The source of the task force protein domain.','text',NULL,'2022-06-01','Task-Force protein domains'),(39,'hexplorer','hexplorer','The HEXplorer delta score (HZEI mutant - HZEI wildtype). HZEI scores were normalized by the total number of nucleotide positions which contribute to the score.','float','1.0','2022-06-30','Splicing'),(40,'hexplorer_mut','hexplorer mut','The HEXplorer score for the mutant sequence. HZEI scores were normalized by the total number of nucleotide positions which contribute to the score.','float','1.0','2022-06-30','Splicing'),(41,'hexplorer_wt','hexplorer wt','The HEXplorer score for the reference sequence. HZEI scores were normalized by the total number of nucleotide positions which contribute to the score.','float','1.0','2022-06-30','Splicing'),(42,'hexplorer_rev','hexplorer reverse','The HEXplorer delta score for the reverse complement of the original sequence (HZEI mutant rev - HZEI wildtype rev). HZEI scores were normalized by the total number of nucleotide positions which contribute to the score.','float','1.0','2022-06-30','Splicing'),(43,'hexplorer_rev_mut','hexplorer reverse mut','The HEXplorer score for the reverse complement of the mutant sequence. HZEI scores were normalized by the total number of nucleotide positions which contribute to the score.','float','1.0','2022-06-30','Splicing'),(44,'hexplorer_rev_wt','hexplorer reverse wt','The HEXplorer score for the reverse complement of the reference sequence. HZEI scores were normalized by the total number of nucleotide positions which contribute to the score.','float','1.0','2022-06-30','Splicing'),(45,'max_hbond','max HBond','The HBond delta score (max HBond mutant - max HBond wildtype). This score shows the change in binding affinity of the U1 snRNA to the splice site motiv, i. e. its ability to form hbonds with the sequence motiv. Negative values show that the mutant sequence is less probable to bind the U1 snRNA (This is a \"worse\" binding site). Positive values mean that the mutant sequence is more likely to bind the U1 snRNA. If there are multiple possible splice sites only the max values are considered.','float','1.0','2022-06-30','Splicing'),(46,'max_hbond_mut','max HBond mut','The max HBond score for the mutant sequence. ','float','1.0','2022-06-30','Splicing'),(47,'max_hbond_wt','max HBond wt','This is the max HBond score for the reference sequence.','float','1.0','2022-06-30','Splicing'),(48,'max_hbond_rev','max HBond reverse','The max HBond delta score for the reverse complement of the original sequence (HZEI mutant rev - HZEI wildtype rev). This score shows the change in binding affinity of the U1 snRNA to the splice site motiv, i. e. its ability to form hbonds with the sequence motiv. Negative values show that the mutant sequence is less probable to bind the U1 snRNA (This is a \"worse\" binding site). Positive values mean that the mutant sequence is more likely to bind the U1 snRNA. If there are multiple possible splice sites only the max values are considered.','float','1.0','2022-06-30','Splicing'),(49,'max_hbond_rev_mut','max HBond reverse mut','This is the max HBond score for the reverse complement of the mutant sequence.','float','1.0','2022-06-30','Splicing'),(50,'max_hbond_rev_wt','max HBond reverse wt','This is the max HBond score for the reverse complement of the reference sequence.','float','1.0','2022-06-30','Splicing'),(51,'gnomad_popmax_AF','popmax AF','The allele frequency of the \"popmax\" population','float','v3.1.2','2021-10-22','gnomAD'),(52,'hci_prior','HCI prior','The prior probability of pathogenicity as reported in the priors HCI website. These range from 0.97 for variants with high probability to damage a donor or acceptor to 0.02 for exonic variants that do not impact a splice junction and are unlikely to create a de novo donor.','float',1,'2022-11-15','Pathogenicity');
UNLOCK TABLES;



--
-- Dumping data for table `task_force_protein_domains`
--

LOCK TABLES `task_force_protein_domains` WRITE;
INSERT INTO `task_force_protein_domains` VALUES (1,'chr11',108229263,108229283,'Substrate binding','BWRL'),
	(2,'chr11',108249020,108249031,'NLS','BWRL'),
	(3,'chr11',108282785,108282847,'Leucine zipper','BWRL'),
	(4,'chr11',108288984,108289013,'Proline rich','BWRL'),
	(5,'chr11',108307899,108365505,'FATKIN','BWRL'),
	(6,'chr2',214792346,214809449,'RING','PMID: 32726901'),
	(7,'chr2',214752552,214780595,'ANK','PMID: 32726901'),
	(8,'chr2',214728709,214745830,'BRCT Domains','PMID: 32726901'),
	(9,'chr17',43104260,43124096,'RING','BWRL/ENIGMA'),
	(10,'chr17',41256889,43104928,'NES','BWRL/ENIGMA'),
	(11,'chr17',41246024,41246041,'NLS1','BWRL/ENIGMA'),
	(12,'chr17',41245706,41245729,'NLS2','BWRL/ENIGMA'),
	(13,'chr17',41245580,41245597,'NLS3','BWRL/ENIGMA'),
	(14,'chr17',41234506,41242975,'COILED-COIL','BWRL/ENIGMA'),
	(15,'chr17',41197698,41222983,'BRCT DOMAINS','BWRL/ENIGMA'),
	(16,'chr13',32316488,32319129,'PALB2 Binding','BWRL/ENIGMA'),
	(17,'chr13',32337362,32340601,'Interaction with RAD51 (BRC-1 bis BRC-8)','Uniprot'),
	(18,'chr13',32354901,32357757,'Interaction with FANCD2','Uniprot'),
	(19,'chr13',32356433,32396954,'DBD (DNA/DSS1 binding domain- helical OB1, OB2, OB3)','BWRL/ENIGMA'),
	(20,'chr13',32363246,32363296,'Nuclear export signal; masked by interaction with SEM1','Uniprot'),
	(21,'chr13',32298300,32398506,'C-terminal RAD51 binding domain (inkl. NLS1 und BRC-) ','BWRL/ENIGMA'),
	(22,'chr17',61686080,61861539,'ATPase/Helicase domain','PMID: 33619228'),
	(23,'chr17',61683857,61686079,'BRCA1 Interaction','PMID: 33619228'),
	(24,'chr1',68737416,68833496,'Bisher bekannten pathogenen CDH1-Varianten sind über den gesamten Locus verteilt und es kann daher keine klinisch relevante funktionelle Proteindomäne definiert werden.','BWRL'),
	(25,'chr22',28734515,28734667,'SQ/TQ-rich','BWRL'),
	(26,'chr22',28719463,28734448,'FHA','BWRL'),
	(27,'chr22',28689174,28719444,'Kinase','BWRL'),
	(28,'chr22',28687915,28687986,'NLS','BWRL'),
	(29,'chr16',23637932,23641133,'BRCA1 interaction domain','BWRL'),
	(30,'chr16',23635827,23641157,'DNA binding and Interaction with BRCA1','https://pubmed.ncbi.nlm.nih.gov/19369211/'),
	(31,'chr16',23635994,23636245,'RAD51 binding site','BWRL'),
	(32,'chr16',23634863,23635432,'DNA binding site','BWRL'),
	(33,'chr16',23629862,23630323,'MRG15 (MORF4L1) interaction domain','BWRL'),
	(34,'chr16',23603462,23629233,'WD40 repeat','BWRL'),
	(35,'chr17',58692644,58694983,'N-terminal region','BWRL'),
	(36,'chr17',58695020,58734219,'ATPase domain and RAD51B, XRCC3, and RAD51D binding','BWRL'),
	(37,'chr17',58734187,58734201,'Nuclear localization signal','BWRL'),
	(38,'chr17',35118515,35119613,'N-terminal region','BWRL https://www.sciencedirect.com/science/article/abs/pii/S1357272510003924'),
	(39,'chr17',35118530,35118586,'Linker','BWRL'),
	(40,'chr17',35101282,35107416,'ATPase domain and RAD51B, RAD51C, and XRCC2 binding','BWRL (PMID 10749867, 14704354, 19327148)'),
	(41,'chr17',7676204,7676594,'Transcription activation (TAD1+TAD2)','https://pubmed.ncbi.nlm.nih.gov/27145840/'),
	(42,'chr17',7676087,7676188,'Proline rich domain','BWRL'),
	(43,'chr17',7673744,7676065,'DNA binding region ','BWRL'),
	(44,'chr17',7673559,7673719,'NLS ','https://pubmed.ncbi.nlm.nih.gov/10321742/'),
	(45,'chr17',7670641,7673555,'Oligomerization region','BWRL'),
	(46,'chr17',7669612,7670643,'CTD (repression of DNA-binding region)','https://pubmed.ncbi.nlm.nih.gov/27145840/'),
	(47,'chr3',36993548,37020439,'N-terminal domain (MutSa interaction)','Insight Richtlinien und PMID: 26249686'),
	(48,'chr3',36993605,37007051,'ATPase domain','Insight Richtlinien und PMID: 26249686'),
	(49,'chr3',37025826,37048570,'EXO1 interaction','Insight Richtlinien und PMID: 28765196'),
	(50,'chr3',37028848,37050611,'PMS2/MLH3/PMS1 interaction','Insight Richtlinien und PMID: 28765196'),
	(51,'chr3',37026003,37028808,'NLS ','Insight Richtlinien und PMID: 28765196'),
	(52,'chr3',37047540,37047572,'NES1','Insight Richtlinien'),
	(53,'chr3',37048568,37048609,'NES2','Insight Richtlinien'),
	(54,'chr2',47403192,47410099,'DNA mismatch binding domain','Insight Richtlinien und PMID: 23391514'),
	(55,'chr2',47410100,47414367,'Connector domain','Insight Richtlinien und PMID: 28765196'),
	(56,'chr2',47410337,47412443,'MutLa interaction','Insight Richtlinien'),
	(57,'chr2',47414374,47445639,'Lever domain','Insight Richtlinien und PMID: 28765196'),
	(58,'chr2',47466807,47475122,'Lever domain','Insight Richtlinien und PMID: 28765196'),
	(59,'chr2',47445640,47466806,'Clamp domain','Insight Richtlinien und PMID: 28765196 PMID: 28765196'),
	(60,'chr2',47475123,47482946,'ATPase and  Helix-Turn-Helix','Insight Richtinien und PMID: 23391514;PMID: 28765196'),
	(61,'chr2',47429797,47475140,'MSH6/MSH3 interaction','Insight Richtlinien und PMID: 28765196'),
	(62,'chr2',47463061,47476419,'MutLa interaction','InSiGHT Richtlinien'),
	(63,'chr2',47480860,47482946,'MSH6/MSH3 interaction','Insight Richtlinien und PMID: 28765196'),
	(64,'chr2',47414272,47476374,'EXO1 stabilisation and interaction','InSiGHT Richtlinien und PMID: 28765196 PMID: 28765196'),
	(65,'chr2',47783243,47783266,'PCNA binding domain','PMID: 23391514; PMID: 28765196; InSiGHT-Richtlinien'),
	(66,'chr2',47790931,47796018,'PWWP domain','PMID: 23391514; PMID: 28765196; InSiGHT-Richtlinien'),
	(67,'chr2',47799067,47799540,'DNA mismatch /MMR binding domain','PMID: 23391514;PMID: 28765196'),
	(68,'chr2',47799499,47800134,'Connector domain','Insight Richtlinien;PMID: 23391514; PMID: 28765196'),
	(69,'chr2',47800135,47800785,'Lever domain','PMID: 23391514; PMID: 28765196'),
	(70,'chr2',47801008,47803472,'Lever domain','PMID: 23391514; PMID: 28765196'),
	(71,'chr2',47800786,47801007,'Clamp domain','PMID: 23391514; PMID: 28765196'),
	(72,'chr2',47803473,47806857,'ATPase/ATP binding','Insight und PMID: 23391514; PMID: 28765196'),
	(73,'chr2',47806554,47806857,'MSH2 interaction','Insight Richtlinien'),
	(74,'chr7',5969849,6009019,'ATPase/ATP binding','InSiGHT Richtlinien'),
	(75,'chr7',5973423,5982975,'Dimerisation/MLH1 interaction','P54278 (P54278) - protein - InterPro (ebi.ac.uk); PMID: 28765196; InSiGHT-Richtlinien'),
	(76,'chr7',5982853,5982906,'Exonuclease active site','PMID: 28765196'),
	(77,'chr7',5986869,5986892,'NLS ','Insight Richtlinien'),
	(78,'chr19',1207076,1207102,'Nucleotide binding ATP','STK11 - Serine/threonine-protein kinase STK11 precursor - Homo sapiens (Human) - STK11 gene & protein (uniprot.org)'),
	(79,'chr19',1207058,1222991,'Protein kinase domain','STK11 - Serine/threonine-protein kinase STK11 precursor - Homo sapiens (Human) - STK11 gene & protein (uniprot.org)'),
	(80,'chr19',1207046,1207183,'SIRT1 interaction','STK11 - Serine/threonine-protein kinase STK11 precursor - Homo sapiens (Human) - STK11 gene & protein (uniprot.org)'),
	(81,'chr10',87864470,87864511,'N-terminal phosphatidylinositol (Ptdlnsf4, 5) P2-binding domain (PBD)','PMID: 24656806, PMID: 34140896'),
	(82,'chr10',87864512,87952177,'phosphatase domain','PMID: 24656806, PMID: 34140896'),
	(83,'chr10',87952178,87965310,'C2 lipid or membrane-binding domain','PMID: 24656806, PMID: 34140896'),
	(84,'chr10',87965311,87965469,'carboxy-terminal tail','PMID: 24656806, PMID: 34140896'),
	(85,'chr10',87965461,87965469,'class I PDZ-binding (PDZ-BD) motif','PMID: 24656806, PMID: 34140896');
UNLOCK TABLES;

--
-- Add data for schemes
--

LOCK TABLES `classification_scheme` WRITE;
INSERT INTO `classification_scheme` VALUES 
	(1,'none','No scheme','none','#'),
	(2,'acmg_standard','ACMG standard','acmg','https://pubmed.ncbi.nlm.nih.gov/25741868/'),
	(3,'acmg_TP53','ACMG gene specific: TP53','acmg','https://pubmed.ncbi.nlm.nih.gov/33300245/'),
	(4,'acmg_CDH1','ACMG gene specific: CDH1','acmg','https://pubmed.ncbi.nlm.nih.gov/30311375/'),
	(5,'task-force','VUS-task-force standard','task-force','#'),
	(6,'task-force-brca','VUS-task-force gene specific: BRCA1/2','task-force','#');
UNLOCK TABLES;


LOCK TABLES `classification_criterium` WRITE;
INSERT INTO `classification_criterium` VALUES (1,2,'pvs1','Null variant (nonsense, frameshift, canonical +/-1 or 2 splice sites, initiation  codon, single or multi-exon deletion) in a gene where loss of function (LOF)  is a known mechanism of disease \n\n Caveats: \n - Beware of genes where LOF is not a known disease mechanism (e.g. GFAP, MYH7) \n - Use caution interpreting LOF variants at the extreme 3\' end of a gene \n - Use caution with splice variants that are predicted to lead to exon skipping but leave the remainder of the protein intact \n - Use caution in the presence of multiple transcripts',1),(2,2,'ps1','Same amino acid change as a previously established pathogenic variant  regardless of nucleotide change. \n\n Example: Val->Leu caused by either G>C or G>T in the same codon \n Caveat:	Beware of changes that impact splicing rather than at the amino acid/protein level',1),(3,2,'ps2','De novo (both maternity and paternity confirmed) in a patient with the  disease and no family history. \n \n Note: Confirmation of paternity only is insufficient. Egg donation, surrogate  motherhood, errors in embryo transfer, etc. can contribute to non-maternity.',1),(4,2,'ps3','Well-established in vitro or in vivo functional studies supportive of a  damaging effect on the gene or gene product. \n\n Note: Functional studies that have been validated and shown to be  reproducible and robust in a clinical diagnostic laboratory setting are  considered the most well-established.',1),(5,2,'ps4','The prevalence of the variant in affected individuals is significantly  increased compared to the prevalence in controls. \n\n Note 1: Relative risk (RR) or odds ratio (OR), as obtained from case-control  studies, is >5.0 and the confidence interval around the estimate of RR or OR  does not include 1.0. See manuscript for detailed guidance. \n\n Note 2: In instances of very rare variants where case-control studies may  not reach statistical significance, the prior observation of the variant in  multiple unrelated patients with the same phenotype, and its absence in  controls, may be used as moderate level of evidence.',1),(6,2,'pm1','Located in a mutational hot spot and/or critical and well-established  functional domain (e.g. active site of an enzyme) without benign variation.',1),(7,2,'pm2','Absent from controls (or at extremely low frequency if recessive) in Exome Sequencing Project, 1000 Genomes or ExAC. \n\n Caveat: Population data for indels may be poorly called by next generation  sequencing.',1),(8,2,'pm3','For recessive disorders, detected in trans with a pathogenic variant. \n\n  Note: This requires testing of parents (or offspring) to determine phase.',1),(9,2,'pm4','Protein length changes due to in-frame deletions/insertions in a non-repeat  region or stop-loss variants.',1),(10,2,'pm5','Novel missense change at an amino acid residue where a different  missense change determined to be pathogenic has been seen before. \n\n  Example: Arg156His is pathogenic; now you observe Arg156Cys. \n Caveat: Beware of changes that impact splicing rather than at the amino  acid/protein level.',1),(11,2,'pm6','Assumed de novo, but without confirmation of paternity and maternity.',1),(12,2,'pp1','Co-segregation with disease in multiple affected family members in a gene  definitively known to cause the disease. \n\n Note: May be used as stronger evidence with increasing segregation data.',1),(13,2,'pp2','Missense variant in a gene that has a low rate of benign missense variation  and where missense variants are a common mechanism of disease.',1),(14,2,'pp3','Multiple lines of computational evidence support a deleterious effect on  the gene or gene product (conservation, evolutionary, splicing impact, etc). \n\n Caveat: As many in silico algorithms use the same or very similar input for  their predictions, each algorithm should not be counted as an independent  criterion. PP3 can be used only once in any evaluation of a variant.',1),(15,2,'pp4','Patient\'s phenotype or family history is highly specific for a disease with a  single genetic etiology.',1),(16,2,'pp5','Reputable source recently reports variant as pathogenic but the evidence is  not available to the laboratory to perform an independent evaluation.',1),(17,2,'ba1','Allele frequency is above 5% in Exome Sequencing Project, 1000 Genomes,  or ExAC.',1),(18,2,'bs1','Allele frequency is greater than expected for disorder.',1),(19,2,'bs2','Observed in a healthy adult individual for a recessive (homozygous),  dominant (heterozygous), or X-linked (hemizygous) disorder with full  penetrance expected at an early age.',1),(20,2,'bs3','Well-established in vitro or in vivo functional studies shows no damaging  effect on protein function or splicing.',1),(21,2,'bs4','Lack of segregation in affected members of a family. \n\n Caveat: The presence of phenocopies for common phenotypes (i.e. cancer,  epilepsy) can mimic lack of segregation among affected individuals. Also,  families may have more than one pathogenic variant contributing to an  autosomal dominant disorder, further confounding an apparent lack of  segregation.',1),(22,2,'bp1','Missense variant in a gene for which primarily truncating variants are  known to cause disease',1),(23,2,'bp2','Observed in trans with a pathogenic variant for a fully penetrant dominant  gene/disorder; or observed in cis with a pathogenic variant in any  inheritance pattern.',1),(24,2,'bp3','In-frame deletions/insertions in a repetitive region without a known  function',1),(25,2,'bp4','Multiple lines of computational evidence suggest no impact on gene or  gene product (conservation, evolutionary, splicing impact, etc) \n\n Caveat: As many in silico algorithms use the same or very similar input for  their predictions, each algorithm cannot be counted as an independent  criterion. BP4 can be used only once in any evaluation of a variant.',1),(26,2,'bp5','Variant found in a case with an alternate molecular basis for disease.',1),(27,2,'bp6','Reputable source recently reports variant as benign but the evidence is not  available to the laboratory to perform an independent evaluation.',1),(28,2,'bp7','A synonymous (silent) variant for which splicing prediction algorithms  predict no impact to the splice consensus sequence nor the creation of a  new splice site AND the nucleotide is not highly conserved.',1),(29,3,'pvs1','Null variant (nonsense, frameshift, canonical ±1 or 2 splice sites, initiation codon, single or multiexon deletion) in a gene where LOF is a known mechanism of disease \n\n Use SVI-approved decision tree to determine the strength of this criterion (refer to Abou Tayoun et al. for more details).',1),(30,3,'ps1','Same amino acid change as a previously established pathogenic variant  regardless of nucleotide change. \n\n Use original description with the following additions: \n PS1: \n - Must confirm there is no difference in splicing using RNA data. \n - Can only be used to compare to variants classified as Pathogenic or Likely Pathogenic by the  TP53 VCEP (see ClinVar for VCEP classifications). \n\n PS1_Moderate: \n - Must confirm there is no difference in splicing using a metapredictor. \n - Can only be used to compare to variants classified as Pathogenic or Likely Pathogenic by the TP53 VCEP (see ClinVar).',1),(31,3,'ps2','De novo (both maternity and paternity confirmed) in a patient with the  disease and no family history. \n\n Use SVI-approved scoring system to determine the strength of this criterion  (refer to Table 2 from original publication: PMC8374922 (linked above) for more details)',1),(32,3,'ps3','Well-established in vitro or in vivo functional studies supportive of a  damaging effect on the gene or gene product. \n\n The following additions have been made by the TP53 ACMG specification: \n - PS3: transactivation assays in yeast demonstrate a low functioning allele  (≤20% activity) AND there is evidence of dominant negative effect and loss-of-function  OR there is a second assay showing low function (colony formation assays, apoptosis assays,  tetramer assays, knock-in mouse models and growth suppression assays).\n\n - PS3_Moderate: transactivation assays in yeast demonstrate a partially  functioning allele (>20% and ≤75% activity) AND there is evidence of dominant  negative effect and loss-of-function OR there is a second assay showing low function  (colony formation assays, apoptosis assays, tetramer assays, knock-in mouse models and  growth suppression assays).\n\n - PS3_Moderate: there is no data available from transactivation assays in yeast BUT  there is evidence of dominant negative effect and loss-of-function AND there is a second  assay showing low function (colony formation assays, apoptosis assays, tetramer assays,  knock-in mouse models and growth suppression assays).\n\n ==> Refer to Figure 1 from original publication: PMC8374922 (linked above) for more details.',1),(33,3,'ps4','The prevalence of the variant in affected individuals is significantly  increased compared to the prevalence in controls. \n\n Use SVI-approved scoring system to determine the strength of this criterion  (refer to Table 3 from original publication: PMC8374922 (linked above) for more details).  This criterion cannot be applied when a variant also meets BA1 or BS1. Refrain from considering  probands who have another pathogenic variant(s) in a highly penetrant cancer gene(s) that is a  logical cause for presentation. \n\n Caveat: \n Please be mindful of the risk of clonal hematopoieses of indeterminate potential with TP53 variants  (Coffee et al., 2017; Weitzel et al., 2017). One should take care to ensure that probands have  germline and not mosaic somatic TP53 variants.',1),(34,3,'pm1','Located in a mutational hot spot and/or critical and well-established  functional domain (e.g. active site of an enzyme) without benign variation. \n\n Located in a mutational hotspot defined as: \n - Variants within the following codons on protein NP_000537.3: 175, 273, 245, 248, 282, 249. \n - Variants seen in cancerhotspots.org (v2) with >10 somatic occurrences (recommendation from the ClinGen  Germline/Somatic Variant Curation Subcommittee).',1),(35,3,'pm2','Absent from controls (or at extremely low frequency if recessive) in Exome Sequencing Project, 1000 Genomes or ExAC. \n\n Caveat: Population data for indels may be poorly called by next generation  sequencing. \n\n PM2_Supporting: absent from population databases (gnomAD (most up-to-date non-cancer dataset) is the  preferred population database at this time http:#gnomad.broadinstitute.org).',1),(36,3,'pm3','Excluded.',0),(37,3,'pm4','Excluded.',0),(38,3,'pm5','Novel missense change at an amino acid residue where a different  missense change determined to be pathogenic has been seen before. \n\n  Example: Arg156His is pathogenic; now you observe Arg156Cys. \n\n PM5: novel missense change at an amino acid residue where at least two other different missense changes  determined to be pathogenic by the TP53 VCEP have been seen before.  PM5_Supporting: novel missense change at an amino acid residue where a different missense  change determined to be pathogenic by the TP53 VCEP has been seen before. \n\n Both criteria require the following additions: \n - Grantham should be used to compare the variants, and the variant being evaluated must have  equal to or higher score than the observed pathogenic variants. \n - Splicing should be ruled out using a metapredictor. \n - This criterion cannot be applied when a variant also meets PM1.',1),(39,3,'pm6','Assumed de novo, but without confirmation of paternity and maternity. \n\n Use SVI-approved scoring system to determine the strength of this criterion (refer to Table 2 from original  publication: PMC8374922 (linked above) for more details).',1),(40,3,'pp1','Co-segregation with disease in multiple affected family members in a gene  definitively known to cause the disease. \n\n PP1: co-segregation with disease is observed in 3–4 meioses in one family. \n PP1_Moderate: co-segregation with disease is observed in 5–6 meioses in one family. \n PP1_Strong: co-segregation with disease is observed >7 meioses in >1 family.',1),(41,3,'pp2','Excluded.',0),(42,3,'pp3','Multiple lines of computational evidence support a deleterious effect on  the gene or gene product (conservation, evolutionary, splicing impact, etc). \n\n Caveat: As many in silico algorithms use the same or very similar input for  their predictions, each algorithm should not be counted as an independent  criterion. PP3 can be used only once in any evaluation of a variant. \n\n PP3: Use original description with the following additions: \n - For missense variants, use a combination of BayesDel (≥0.16) and optimised Align-GVGD (C55-C25). \n - For splicing variants, use a metapredictor. \n\n PP3_Moderate: for missense variants, use a combination of BayesDel (≥0.16) and optimized Align-GVGD (C65).',1),(43,3,'pp4','Excluded.',0),(44,3,'pp5','Excluded.',0),(45,3,'ba1','Allele frequency is above 5% in Exome Sequencing Project, 1000 Genomes,  or ExAC.\n\n Allele frequency is ≥0.1% in a non-founder population with a minimum of five alleles  (gnomAD (most up-to-date non-cancer dataset)) is the preferred population database  at this time http:#gnomad.broadinstitute.org).',1),(46,3,'bs1','Allele frequency is greater than expected for disorder. \n\n Allele frequency is ≥0.03% and <0.1% in a non-founder population with a minimum of five alleles  (gnomAD (most up-to-date non-cancer dataset) is the preferred population database at this time  http:#gnomad.broadinstitute.org).',1),(47,3,'bs2','Observed in a healthy adult individual for a recessive (homozygous),  dominant (heterozygous), or X-linked (hemizygous) disorder with full  penetrance expected at an early age.\n\n BS2: observed in a single dataset in ≥8 females, who have reached at least 60 years of age without cancer  (i.e. cancer diagnoses after age 60 are ignored). \n\n BS2_Supporting: observed in a single dataset in 2–7 females, who have reached at least 60 years of age without cancer. \n\n Caveat: Be mindful of the risk of clonal hematopoiesis of indeterminate potential with TP53 variants (Coffee et al., 2017; Weitzel et al., 2017).  Individuals with mosaic somatic TP53 variants should not be included as evidence for BS2.',1),(48,3,'bs3','Well-established in vitro or in vivo functional studies shows no damaging  effect on protein function or splicing. \n\n - BS3: transactivation assays in yeast demonstrate a functional allele or super-transactivation  (>75% activity) AND there is no evidence of dominant negative effect and loss-of-function OR  there is a second assay showing retained function (colony formation assays, apoptosis assays,  tetramer assays, knock-in mouse models and growth suppression assays). \n\n - BS3_Supporting: transactivation assays in yeast demonstrate a partially functioning allele  (>20% and ≤75% activity) AND there is no evidence of dominant negative effect and loss-of-function  OR there is a second assay showing retained function (colony formation assays, apoptosis assays,  tetramer assays, knock-in mouse models and growth suppression assays). \n\n - BS3_Supporting: there is no data available from transactivation assays in yeast BUT there is no  evidence of dominant negative effect and loss-of-function AND there is a second assay showing  retained function (colony formation assays, apoptosis assays, tetramer assays, knock-in mouse  models and growth suppression assays). \n\n ==> Refer to Figure 1 from original publication: PMC8374922 (linked above) for more details.',1),(49,3,'bs4','Lack of segregation in affected members of a family. \n\n The variant segregates to opposite side of the family meeting LFS criteria, or the variant is  present in >3 living unaffected individuals (at least two of three should be female) above 55 years of age.',1),(50,3,'bp1','Excluded',0),(51,3,'bp2','Observed in trans with a pathogenic variant for a fully penetrant dominant  gene/disorder; or observed in cis with a pathogenic variant in any  inheritance pattern. \n\n Variant is observed in trans with a TP53 pathogenic variant (phase confirmed),  or there are three or more observations with a TP53 pathogenic variant when phase is unknown (at least two different  TP53 pathogenic variants). The other observed pathogenic variants must have been classified using  the TP53-specific guidelines.',1),(52,3,'bp3','Excluded',0),(53,3,'bp4','Multiple lines of computational evidence suggest no impact on gene or  gene product (conservation, evolutionary, splicing impact, etc) \n\n Caveat: As many in silico algorithms use the same or very similar input for  their predictions, each algorithm cannot be counted as an independent  criterion. BP4 can be used only once in any evaluation of a variant. \n\n Same rule description with the following additions: \n - For missense variants, use a combination of BayesDel (<0.16) and optimized Align-GVGD (C15-C0). \n - For splicing variants, use a metapredictor.',1),(54,3,'bp5','Excluded',0),(55,3,'bp6','Excluded',0),(56,3,'bp7','A synonymous (silent) variant for which splicing prediction algorithms  predict no impact to the splice consensus sequence nor the creation of a  new splice site AND the nucleotide is not highly conserved. \n\n Same description with the following additions: \n - Splicing should be ruled out using a metapredictor. \n - If a new alternate site is predicted, compare strength to native site in interpretation.',1),(57,4,'pvs1','Null variant (nonsense, frameshift, canonical ±1 or 2 splice sites, initiation codon, single or multiexon deletion) in a gene where LOF is a known mechanism of disease \n\n - Very strong: Per ClinGen SVI guidelines with the exception of canonical splice sites \n - Strong: Per ClinGen SVI guidelines. Use the strong strength of evidence for canonical splice sites. \n caveat: \n CDH1 exonic deletions or tandem duplications of in-frame exon truncations in NMD-resistant  zone located upstream the most 3\' well characterized pathogenic variant c.2506G>T (p.Glu836Ter).  Use moderate strength if premature stop is downstream of this variant \n  - Moderate: Per ClinGen SVI guidelines. \n caveats: \n  1. G to non-G variants disrupting the last nucleotide of an exon \n 2. Canonical splice sites located in exons demonstrated experimentally to result in in-frame partial skipping/insertion (e.g., Exon 3 donor site)  - Supporting: Per ClinGen SVI guidelines. \n\n Additional comment: \n  RNA analysis is recommended for splicing alterations, and if the RNA evidence does not support the prediction, the strength should be updated  PP3 cannot be applied for canonical splice sites',1),(58,4,'ps1','Same amino acid change as a previously established pathogenic variant  regardless of nucleotide change. \n\n Example:	Val->Leu caused by either G>C or G>T in the same codon \n Caveat:	Beware of changes that impact splicing rather than at the amino acid/protein level \n\n Additional comment: \n Variant must not impact splicing.',1),(59,4,'ps2','De novo (both maternity and paternity confirmed) in a patient with the  disease and no family history. \n \n Strength specifications: \n - Very strong: ≥2 patients with DGC and/or LBC w/parental confirmation  - Strong: 1 patient with DGC and/or LBC w/parental confirmation \n Additional comment: \n Use ClinGen\'s de novo point system for a highly specific phenotype (see Table S2 from  original publication linked at the top of the page)',1),(60,4,'ps3','Well-established in vitro or in vivo functional studies supportive of a  damaging effect on the gene or gene product. \n\n Strength specifications: \n - Strong: RNA assay demonstrating abnormal out-of-frame transcripts \n - Supporting: RNA assay demonstrating abnormal in-frame transcripts \n Additional comment: \n This rule can only be applied to demonstrate splicing defects.',1),(61,4,'ps4','The prevalence of the variant in affected individuals is significantly  increased compared to the prevalence in controls. \n\n Strength specifications: \n - Very strong: 16 families meet HDGC criteria \n - Strong: 4 families meet HDGC criteria \n - Moderate: 2 families meet HDGC criteria \n - Supporting: 1 family meets HDGC criteria \n\n Additional comment: \n This rule assumes 30% penetrance in individuals with pathogenic variants. For example,  if the variant in observed in 3 families, at least one of those families need to meet  criteria for HDGC in order to apply this rule. PS4 cannot be applied to variants that meet BS1 or BA1',1),(62,4,'pm1','Excluded.',0),(63,4,'pm2','Absent from controls (or at extremely low frequency if recessive) in Exome Sequencing Project, 1000 Genomes or ExAC. \n\n <1/100,000 alleles in gnomAD cohort; if present in ≥2 individuals, must be present in  <1/50,000 alleles within a sub-population \n\n Additional comment: \n Use gnomAD to determine allele frequency. Beware of technical limitations that  can inaccurately represent allele frequency in this population database',1),(64,4,'pm3','Excluded',0),(65,4,'pm4','Protein length changes due to in-frame deletions/insertions in a non-repeat  region or stop-loss variants. \n\n Additional comment: \n No rule specification proposed. Variant example - CDH1 c.2647T>C (p.Ter883Glnext*29)',1),(66,4,'pm5','Excluded',0),(67,4,'pm6','Assumed de novo, but without confirmation of paternity and maternity. \n\n Strength specification: \n - Very strong: ≥4 patients with DGC and/or LBC w/o parental confirmation \n - Strong: ≥2 patients with DGC and/or LBC w/o parental confirmation \n - Moderate: 1 patient with DGC and/or LBC w/o parental confirmation \n\n Additional comment: \n Use ClinGen\'s de novo point system for a highly specific phenotype (See Table S2  of original publication linked at the top of this page)',1),(68,4,'pp1','Co-segregation with disease in multiple affected family members in a gene  definitively known to cause the disease. \n\n Strength specification: \n - Strong: ≥7 meioses across ≥2 families \n - Moderate: 5-6 meioses across ≥1 families \n - Supporting: 3-4 meioses across ≥1 families \n\n Additional comment: \n Based strength of rule code on number of meioses across one or more families.',1),(69,4,'pp2','Excluded',0),(70,4,'pp3','Multiple lines of computational evidence support a deleterious effect on  the gene or gene product (conservation, evolutionary, splicing impact, etc). \n\n Strength specification: \n - Moderate: Variants affecting the same splice site as a well-characterized variant with  similar or worse in silico/RNA predictions \n - Supporting: At least 3 in silico splicing predictors in agreement (.Human Splicing  Finder (HSF), Maximum Entropy (MaxEnt), Berkeley Drosophilia Genome Project (BDGP), or ESEfinder) \n\n Additional comment: \n Rule code is only for non-canonical splicing variants. Code also does not apply to last  nucleotide of exon 3 (c.387G). Do not use protein-based computational prediction models for missense variants',1),(71,4,'pp4','Use PS4 in place of PP4.',1),(72,4,'pp5','Excluded',0),(73,4,'ba1','Allele frequency is above 5% in Exome Sequencing Project, 1000 Genomes,  or ExAC. \n\n MAF cutoff of 0.2% \n\n Additional comment: \n 99.99% CI; subpopulation must have a minimum of 5 alleles present.',1),(74,4,'bs1','Allele frequency is greater than expected for disorder. \n\n Stand alone: MAF cutoff of 0.1% \n\n Additional comment: \n 99.99% CI; subpopulation must have a minimum of 5 alleles present',1),(75,4,'bs2','Observed in a healthy adult individual for a recessive (homozygous),  dominant (heterozygous), or X-linked (hemizygous) disorder with full  penetrance expected at an early age. \n\n Strength specification: \n - Strong: Variant seen in ≥10 individuals w/o DCG, SRC tumors, or LBC & whose families do not suggest HDGC \n - Supporting: Variant seen in ≥3 individuals w/o DCG, SRC tumors, or LBC & whose families do not suggest HDGC	',1),(76,4,'bs3','Well-established in vitro or in vivo functional studies shows no damaging  effect on protein function or splicing. \n Functional RNA studies demonstrating no impact on transcript composition. \n\n Additional comment: \n This rule can only be used to demonstrate lack of splicing and can be downgraded based on quality of data.',1),(77,4,'bs4','Lack of segregation in affected members of a family. \n\n Caveat: The presence of phenocopies for common phenotypes (i.e. cancer,  epilepsy) can mimic lack of segregation among affected individuals. Also,  families may have more than one pathogenic variant contributing to an  autosomal dominant disorder, further confounding an apparent lack of  segregation. \n\n Additional comment: \n Beware of the presence of phenocopies (e.g., breast cancer) that can  mimic lack of segregation. Also, families may have more than one pathogenic  variant contributing to another AD disorder',1),(78,4,'bp1','Excluded',0),(79,4,'bp2','Observed in trans with a pathogenic variant for a fully penetrant dominant  gene/disorder; or observed in cis with a pathogenic variant in any  inheritance pattern. \n\n Strength specifications: \n - Strong: Variant observed in trans w/known pathogenic variant (phase confirmed)  OR observed in the homozygous state in individual w/o personal &/or family  history of DGC, LBC, or SRC tumors \n - Supporting: Variant is observed in cis (or phase is unknown) w/ a pathogenic variant \n\n Additional comment: \n Evidence code is dependent on strength of data. Take consideration of quality of  sequencing data when applying code. Note that code requires knowledge of individuals\' phenotype. Therefore, data from population databases should only be used when phenotypic  info is available.',1),(80,4,'bp3','Excluded',0),(81,4,'bp4','Multiple lines of computational evidence suggest no impact on gene or  gene product (conservation, evolutionary, splicing impact, etc) \n\n Splicing predictions only. At least 3 in silico splicing predictors in agreement  (Human Splicing Finder (HSF), Maximum Entropy (MaxEnt), Berkeley Drosophilia  Genome Project (BDGP), or ESEfinder) \n\n Additional comment: \n This rule can only be used when splicing predictions models suggest no  impact on protein. Do not use protein based computational prediction models  for missense. variants',1),(82,4,'bp5','Variant found in a case with an alternate molecular basis for disease. \n\n Additional comment: \n This applies if a P/LP variant is identified in an alternate gene known to cause HDGC (e.g., CTNNA1)',1),(83,4,'bp6','Excluded',0),(84,4,'bp7','A synonymous (silent) variant for which splicing prediction algorithms  predict no impact to the splice consensus sequence nor the creation of a  new splice site AND the nucleotide is not highly conserved. \n\n Synonymous variants where nucleotide is not highly conserved; variant is  the reference nucleotide in 1 primate and/or >3 mammal species \n\n Additional comment: \n Note the CDH1 rule specification does not require a benign in silico splice prediction.  This allows use with BP4, as appropriate, to classify variants meeting both criteria as likely benign ',1),(85,5,'1.1','Allele frequency ≥ 1 % (MAF ≥ 0.01) in large populations like Caucasians, Africans or Asians. \n\n CAVE: Allele freuqency ≥ 1 % in subpopulations with low mixed gene pool (e. g. Finnish populations, Foundermutations)  does NOT suffice this criterium.',1),(86,5,'1.2','Variants with a multifactorial calculated pobability of < 0,001 (< 0,1 %) to be pathogenic. \n\n CAVE: Currently only applicable to BRCA1/2.',1),(87,5,'1.3','Variants in high risk genes which occur in at least 10 individuals within suitable groups of non-diseased individuals (e. g. FLOSSIES).',1),(88,5,'2.1','Allele frequency between 0.5 and 1 % (MAF 0.005–0,01) in large populations like Caucasians, Africans or Asians. \n\n CAVE: Allele freuqency between 0.5 and 1 % in subpopulations with low mixed gene pool (e. g. Finnish populations, Foundermutations)  does NOT suffice this criterium.',1),(89,5,'2.2','Either exonic variants (A), which lead to the substitution of an amino acid  (missense variants), or small in-frame insertions/  deletions, which lead to insertions/deletions of one or  amino acid(s) and whose a priori probability for pathogenicity is  for pathogenicity is ≤ 2% (A-GVGD analysis,  http:#priors.hci.utah.edu/PRIORS/), and (B) synonymous  variants, if these variants (A, B) are likely to be pathogenic according to bioinformatic  prediction programs the splicing result with a high probability and (A) are outside the relevant and (A) are located outside of the relevant functional domains defined by the VUS task-force (see tables A5.1–5.9 from the original proposal linked at the top of this page). For the non-BRCA1/2 genes, the above variants must be In large populations with an allele frequency of. 0.001 ≤ MAF < 0.01 (0.1-1%).',1),(90,5,'2.3','Synonymous substitutions or intronic variants, which  do not contain mRNA aberrations in the form of exon deletions/  duplications or monoallelic expression of the wild-type  transcript in RNA analyses. This applies even if they are likely to alter the splice-result  according to bioinformatic prediction programs (for programs and thresholds, see Appendix A1  of the original proposal liked at the top of this page).',1),(91,5,'2.4','Variants that occur in the same gene with a clearly pathogenic  variant in trans (co-occurrence). It must be confirmed that a homozygous  or compound heterozygous genotype is associated with a known clinically distinct  phenotype.',1),(92,5,'2.5','Variants with a multifactorial calculated probability to be pathogenic of 0.001-0.049. \n\n CAVE: Does only apply to BRCA1/2.',1),(93,5,'2.6','Exonic variants which cause an amino acid change equal to a known class 1 variant, but  encode a different nucleotide change. Additionally, the variant must not show a conspicious splice prediction.',1),(94,5,'2.7','Missense variants which have information from functional analyses (or similar). These, however, do not suffice for  a multifactorial classification. Additionally, the variant was previously classified by expert panels like  ENIGMA or the ClinGen-expert-group as class 2',1),(95,5,'2.8','Suitable functional analyses do not show a loss of function or functional relevance. Additionally there must not  be contradictory data. \n\n Comment: The suitable functional analyses are dependent on the gene of the variant.',1),(96,5,'2.9','Paired LOH-analyses in blood or tumor samples show a loss of the allele which contains the variant under consideration.  This was proven among tumor tissue (BC or OC).',1),(97,5,'2.10','Variants within genes of intermediate risk without hints to potential function loss. These variants must also occour  in at least 20 individuals of suitable non-diseased cohorts (e. g. FLOSSIES) \n\n CAVE: Exceptions are possible in case of frequent foundermutations (e. g. CHEK2, c.1100del).',1),(98,5,'3.1','A special case in which the criteria clearly state a certain classification. However, the variant is listed among  the special cases of the genes or other exceptions occur (see table 5 of the original proposal linked at the top of the page)',1),(99,5,'3.2','Variants with controversial data with regards to its classification.',1),(100,5,'3.3','Variants which can be found within -20 to +3 bp and -3 to +8 bp from an exon/intron border. This applies only if  there is no in-vitro mRNA analysis and criteria 4.3, 4.4 or 2.6 do not apply.',1),(101,5,'3.4','Exon duplications without additional analyses (e. g. cDNA analyses, break-point analyses, ...)',1),(102,5,'3.5','Variants with a multifaktorial calculated pathogenicity probability between 0.05 and 0.949. \n\n CAVE: This criterium only applies to BRCA1/2 variants.',1),(103,5,'4.1','Variants with a multifaktorial calculated pathogenicity probability between 0.95 and 0.99. \n\n CAVE: This criterium only applies to BRCA1/2 variants.',1),(104,5,'4.2','Variants which encode an early stop of the protein synthesis (nonsense- or frameshift variants). In addition,  variants must not cause damage to known clinical relevant functional protein domains as long as the induced stop  codon is found approximately 50 bp upstream from the last exon-exon-junction. \n\n Comment: If there is at least one exon-exon-junction complex downstream of the new, early stop codon, the early one  would be able to recruit the Upf1 and, thus, induce nonsense-mediated decay (NMD))',1),(105,5,'4.3','Intronic variants at position ± 1,2 or a G to A/T or C change at the last position of the exon. Apply this criterium if there is  a positive splice prediction and there is no mRNA analysis. \n\n CAVE: Applies to BRCA1/2 variants at the last position of the exon only if the first 6 bases within the intron are not equal to \"GTRRGT\". \n\n Exceptions: \n - A cryptic spice site (AG/GT) is activated by the variant and the (predicted) new exon yields in-frame splicing --> class 3 \n - A transcript with (predicted) skipped exon(s) exists as a relevant alternatively spliced transcipt --> class 3 \n - The (predicted) skipped exon(s) is spliced in-frame and does not contain known functional domains --> class 3',1),(106,5,'4.4','Variants which cause the same amino acid change as a known class 5 pathogenic missence variant, but is characterized by another nucleotide change.  Also, it is required that there is no prediction of abberant splicing.',1),(107,5,'4.5','In-frame deletions which cause the loss of a class 5 missence variant and which disrupt or cause the loss of funcionally important protein domains.',1),(108,5,'4.6','In-frame insertions which were verified via in-vitro mRNA analyses, that disrupt functionally important protein domains.',1),(109,5,'4.7','Variants which cause a change in the tranlation initiation codon (AUG, Methionin). Additionally, there must not be evidence  (e. g. close alternative start-codon) for an alternative classification.',1),(110,5,'4.8','Variants which do have information from functional analyses, clinical data, or other evidence that do, however, not suffice for a multifactorial classification and which were classified as class 4 by expert panels like ENIGMA or ClinGen.',1),(111,5,'4.9','Variants which have functional analyses that depict loss of function or another functional relevance and which do not have contradictory information.',1),(112,5,'5.1','Nonsense- or frameshift variants which induce an early stop codon. This stop codon prevents the expression of known relevant functional protein domains.',1),(113,5,'5.2','Variants with a multifactorial calculated probability to be pathogenic of more than 0.99. \n\n CAVE: Only applies to BRCA1/2.',1),(114,5,'5.3','Splice variants which were shown to induce a frame shift that causes an early stop of the proteinbiosynthesis and, thus, prevents the expression of known relevant functional protein domains. This was proven via in-vitro mRNA analyses. It is also important that NO wildtype transcript of the mutated allele is detectable (monoallelic expression).',1),(115,5,'5.4','Splice variants in which an invitro mRNA analysis has detected an in-frame deletion/insertion that leads to the  interruption or loss of a known clinically relevant domain or to a change in the protein structure which functionally inactivates the protein. It is also important that NO wildtype transcript of the mutated allele is detectable (monoallelic expression).',1),(116,5,'5.5','Copy number deletions which cause the disruption or loss of (an) exon(s) which contain clinically relevant functional domain(s)  or which cause a predicted inactivation of known clinically relevant functional domains due to a frame shift.',1),(117,5,'5.6','Copy number duplications of any size which were proven (with lab-analyses) to duplicate one or multiple  exons that cause a frame shift and, thus, inactivate known clinically relevant functional protein domains.',1),(118,6,'1.1','Allele frequency ≥ 1 % (MAF ≥ 0.01) in large populations like Caucasians, Africans or Asians. \n\n CAVE: Allele freuqency ≥ 1 % in subpopulations with low mixed gene pool (e. g. Finnish populations, Foundermutations)  does NOT suffice this criterium.',1),(119,6,'1.2','Variants with a multifactorial calculated pobability of < 0,001 (< 0,1 %) to be pathogenic. \n\n CAVE: Currently only applicable to BRCA1/2.',1),(120,6,'1.3','Variants in high risk genes which occur in at least 10 individuals within suitable groups of non-diseased individuals (e. g. FLOSSIES).',1),(121,6,'2.1','Allele frequency between 0.5 and 1 % (MAF 0.005–0,01) in large populations like Caucasians, Africans or Asians. \n\n CAVE: Allele freuqency between 0.5 and 1 % in subpopulations with low mixed gene pool (e. g. Finnish populations, Foundermutations)  does NOT suffice this criterium.',1),(122,6,'2.2','Either exonic variants (A), which lead to the substitution of an amino acid  (missense variants), or small in-frame insertions/  deletions, which lead to insertions/deletions of one or  amino acid(s) and whose a priori probability for pathogenicity is  for pathogenicity is ≤ 2% (A-GVGD analysis,  http:#priors.hci.utah.edu/PRIORS/), and (B) synonymous  variants, if these variants (A, B) are likely to be pathogenic according to bioinformatic  prediction programs the splicing result with a high probability and (A) are outside the relevant and (A) are located outside of the relevant functional domains defined by the VUS task-force (see tables A5.1–5.9 from the original proposal linked at the top of this page). For the non-BRCA1/2 genes, the above variants must be In large populations with an allele frequency of. 0.001 ≤ MAF < 0.01 (0.1-1%).',1),(123,6,'2.3','Synonymous substitutions or intronic variants, which  do not contain mRNA aberrations in the form of exon deletions/  duplications or monoallelic expression of the wild-type  transcript in RNA analyses. This applies even if they are likely to alter the splice-result  according to bioinformatic prediction programs (for programs and thresholds, see Appendix A1  of the original proposal liked at the top of this page).',1),(124,6,'2.4','Variants that occur in the same gene with a clearly pathogenic  variant in trans (co-occurrence). It must be confirmed that a homozygous  or compound heterozygous genotype is associated with a known clinically distinct  phenotype.',1),(125,6,'2.5','Variants with a multifactorial calculated probability to be pathogenic of 0.001-0.049. \n\n CAVE: Does only apply to BRCA1/2.',1),(126,6,'2.6','Exonic variants which cause an amino acid change equal to a known class 1 variant, but  encode a different nucleotide change. Additionally, the variant must not show a conspicious splice prediction.',1),(127,6,'2.7','Missense variants which have information from functional analyses (or similar). These, however, do not suffice for  a multifactorial classification. Additionally, the variant was previously classified by expert panels like  ENIGMA or the ClinGen-expert-group as class 2',1),(128,6,'2.8','Suitable functional analyses do not show a loss of function or functional relevance. Additionally there must not  be contradictory data. \n\n Comment: The suitable functional analyses are dependent on the gene of the variant.',1),(129,6,'2.9','Paired LOH-analyses in blood or tumor samples show a loss of the allele which contains the variant under consideration.  This was proven among tumor tissue (BC or OC).',1),(130,6,'2.10','Variants within genes of intermediate risk without hints to potential function loss. These variants must also occour  in at least 20 individuals of suitable non-diseased cohorts (e. g. FLOSSIES) \n\n CAVE: Exceptions are possible in case of frequent foundermutations (e. g. CHEK2, c.1100del).',1),(131,6,'3.1','A special case in which the criteria clearly state a certain classification. However, the variant is listed among  the special cases of the genes or other exceptions occur (see table 5 of the original proposal linked at the top of the page)',1),(132,6,'3.2','Variants with controversial data with regards to its classification.',1),(133,6,'3.3','Variants which can be found within -20 to +3 bp and -3 to +8 bp from an exon/intron border. This applies only if  there is no in-vitro mRNA analysis and criteria 4.3, 4.4 or 2.6 do not apply.',1),(134,6,'3.4','Exon duplications without additional analyses (e. g. cDNA analyses, break-point analyses, ...)',1),(135,6,'3.5','Variants with a multifaktorial calculated pathogenicity probability between 0.05 and 0.949. \n\n CAVE: This criterium only applies to BRCA1/2 variants.',1),(136,6,'4.1','Variants with a multifaktorial calculated pathogenicity probability between 0.95 and 0.99. \n\n CAVE: This criterium only applies to BRCA1/2 variants.',1),(137,6,'4.2','Variants which encode an early stop of the protein synthesis (nonsense- or frameshift variants). In addition,  variants must not cause damage to known clinical relevant functional protein domains as long as the induced stop  codon is found approximately 50 bp upstream from the last exon-exon-junction. \n\n Comment: If there is at least one exon-exon-junction complex downstream of the new, early stop codon, the early one  would be able to recruit the Upf1 and, thus, induce nonsense-mediated decay (NMD))',1),(138,6,'4.3','Intronic variants at position ± 1,2 or a G to A/T or C change at the last position of the exon. Apply this criterium if there is  a positive splice prediction and there is no mRNA analysis. \n\n CAVE: Applies to BRCA1/2 variants at the last position of the exon only if the first 6 bases within the intron are not equal to \"GTRRGT\". \n\n Exceptions: \n - A cryptic spice site (AG/GT) is activated by the variant and the (predicted) new exon yields in-frame splicing --> class 3 \n - A transcript with (predicted) skipped exon(s) exists as a relevant alternatively spliced transcipt --> class 3 \n - The (predicted) skipped exon(s) is spliced in-frame and does not contain known functional domains --> class 3',1),(139,6,'4.4','Variants which cause the same amino acid change as a known class 5 pathogenic missence variant, but is characterized by another nucleotide change.  Also, it is required that there is no prediction of abberant splicing.',1),(140,6,'4.5','In-frame deletions which cause the loss of a class 5 missence variant and which disrupt or cause the loss of funcionally important protein domains.',1),(141,6,'4.6','In-frame insertions which were verified via in-vitro mRNA analyses, that disrupt functionally important protein domains.',1),(142,6,'4.7','Variants which cause a change in the tranlation initiation codon (AUG, Methionin). Additionally, there must not be evidence  (e. g. close alternative start-codon) for an alternative classification.',1),(143,6,'4.8','Variants which do have information from functional analyses, clinical data, or other evidence that do, however, not suffice for a multifactorial classification and which were classified as class 4 by expert panels like ENIGMA or ClinGen.',1),(144,6,'4.9','Variants which have functional analyses that depict loss of function or another functional relevance and which do not have contradictory information.',1),(145,6,'5.1','Nonsense- or frameshift variants which induce an early stop codon. This stop codon prevents the expression of known relevant functional protein domains.',1),(146,6,'5.2','Variants with a multifactorial calculated probability to be pathogenic of more than 0.99. \n\n CAVE: Only applies to BRCA1/2.',1),(147,6,'5.3','Splice variants which were shown to induce a frame shift that causes an early stop of the proteinbiosynthesis and, thus, prevents the expression of known relevant functional protein domains. This was proven via in-vitro mRNA analyses. It is also important that NO wildtype transcript of the mutated allele is detectable (monoallelic expression).',1),(148,6,'5.4','Splice variants in which an invitro mRNA analysis has detected an in-frame deletion/insertion that leads to the  interruption or loss of a known clinically relevant domain or to a change in the protein structure which functionally inactivates the protein. It is also important that NO wildtype transcript of the mutated allele is detectable (monoallelic expression).',1),(149,6,'5.5','Copy number deletions which cause the disruption or loss of (an) exon(s) which contain clinically relevant functional domain(s)  or which cause a predicted inactivation of known clinically relevant functional domains due to a frame shift.',1),(150,6,'5.6','Copy number duplications of any size which were proven (with lab-analyses) to duplicate one or multiple  exons that cause a frame shift and, thus, inactivate known clinically relevant functional protein domains.',1);
UNLOCK TABLES;

LOCK TABLES `classification_criterium_strength` WRITE;
INSERT INTO `classification_criterium_strength` VALUES 
	(1,1,'pvs','very strong pathogenic',1),
	(2,2,'ps','strong pathogenic',1),
	(3,2,'pvs','very strong pathogenic',0),
	(4,2,'pm','medium pathogenic',0),
	(5,2,'pp','supporting pathogenic',0),
	(6,3,'ps','strong pathogenic',1),
	(7,4,'ps','strong pathogenic',1),
	(8,5,'ps','strong pathogenic',1),
	(9,6,'pm','medium pathogenic',1),
	(10,7,'pm','medium pathogenic',1),
	(11,8,'pm','medium pathogenic',1),
	(12,9,'pm','medium pathogenic',1),
	(13,10,'pm','medium pathogenic',1),
	(14,11,'pm','medium pathogenic',1),
	(15,12,'pp','supporting pathogenic',1),
	(16,12,'pvs','very strong pathogenic',0),
	(17,12,'ps','strong pathogenic',0),
	(18,12,'pm','medium pathogenic',0),
	(19,13,'pp','supporting pathogenic',1),
	(20,14,'pp','supporting pathogenic',1),
	(21,15,'pp','supporting pathogenic',1),
	(22,16,'pp','supporting pathogenic',1),
	(23,17,'ba','stand-alone benign',1),
	(24,18,'bs','strong benign',1),
	(25,18,'ba','stand-alone benign',0),
	(26,18,'bp','supporting benign',0),
	(27,19,'bs','strong benign',1),
	(28,20,'bs','strong benign',1),
	(29,21,'bs','strong benign',1),
	(30,22,'bp','supporting benign',1),
	(31,22,'ba','stand-alone benign',0),
	(32,22,'bs','strong benign',0),
	(33,23,'bp','supporting benign',1),
	(34,24,'bp','supporting benign',1),
	(35,25,'bp','supporting benign',1),
	(36,26,'bp','supporting benign',1),
	(37,27,'bp','supporting benign',1),
	(38,28,'bp','supporting benign',1),
	(39,29,'pvs','very strong pathogenic',1),
	(40,30,'ps','strong pathogenic',1),
	(41,30,'pvs','very strong pathogenic',0),
	(42,30,'pm','medium pathogenic',0),
	(43,30,'pp','supporting pathogenic',0),
	(44,31,'ps','strong pathogenic',1),
	(45,32,'ps','strong pathogenic',1),
	(46,33,'ps','strong pathogenic',1),
	(47,34,'pm','medium pathogenic',1),
	(48,35,'pm','medium pathogenic',1),
	(49,36,'pm','medium pathogenic',1),
	(50,37,'pm','medium pathogenic',1),
	(51,38,'pm','medium pathogenic',1),
	(52,39,'pm','medium pathogenic',1),
	(53,40,'pp','supporting pathogenic',1),
	(54,40,'pvs','very strong pathogenic',0),
	(55,40,'ps','strong pathogenic',0),
	(56,40,'pm','medium pathogenic',0),
	(57,41,'pp','supporting pathogenic',1),
	(58,42,'pp','supporting pathogenic',1),
	(59,43,'pp','supporting pathogenic',1),
	(60,44,'pp','supporting pathogenic',1),
	(61,45,'ba','stand-alone benign',1),
	(62,46,'bs','strong benign',1),
	(63,46,'ba','stand-alone benign',0),
	(64,46,'bp','supporting benign',0),
	(65,47,'bs','strong benign',1),
	(66,48,'bs','strong benign',1),
	(67,49,'bs','strong benign',1),
	(68,50,'bp','supporting benign',1),
	(69,50,'ba','stand-alone benign',0),
	(70,50,'bs','strong benign',0),
	(71,51,'bp','supporting benign',1),
	(72,52,'bp','supporting benign',1),
	(73,53,'bp','supporting benign',1),
	(74,54,'bp','supporting benign',1),
	(75,55,'bp','supporting benign',1),
	(76,56,'bp','supporting benign',1),
	(77,57,'pvs','very strong pathogenic',1),
	(78,58,'ps','strong pathogenic',1),
	(79,58,'pvs','very strong pathogenic',0),
	(80,58,'pm','medium pathogenic',0),
	(81,58,'pp','supporting pathogenic',0),
	(82,59,'ps','strong pathogenic',1),
	(83,60,'ps','strong pathogenic',1),
	(84,61,'ps','strong pathogenic',1),
	(85,62,'pm','medium pathogenic',1),
	(86,63,'pm','medium pathogenic',1),
	(87,64,'pm','medium pathogenic',1),
	(88,65,'pm','medium pathogenic',1),
	(89,66,'pm','medium pathogenic',1),
	(90,67,'pm','medium pathogenic',1),
	(91,68,'pp','supporting pathogenic',1),
	(92,68,'pvs','very strong pathogenic',0),
	(93,68,'ps','strong pathogenic',0),
	(94,68,'pm','medium pathogenic',0),
	(95,69,'pp','supporting pathogenic',1),
	(96,70,'pp','supporting pathogenic',1),
	(97,71,'pp','supporting pathogenic',1),
	(98,72,'pp','supporting pathogenic',1),
	(99,73,'ba','stand-alone benign',1),
	(100,74,'bs','strong benign',0),
	(101,74,'ba','stand-alone benign',1),
	(102,74,'bp','supporting benign',0),
	(103,75,'bs','strong benign',1),
	(104,76,'bs','strong benign',1),
	(105,77,'bs','strong benign',1),
	(106,78,'bp','supporting benign',1),
	(107,78,'ba','stand-alone benign',0),
	(108,78,'bs','strong benign',0),
	(109,79,'bp','supporting benign',1),
	(110,80,'bp','supporting benign',1),
	(111,81,'bp','supporting benign',1),
	(112,82,'bp','supporting benign',1),
	(113,83,'bp','supporting benign',1),
	(114,84,'bp','supporting benign',1),
	(115,85,'pp','supporting pathogenic',1),
	(116,86,'pp','supporting pathogenic',1),
	(117,87,'pp','supporting pathogenic',1),
	(118,88,'pm','medium pathogenic',1),
	(119,89,'pm','medium pathogenic',1),
	(120,90,'pm','medium pathogenic',1),
	(121,91,'pm','medium pathogenic',1),
	(122,92,'pm','medium pathogenic',1),
	(123,93,'pm','medium pathogenic',1),
	(124,94,'pm','medium pathogenic',1),
	(125,95,'pm','medium pathogenic',1),
	(126,96,'pm','medium pathogenic',1),
	(127,97,'pm','medium pathogenic',1),
	(128,98,'bp','supporting benign',1),
	(129,99,'bp','supporting benign',1),
	(130,100,'bp','supporting benign',1),
	(131,101,'bp','supporting benign',1),
	(132,102,'bp','supporting benign',1),
	(133,103,'ps','strong pathogenic',1),
	(134,104,'ps','strong pathogenic',1),
	(135,105,'ps','strong pathogenic',1),
	(136,106,'ps','strong pathogenic',1),
	(137,107,'ps','strong pathogenic',1),
	(138,108,'ps','strong pathogenic',1),
	(139,109,'ps','strong pathogenic',1),
	(140,110,'ps','strong pathogenic',1),
	(141,111,'ps','strong pathogenic',1),
	(142,112,'pvs','very strong pathogenic',1),
	(143,113,'pvs','very strong pathogenic',1),
	(144,114,'pvs','very strong pathogenic',1),
	(145,115,'pvs','very strong pathogenic',1),
	(146,116,'pvs','very strong pathogenic',1),
	(147,117,'pvs','very strong pathogenic',1),
	(148,118,'pp','supporting pathogenic',1),
	(149,119,'pp','supporting pathogenic',1),
	(150,120,'pp','supporting pathogenic',1),
	(151,121,'pm','medium pathogenic',1),
	(152,122,'pm','medium pathogenic',1),
	(153,123,'pm','medium pathogenic',1),
	(154,124,'pm','medium pathogenic',1),
	(155,125,'pm','medium pathogenic',1),
	(156,126,'pm','medium pathogenic',1),
	(157,127,'pm','medium pathogenic',1),
	(158,128,'pm','medium pathogenic',1),
	(159,129,'pm','medium pathogenic',1),
	(160,130,'pm','medium pathogenic',1),
	(161,131,'bp','supporting benign',1),
	(162,132,'bp','supporting benign',1),
	(163,133,'bp','supporting benign',1),
	(164,134,'bp','supporting benign',1),
	(165,135,'bp','supporting benign',1),
	(166,136,'ps','strong pathogenic',1),
	(167,137,'ps','strong pathogenic',1),
	(168,138,'ps','strong pathogenic',1),
	(169,139,'ps','strong pathogenic',1),
	(170,140,'ps','strong pathogenic',1),
	(171,141,'ps','strong pathogenic',1),
	(172,142,'ps','strong pathogenic',1),
	(173,143,'ps','strong pathogenic',1),
	(174,144,'ps','strong pathogenic',1),
	(175,145,'pvs','very strong pathogenic',1),
	(176,146,'pvs','very strong pathogenic',1),
	(177,147,'pvs','very strong pathogenic',1),
	(178,148,'pvs','very strong pathogenic',1),
	(179,149,'pvs','very strong pathogenic',1),
	(180,150,'pvs','very strong pathogenic',1);
UNLOCK TABLES;



LOCK TABLES `mutually_exclusive_criteria` WRITE;
INSERT INTO `mutually_exclusive_criteria` VALUES (1,12,21),(2,18,5),(3,21,12),(4,17,5),(5,40,49),(6,46,61),(7,49,40),(8,45,33),(9,74,61),(10,77,68),(11,73,61),(12,93,100),(13,105,100),(14,106,100),(15,126,133),(16,138,133);
UNLOCK TABLES;
	
--
-- Insert relevant genes
--

LOCK TABLES `gene` WRITE;
INSERT INTO `gene` VALUES 
	(2174,952,'BARD1','BRCA1 associated RING domain 1','protein-coding gene',601593,18430),
	(2566,1101,'BRCA2','BRCA2 DNA repair associated','protein-coding gene',600185,15378),
	(2564,1100,'BRCA1','BRCA1 DNA repair associated','protein-coding gene',113705,15377),
	(21914,20691,'NBR2','neighbor of BRCA1 lncRNA 2','non-coding RNA',618708,NULL),
	(42061,37116,'ZAR1L','zygote arrest 1 like','protein-coding gene',NULL,NULL),
	(11973,28242,'HPDL','4-hydroxyphenylpyruvate dioxygenase like','protein-coding gene',618994,30681),
	(21541,7527,'MUTYH','mutY DNA glycosylase','protein-coding gene',604933,16490),
	(13764, 16636,'KIF1B','kinesin family member 1B','protein-coding gene',605995,16304),
	(28804, 46747,'RN7SL731P','RNA, 7SL, cytoplasmic 731, pseudogene','pseudogene',NULL,NULL),
	(4183,1817,'CEACAM5','CEA cell adhesion molecule 5','protein-coding gene',114890,NULL),
	(1817,795,'ATM','ATM serine/threonine kinase','protein-coding gene',607585,15962),
	(38963,11998,'TP53','tumor protein p53','protein-coding gene',191170,15644);
UNLOCK TABLES;

--
-- Insert relevant gene aliases
--

LOCK TABLES `gene_alias` WRITE;
INSERT INTO `gene_alias` VALUES 
	(4430,2564,'RNF53'),
	(4432,2564,'PPP1R53'),
	(4433,2564,'FANCS'),
	(4440,2566,'XRCC11'),
	(4441,2566,'FANCD1'),
	(51290,38963,'p53'),
	(51291,38963,'LFS1');
UNLOCK TABLES;


--
-- Dumping data for table `variant`
--

LOCK TABLES `variant` WRITE;
INSERT INTO `variant` VALUES 
	(15,'chr2',214730440,'G','A',0,NULL,'chr2',214730440,'G','A'),
	(52,'chr13',32314943,'A','G',0,'dummy BRCA variant','chr13',32314943,'A','G'),
	(71,'chr17',43124032,'AAGATTTTCTGCAT','A',0,'ARUP BRCA classification example','chr17',43124032,'AAGATTTTCTGCAT','A'),
	(72,'chr17',7670685,'G','A',0,'dummy TP53 variant','chr17',7670685,'G','A'),
	(130,'chr1',45331755,'G','A',0,'variant with two mane select transcripts in consequences','chr1',45331755,'G','A'),
	(146,'chr11',108229267,'A','C',0,NULL,'chr11',108229267,'A','C'),
	(32,'chr13',32362509,'T','C',0,NULL,'chr1',32362509,'T','C'),
	(139,'chr1',10304277,'T','C',0,NULL,'chr1',10364335,'T','C'),
	(164,'chr14',39335204,'A','G',0,NULL,'chr14',39335204,'A','G'),
	(168,'chr17',43095845,'C','G',0,'dummy BRCA variant with prior','chr17',43095845,'C','G');
UNLOCK TABLES;


--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*The outdated information will be overwritten with the data stored in keycloak upon login of that person*/;
INSERT INTO `user` VALUES 
	(3,'superuser','outdated_first_name','outdated_last_name','outdated_affiliation'),
	(4,'norights','fn','ln','aff');
UNLOCK TABLES;


--
-- Dumping data for table `heredicare_center_classification`
--

LOCK TABLES `heredicare_center_classification` WRITE;
INSERT INTO `heredicare_center_classification` VALUES 
	(60,'5',139,'Uniklinik Tübingen','this is a test','1999-01-01'),
	(61,'5',139,'Hamburger Hähnchenfabrik','this is a test for the second classificatoin center','2020-05-01');
UNLOCK TABLES;




--
-- Dumping data for table `pfam_id_mapping`
--

LOCK TABLES `pfam_id_mapping` WRITE;
INSERT INTO `pfam_id_mapping` VALUES 
	(1711,'PF00028','Cadherin domain'),
	(9095,'PF00498','FHA domain'),
	(17449,'PF11640','Telomere-length maintenance and DNA damage repair'),
	(16,'PF20150','2EXR family'),
	(13575,'PF07710','P53 tetramerisation motif');
UNLOCK TABLES;


--
-- Dumping data for table `pfam_legacy`
--

LOCK TABLES `pfam_legacy` WRITE;
INSERT INTO `pfam_legacy` VALUES 
	(1,'PF11641','PF20150');
UNLOCK TABLES;


--
-- Dumping data for table `variant_consequence`
--

LOCK TABLES `variant_consequence` WRITE;
INSERT INTO `variant_consequence` VALUES 
	(838,15,'ENST00000260947','c.1972C>T','p.Arg658Cys','missense variant','moderate',10,NULL,2174,'ensembl',NULL,NULL),
	(839,15,'ENST00000421162','c.619C>T','p.Arg207Cys','missense variant','moderate',6,NULL,2174,'ensembl',NULL,NULL),
	(840,15,'ENST00000432456','c.70C>T','p.Arg24Cys','missense variant','moderate',1,NULL,2174,'ensembl',NULL,NULL),
	(841,15,'ENST00000455743','c.*1592C>T',NULL,'3 prime UTR variant & NMD transcript variant','modifier',9,NULL,2174,'ensembl',NULL,NULL),
	(842,15,'ENST00000471590','n.307C>T',NULL,'non coding transcript exon variant','modifier',2,NULL,2174,'ensembl',NULL,NULL),
	(843,15,'ENST00000613192','c.*35C>T',NULL,'3 prime UTR variant & NMD transcript variant','modifier',2,NULL,2174,'ensembl',NULL,NULL),
	(844,15,'ENST00000613374','c.562C>T','p.Arg188Cys','missense variant','moderate',5,NULL,2174,'ensembl',NULL,NULL),
	(845,15,'ENST00000613706','c.1564C>T','p.Arg522Cys','missense variant','moderate',10,NULL,2174,'ensembl',NULL,NULL),
	(846,15,'ENST00000617164','c.1915C>T','p.Arg639Cys','missense variant','moderate',9,NULL,2174,'ensembl',NULL,NULL),
	(847,15,'ENST00000619009','c.433C>T','p.Arg145Cys','missense variant','moderate',4,NULL,2174,'ensembl',NULL,NULL),
	(848,15,'ENST00000620057','c.*638C>T',NULL,'3 prime UTR variant','modifier',9,NULL,2174,'ensembl',NULL,NULL),
	(849,15,'ENST00000650978','c.*2050C>T',NULL,'3 prime UTR variant & NMD transcript variant','modifier',9,NULL,2174,'ensembl',NULL,NULL),
	(850,15,'ENSR00001044281',NULL,NULL,'regulatory region variant','modifier',NULL,NULL,NULL,'ensembl',NULL,NULL),
	(851,15,'NM_000465','c.1972C>T','p.Arg658Cys','missense variant','moderate',10,NULL,2174,'refseq',NULL,NULL),
	(852,15,'NM_001282543','c.1915C>T','p.Arg639Cys','missense variant','moderate',9,NULL,2174,'refseq',NULL,NULL),
	(853,15,'NM_001282545','c.619C>T','p.Arg207Cys','missense variant','moderate',6,NULL,2174,'refseq',NULL,NULL),
	(854,15,'NM_001282548','c.562C>T','p.Arg188Cys','missense variant','moderate',5,NULL,2174,'refseq',NULL,NULL),
	(855,15,'NM_001282549','c.433C>T','p.Arg145Cys','missense variant','moderate',4,NULL,2174,'refseq',NULL,NULL),
	(856,15,'NR_104212','n.1937C>T',NULL,'non coding transcript exon variant','modifier',9,NULL,2174,'refseq',NULL,NULL),
	(857,15,'NR_104215','n.1880C>T',NULL,'non coding transcript exon variant','modifier',8,NULL,2174,'refseq',NULL,NULL),
	(858,15,'NR_104216','n.1136C>T',NULL,'non coding transcript exon variant','modifier',9,NULL,2174,'refseq',NULL,NULL),
	(859,15,'XM_017004613','c.2071C>T','p.Arg691Cys','missense variant','moderate',11,NULL,2174,'refseq',NULL,NULL),
	(860,15,'XR_002959322','n.2162C>T',NULL,'non coding transcript exon variant','modifier',11,NULL,2174,'refseq',NULL,NULL),
	
	(885,71,'ENST00000352993','c.52_64del','p.Met18Ter','frameshift variant','high',2,NULL,2564,'ensembl',NULL,NULL),
	(886,71,'ENST00000354071','c.52_64del','p.Met18Ter','frameshift variant','high',2,NULL,2564,'ensembl',NULL,NULL),
	(887,71,'ENST00000356906',NULL,NULL,'upstream gene variant','modifier',NULL,NULL,21914,'ensembl',NULL,NULL),
	(888,71,'ENST00000357654','c.52_64del','p.Met18Ter','frameshift variant','high',2,NULL,2564,'ensembl',NULL,NULL),
	(889,71,'ENST00000460115',NULL,NULL,'upstream gene variant','modifier',NULL,NULL,21914,'ensembl',NULL,NULL),
	(890,71,'ENST00000461221','c.52_64del','p.Met18Ter','frameshift variant & NMD transcript variant','high',2,NULL,2564,'ensembl',NULL,NULL),
	(891,71,'ENST00000461798','c.52_64del','p.Met18Ter','frameshift variant & NMD transcript variant','high',2,NULL,2564,'ensembl',NULL,NULL),
	(892,71,'ENST00000467245',NULL,NULL,'upstream gene variant','modifier',NULL,NULL,21914,'ensembl',NULL,NULL),
	(893,71,'ENST00000468300','c.52_64del','p.Met18Ter','frameshift variant','high',2,NULL,2564,'ensembl',NULL,NULL),
	(894,71,'ENST00000470026','c.52_64del','p.Met18Ter','frameshift variant','high',2,NULL,2564,'ensembl',NULL,NULL),
	(895,71,'ENST00000471181','c.52_64del','p.Met18Ter','frameshift variant','high',2,NULL,2564,'ensembl',NULL,NULL),
	(896,71,'ENST00000476777','c.52_64del','p.Met18Ter','frameshift variant','high',2,NULL,2564,'ensembl',NULL,NULL),
	(897,71,'ENST00000477152','c.52_64del','p.Met18Ter','frameshift variant','high',2,NULL,2564,'ensembl',NULL,NULL),
	(898,71,'ENST00000478531','c.52_64del','p.Met18Ter','frameshift variant','high',2,NULL,2564,'ensembl',NULL,NULL),
	(899,71,'ENST00000489037','c.52_64del','p.Met18Ter','frameshift variant','high',2,NULL,2564,'ensembl',NULL,NULL),
	(900,71,'ENST00000491747','c.52_64del','p.Met18Ter','frameshift variant','high',2,NULL,2564,'ensembl',NULL,NULL),
	(901,71,'ENST00000492859','c.52_64del','p.Met18Ter','frameshift variant & NMD transcript variant','high',2,NULL,2564,'ensembl',NULL,NULL),
	(902,71,'ENST00000493795','c.-36_-24del',NULL,'5 prime UTR variant','modifier',2,NULL,2564,'ensembl',NULL,NULL),
	(903,71,'ENST00000493919','c.-36_-24del',NULL,'5 prime UTR variant','modifier',2,NULL,2564,'ensembl',NULL,NULL),
	(904,71,'ENST00000494123','c.52_64del','p.Met18Ter','frameshift variant','high',2,NULL,2564,'ensembl',NULL,NULL),
	(905,71,'ENST00000497488','c.-219+1226_-219+1238del',NULL,'intron variant','modifier',NULL,1,2564,'ensembl',NULL,NULL),
	(906,71,'ENST00000586385','c.4+1137_4+1149del',NULL,'intron variant','modifier',NULL,1,2564,'ensembl',NULL,NULL),
	(907,71,'ENST00000591534','c.-44+1226_-44+1238del',NULL,'intron variant','modifier',NULL,1,2564,'ensembl',NULL,NULL),
	(908,71,'ENST00000591849','c.-99+1226_-99+1238del',NULL,'intron variant','modifier',NULL,1,2564,'ensembl',NULL,NULL),
	(909,71,'ENST00000618469','c.52_64del','p.Met18Ter','frameshift variant','high',2,NULL,2564,'ensembl',NULL,NULL),
	(910,71,'ENST00000634433','c.52_64del','p.Met18Ter','frameshift variant','high',2,NULL,2564,'ensembl',NULL,NULL),
	(911,71,'ENST00000642945','c.52_64del','p.Met18Ter','frameshift variant & NMD transcript variant','high',2,NULL,2564,'ensembl',NULL,NULL),
	(912,71,'ENST00000644555','c.-235_-223del',NULL,'5 prime UTR variant','modifier',2,NULL,2564,'ensembl',NULL,NULL),
	(913,71,'ENST00000652672','c.-209_-197del',NULL,'5 prime UTR variant','modifier',2,NULL,2564,'ensembl',NULL,NULL),
	(914,71,'ENST00000657841',NULL,NULL,'upstream gene variant','modifier',NULL,NULL,21914,'ensembl',NULL,NULL),
	(915,71,'ENSR00000094515',NULL,NULL,'regulatory region variant','modifier',NULL,NULL,NULL,'ensembl',NULL,NULL),
	(916,71,'NM_007294','c.52_64del','p.Met18Ter','frameshift variant','high',2,NULL,2564,'refseq',NULL,NULL),
	(917,71,'NM_007297','c.-36_-24del',NULL,'5 prime UTR variant','modifier',2,NULL,2564,'refseq',NULL,NULL),
	(918,71,'NM_007298','c.52_64del','p.Met18Ter','frameshift variant','high',1,NULL,2564,'refseq',NULL,NULL),
	(919,71,'NM_007299','c.52_64del','p.Met18Ter','frameshift variant','high',2,NULL,2564,'refseq',NULL,NULL),
	(920,71,'NM_007300','c.52_64del','p.Met18Ter','frameshift variant','high',2,NULL,2564,'refseq',NULL,NULL),
	(921,71,'NR_003108',NULL,NULL,'upstream gene variant','modifier',NULL,NULL,21914,'refseq',NULL,NULL),
	(922,71,'NR_027676','n.254_266del',NULL,'non coding transcript exon variant','modifier',2,NULL,2564,'refseq',NULL,NULL),
	(923,71,'NR_138145',NULL,NULL,'upstream gene variant','modifier',NULL,NULL,21914,'refseq',NULL,NULL),

	(924,72,'ENST00000269305','c.1024C>T','p.Arg342Ter','stop gained','high',10,NULL,38963,'ensembl','PF07710','P53 tetramerisation motif'),
	(925,72,'ENST00000359597','c.993+2850C>T',NULL,'intron variant','modifier',NULL,8,38963,'ensembl',NULL,NULL),
	(926,72,'ENST00000413465','c.782+3496C>T',NULL,'intron variant','modifier',NULL,6,38963,'ensembl',NULL,NULL),
	(927,72,'ENST00000420246','c.*131C>T',NULL,'3 prime UTR variant','modifier',11,NULL,38963,'ensembl',NULL,NULL),
	(928,72,'ENST00000445888','c.1024C>T','p.Arg342Ter','stop gained','high',10,NULL,38963,'ensembl','PF07710','P53 tetramerisation motif'),
	(929,72,'ENST00000455263','c.*43C>T',NULL,'3 prime UTR variant','modifier',11,NULL,38963,'ensembl',NULL,NULL),
	(930,72,'ENST00000503591',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,38963,'ensembl',NULL,NULL),
	(931,72,'ENST00000504290','c.*43C>T',NULL,'3 prime UTR variant','modifier',7,NULL,38963,'ensembl',NULL,NULL),
	(932,72,'ENST00000504937','c.628C>T','p.Arg210Ter','stop gained','high',6,NULL,38963,'ensembl','PF07710','P53 tetramerisation motif'),
	(933,72,'ENST00000505014',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,38963,'ensembl',NULL,NULL),
	(934,72,'ENST00000508793',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,38963,'ensembl',NULL,NULL),
	(935,72,'ENST00000509690',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,38963,'ensembl',NULL,NULL),
	(936,72,'ENST00000510385','c.*131C>T',NULL,'3 prime UTR variant','modifier',7,NULL,38963,'ensembl',NULL,NULL),
	(937,72,'ENST00000514944',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,38963,'ensembl',NULL,NULL),
	(938,72,'ENST00000574684',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,38963,'ensembl',NULL,NULL),
	(939,72,'ENST00000576024','c.54-995C>T',NULL,'intron variant','modifier',NULL,1,38963,'ensembl',NULL,NULL),
	(940,72,'ENST00000604348',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,38963,'ensembl',NULL,NULL),
	(941,72,'ENST00000610292','c.907C>T','p.Arg303Ter','stop gained','high',9,NULL,38963,'ensembl','PF07710','P53 tetramerisation motif'),
	(942,72,'ENST00000610538','c.*43C>T',NULL,'3 prime UTR variant','modifier',11,NULL,38963,'ensembl',NULL,NULL),
	(943,72,'ENST00000610623','c.*43C>T',NULL,'3 prime UTR variant','modifier',7,NULL,38963,'ensembl',NULL,NULL),
	(944,72,'ENST00000618944','c.*131C>T',NULL,'3 prime UTR variant','modifier',7,NULL,38963,'ensembl',NULL,NULL),
	(945,72,'ENST00000619186','c.547C>T','p.Arg183Ter','stop gained','high',6,NULL,38963,'ensembl','PF07710','P53 tetramerisation motif'),
	(946,72,'ENST00000619485','c.907C>T','p.Arg303Ter','stop gained','high',10,NULL,38963,'ensembl','PF07710','P53 tetramerisation motif'),
	(947,72,'ENST00000620739','c.907C>T','p.Arg303Ter','stop gained','high',10,NULL,38963,'ensembl','PF07710','P53 tetramerisation motif'),
	(948,72,'ENST00000622645','c.*131C>T',NULL,'3 prime UTR variant','modifier',11,NULL,38963,'ensembl',NULL,NULL),
	(949,72,'ENST00000635293','c.907C>T','p.Arg303Ter','stop gained & NMD transcript variant','high',10,NULL,38963,'ensembl',NULL,NULL),
	(950,72,'NM_000546','c.1024C>T','p.Arg342Ter','stop gained','high',10,NULL,38963,'refseq',NULL,NULL),
	(951,72,'NM_001126112','c.1024C>T','p.Arg342Ter','stop gained','high',10,NULL,38963,'refseq',NULL,NULL),
	(952,72,'NM_001126113','c.*43C>T',NULL,'3 prime UTR variant','modifier',11,NULL,38963,'refseq',NULL,NULL),
	(953,72,'NM_001126114','c.*131C>T',NULL,'3 prime UTR variant','modifier',11,NULL,38963,'refseq',NULL,NULL),
	(954,72,'NM_001126115','c.628C>T','p.Arg210Ter','stop gained','high',6,NULL,38963,'refseq',NULL,NULL),
	(955,72,'NM_001126116','c.*131C>T',NULL,'3 prime UTR variant','modifier',7,NULL,38963,'refseq',NULL,NULL),
	(956,72,'NM_001126117','c.*43C>T',NULL,'3 prime UTR variant','modifier',7,NULL,38963,'refseq',NULL,NULL),
	(957,72,'NM_001126118','c.907C>T','p.Arg303Ter','stop gained','high',9,NULL,38963,'refseq',NULL,NULL),
	(958,72,'NM_001276695','c.*43C>T',NULL,'3 prime UTR variant','modifier',11,NULL,38963,'refseq',NULL,NULL),
	(959,72,'NM_001276696','c.*131C>T',NULL,'3 prime UTR variant','modifier',11,NULL,38963,'refseq',NULL,NULL),
	(960,72,'NM_001276697','c.547C>T','p.Arg183Ter','stop gained','high',6,NULL,38963,'refseq',NULL,NULL),
	(961,72,'NM_001276698','c.*131C>T',NULL,'3 prime UTR variant','modifier',7,NULL,38963,'refseq',NULL,NULL),
	(962,72,'NM_001276699','c.*43C>T',NULL,'3 prime UTR variant','modifier',7,NULL,38963,'refseq',NULL,NULL),
	(963,72,'NM_001276760','c.907C>T','p.Arg303Ter','stop gained','high',10,NULL,38963,'refseq',NULL,NULL),
	(964,72,'NM_001276761','c.907C>T','p.Arg303Ter','stop gained','high',10,NULL,38963,'refseq',NULL,NULL),

	(1228,130,'ENST00000334815','c.9866C>T',NULL,'downstream gene variant','modifier',NULL,NULL,11973,'ensembl',NULL,NULL),
	(1229,130,'ENST00000354383','c.1011C>T','p.Arg337%3D','synonymous variant','low',12,NULL,21541,'ensembl',NULL,NULL),
	(1230,130,'ENST00000355498','c.1008C>T','p.Arg336%3D','synonymous variant','low',12,NULL,21541,'ensembl',NULL,NULL),
	(1231,130,'ENST00000372098','c.1083C>T','p.Arg361%3D','synonymous variant','low',12,NULL,21541,'ensembl',NULL,NULL),
	(1232,130,'ENST00000372104','c.1008C>T','p.Arg336%3D','synonymous variant','low',13,NULL,21541,'ensembl',NULL,NULL),
	(1233,130,'ENST00000372110','c.1053C>T','p.Arg351%3D','synonymous variant','low',12,NULL,21541,'ensembl',NULL,NULL),
	(1234,130,'ENST00000372115','c.1050C>T','p.Arg350%3D','synonymous variant','low',12,NULL,21541,'ensembl',NULL,NULL),
	(1235,130,'ENST00000412971','c.624C>T','p.Arg208%3D','synonymous variant','low',7,NULL,21541,'ensembl',NULL,NULL),
	(1236,130,'ENST00000435155',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,21541,'ensembl',NULL,NULL),
	(1237,130,'ENST00000448481','c.1041C>T','p.Arg347%3D','synonymous variant','low',12,NULL,21541,'ensembl',NULL,NULL),
	(1238,130,'ENST00000450313',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,21541,'ensembl',NULL,NULL),
	(1239,130,'ENST00000456914','c.1008C>T','p.Arg336%3D','synonymous variant','low',12,NULL,21541,'ensembl',NULL,NULL),
	(1240,130,'ENST00000461495',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,21541,'ensembl',NULL,NULL),
	(1241,130,'ENST00000462387',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,21541,'ensembl',NULL,NULL),
	(1242,130,'ENST00000462388','n.872C>T',NULL,'non coding transcript exon variant','modifier',5,NULL,21541,'ensembl',NULL,NULL),
	(1243,130,'ENST00000466231',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,21541,'ensembl',NULL,NULL),
	(1244,130,'ENST00000467459','c.425C>T','p.Ala142Val','missense variant & NMD transcript variant','moderate',4,NULL,21541,'ensembl',NULL,NULL),
	(1245,130,'ENST00000467940',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,21541,'ensembl',NULL,NULL),
	(1246,130,'ENST00000470256',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,21541,'ensembl',NULL,NULL),
	(1247,130,'ENST00000474703',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,21541,'ensembl',NULL,NULL),
	(1248,130,'ENST00000475516','c.*821C>T',NULL,'3 prime UTR variant & NMD transcript variant','modifier',12,NULL,21541,'ensembl',NULL,NULL),
	(1249,130,'ENST00000476789',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,21541,'ensembl',NULL,NULL),
	(1250,130,'ENST00000478796',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,21541,'ensembl',NULL,NULL),
	(1251,130,'ENST00000479746',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,21541,'ensembl',NULL,NULL),
	(1252,130,'ENST00000481139',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,21541,'ensembl',NULL,NULL),
	(1253,130,'ENST00000481571','c.*821C>T',NULL,'3 prime UTR variant & NMD transcript variant','modifier',12,NULL,21541,'ensembl',NULL,NULL),
	(1254,130,'ENST00000482094','n.329C>T',NULL,'non coding transcript exon variant','modifier',1,NULL,21541,'ensembl',NULL,NULL),
	(1255,130,'ENST00000483127',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,21541,'ensembl',NULL,NULL),
	(1256,130,'ENST00000483642',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,21541,'ensembl',NULL,NULL),
	(1257,130,'ENST00000485271',NULL,NULL,'upstream gene variant','modifier',NULL,NULL,21541,'ensembl',NULL,NULL),
	(1258,130,'ENST00000485484',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,21541,'ensembl',NULL,NULL),
	(1259,130,'ENST00000488731','c.188-199C>T',NULL,'intron variant','modifier',NULL,3,21541,'ensembl',NULL,NULL),
	(1260,130,'ENST00000492494',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,21541,'ensembl',NULL,NULL),
	(1261,130,'ENST00000525160',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,21541,'ensembl',NULL,NULL),
	(1262,130,'ENST00000528013','c.1050C>T','p.Arg350%3D','synonymous variant','low',12,NULL,21541,'ensembl',NULL,NULL),
	(1263,130,'ENST00000529892','c.178-199C>T',NULL,'intron variant','modifier',NULL,2,21541,'ensembl',NULL,NULL),
	(1264,130,'ENST00000529984','c.188-199C>T',NULL,'intron variant','modifier',NULL,3,21541,'ensembl',NULL,NULL),
	(1265,130,'ENST00000531105','c.116-2318C>T',NULL,'intron variant','modifier',NULL,2,21541,'ensembl',NULL,NULL),
	(1266,130,'ENST00000533178','c.*337C>T',NULL,'3 prime UTR variant & NMD transcript variant','modifier',6,NULL,21541,'ensembl',NULL,NULL),
	(1267,130,'ENST00000534453',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,21541,'ensembl',NULL,NULL),
	(1268,130,'ENST00000671856',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,21541,'ensembl',NULL,NULL),
	(1269,130,'ENST00000671898','c.1596C>T','p.Arg532%3D','synonymous variant & NMD transcript variant','low',16,NULL,NULL,'ensembl',NULL,NULL),
	(1270,130,'ENST00000672011','c.*337C>T',NULL,'3 prime UTR variant & NMD transcript variant','modifier',11,NULL,21541,'ensembl',NULL,NULL),
	(1271,130,'ENST00000672314','c.1008C>T','p.Arg336%3D','synonymous variant','low',12,NULL,21541,'ensembl',NULL,NULL),
	(1272,130,'ENST00000672593','c.*1234C>T',NULL,'3 prime UTR variant & NMD transcript variant','modifier',9,NULL,21541,'ensembl',NULL,NULL),
	(1273,130,'ENST00000672764','c.*337C>T',NULL,'3 prime UTR variant & NMD transcript variant','modifier',11,NULL,21541,'ensembl',NULL,NULL),
	(1274,130,'ENST00000672818','c.1083C>T','p.Arg361%3D','synonymous variant','low',12,NULL,21541,'ensembl',NULL,NULL),
	(1275,130,'ENST00000673134','c.*705C>T',NULL,'3 prime UTR variant & NMD transcript variant','modifier',10,NULL,21541,'ensembl',NULL,NULL),
	(1276,130,'ENST00000674679',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,21541,'ensembl',NULL,NULL),
	(1277,130,'NM_001048171','c.1008C>T','p.Arg336%3D','synonymous variant','low',12,NULL,21541,'refseq',NULL,NULL),
	(1278,130,'NM_001048172','c.1011C>T','p.Arg337%3D','synonymous variant','low',12,NULL,21541,'refseq',NULL,NULL),
	(1279,130,'NM_001048173','c.1008C>T','p.Arg336%3D','synonymous variant','low',12,NULL,21541,'refseq',NULL,NULL),
	(1280,130,'NM_001048174','c.1008C>T','p.Arg336%3D','synonymous variant','low',12,NULL,21541,'refseq',NULL,NULL),
	(1281,130,'NM_001128425','c.1092C>T','p.Arg364%3D','synonymous variant','low',12,NULL,21541,'refseq',NULL,NULL),
	(1282,130,'NM_001293190','c.1053C>T','p.Arg351%3D','synonymous variant','low',12,NULL,21541,'refseq',NULL,NULL),
	(1283,130,'NM_001293191','c.1041C>T','p.Arg347%3D','synonymous variant','low',12,NULL,21541,'refseq',NULL,NULL),
	(1284,130,'NM_001293192','c.732C>T','p.Arg244%3D','synonymous variant','low',12,NULL,21541,'refseq',NULL,NULL),
	(1285,130,'NM_001293195','c.1008C>T','p.Arg336%3D','synonymous variant','low',13,NULL,21541,'refseq',NULL,NULL),
	(1286,130,'NM_001293196','c.732C>T','p.Arg244%3D','synonymous variant','low',12,NULL,21541,'refseq',NULL,NULL),
	(1287,130,'NM_001350650','c.663C>T','p.Arg221%3D','synonymous variant','low',11,NULL,21541,'refseq',NULL,NULL),
	(1288,130,'NM_001350651','c.663C>T','p.Arg221%3D','synonymous variant','low',11,NULL,21541,'refseq',NULL,NULL),
	(1289,130,'NM_012222','c.1083C>T','p.Arg361%3D','synonymous variant','low',12,NULL,21541,'refseq',NULL,NULL),
	(1290,130,'NM_032756',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,11973,'refseq',NULL,NULL),
	(1291,130,'NR_146882','n.1236C>T',NULL,'non coding transcript exon variant','modifier',12,NULL,21541,'refseq',NULL,NULL),
	(1292,130,'NR_146883','n.1085C>T',NULL,'non coding transcript exon variant','modifier',11,NULL,21541,'refseq',NULL,NULL),
	(1293,130,'XM_011541497','c.1068C>T','p.Arg356%3D','synonymous variant','low',12,NULL,21541,'refseq',NULL,NULL),
	(1294,130,'XM_011541498','c.1050C>T','p.Arg350%3D','synonymous variant','low',12,NULL,21541,'refseq',NULL,NULL),
	(1295,130,'XM_011541499','c.1050C>T','p.Arg350%3D','synonymous variant','low',12,NULL,21541,'refseq',NULL,NULL),
	(1296,130,'XM_011541500','c.1050C>T','p.Arg350%3D','synonymous variant','low',12,NULL,21541,'refseq',NULL,NULL),
	(1297,130,'XM_011541501','c.1050C>T','p.Arg350%3D','synonymous variant','low',13,NULL,21541,'refseq',NULL,NULL),
	(1298,130,'XM_011541502','c.1050C>T','p.Arg350%3D','synonymous variant','low',12,NULL,21541,'refseq',NULL,NULL),
	(1299,130,'XM_011541503','c.1050C>T','p.Arg350%3D','synonymous variant','low',11,NULL,21541,'refseq',NULL,NULL),
	(1300,130,'XM_011541504','c.1041C>T','p.Arg347%3D','synonymous variant','low',12,NULL,21541,'refseq',NULL,NULL),
	(1301,130,'XM_011541505','c.630C>T','p.Arg210%3D','synonymous variant','low',8,NULL,21541,'refseq',NULL,NULL),
	(1302,130,'XM_011541506','c.630C>T','p.Arg210%3D','synonymous variant','low',8,NULL,21541,'refseq',NULL,NULL),
	(1303,130,'XM_017001331','c.1050C>T','p.Arg350%3D','synonymous variant','low',12,NULL,21541,'refseq',NULL,NULL),
	(1304,130,'XM_017001332','c.1050C>T','p.Arg350%3D','synonymous variant','low',12,NULL,21541,'refseq',NULL,NULL),
	(1305,130,'XM_017001333','c.1050C>T','p.Arg350%3D','synonymous variant','low',12,NULL,21541,'refseq',NULL,NULL),
	(1306,130,'XM_017001334','c.1011C>T','p.Arg337%3D','synonymous variant','low',12,NULL,21541,'refseq',NULL,NULL),
	(1307,130,'XM_017001335','c.732C>T','p.Arg244%3D','synonymous variant','low',12,NULL,21541,'refseq',NULL,NULL),
	(1308,130,'XM_017001336','c.663C>T','p.Arg221%3D','synonymous variant','low',11,NULL,21541,'refseq',NULL,NULL),
	(1309,130,'XM_017001337','c.663C>T','p.Arg221%3D','synonymous variant','low',11,NULL,21541,'refseq',NULL,NULL),
	(1310,130,'XM_024447244','c.663C>T','p.Arg221%3D','synonymous variant','low',11,NULL,21541,'refseq',NULL,NULL),
	(1311,130,'XM_024447245','c.663C>T','p.Arg221%3D','synonymous variant','low',11,NULL,21541,'refseq',NULL,NULL),
	(1312,130,'XM_024447248','c.621C>T','p.Arg207%3D','synonymous variant','low',10,NULL,21541,'refseq',NULL,NULL),
	(1313,130,'XM_024447249','c.492C>T','p.Arg164%3D','synonymous variant','low',10,NULL,21541,'refseq',NULL,NULL),
	(1314,130,'XM_024447250','c.492C>T','p.Arg164%3D','synonymous variant','low',10,NULL,21541,'refseq',NULL,NULL),
	(1315,130,'XM_024447251','c.492C>T','p.Arg164%3D','synonymous variant','low',10,NULL,21541,'refseq',NULL,NULL),
	(1316,130,'XR_001737190','n.1053C>T',NULL,'non coding transcript exon variant','modifier',12,NULL,21541,'refseq',NULL,NULL),
	(1317,130,'XR_001737192','n.865C>T',NULL,'non coding transcript exon variant','modifier',10,NULL,21541,'refseq',NULL,NULL),
	(1318,130,'XR_002956643','n.1045C>T',NULL,'non coding transcript exon variant','modifier',10,NULL,21541,'refseq',NULL,NULL),
	(1319,130,'XR_002956644','n.1580C>T',NULL,'non coding transcript exon variant','modifier',9,NULL,21541,'refseq',NULL,NULL),
	(1320,130,'XR_946658','n.1153C>T',NULL,'non coding transcript exon variant','modifier',12,NULL,21541,'refseq',NULL,NULL),

	(2328,52,'ENST00000345108',NULL,NULL,'upstream gene variant','modifier',NULL,NULL,42061,'ensembl',NULL,NULL),
	(2329,52,'ENST00000380152',NULL,NULL,'upstream gene variant','modifier',NULL,NULL,2566,'ensembl',NULL,NULL),
	(2330,52,'ENST00000530893',NULL,NULL,'upstream gene variant','modifier',NULL,NULL,2566,'ensembl',NULL,NULL),
	(2331,52,'ENST00000533490','c.-390+372T>C',NULL,'intron variant','modifier',NULL,1,42061,'ensembl',NULL,NULL),
	(2332,52,'ENST00000544455',NULL,NULL,'upstream gene variant','modifier',NULL,NULL,2566,'ensembl',NULL,NULL),
	(2333,52,'ENST00000614259',NULL,NULL,'upstream gene variant','modifier',NULL,NULL,2566,'ensembl',NULL,NULL),
	(2334,52,'ENST00000680887',NULL,NULL,'upstream gene variant','modifier',NULL,NULL,2566,'ensembl',NULL,NULL),
	(2335,52,'ENSR00000060894',NULL,NULL,'regulatory region variant','modifier',NULL,NULL,NULL,'ensembl',NULL,NULL),
	(2336,52,'ENSM00526233310',NULL,NULL,'TF binding site variant','modifier',NULL,NULL,NULL,'ensembl',NULL,NULL),
	(2337,52,'ENSM00522614247',NULL,NULL,'TF binding site variant','modifier',NULL,NULL,NULL,'ensembl',NULL,NULL),
	(2338,52,'NM_000059',NULL,NULL,'upstream gene variant','modifier',NULL,NULL,2566,'refseq',NULL,NULL),
	(2339,52,'NM_001136571','c.-390+372T>C',NULL,'intron variant','modifier',NULL,1,42061,'refseq',NULL,NULL);
UNLOCK TABLES;





--
-- Dumping data for table `variant_ids`
--

LOCK TABLES `variant_ids` WRITE;
INSERT INTO `variant_ids` VALUES 
	(40, 52, '11740058', 'heredicare'),
	(41, 52, 'blimblam2', 'sometest'),

	(51,139,'11334923','heredicare'),
	(52,139,'11509431','heredicare');
UNLOCK TABLES;



--
-- Dumping data for table `variant_annotation`
--

LOCK TABLES `variant_annotation` WRITE;
/*!40000 ALTER TABLE `variant_annotation` DISABLE KEYS */;
INSERT INTO `variant_annotation` VALUES 
	(1,15,4,'5.269',NULL),
	(3,15,6,'0.104',NULL),
	(6,15,7,'BARD1|0.00|0.00|0.00|0.01|46|-25|43|-29',NULL),
	(7,15,8,'0.01',NULL),
	(8,15,5,'24.3',NULL),
	(42,15,12,'0.00732654',NULL),
	(43,15,11,'1114',NULL),
	(44,15,13,'15',NULL),
	(45,15,15,'1084',NULL),
	(46,15,16,'eas',NULL),
	(55,15,25,'000000000000000',NULL),
	(56,15,26,'3738999',NULL),
	(123,15,3,'3738888',NULL),
	(124,15,20,'130',NULL),
	(125,15,19,'9',NULL),
	(194,15,39,'-1.71',NULL),
	(195,15,40,'4.34',NULL),
	(196,15,41,'6.05',NULL),
	(197,15,42,'-0.51',NULL),
	(198,15,43,'7.99',NULL),
	(199,15,44,'8.51',NULL),
	(200,15,45,'-4.50',NULL),
	(201,15,47,'4.50',NULL),
	(202,15,48,'0.00',NULL),
	(203,15,49,'10.10',NULL),
	(1154,15,50,'10.10',NULL),
	(1168,15,36,'BRCT Domains',NULL),
	(1169,15,37,'PMID: 32726901',NULL),
	(16009,15,51,'0.00984176',NULL),

	(3876,52,3,'7988901',NULL),
	(3869,52,4,'-0.021',NULL),
	(3877,52,5,'7.930',NULL),
	(3884,52,7,'ZAR1L|0.00|0.00|0.02|0.00|31|-39|-44|32',NULL),
	(3885,52,8,'0.02',NULL),
	(3878,52,11,'5753',NULL),
	(3879,52,12,'0.0378129',NULL),
	(3880,52,13,'353',NULL),
	(3881,52,15,'5047',NULL),
	(3882,52,16,'afr',NULL),
	(36,52,18,'Benign / Little Clinical Significance',NULL),
	(3886,52,36,'C-terminal RAD51 binding domain (inkl. NLS1 und BRC-) ',NULL),
	(3887,52,37,'BWRL/ENIGMA',NULL),
	(3870,52,39,'-5.12',NULL),
	(3872,52,40,'-4.84',NULL),
	(3871,52,41,'0.28',NULL),
	(3873,52,42,'4.56',NULL),
	(3875,52,43,'-1.44',NULL),
	(3874,52,44,'-6.00',NULL),
	(16790,52,51,'0.131678',NULL);
/*!40000 ALTER TABLE `variant_annotation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- insert some literature entries
--

LOCK TABLES `variant_literature` WRITE;
INSERT INTO `variant_literature` VALUES 
	(16,15,25741868,'Standards and guidelines for the interpretation of sequence variants: a joint consensus recommendation of the American College of Medical Genetics and Genomics and the Association for Molecular Pathology.','Sue Richards, Nazneen Aziz, Sherri Bale, David Bick, Soma Das, Julie Gastier-Foster, Wayne W Grody, Madhuri Hegde, Elaine Lyon, Elaine Spector, Karl Voelkerding, Heidi L Rehm, ACMG Laboratory Quality Assurance Committee','Genetics in medicine : official journal of the American College of Medical Genetics',2015,'vep'),
	(17,15,29458332,'Identification of genetic variants for clinical management of familial colorectal tumors.','Mev Dominguez-Valentin, Sigve Nakken, Hélène Tubeuf, Daniel Vodak, Per Olaf Ekstrøm, Anke M Nissen, Monika Morak, Elke Holinski-Feder, Alexandra Martins, Pål Møller, Eivind Hovig','BMC medical genetics',2018,'vep'),
	(18,15,32039725,'Germline variants in DNA repair genes associated with hereditary breast and ovarian cancer syndrome: analysis of a 21 gene panel in the Brazilian population.','Simone da Costa E Silva Carvalho, Nathalia Moreno Cury, Danielle Barbosa Brotto, Luiza Ferreira de Araujo, Reginaldo Cruz Alves Rosa, Lorena Alves Texeira, Jessica Rodrigues Plaça, Adriana Aparecida Marques, Kamila Chagas Peronni, Patricia de Cássia Ruy, Greice Andreotti Molfetta, Julio Cesar Moriguti, Dirce Maria Carraro, Edenir Inêz Palmero, Patricia Ashton-Prolla, Victor Evangelista de Faria Ferraz, Wilson Araujo Silva','BMC medical genomics',2020,'vep'),
	(19,15,16741161,'Variants in the GH-IGF axis confer susceptibility to lung cancer.','Matthew F Rudd, Emily L Webb, Athena Matakidou, Gabrielle S Sellick, Richard D Williams, Helen Bridle, Tim Eisen, Richard S Houlston, GELCAPS Consortium','Genome research',2006,'vep'),
	(20,15,19584272,'Modification of ovarian cancer risk by BRCA1/2-interacting genes in a multicenter cohort of BRCA1/2 mutation carriers.','Timothy R Rebbeck, Nandita Mitra, Susan M Domchek, Fei Wan, Shannon Chuai, Tara M Friebel, Saarene Panossian, Amanda Spurdle, Georgia Chenevix-Trench, kConFab, Christian F Singer, Georg Pfeiler, Susan L Neuhausen, Henry T Lynch, Judy E Garber, Jeffrey N Weitzel, Claudine Isaacs, Fergus Couch, Steven A Narod, Wendy S Rubinstein, Gail E Tomlinson, Patricia A Ganz, Olufunmilayo I Olopade, Nadine Tung, Joanne L Blum, Roger Greenberg, Katherine L Nathanson, Mary B Daly','Cancer research',2009,'vep'),
	(21,15,26315354,'Germline Mutations in the BRIP1, BARD1, PALB2, and NBN Genes in Women With Ovarian Cancer.','Susan J Ramus, Honglin Song, Ed Dicks, Jonathan P Tyrer, Adam N Rosenthal, Maria P Intermaggio, Lindsay Fraser, Aleksandra Gentry-Maharaj, Jane Hayward, Susan Philpott, Christopher Anderson, Christopher K Edlund, David Conti, Patricia Harrington, Daniel Barrowdale, David D Bowtell, Kathryn Alsop, Gillian Mitchell, AOCS Study Group, Mine S Cicek, Julie M Cunningham, Brooke L Fridley, Jennifer Alsop, Mercedes Jimenez-Linan, Samantha Poblete, Shashi Lele, Lara Sucheston-Campbell, Kirsten B Moysich, Weiva Sieh, Valerie McGuire, Jenny Lester, Natalia Bogdanova, Matthias Dürst, Peter Hillemanns, Ovarian Cancer Association Consortium, Kunle Odunsi, Alice S Whittemore, Beth Y Karlan, Thilo Dörk, Ellen L Goode, Usha Menon, Ian J Jacobs, Antonis C Antoniou, Paul D P Pharoah, Simon A Gayther','Journal of the National Cancer Institute',2015,'vep'),
	(22,15,19412175,'Common variations in BARD1 influence susceptibility to high-risk neuroblastoma.','Mario Capasso, Marcella Devoto, Cuiping Hou, Shahab Asgharzadeh, Joseph T Glessner, Edward F Attiyeh, Yael P Mosse, Cecilia Kim, Sharon J Diskin, Kristina A Cole, Kristopher Bosse, Maura Diamond, Marci Laudenslager, Cynthia Winter, Jonathan P Bradfield, Richard H Scott, Jayanti Jagannathan, Maria Garris, Carmel McConville, Wendy B London, Robert C Seeger, Struan F A Grant, Hongzhe Li, Nazneen Rahman, Eric Rappaport, Hakon Hakonarson, John M Maris','Nature genetics',2009,'vep'),
	(23,15,31258718,'Functional Polymorphisms in <i>BARD1</i> Association with Neuroblastoma in a regional Han Chinese Population.','Jin Shi, Yongbo Yu, Yaqiong Jin, Jie Lu, Jie Zhang, Huanmin Wang, Wei Han, Ping Chu, Jun Tai, Feng Chen, Huimin Ren, Yongli Guo, Xin Ni','Journal of Cancer',2019,'vep'),
	(24,15,16061562,'Identification and characterization of missense alterations in the BRCA1 associated RING domain (BARD1) gene in breast and ovarian cancer.','M K Sauer, I L Andrulis','Journal of medical genetics',2005,'vep'),
	(25,15,20077502,'Cancer predisposing missense and protein truncating BARD1 mutations in non-BRCA1 or BRCA2 breast cancer families.','Sylvia De Brakeleer, Jacques De Grève, Remy Loris, Nicolas Janin, Willy Lissens, Erica Sermijn, Erik Teugels','Human mutation',2010,'vep'),
	(26,15,9425226,'Mutations in the BRCA1-associated RING domain (BARD1) gene in primary breast, ovarian and uterine cancers.','T H Thai, F Du, J T Tsan, Y Jin, A Phung, M A Spillman, H F Massa, C Y Muller, R Ashfaq, J M Mathis, D S Miller, B J Trask, R Baer, A M Bowcock','Human molecular genetics',1998,'vep'),
	(27,15,15342711,'Mutation screening of the BARD1 gene: evidence for involvement of the Cys557Ser allele in hereditary susceptibility to breast cancer.','S-M Karppinen, K Heikkinen, K Rapakko, R Winqvist','Journal of medical genetics',2004,'vep'),
	(28,15,16333312,'BARD1 variants Cys557Ser and Val507Met in breast cancer predisposition.','Pia Vahteristo, Kirsi Syrjäkoski, Tuomas Heikkinen, Hannaleena Eerola, Kristiina Aittomäki, Karl von Smitten, Kaija Holli, Carl Blomqvist, Olli-Pekka Kallioniemi, Heli Nevanlinna','European journal of human genetics : EJHG',2006,'vep'),
	(29,15,25994375,'Analysis of large mutations in BARD1 in patients with breast and/or ovarian cancer: the Polish population as an example.','Katarzyna Klonowska, Magdalena Ratajska, Karol Czubak, Alina Kuzniacka, Izabela Brozek, Magdalena Koczkowska, Marcin Sniadecki, Jaroslaw Debniak, Dariusz Wydra, Magdalena Balut, Maciej Stukan, Agnieszka Zmienko, Beata Nowakowska, Irmgard Irminger-Finger, Janusz Limon, Piotr Kozlowski','Scientific reports',2015,'vep'),
	(30,15,26350354,'Functional Analysis of BARD1 Missense Variants in Homology-Directed Repair of DNA Double Strand Breaks.','Cindy Lee, Tapahsama Banerjee, Jessica Gillespie, Amanda Ceravolo, Matthew R Parvinsmith, Lea M Starita, Stanley Fields, Amanda E Toland, Jeffrey D Parvin','Human mutation',2015,'vep'),

	(31,52,9425226,'Mutations in the BRCA1-associated RING domain (BARD1) gene in primary breast, ovarian and uterine cancers.','T H Thai, F Du, J T Tsan, Y Jin, A Phung, M A Spillman, H F Massa, C Y Muller, R Ashfaq, J M Mathis, D S Miller, B J Trask, R Baer, A M Bowcock','Human molecular genetics',1998,'vep'),
	(32,52,15342711,'Mutation screening of the BARD1 gene: evidence for involvement of the Cys557Ser allele in hereditary susceptibility to breast cancer.','S-M Karppinen, K Heikkinen, K Rapakko, R Winqvist','Journal of medical genetics',2004,'vep'),
	(33,52,16333312,'BARD1 variants Cys557Ser and Val507Met in breast cancer predisposition.','Pia Vahteristo, Kirsi Syrjäkoski, Tuomas Heikkinen, Hannaleena Eerola, Kristiina Aittomäki, Karl von Smitten, Kaija Holli, Carl Blomqvist, Olli-Pekka Kallioniemi, Heli Nevanlinna','European journal of human genetics : EJHG',2006,'vep'),
	(34,52,25994375,'Analysis of large mutations in BARD1 in patients with breast and/or ovarian cancer: the Polish population as an example.','Katarzyna Klonowska, Magdalena Ratajska, Karol Czubak, Alina Kuzniacka, Izabela Brozek, Magdalena Koczkowska, Marcin Sniadecki, Jaroslaw Debniak, Dariusz Wydra, Magdalena Balut, Maciej Stukan, Agnieszka Zmienko, Beata Nowakowska, Irmgard Irminger-Finger, Janusz Limon, Piotr Kozlowski','Scientific reports',2015,'vep');
UNLOCK TABLES;


--
-- Dumping data for table `clinvar_variant_annotation`
--

LOCK TABLES `clinvar_variant_annotation` WRITE;
INSERT INTO `clinvar_variant_annotation` VALUES 
	(702,15,136500,'Conflicting_interpretations_of_pathogenicity|Uncertain_significance(1)|_Benign(8)|_Likely_benign(4)','criteria_provided,_conflicting_interpretations'),
	(684,52,209597,'Benign','reviewed_by_expert_panel');
UNLOCK TABLES;


--
-- Dumping data for table `clinvar_submission`
--

LOCK TABLES `clinvar_submission` WRITE;
INSERT INTO `clinvar_submission` VALUES
	(7886,702,'Benign','2021-02-25','criteria provided, single submitter','C0346153:Familial cancer of breast','ARUP Laboratories, Molecular Genetics and Genomics, ARUP Laboratories',NULL),
	(7887,702,'Likely benign','2017-02-06','criteria provided, single submitter','CN169374:not specified','Quest Diagnostics Nichols Institute San Juan Capistrano',NULL),
	(7888,702,'Likely benign','2016-06-03','criteria provided, single submitter','C0346153:Familial cancer of breast','Counsyl',NULL),
	(7889,702,'Benign','2013-10-14','criteria provided, single submitter','CN169374:not specified','GeneDx','description: This variant is considered likely benign or benign based on one or more of the following criteria: it is a conservative change, it occurs at a poorly conserved position in the protein, it is predicted to be benign by multiple in silico algorithms, and/or has population frequency not consistent with disease.'),
	(7890,702,'Benign','2020-12-04','criteria provided, single submitter','C0346153:Familial cancer of breast','Invitae',NULL),
	(7891,702,'Benign','2020-05-27','criteria provided, single submitter','CN169374:not specified','Genetic Services Laboratory, University of Chicago',NULL),
	(7892,702,'Likely benign','2021-09-27','no assertion criteria provided','C0027672:Hereditary cancer-predisposing syndrome','Institute for Biomarker Research, Medical Diagnostic Laboratories, L.L.C.',NULL),
	(7893,702,'Uncertain significance','2018-07-02','criteria provided, single submitter','C0346153:Familial cancer of breast','Mendelics',NULL),
	(7894,702,'Benign','2014-06-26','criteria provided, single submitter','C0027672:Hereditary cancer-predisposing syndrome','Ambry Genetics','description: This alteration is classified as benign based on a combination of the following: population frequency, intact protein function, lack of segregation with disease, co-occurrence, RNA analysis, in silico models, amino acid conservation, lack of disease association in case-control studies, and/or the mechanism of disease or impacted region is inconsistent with a known cause of pathogenicity.'),
	(7895,702,'Benign','2017-08-19','criteria provided, single submitter','CN517202:not provided','Quest Diagnostics Nichols Institute San Juan Capistrano',NULL),
	(7896,702,'Likely benign','2017-05-01','criteria provided, single submitter','CN517202:not provided','CeGaT Praxis fuer Humangenetik Tuebingen',NULL),
	(7897,702,'Uncertain significance','2015-02-01','no assertion criteria provided','C2348819:Triple-Negative Breast Cancer Finding','Lab. Molecular Oncology, VUB, Free University of Brussels',NULL),
	(7898,702,'Likely benign',NULL,'no assertion criteria provided','C0006142:Malignant tumor of breast','Department of Pathology and Laboratory Medicine, Sinai Health System','description: The BARD1 p.Arg658Cys variant was identified in 9 of 2368 proband chromosomes (frequency: 0.004) from individuals or families with breast and/or ovarian cancer (Karppinen 2004, Klonowska 2015, Vahteristo 2006). The variant was also identified in the following databases: dbSNP (ID: rs3738888) as â€šÃ„ÃºWith other alleleâ€šÃ„Ã¹, ClinVar (6x, as benign by GeneDx, Ambry Genetics, Invitae, Color Genomics.Inc, and as likely benign by Illumina Clinical Services, Counsyl), Clinvitae (4x, as benign and likely benign), and Zhejiang Colon Cancer Database (6x, as probably pathogenic). The variant was not identified in Cosmic nor MutDB databases. The variant was identified in control databases in 2270 (11 homozygous) of 277098 chromosomes at a frequency of 0.008 in the following populations: Finnish in 336 of 25784 chromosomes (freq. 0.013), Latino in 425 of 34414 chromosomes (freq. 0.012), East Asian in 206 of 18868 chromosomes (freq. 0.01), European in 1067 of 126610 chromosomes (freq. 0.0084), other in 53 of 6462 chromosomes (freq. 0.008), South Asian in 125 of 30782 chromosomes (freq. 0.004), and African in 58 of 2403 chromosomes (freq. 0.0024), increasing the likelihood this could be a low frequency benign variant (Genome Aggregation Consortium Feb 27, 2017). Although the p.Arg658Cys residue is not conserved in mammals and other organisms, computational analyses (PolyPhen-2, SIFT, AlignGVGD, BLOSUM, MutationTaster) suggest that the variant may impact the protein. The variant occurs outside of the splicing consensus sequence and in silico or computational prediction software programs (SpliceSiteFinder, MaxEntScan, NNSPLICE, GeneSplicer, HumanSpliceFinder) do not predict a difference in splicing. There are conflicting predictions in the literature regarding the clinical significance of the p.Arg658Cys variant. Some studies refer to this variant as potentially pathological (Klonowska 2015), but functional studies do not predict clinical significance for this variant although it is in a functional domain (Lee 2015). In another study this variant has been utilized as putative benign polymorphism in multiple functional assays (Sauer 2005). A co-occurring pathogenic BRCA1 variant (c.709G>T, p.Glu237X) was identified in 1 individual with breast cancer by our laboratory, increasing the likelihood that p.Arg658Cys variant does not have clinical significance. In summary, based on the above information the clinical significance of this variant cannot be determined with certainty at this time although we would lean towards a more benign role for this variant. This variant is classified as likely benign.'),
	(7899,702,'Benign','2016-11-22','criteria provided, single submitter','CN169374:not specified','PreventionGenetics, PreventionGenetics',NULL),
	(7900,702,'Benign','2014-11-11','criteria provided, single submitter','C0027672:Hereditary cancer-predisposing syndrome','Color Health, Inc',NULL),
	(7901,702,'Likely benign','2017-04-27','criteria provided, single submitter','C0346153:Familial cancer of breast','Illumina Laboratory Services, Illumina','description: This variant was observed as part of a predisposition screen in an ostensibly healthy population. A literature search was performed for the gene, cDNA change, and amino acid change (where applicable). Publications were found based on this search. The evidence from the literature, in combination with allele frequency data from public databases where available, was sufficient to determine this variant is unlikely to cause disease. Therefore, this variant is classified as likely benign.'),
	
	(7776,684,'Benign','2015-01-12','reviewed by expert panel','C2675520:Breast-ovarian cancer, familial 2','Evidence-based Network for the Interpretation of Germline Mutant Alleles (ENIGMA)','description: Class 1 not pathogenic based on frequency >1% in an outbred sampleset. Frequency 0.14 (African), derived from 1000 genomes (2012-04-30).');
UNLOCK TABLES;





LOCK TABLES `user_variant_lists` WRITE;
/*The outdated information will be overwritten with the data stored in keycloak upon login of that person*/;
INSERT INTO `user_variant_lists` VALUES 
	(8,4,'public read',1,0),
	(9,4,'public edit',1,1),
	(10,4,'private inaccessible',0,0);
UNLOCK TABLES;


LOCK TABLES `list_variants` WRITE;
/*!40000 ALTER TABLE `list_variants` DISABLE KEYS */;
INSERT INTO `list_variants` VALUES 
	(5,8,15),
	(6,10,15);
/*!40000 ALTER TABLE `list_variants` ENABLE KEYS */;
UNLOCK TABLES;



--
-- Insert some user classification(s)
--

LOCK TABLES `user_classification` WRITE;
INSERT INTO `user_classification` VALUES 
	(2,'4',15,4,'This is another test','2022-05-31 01:00:00',1),
	(11,'4',15,3,'rdfgsd','2022-10-18 10:59:14',2),
	(20,'5',15,3,'reha24365','2022-10-18 00:00:00',3),
	(26,'3',52,3,'this is a comment with\\tpecial characters','2022-10-06 06:00:00',2),
	(28,'3',15,3,'dsvsagbruj','2022-10-17 08:00:00',1),
	(29,'5',15,3,'zterjdkzfrkfrk','2022-10-17 09:00:00',5);
UNLOCK TABLES;


LOCK TABLES `user_classification_criteria_applied` WRITE;
INSERT INTO `user_classification_criteria_applied` VALUES 
	(1,26,2,5,'evidence1'),
	(2,26,3,6,'evidence2'),
	(3,26,12,17,'evidence3'),
	(7,11,2,5,'dsafds'),
	(8,20,31,44,'rgjrjqrqwrq'),
	(9,11,3,6,'zjhdjhjh'),
	(10,11,12,17,'fasfd'),
	(11,29,113,143,'fdhsjj\\srjerssb \\/x shzwsh\r\n wh '),
	(12,20,32,45,'qwerqwr'),
	(14,11,8,11,'ewqrqfr');
UNLOCK TABLES;


--
-- Insert some consensus classifications
--

LOCK TABLES `consensus_classification` WRITE;
INSERT INTO `consensus_classification` VALUES 
	(36,3,139,'3','Evidence provided äöüß','2022-06-12 00:00:00',_binary 'JVBERi0xLjMKJZOMi54gUmVwb3J0TGFiIEdlbmVyYXRlZCBQREYgZG9jdW1lbnQgaHR0cDovL3d3dy5yZXBvcnRsYWIuY29tCjEgMCBvYmoKPDwKL0YxIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9CYXNlRm9udCAvSGVsdmV0aWNhIC9FbmNvZGluZyAvV2luQW5zaUVuY29kaW5nIC9OYW1lIC9GMSAvU3VidHlwZSAvVHlwZTEgL1R5cGUgL0ZvbnQKPj4KZW5kb2JqCjMgMCBvYmoKPDwKL0NvbnRlbnRzIDcgMCBSIC9NZWRpYUJveCBbIDAgMCA1OTUuMjc1NiA4NDEuODg5OCBdIC9QYXJlbnQgNiAwIFIgL1Jlc291cmNlcyA8PAovRm9udCAxIDAgUiAvUHJvY1NldCBbIC9QREYgL1RleHQgL0ltYWdlQiAvSW1hZ2VDIC9JbWFnZUkgXQo+PiAvUm90YXRlIDAgL1RyYW5zIDw8Cgo+PiAKICAvVHlwZSAvUGFnZQo+PgplbmRvYmoKNCAwIG9iago8PAovUGFnZU1vZGUgL1VzZU5vbmUgL1BhZ2VzIDYgMCBSIC9UeXBlIC9DYXRhbG9nCj4+CmVuZG9iago1IDAgb2JqCjw8Ci9BdXRob3IgKGFub255bW91cykgL0NyZWF0aW9uRGF0ZSAoRDoyMDIyMDUzMDE0NTc0MC0wMScwMCcpIC9DcmVhdG9yIChSZXBvcnRMYWIgUERGIExpYnJhcnkgLSB3d3cucmVwb3J0bGFiLmNvbSkgL0tleXdvcmRzICgpIC9Nb2REYXRlIChEOjIwMjIwNTMwMTQ1NzQwLTAxJzAwJykgL1Byb2R1Y2VyIChSZXBvcnRMYWIgUERGIExpYnJhcnkgLSB3d3cucmVwb3J0bGFiLmNvbSkgCiAgL1N1YmplY3QgKHVuc3BlY2lmaWVkKSAvVGl0bGUgKHVudGl0bGVkKSAvVHJhcHBlZCAvRmFsc2UKPj4KZW5kb2JqCjYgMCBvYmoKPDwKL0NvdW50IDEgL0tpZHMgWyAzIDAgUiBdIC9UeXBlIC9QYWdlcwo+PgplbmRvYmoKNyAwIG9iago8PAovRmlsdGVyIFsgL0FTQ0lJODVEZWNvZGUgL0ZsYXRlRGVjb2RlIF0gL0xlbmd0aCAxODAKPj4Kc3RyZWFtCkdhcHBXWW4iVykmND8yQEt1XyYsKUg3T2pXQl5rY2teTUhTPmd1K2Q1dFAlKVQ+RkUtbyYrLlIyV3RzRl5ZOGFZJCttNmhmbjJFMmNqY1gwMCU7R189Zl1TMSVnbHVhZFhtbW5FaWNKdS9rKkhXWSpwUD5QKEsmTi1DdEMiL0ZTZz1bZkpXWD5JNHEiUDJaZE9uX2pOWTU6ZDouVmd0N0lFQjgtK0ZnLTZZbyoqPXExKkh+PmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDgKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDczIDAwMDAwIG4gCjAwMDAwMDAxMDQgMDAwMDAgbiAKMDAwMDAwMDIxMSAwMDAwMCBuIAowMDAwMDAwNDE0IDAwMDAwIG4gCjAwMDAwMDA0ODIgMDAwMDAgbiAKMDAwMDAwMDc3OCAwMDAwMCBuIAowMDAwMDAwODM3IDAwMDAwIG4gCnRyYWlsZXIKPDwKL0lEIApbPDY0ZjIyOTVkMzQzY2EyODdkNjU3MDA1MWRlYWY5Nzg0Pjw2NGYyMjk1ZDM0M2NhMjg3ZDY1NzAwNTFkZWFmOTc4ND5dCiUgUmVwb3J0TGFiIGdlbmVyYXRlZCBQREYgZG9jdW1lbnQgLS0gZGlnZXN0IChodHRwOi8vd3d3LnJlcG9ydGxhYi5jb20pCgovSW5mbyA1IDAgUgovUm9vdCA0IDAgUgovU2l6ZSA4Cj4+CnN0YXJ0eHJlZgoxMTA3CiUlRU9GCg==',1,1),
	(183,3,15,'3','fsghfjmmgf','2022-07-27 01:00:00',_binary 'JVBERi0xLjQKJZOMi54gUmVwb3J0TGFiIEdlbmVyYXRlZCBQREYgZG9jdW1lbnQgaHR0cDovL3d3dy5yZXBvcnRsYWIuY29tCjEgMCBvYmoKPDwKL0YxIDIgMCBSIC9GMiAzIDAgUgo+PgplbmRvYmoKMiAwIG9iago8PAovQmFzZUZvbnQgL0hlbHZldGljYSAvRW5jb2RpbmcgL1dpbkFuc2lFbmNvZGluZyAvTmFtZSAvRjEgL1N1YnR5cGUgL1R5cGUxIC9UeXBlIC9Gb250Cj4+CmVuZG9iagozIDAgb2JqCjw8Ci9CYXNlRm9udCAvVGltZXMtUm9tYW4gL0VuY29kaW5nIC9XaW5BbnNpRW5jb2RpbmcgL05hbWUgL0YyIC9TdWJ0eXBlIC9UeXBlMSAvVHlwZSAvRm9udAo+PgplbmRvYmoKNCAwIG9iago8PAovQ29udGVudHMgMTIgMCBSIC9NZWRpYUJveCBbIDAgMCA1OTUuMjc1NiA4NDEuODg5OCBdIC9QYXJlbnQgMTEgMCBSIC9SZXNvdXJjZXMgPDwKL0ZvbnQgMSAwIFIgL1Byb2NTZXQgWyAvUERGIC9UZXh0IC9JbWFnZUIgL0ltYWdlQyAvSW1hZ2VJIF0KPj4gL1JvdGF0ZSAwIC9UcmFucyA8PAoKPj4gCiAgL1R5cGUgL1BhZ2UKPj4KZW5kb2JqCjUgMCBvYmoKPDwKL0NvbnRlbnRzIDEzIDAgUiAvTWVkaWFCb3ggWyAwIDAgNTk1LjI3NTYgODQxLjg4OTggXSAvUGFyZW50IDExIDAgUiAvUmVzb3VyY2VzIDw8Ci9Gb250IDEgMCBSIC9Qcm9jU2V0IFsgL1BERiAvVGV4dCAvSW1hZ2VCIC9JbWFnZUMgL0ltYWdlSSBdCj4+IC9Sb3RhdGUgMCAvVHJhbnMgPDwKCj4+IAogIC9UeXBlIC9QYWdlCj4+CmVuZG9iago2IDAgb2JqCjw8Ci9Db250ZW50cyAxNCAwIFIgL01lZGlhQm94IFsgMCAwIDU5NS4yNzU2IDg0MS44ODk4IF0gL1BhcmVudCAxMSAwIFIgL1Jlc291cmNlcyA8PAovRm9udCAxIDAgUiAvUHJvY1NldCBbIC9QREYgL1RleHQgL0ltYWdlQiAvSW1hZ2VDIC9JbWFnZUkgXQo+PiAvUm90YXRlIDAgL1RyYW5zIDw8Cgo+PiAKICAvVHlwZSAvUGFnZQo+PgplbmRvYmoKNyAwIG9iago8PAovQ29udGVudHMgMTUgMCBSIC9NZWRpYUJveCBbIDAgMCA1OTUuMjc1NiA4NDEuODg5OCBdIC9QYXJlbnQgMTEgMCBSIC9SZXNvdXJjZXMgPDwKL0ZvbnQgMSAwIFIgL1Byb2NTZXQgWyAvUERGIC9UZXh0IC9JbWFnZUIgL0ltYWdlQyAvSW1hZ2VJIF0KPj4gL1JvdGF0ZSAwIC9UcmFucyA8PAoKPj4gCiAgL1R5cGUgL1BhZ2UKPj4KZW5kb2JqCjggMCBvYmoKPDwKL0NvbnRlbnRzIDE2IDAgUiAvTWVkaWFCb3ggWyAwIDAgNTk1LjI3NTYgODQxLjg4OTggXSAvUGFyZW50IDExIDAgUiAvUmVzb3VyY2VzIDw8Ci9Gb250IDEgMCBSIC9Qcm9jU2V0IFsgL1BERiAvVGV4dCAvSW1hZ2VCIC9JbWFnZUMgL0ltYWdlSSBdCj4+IC9Sb3RhdGUgMCAvVHJhbnMgPDwKCj4+IAogIC9UeXBlIC9QYWdlCj4+CmVuZG9iago5IDAgb2JqCjw8Ci9QYWdlTW9kZSAvVXNlTm9uZSAvUGFnZXMgMTEgMCBSIC9UeXBlIC9DYXRhbG9nCj4+CmVuZG9iagoxMCAwIG9iago8PAovQXV0aG9yIChcKGFub255bW91c1wpKSAvQ3JlYXRpb25EYXRlIChEOjIwMjIwNzI3MTExMDQzLTAxJzAwJykgL0NyZWF0b3IgKFwodW5zcGVjaWZpZWRcKSkgL0tleXdvcmRzICgpIC9Nb2REYXRlIChEOjIwMjIwNzI3MTExMDQzLTAxJzAwJykgL1Byb2R1Y2VyIChSZXBvcnRMYWIgUERGIExpYnJhcnkgLSB3d3cucmVwb3J0bGFiLmNvbSkgCiAgL1N1YmplY3QgKFwodW5zcGVjaWZpZWRcKSkgL1RpdGxlIChcKGFub255bW91c1wpKSAvVHJhcHBlZCAvRmFsc2UKPj4KZW5kb2JqCjExIDAgb2JqCjw8Ci9Db3VudCA1IC9LaWRzIFsgNCAwIFIgNSAwIFIgNiAwIFIgNyAwIFIgOCAwIFIgXSAvVHlwZSAvUGFnZXMKPj4KZW5kb2JqCjEyIDAgb2JqCjw8Ci9GaWx0ZXIgWyAvQVNDSUk4NURlY29kZSAvRmxhdGVEZWNvZGUgXSAvTGVuZ3RoIDE3NTcKPj4Kc3RyZWFtCkdiITtmZ01ZYjgmOk86U2xyMFNuKDshWFMlKChRRixdODRMQk9XLDw3NyIjU1BzZzZgUEVbX041SkJLVy03LC5XWzNZRUEkXk4+YDIudDRbU0RpbjskLFowU2pnLGFJb08zSydzJUV1dEJYVTBaKV1bLDpUaGkiWV0rX0lqYWdmMHNhXD87K19AVzRscGA8XFtqbExUMCFaIj08Rj1QV2ciSCpzK1gwYkQqSF1zQFFBc3BGJzRkbDFlS01uKVJDJlRXT2g0aVNAImtuMEYxYSY1ZillLyVmWHFBSWhOWlsyWzxWUztaUWAyWDU/KS9DWCtVMk5nWl1IS0Uoc3JlZElDUC1DOSdNUVFEREI/cVNtRzE8P2E4O1U3UUA1Jz84MmlEXidJQmgoWS9jNzhJN1BIXGB1WHJOXW81O1BZU0pAVixpb2pQXG8nbkBBciVAIlhYIk8vQCtBUEU+c1lVNzshJCQtZHA1Ml5HP0RzJVxzdUtSLWNsWVJ1SUAnUmI/S1FhbT1FXlEuKixxPm1hLjs6YlZnQGFnRHFfLlJVcm4pK0FPTyQ3XCwhNVlJWDgrUChMIyk7KTduRT0mNyVebWhPc0hbRz4wXltUcVNRMGAxOmxsJic5SzVmRyEmWENzNyxUJzQ1OWVDVCdUXjIiOzI6SSxrK0NNamRoKXA0VGVIITs6WixyNUBvYj4/JDkvKGdWOlE2ZSpsOEw2dWciZGxhS0wmPWxGOmpOckxsPF9FRiNXXSRUVU4zOiNTZFxBQyt1cF8rPT0pIT0yRik/WVgndHArQ1dcYSxkSl1iNFhHTiNZJmBiM2MxY20iSG5eJCtIUXBla0klRjcrYlNlKFdVYFNeWkUiMW5Sbi1zRGAlKDhRViYwNGRnUTtKWEVcTFlBQEduPDthT3E4LykjcW5DVjgnKnNpWHNsM1tFK2A5WWZXblohaVY2Z24pRG5PKFEvUkZPQzBpN3NVNEkwUEdfZmU2aFwmTj8iRVpqaChGOmpILlZ0TDEoSThKIShSO1BZM1ghIWhVVS9ASGBnZEdOcj5sY18qaE5nSz1HJSYoLU1qIVI5RUo8Kk8mJzdYJHFvV1BfWCheOllEQl5JSEA0Zmo/Pj1GNkxGTCIjbmg8NkI6cE5QSkw/Rlx0XnA4JVoqNWROWGFZPmhNcUtsYjVQJVUpU1pOWHJPLGs3NEtOZlwlYjxkOlEhWDk5NlxqNC1qRE5QQGNLRV5PTFNBU01cJ0ltckU4MSF1ZEBMP1pJTUVYX21fYkBEJjdDbWIucFwvW3M6VXRBK08mPkkpN15KRiYhXFlkT1Qla0BXZGkoKk1zRmdqTUxbcjFZb2NISnJbPlFHMShkZU1ba1g4KzQ4aWIvPzNwIllVb2FILDdvUCxgQT9uYUl0TVE9dVw8ZzdxQWhaWWpTcz8yRCo/PzIwUF1dPSFNWUZcI1N0UipIMyRYLkpAa0pjQVlNUEYvUiRAJXQ/OCQtUiwlMlUwTiIzVDVyYHJ1QiprIzRpZThfcnFMXHIldVMvbGlNJyhNWixraWp0OilmajEwMktBRUo2Oi1yVVw3cTAnXFowZCleQ0VcZUZZMDBfbyRiInBvJDluSU5NKDVfQykxLHNbZ2hkZD4mZHNTUGI+IVxDalMmIl0tJ1VPSTAlbE5FMEVENCInWWJqXW5wJU9BRm5HcyFNTzdkJUxhc1tAWyxXV0ghVGthOCczXT8xKG8lMyFMQ1RsOTEtMUpYR1A/LS1IRitbQ1dIXlZVSCgicy4qNDMiXidZN0wrSzlWZzlbM2xtLTlmVU8rKU86IzszczdCRkZlJmJVKVspODhDNUQxW2VTZldeKGlLZG1bYmtoRUhXXnJpTCRLcnFPTTspVVtcTTBEKThPJy9nZGw6RVg6JFE0LjhqQCVxRjBLKE1jP2s4W1hBYzZ1QEdmRkdaaCEjMSVKbldKJGw7LlhgIiU5Rj1QN2QlVy9vbidGZ0M1TVQ8bjdxaDg9UEpTPlQiWWZHQD9OO2NCWyxMXSxUR1pEJlxAW2pVO2liM2Y/NVwhTTQ6K00oInE0Y0Q8TmVUUmVFX3I9WjlbQ11VNlt0aW9RazxEL0VoLSVIaGxLQms4VzNYYjlQKGszST4qR2NSP1JXS0NhWG5eLHA+QXI+bSIjYGQkc05zLlpBN3RxXFpXP209YClEUVlOI25TQyVHZFtTbGEqc1dxN2ROSks6b0Eqa1hiN3JrZFJZV09BYjRMTjIjc2Rdb1FETTZyJnMiJT44XmI6YigsQENULTRLQWokJ0hbQjMtJSpOOjg/R0NCZTAjXy5OZ1ZtY1k9cEVvS2lhJzYlNXB1WzVyVktaRH4+ZW5kc3RyZWFtCmVuZG9iagoxMyAwIG9iago8PAovRmlsdGVyIFsgL0FTQ0lJODVEZWNvZGUgL0ZsYXRlRGVjb2RlIF0gL0xlbmd0aCAyNzc0Cj4+CnN0cmVhbQpHYiE8Uz8kImM/J28pMk0vLCQhPEFuI2tzIVZFKkJNV05MOTwycTFsUjwxS1wkciJQTztBLCZsMFg6ViooNkglZkNncURaJEZFYVRaOlRSa2htNEVObUssQSRALDFeOnJubGgrWjBySXBEcjFwTCxbN29vNjpbSXJybExgYE5dbkc+XTInbXMuO2NKKDtRSWxQVjstJy4ydCh0QlFVYjZgaENIW25Oam02cm9eY1JHJiZdS29GcVhAc2A6OVNJYiU9Y21mLkIpMWYoaVwraWBFU2BWTl8jLHI9JjdyTHEkJldONEhUR3JtVTJwVzQoJm0nSiQvJW1IW1ZkYV4mSU4sO0pTYDxTP0ZUMkwyaFFZOE5iKDs7Wj5TX29xXnFbVlNJUVBuSHJfQk5JJ29sMyQkNG1vNGYxWXEhNjphNi5TJW1VSWheblpsdEhVNUEiZjhkcz1FZSs6NXJma14ldVpbUSxcYGtBYTk8NlBPMG9yPjFLXUdRTks+LTUtaW1IOEA5TygsKEdlZCZvckFYQ1o/W1ZIXWwnX05iQ21eTixpbE5RYlZCSTEnayJLaGNoQUpGYTZzJl1pSiMvbV4/UFBTMkJWYDNYOTFWYUlgWURdOiIqVCQubFg9Z2YhU0E+NUZgMi5kSGYzKDEhSGprWjFsNjZXblRRamUuajA5J28iM1RNbD5iJGhwNDdHOlhkJTNyc1xLYExqVkArNGZkdSdDXVBYJFInWkFkUUdKcWJWRmhQMk8sVHM0bkAhLE5pM0Y+YS9CKkcsc10sZElfKTtxW1soQls4I3UvQWM1Z0FCLD1PYz1TV29HUkpnVSZYLWNPO0lOKzgsNFttZTxpJSckJlZMJkBLTnVUOywzbjQrRD9oUGA4OnFSUS1HaGNtY3MmSUFqWEUwa0dtcDM4YD10OTRQQFw6K1VwMTYpaGJLXDU2PVVaXyE4J1xFa1xMPWMtSG1nMDg3V0IxVlFyNC9kJTNyc0gmPjw6NENhc2plKm8xaCNdJ1BoYk5LbmUlSUspZmQxPWgnSj5LbXQlM00xcC1fOTghT09yPDdaWF50V2xYSEVrMmlFU2lkNi5DOTQkUGY8WGhQRzFHTC4zMyRMOE5daEE6SDM/bDJfNFFzXSNvUzpQKjZSRUckYzYkbj1lamJYWExib1xtWmBnaCJpI1ZnPVc/WGtyJkA2aFEhQCNeRFgjbzUycC08UzM/NS9APGNAX0NtckY5N1VuM1dXZUFTWy9SZ2wlRWUyOD5mJyQwdUlgVEtVKCMuK3N0TFNNTmU1a1U0LkdYUWNDQDImVkwmQEtOdVQ7LDNuNEtEVD0pdTg3TjwxLUYsWF1jcyZDP2pYRStULEFzcyJSOF1tcTI/PUsjcUdqbyc3WWoqQm1BbVZpWmBTWTxfVUAmTU0jKUFucEI4Z3UzITchSTE2cGVOS0QjRU1hcUpQdCxwLjQtLlFLRkJKUkg6MyZTdEg2NlB0bjQrcSxrKSNTKUBrKSFxPk5USDY5R1NcPC9OMEVHYDdSJ1IlYl8kJCIjVkgzXGA0OWY7KVhVJjs5LTRXXlg7VkdcaDclWnJHOWBCRicubz1rXSheQUo7KG5TP1ojKTMuaS5gOFJ0bTI2K20tUk1vL0pIPXJuKFhcZV5OYUxINW9ITmo7LGEqaCg8Pl5VYiMtUz4+LG5QNjRqQWo8ZiVbWmEsKFQkcHRcIXI9KztEXkc3TSMtbVBKLkMsX1MmMXFYLWtmSUs1TmpdIU0iMjdbaVFUPWJXZT5GcTcsRlgmJV0sa1Y2ci0wTUlWaSY4VUAhTF1USDlcKUI1YFkuPEJ1dDBsS2dmYDt1dSkwPCZvc2dpQzQ4I21uYWJBZFNOQiwtX1ckPFlEayMuWm9xNGhlMGUoYF0uIXFgIUcqYVxaTm9rcCJkQ0IyJ2VwOWRmZThqJ1I3TyhaVz1hcGc0YChMJmheYE9NMSJjTkclSEtqaUVKKDNGZSE/WUU2TlJvdS1BIjctY3MmMTlqYl4kMl8+cExdIi40YTc5OExKLGFoRVQvP0hLcDshQy8hazY3M0ZDJW84VGleUy1ici1yXDZYNF9SVjxUS0daPyMvMnVMT0BjcnVLSy4+Iio+JW5XRVpHXG4hKTE9YiVPUmhpYz80WkslMVB1clIwcipDNiRrOWRqWERsMG48SlAqOVl1IyomLXImVWYrQFZnXjpUKzohKzchJ0Y+KmFnbjk8S1dERjRMPjpvOGgpSGRFZy01XjxdMSxiKSVAUEE8Z1owIVdATjFhXGYnVTU/TTUmNVAkcThFKThfNkg9LUdgKks9bmQndTJDaXBRXzFIUzFGISg0ODVWYkNGXVBULGo0QW1fQk5pO2JTVFBmLkFjXiN1ITBnZjs9LzxqVkxNQTRfVmhmUCMhIUYjZkZJa0ZxOXFDSGElVHQ1Xjs6Jy89KkFhZEFbSlVbN25UQF9fWDtzbVxAaG0/dG0yIXI1YkB1Rz43QiNFak5wQldrTXAwQVRAMSQ1JUhEWlJZYStNQVRfZjEvLzxBUGlAVUsnYkpWbEhcYWhXYkQzc2c9am5oWERCITtYPj1wQ2M9cmQ8WypcMiNxQFAqR2tJaklXN2BgN2xbRmJLZ28xcWk5aSpEZzlQa11jSl89cE1gLilMSi0+ITY0IVZMSVhhTTwkbD5sWG0qa3RmVCJFZ24rLWsuIy4qXj5lYT5lNSFNPmxuIl4kXiJhWyVpLUNUcyxjJjRyaGA4NnVDLSs4L1ZkKkNAaC1NSiZibGUyTGNoOzA3c2VNazstZHFjWUMsIV1kajgxTCNvSkFzN3JrUXA/azQ7STBeQFVgamdCXUIrPyM4KmJFKzQ8TFpUKVBJU29UbW9BKjBpal8yPGBdVydrbiwuXWwnRTxYMk9sYGIrNGFiMy9aJytPaj1JTy9yJyUvJjE4QThYamVMIi1jXGxVNjAsLWZyXlgrWD4+R01DUEZYNFsoISUpOlc8R29SZGtOWSYwXVsjRmxgPiJJVTlrSVs0ZjovK2pMcDAkTVZNIWUzLT5AREBCYiZuZEQkYiYoXiMiZmNDR2pOVWpgKzZGIXFHV3NiPGBHUUMvUVoqKFxEXzptWztKaTBsITsvVzUuTFVMcEZgLVpQY2JiQUheQDl0YDdqLyJCdDpRa111XU87PzFDaW9aVj9ZODVaUEdMZlNxbzVOW10mNz1mSVghNUNGQV4oTENNL0xxIy5ESllfMFtKXztpZTs5VF0zImIjdEBJQmI5dSQ2PEwnKF9wYTswU0BqJEgkKSdtRV03MDBvaitdT0ghbmEnPWE2Z3IxSj5WRVRGQWlPSE5lU1lJSXRHMGZxcktUSENePl0yPT9xSi1wYT1dRDczNkAhWmw1S09cXjYiLGQ+U2Y5b0UhJmlpNltacWpYam4xaUReN1tsIiFcV2BXU01nUkhJXEZrKyJ0XVdLaUBnak8hPVstXT5VRGk5cGBXcStSSShAPismXG1dKjRYV21LLUM7WkEqRDRQPT9lSUIuSSUjYSNFXVEidTc+PzchVGFwZztjRUBuZUIjSFdnX2pValI3czQ/OExaTz9LaGVgazM4PWZBT0tHU0EmP1tKYFA/TUwmRnVbRlk5aDNuVzohOXNyOSFnLWBvNHFpciM1Rm0vX1Fyb3RsRixBSGpgXUxCcmM9LlNzc1YySF1yXGp1X1RSam0lPCsuXmlRYTh+PmVuZHN0cmVhbQplbmRvYmoKMTQgMCBvYmoKPDwKL0ZpbHRlciBbIC9BU0NJSTg1RGVjb2RlIC9GbGF0ZURlY29kZSBdIC9MZW5ndGggMTg4Ngo+PgpzdHJlYW0KR2IhJEk/ISNjPyY7S1pMJ20jZjIrXlc/WG1DNz9TW09rZUtCaFIpL0RBNVNhQ0FoL1MlYURjR09UP3Uvcl5hRG1oJUxwOSo1Lk1JKmZXV0UiQy0+OmsmNkNgXVVIYTFZNmJhTmpzcVMoVGVPNjNeWkokbk8zIzN0SUhwU2FVYGktajMhJl0jWEc9OkBrLWhvY0g7bmkmIm4uNkMrVSRsSC5cdUc6ZiNVXChxYkNSP1JQTF5HXyMtIjRzM1EnNm5SWFBWbGFTM3IhXDxNTmBGWjVuKicwM0QkZ2chJ1o8RSlhWVkjVVREWl85UypVNDlMIzBwPmlIXi1hRzxmKmZIOywzJCNqKkIwKipeWjRSTkBLP1VTYUQ0O2lzdFxjcWhmIk5PTSwxRiw/YklOYz5OUDY+anVqalZcVlkwcmQtaXM4ZGVxTm90NzdDOjBpQSlULC4hdTQyczlSZlQ4PC4oOF4nWjRCclNrLjJaPUhwXnA2TEk0Iil0cTlbUURfOjBpWlxGPG8hcS0jMl4rLW1fblJTMFRobEMrOjRuRnVPOic9XTp0I3M8WTlvRUs2aypUYWtwKS5YPFJmVWxnbWwpUE4kKU85LlhSVFQlU2M3R106YCJEUHNETiJFNy06LTE/OUlQVVc6cWMzUTpZUWo0VCZbQDwzZGJYdWlrYkNVNCtsQDc/PycsVlhBKnBzKjQrblIkLiw5S0FUSlszXDhLL0IvP0xYYzBEZ2xSIjMyWFhtR0wxdU5TbyJ0SE9AZW9wVExBPCxZbVwxXDdpZl1YJSdmO0s7UzVHZytKc280OGdbKDssbidZIllXMlBgUGY3UXM0Rj1mY3NcIzwvbDNBRCRXIjc2JFBraUBcLDRNZSVNIzBjI2EpKSo6VkNFUFQpPVRUW1VaJTc8cypeS1IjLGdubGZDXF4iWmYpWmJLSF1HYEM7RDZUUGNkXUsjJ2FhPyhINWAsdEg9TGdrJlxYLUAqSmlbKyc7IT1XJCdjSVZVUkVxLC8hXTp0IyFPLV8xXS0zcExoWkgqL1ZvZUozaj5ARF4sOjsuTkBMMSI+M1E8MU0nQElHQyxuQF1wSHJqdCldUF8vQWlHZVdSQilKaDc+T1deNyZxOVo3RCZfRHVjNFFrJ3JkXWVBcio5OCxYK19eL1tXYWhFYy40bz0qY2xkJUBrcDhNdF0+cWI/XGhwSWExRiNiL0NnNS8pLFFGakVUcG1QYz9MTElcYVIlPUlYWEEkIWBTOTpcOTpPcjFMJGZGZkU/JTNbbG9XaCM1O1ElYWNzK11cVl86SDBARWpyOW9ZZz9BOWVLME0lTDdUIjByUnBlWURQTjJxXTJPOmZCN0NdUl9YPm5RKXNpJUNScGllMXBqJ1RpLSJnV01HYmlZVEkjTDctY3NIYTM0cSRiNDUyPkpqUEBmJ1dSRnB1JGNYT2kmbS9nO1k3Jys8bD4xM1E4JUhtIy1mQEBsLj91MVU/YFQ5UTctSyg6P1wyQG0uY0diTjItKiRBIzZvXEleM2NTQmohTlVvKzdVWW4qbyNiYDJQcSsxVDI/c1RaNzw5RHBraWs6VlpZLE9dUE0rSEYwUk1IKUI6RmtRPWFARzJwZVFqRzJBWCdncTMlWWNpL10qdCw8cHBdcWdAcWA3TjsuanBoIUc7TzdQazJQKzFARVQ+Y1YvNDw8NihbWTBlJWo+Y0xCaWFdWkM3XmZYdTFAYiJNOENnNEVZMEh0NU1PRTtmXTZgWiJQYStSOFAzJSYvPFpBWjBKNG10VmpBLnBnK1B1I3AyPzdiT0ZvKVw4PkVJbig7cFxtdFotQGUwajRJdGJWdS4hPiYkLi0jLGw4byZYRC8wb0RxaV0kQSwwdSo0YV50ZWp1JEtPPnJpSXFjK2xoNyUwb0UiO2BUaGxmQWg8UmwhRjFkNUFaZnJPNk9hV11dVkwtMzg+UzxCaiwtbjJ0ZXFubGpxZFAxIiJIUiInUCFMN2kraCRjcUMzIWEqXDM8ZSE1b0FvVFdFcmB0VDNxTCMoXVxecz08aidjSURyNDw/LFRrKV5OWUpGYWIoU2lzQSFFL0VQYSZyVWk+Q1gxQENdbk5hP2xhMXI1aTRvWXApQF1gdFAvSTVJQCsvTipqZjRDW1tZU2l1WFVRLm8/NjtPVHBBUDJYW0BaTyRxVlZNJ1UmJDt1Jl4scj1cPSktUzNOQkJqYDVJTmI7TFw1UzBuSCora1lnNEUiYUJmaVguaShTIl1PJiVOaSg1X1xGNVE0IzMhP1RZdCwyJkE8RDtsLHI6M2EqJ0dROUw2OD9xTC0mODdKWWFla0Zab2AzN1lORUY9aUtmP2IsLStQSlNzL0JdYW9QSzBUa1knKyNkNHRvYTNWWEp0bERJIWdYZ3FgRjhCOF4tO0IkNUx0LDZgIilhSktbbjRlKCZgaGdvNENDUlVNV20oQyRlPWdGJFsuO2UqX1pdXHJUJFwtYF9TWUBnZUMyJS81KHRUbCpQbjlDbkFXTnJCMi80NiYwfj5lbmRzdHJlYW0KZW5kb2JqCjE1IDAgb2JqCjw8Ci9GaWx0ZXIgWyAvQVNDSUk4NURlY29kZSAvRmxhdGVEZWNvZGUgXSAvTGVuZ3RoIDE2MDYKPj4Kc3RyZWFtCkdiISNcPyRHIV4mOk5fQ2JUal8pVys/bk1IIyhpJlMiPUc+UEU6Mm9LRSptPGpOOTZCSiVtMzVDc3M8V0dkbD9ocSlYRDdcWEpwSkdLKDI1bjtDaGw9VGlcKExOaD5RTF5XZiMmOmBjWXIiYWFOcFYtQEJyXmtFWEglK1pWaTAhUENtIUJlRl9lZ2RVZXVSWkRKczA+VklsSk8jKyxrXDM2aDYtSGAvTiZ0SFhybiQsN1c4MHJXVkZrQC9fXEtcWTJKQEd1dTwyNGFuLCpyY0J0RFpYRD5ybVpvMnNedFItaFYxcFd1VShNJCNFZiZRJFxIZmhcSSUwLkJrWmFMRyJxL0xjaylAQD06RjozbERDKmwhT3BiLCszZ1g3QEFsSEk2clEiT2omZEZQQmdBVjUtMidaR1pxYVY2YmsrbS5ESlFKSXJpKl5iNDo6UFEtaUBbcEIxUkRTJEwwXTgxJFtyaFRsXUI2OEVKSTw5SmtxJ0xnMzlPc1FrZ05nNiQkc1JYWXNZKShQQDxLNkVXWF0vL3NkUk9LTzVWO0FpIzdjR1dXMSdOKi47RGQhTVw8Kz1YXF1NdTBZIkM0VGEocj5jKGxKRG9WPGFpOElPZ289LV9yNmE/V1U+NzI5OGI7PU1vOTlZPD06Xi8jZ0FqJl1TPU5MMUAvODBRUyJXW2BBVEoxKF9TVEdoLkdlcTxOWTRFQVNyPEZjWGo3ZC5tPD0tJEtGcSwybExDPGFXQ28qLGUpUEw1ZGpobnBbdE47YyI5UmtuW09GPToyTzI3PEg1dGlVRGxXQnI6WlIubDskV15vQ2BtO1hJW1wwQ0RyJStjbkddODwmMVVCL1c1RiM/NWRLbHB0SHRPPSI5S1cvbzhBRCVgVEk/a14pbjg2dE8kJkNpZygjNzkpWCpJKUhZMXE3Z19LUmdKP2FwImZFSDYtIS4mLVM1VlhgQkMyTi00LCEjUmRqLlpbS1MmN3FRczcnYV1zYGBqTU8nbl9EKzFZaC9La2RATm1eNFJ1RGA/L1Q8XDdYKEopOCdbSWo1RFgkYUBMXGI7MVM+QEFcXyNLS2lLa2UiRyRNZ20nYjVramA/SVxQMCdIPTFnQDxVYyddJHIvdTREXl80Pm87JGUiKFlUbUJgSDI5ZClAbz9galw7OkJnSF5kMEpnRFUhZEQ2Jy1hI0pEPClMPTI8YTxnJ0hQa00uLFpbRTouaSg0V2NtaClJaE9PKEc7RzNQRl4zYlFdZiduT0ZkJmAvYGdkcCFpZTFSLy0sLShQM1ZWKlQxMVNXbS1pM21rQFMsTTYhZmUrKGUkXyE3NG51OE1OcXJoMCFkcGAuRFtYUGZpbUshXWU/c1s8cyoldF42KCgiQWdFMU1FRSJMcW5hMlU/M25hIkBfJlA6QV1EIlA8REsiZkEjLCtjZWc2bERsNHUyMkEiODZhYW5DPnNQSyNDYjsoIlY8MixgMCVrK0I2NW11VCs6U19xXDxCTnMqdVI9N2ZoOGxKLF5jR3BjQUNfbl9RM2NaSzVIZV8mOlVQcDk9NzZJXDl0ZjUlb2d0clFcYFQ2YSREJGQ5TDVIaWZUJDwxaUlrbWIhW1xbcjYvbGpmVGghMC8hJzwxaC1NR2lLODxcXTtuViM6PktaJ1lvXzk1bUBpWjc8Qm9mXztOOXIxQ1RaOCgsSjsyZCw7bkJkZVVLUz9kN150Mz1La0JaYSdpOFRZbz5EbnMoZG4+THI9Zlc7Iko3Nj45ZU9bbVlyMyJhUz1aVnA+QEldKWopJXNcUSNPRi1MckRbNGlpOiEnZWFXMXFvLUBHVT5pWUE2Nm8lN2UsI1RKWis3O2M5ZFlZOD4pZm47JitMSFIkZTtZdGZYLW9KYidERls8MyonUjcpMzJHc0Q2aj5uTG9uXyklL1lYITIyL1sjO05YcUxUSCxOPGhdWWpeU19UIiY7TEtfKU5IWUZBYVhfNFoqUShMb3VodShYLWZGRkk3MVJnQTEpOWZTOk80KUQtWitWRC4xZ0RLQm5pQipfZnBEUlNGZzRRcl5zXGwobS9yJCpSNGJPQjw/WmszVC5kbipmWU8iJG5HVjciTzE7bWo4UD4sW0thOldBTyprVSZCP0xpLTFIWT1va2t0cihfQGw4fj5lbmRzdHJlYW0KZW5kb2JqCjE2IDAgb2JqCjw8Ci9GaWx0ZXIgWyAvQVNDSUk4NURlY29kZSAvRmxhdGVEZWNvZGUgXSAvTGVuZ3RoIDIyMDUKPj4Kc3RyZWFtCkdhdD0rPkJBTGgpTF9AYHBgQE5tQDw9bHA0RF45OU04cVxRZWU/XiZlZVRvdWUzSVpCREc+PF9MQUNMaFxjbjdRXylsNT9IcExaJm1ySF10OytMYCU2aVQ0dU0vTU1LZSMvO0VMdXAycFA+T1s8LWksZztxWV9tKzQ7Zk5BMyhdPHVpYyUhdS1aUClkXC9rQSFIQDlwKCNXdEhHaWQ9P2kzZHU/JENgTmdqWk5OYT5KaF9NN1FLcS9YVVxULCZzLEA2PDErU1NPSVlOaGhuX01raVZQQS1VU1IwKFlnXzJLUFphRkA1YnEuMG89cG91US1qbGBZIzU9QyQibEhgXSR0PzleQVJmRjZcZGxfaThnXWJSTiglQXJoJ25iTT0mVG9oYVBITUdHb1FhYT9DJkhbWE5VQVAsalJMTWhzLFxvRWJSMiRLN2lyQSVhbFRpWnFuNCxOPk1KWEpnSGFtckUlTDZdR2ErV2NJPFhWcS1RcnJGSmNFa2FkSmBRUUFWJWE+a2UlN0E2T0tuXzpmOV48YTFeJC1LZUU8RGZPYm0vISlqREVBWG5CV0FMU1NRWDdwYCJhNCUibmAzXCItWUtFa2s3dUlTMDlVbGlkNS8qSjxOKCZcMHA/R1k7IiUmUlI4cGkxckwpZ20nOVdtXC5sLz86VFYiNHBtJiVEKTJqVGcxP2dPc0MxLmZjJzE/U2wmPEs+PDcxdUU4YF4lbHNyO0RsJjVsWj44JmdEZWolMEluYUJRbSREdVhdUG4kUEU5bUdLTXJTX2RtITRuIkFSUT1YJjlnOEVeUGMkOShVcVUwIWtLXSQ6Wz1DL0RlYl1wQXBCYWFKPEYlK2dBRmJWJ2xJQWxwTk4nTC5EQzI6UUZEUilwNFBsXC1EWFs5Tk1zTC1uLDVnT0ZBWEM8JzBbal9ya3UkVWkxKTBVaFFvRiZiMDg/R1c1M1BwNEl1OmxBI1dzKmEsSjo6Y2ZpUFBWXkxLYl0qMClvJl01XUYsUk9GNFBrUTFEO24sTGA+QE05Z2BmTGYiYCxjYjMqTzZkTjtvKyhtai5gZytzWz42JUJCWGNwYVpsMTZiNGUkcjVOIU9rb1c5I3MzTy9JXFlmWmJxKXJXUFBZOWhbWjZEKGxIQl9XQikkXkFBV1NKImBpbDoxWkFqX3A3NSRIbywnUXAoMDc4XUQ1VWojKDdYSXBIXz5FTnBjbjdsXDJgU3QxYFQhbmIrUEh0YFs2UlYqY1IoTi5OJUs/bj5mJXJQXUc3Q1xLTElBbGNmRilMJVIqJC91KUhiWlEuXSdGODBSOVEpaWwyRiVUNS9lJ2dFTyklXi1qdE1hSFgmOCdxR11lYEAuL1huMWtEVl1GQlBva0MwT0ohdVxXRlFxVyt0a3QrO3RhSTFiVkUiQkxiUWxaQ14sJ0NjJzwpamBgKWhJV0YjcTpTXVw+U0BIb2Q3WmxGTCU1ajJmY0U6TipRK2dPOzJIZjMxRTxHRztgM1puRkc4Um5hdDVaaGkyVmVrOTpEYUlcLihJZHJdcCtdS11fPDxVbzNqKG8uZ1goI3BZTks1US4uNTk8SzMjTExzLDo2L24vKDk6a2NjPHVSbTpWKTA3PE1SY0FjYmksZ18uN2otaTdPUjQxMF8sVFElbmltXmosLk5TSFNLJWosbFBaQUVMSWhVVFJDa1k1a2gpLmBaKy9UVyNIQzslUVArTSFjX086YzFgcC9kQiUrNC5yKTk+NF0tPCJHQUBkX0RuXGtxU1xfXmdYKClXTTV1TFE5Ryg6LjJuazpFPklyciREN0BDcjl1VEJWUi1gUXNtTmpBVmY5ZmovMkBNIklBbClmamltMVMsZV1pUSVWU01cOk8rUVRnX2UzITlUL1UjaE8kTFZDVmA+WlopcWJiWipxImYqcXQvNGZeSE4wNithU3IpIk5FPUFgUk8zMkxZMXNKb2dYOzMuU0kydDstIzZTOWhcX24wJyRhLldbdDIuIyJpX0UsXjU0PzNBPUlsQighNTo8Z3FhKEMhdDpUVy8wNTokPiVAU1VzaCJKbUg0KWBpYV5LXG1bM14+WD5NTiEoaFYlcFQ0JnMyVjwyIy06QTJedUJrTDhpT002KzE0WzIqZElJJ1NTcCQxWkoqcldXJVI7PiZFVmlkNkxIJDBcWytkUUI3PGE6ITxTXCdaNVxjUCxUaTAmLWg2KjpSWFpZTGJlcXJUbGwkRmRKJjlgUnNNNG1EbTs9TlYtUF4nYlk5VGJJOi1IViFEMy0iMklxLmxlSk9rQUhBcyVSOCg4N2RjJUVdJ1tTM1ohI1tmMGBxcSwqVUFvXTFEb0krS0E5SldaRjctP0FUamEsQlZcM3FEYUg5cDNlZm1JWS01V1VoXGZuRClBLz5SNHUnLU9VbWkhc0FAVCljNEU1Z2hCUz4lR2FZXkVhU0NzTVlEXDFmaEBranI3IlNGLSwpNz5JKltlczdtKCRZckFDXiNAOz0nbzY4OyYtX2MwX1RDbXBCa0NmOU9fNEY/P0FtQkNxb2AoZjpNRFI1Z28mT106NiVWOXNQQCNkX2pzPlBoInVrVzIiVi4rMzg5TUY3NDVBS3RVNCowNSNCL2FwcVZtMj9kKXIuYlk/QGhaNk88cG5TIiQlJWMzMEYyYVZsWnNkMGZUI05cUHBaVC8tM2xeTDxJLTlBRWQ2Wi1lUy0qWHFVTiYuUExMWE9pLnEkLC5cbjU9MW9NWEo9OWgiISZPMXNRYms4QEhIYzs/WFRORjlcOyJGNzRKTHUjXS1tV0RuQC5cVy1aTm1sOl1xZWQ3XE9fPktAN3Vlb2grTVNXbltaJFBGRlxUJDovaVBzJC4mJW1MZEx0LllXcVkqNiYsXmdpKU49ajM/QUErNGhsZFIjXXQ5SHFQbFlzN1VpRFdYUDJKQ2srMGJmbFM2ckpgbEAwTGk5ayJ+PmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDE3CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDA3MyAwMDAwMCBuIAowMDAwMDAwMTE0IDAwMDAwIG4gCjAwMDAwMDAyMjEgMDAwMDAgbiAKMDAwMDAwMDMzMCAwMDAwMCBuIAowMDAwMDAwNTM1IDAwMDAwIG4gCjAwMDAwMDA3NDAgMDAwMDAgbiAKMDAwMDAwMDk0NSAwMDAwMCBuIAowMDAwMDAxMTUwIDAwMDAwIG4gCjAwMDAwMDEzNTUgMDAwMDAgbiAKMDAwMDAwMTQyNCAwMDAwMCBuIAowMDAwMDAxNzA4IDAwMDAwIG4gCjAwMDAwMDE3OTIgMDAwMDAgbiAKMDAwMDAwMzY0MSAwMDAwMCBuIAowMDAwMDA2NTA3IDAwMDAwIG4gCjAwMDAwMDg0ODUgMDAwMDAgbiAKMDAwMDAxMDE4MyAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9JRCAKWzw4Y2MwNmY2OGFhYTNmNzg0NjdmMGQ3NTZiYTc4Y2E5MT48OGNjMDZmNjhhYWEzZjc4NDY3ZjBkNzU2YmE3OGNhOTE+XQolIFJlcG9ydExhYiBnZW5lcmF0ZWQgUERGIGRvY3VtZW50IC0tIGRpZ2VzdCAoaHR0cDovL3d3dy5yZXBvcnRsYWIuY29tKQoKL0luZm8gMTAgMCBSCi9Sb290IDkgMCBSCi9TaXplIDE3Cj4+CnN0YXJ0eHJlZgoxMjQ4MAolJUVPRgo=',0,2),
	(195,3,15,'4','rgadg','2022-07-27 02:00:00',_binary 'JVBERi0xLjQKJZOMi54gUmVwb3J0TGFiIEdlbmVyYXRlZCBQREYgZG9jdW1lbnQgaHR0cDovL3d3dy5yZXBvcnRsYWIuY29tCjEgMCBvYmoKPDwKL0YxIDIgMCBSIC9GMiAzIDAgUgo+PgplbmRvYmoKMiAwIG9iago8PAovQmFzZUZvbnQgL0hlbHZldGljYSAvRW5jb2RpbmcgL1dpbkFuc2lFbmNvZGluZyAvTmFtZSAvRjEgL1N1YnR5cGUgL1R5cGUxIC9UeXBlIC9Gb250Cj4+CmVuZG9iagozIDAgb2JqCjw8Ci9CYXNlRm9udCAvVGltZXMtUm9tYW4gL0VuY29kaW5nIC9XaW5BbnNpRW5jb2RpbmcgL05hbWUgL0YyIC9TdWJ0eXBlIC9UeXBlMSAvVHlwZSAvRm9udAo+PgplbmRvYmoKNCAwIG9iago8PAovQ29udGVudHMgMTMgMCBSIC9NZWRpYUJveCBbIDAgMCA1OTUuMjc1NiA4NDEuODg5OCBdIC9QYXJlbnQgMTIgMCBSIC9SZXNvdXJjZXMgPDwKL0ZvbnQgMSAwIFIgL1Byb2NTZXQgWyAvUERGIC9UZXh0IC9JbWFnZUIgL0ltYWdlQyAvSW1hZ2VJIF0KPj4gL1JvdGF0ZSAwIC9UcmFucyA8PAoKPj4gCiAgL1R5cGUgL1BhZ2UKPj4KZW5kb2JqCjUgMCBvYmoKPDwKL0NvbnRlbnRzIDE0IDAgUiAvTWVkaWFCb3ggWyAwIDAgNTk1LjI3NTYgODQxLjg4OTggXSAvUGFyZW50IDEyIDAgUiAvUmVzb3VyY2VzIDw8Ci9Gb250IDEgMCBSIC9Qcm9jU2V0IFsgL1BERiAvVGV4dCAvSW1hZ2VCIC9JbWFnZUMgL0ltYWdlSSBdCj4+IC9Sb3RhdGUgMCAvVHJhbnMgPDwKCj4+IAogIC9UeXBlIC9QYWdlCj4+CmVuZG9iago2IDAgb2JqCjw8Ci9Db250ZW50cyAxNSAwIFIgL01lZGlhQm94IFsgMCAwIDU5NS4yNzU2IDg0MS44ODk4IF0gL1BhcmVudCAxMiAwIFIgL1Jlc291cmNlcyA8PAovRm9udCAxIDAgUiAvUHJvY1NldCBbIC9QREYgL1RleHQgL0ltYWdlQiAvSW1hZ2VDIC9JbWFnZUkgXQo+PiAvUm90YXRlIDAgL1RyYW5zIDw8Cgo+PiAKICAvVHlwZSAvUGFnZQo+PgplbmRvYmoKNyAwIG9iago8PAovQ29udGVudHMgMTYgMCBSIC9NZWRpYUJveCBbIDAgMCA1OTUuMjc1NiA4NDEuODg5OCBdIC9QYXJlbnQgMTIgMCBSIC9SZXNvdXJjZXMgPDwKL0ZvbnQgMSAwIFIgL1Byb2NTZXQgWyAvUERGIC9UZXh0IC9JbWFnZUIgL0ltYWdlQyAvSW1hZ2VJIF0KPj4gL1JvdGF0ZSAwIC9UcmFucyA8PAoKPj4gCiAgL1R5cGUgL1BhZ2UKPj4KZW5kb2JqCjggMCBvYmoKPDwKL0NvbnRlbnRzIDE3IDAgUiAvTWVkaWFCb3ggWyAwIDAgNTk1LjI3NTYgODQxLjg4OTggXSAvUGFyZW50IDEyIDAgUiAvUmVzb3VyY2VzIDw8Ci9Gb250IDEgMCBSIC9Qcm9jU2V0IFsgL1BERiAvVGV4dCAvSW1hZ2VCIC9JbWFnZUMgL0ltYWdlSSBdCj4+IC9Sb3RhdGUgMCAvVHJhbnMgPDwKCj4+IAogIC9UeXBlIC9QYWdlCj4+CmVuZG9iago5IDAgb2JqCjw8Ci9Db250ZW50cyAxOCAwIFIgL01lZGlhQm94IFsgMCAwIDU5NS4yNzU2IDg0MS44ODk4IF0gL1BhcmVudCAxMiAwIFIgL1Jlc291cmNlcyA8PAovRm9udCAxIDAgUiAvUHJvY1NldCBbIC9QREYgL1RleHQgL0ltYWdlQiAvSW1hZ2VDIC9JbWFnZUkgXQo+PiAvUm90YXRlIDAgL1RyYW5zIDw8Cgo+PiAKICAvVHlwZSAvUGFnZQo+PgplbmRvYmoKMTAgMCBvYmoKPDwKL1BhZ2VNb2RlIC9Vc2VOb25lIC9QYWdlcyAxMiAwIFIgL1R5cGUgL0NhdGFsb2cKPj4KZW5kb2JqCjExIDAgb2JqCjw8Ci9BdXRob3IgKFwoYW5vbnltb3VzXCkpIC9DcmVhdGlvbkRhdGUgKEQ6MjAyMjA3MjcxMzQxMDItMDEnMDAnKSAvQ3JlYXRvciAoXCh1bnNwZWNpZmllZFwpKSAvS2V5d29yZHMgKCkgL01vZERhdGUgKEQ6MjAyMjA3MjcxMzQxMDItMDEnMDAnKSAvUHJvZHVjZXIgKFJlcG9ydExhYiBQREYgTGlicmFyeSAtIHd3dy5yZXBvcnRsYWIuY29tKSAKICAvU3ViamVjdCAoXCh1bnNwZWNpZmllZFwpKSAvVGl0bGUgKFwoYW5vbnltb3VzXCkpIC9UcmFwcGVkIC9GYWxzZQo+PgplbmRvYmoKMTIgMCBvYmoKPDwKL0NvdW50IDYgL0tpZHMgWyA0IDAgUiA1IDAgUiA2IDAgUiA3IDAgUiA4IDAgUiA5IDAgUiBdIC9UeXBlIC9QYWdlcwo+PgplbmRvYmoKMTMgMCBvYmoKPDwKL0ZpbHRlciBbIC9BU0NJSTg1RGVjb2RlIC9GbGF0ZURlY29kZSBdIC9MZW5ndGggMTc1MAo+PgpzdHJlYW0KR2IhO2ZnTVliOCY6TzpTbHIwU24oOyFYUyUoKFFGLF04NExCT1csPDc3IiNzUSxKM15PSF5DXHJxSHNQUj9WTk5lcm5OTS9RZjxzZVhTV1VGLCMjcjVvOlo9SE0vUDloQ1IlQm1nMTBQL1hEMzNLOzZDNW9QU1tCckpeKTQxMlxkYEVZRFQ5MEVjInNeJ0MhRUZaRVpzSkhccGpTSTtmXF5gbDRjV1t1VEhoV3VfVkdvZUw9OkRRNS9VSi5MVTxyQGdqaHBDQWwnKCVKOz1xRkUvJGFLNz8yW0VmJGNPXU5xLmZHYWpiOkpiRjUjUiRtJi1GX0Q9aV81KE45SFNTK2woOkdCNjZsVFtpIjZJY2BjTXVjZSc0XixGbG1xWURiZl8wPmMwM0wlUmBRO0YxMmM7I1NKWmQ3OigkZFErYnVlRVYrK1o3WXIhTVVaRlBUTEBbcUNhSyRbRHRralwvLl9ZWzY4L0MkQiw3Zm9hKkNQK1QwJXQiZ051QTtXMUdKOj5MU2psNmpgUEkmIjs9IzhaJFAjJF4sTSInVT4hVE1eKWNOa29POjk9KkIqN2dGcTFKcSUlYEEmVXFLY3JVVltpayEpY2FELEZRXVZfOFVxcEw7KGtbMFInQ0BCbGQ4RGFKUVgkWFl0OXBeN19TOUFBaDlMZms4OENFKSMjOF80Sl1QLkNlVis3Yyw1QTNmcEVgTHNGP1BgLjtwV0RQOmJZdCdySFYha3ErLVVaRWpyRjtkJkUpTT1GTkNQX0ZlQGMyOmtDPSJuXEhXQShOWnNVYEBHaVJQXEBzRycmQFVJK2BwcG4/bl9mNmRFcT05R2A/VCRiVS9RQi46VyMmUTVDbWBUYUFdO2gpTUk9YWBpdD5hOEddTF0tS2RaI2Q0JUNFWHNaQCU9SXU+Ymk0R2w1QClKT1RJOjowLlNPQ3IpNzsxJlBgY1siYClRSjRDMWw7TEdGbi1dcWFhUWAqOWlCQDpqQlJxbjI1bWEhSm1YNj1YQlNabGBnWzdwUCJqNGtVRG44MDpAbmNyZTdPIlpLT0c8SkdiIiFMbD1WJFBDajo3RUYoLzVpcENxNSNQQzYwRE5BZjY5Xlt0RVZNYEZRLiVAODBjO1pTMVtGQ1RRZUxeSGc7VmxxZ2sjYjttL2oucS9panM1KF0pKjFEdTdPQWF0YFRJQjNBbyI1dTNvYUMvM0JeXistMVVVOFpvTCd1N1Q2MjgzO3FHczo2PzJhLlVucUkpXy5jNElsVTZTaTUzTFVzKyY5YWpBM291WmolWzc6Qi0qJjovR2A7SS40V01pLlhJRTAvSWddPzBzUSlIXXA4V1pDayRFSyRsM1wldCpLMiw7NG4/WVlbISlHX0xfZFksN1dARChaa08hYi4iSCYyWUdGW2w5ZTljKC5MN1wjYDRlRXFPalVAU1wjTlglPnV0JitTPkVqNDhlXWUjayNQQDg9VStwVD5pOlk3OTVDSFQwIlBEYl4qKjpwK2hwRG4oWWAkYV4+Sl1LaVwuXDVPOkEhc1E2SUpzW3EiRXBtTltHaXBKVk86JElyaWhARChhXVEqYSRDK1xfVUxHNlMwPF84My0/bVgiJVFrVyM1R2A7LDlLJCVZaEIvakJiTCdWWkg4ODZxXzY5YVRsQ0JvM2gvWjk+VTlFX1ZqXTptYCQ5Pz8nQ2x1aCEjRlZAa1xyaS0/b1dDQTkoXXM5W3AiKkVPZHJbMjJUci06NmRoSGtVO2FDWVZeMW5BOSU6RDk7RE9YclNpJ1dgJFlOSztUJl06azY2ZktMLzQ+WyEpQkBCWGgyanImJkEiKDpINS9dbTUsUjAkLkwrUCkkIyc/dFZLbDFcIUxaZ0FUUTRgO3M/a3QqLFRgMzYiNjNSZ3Rbbi5pdFwvV1ouTC4rKkVQbEBbWUZkZSYtNmErYmdJc1hFRTJuJzAicl9PN2lyOnI/YWdFRTRSTCdRUFZVL3Vncz81TjU2bGAibGxYXDwvMTRgbElWPHFRSWk7MzlzUDpJWnVKYjwocU8iOWBUcWcjM2ZqTFU3OidEamRXbTk2bCcsUmpARUZbP2c0XF9mJTBCXVJAPnJJJWYnMz8lLF01T1Ffam4sRjFmX1YiX1ZPcURIQUgsK1MpXmVYQEouJks7LV83bklgT25fUkEsPjN0WGJBdWpOVCUrQCZKUztBJ1QxbywkJiQ+czdsWCluPXA6aGQtQiVlYGpgPCclZlNtMW5tOD1mPWJNXyFtSTFTX1c8U09VYSdNV2k8dSw4LDMlK0FkQWdvQjdjX2ltWm9LZT4odF9tQFlJdGlpMDNfO1pXXVktcnJKMDc8RlB+PmVuZHN0cmVhbQplbmRvYmoKMTQgMCBvYmoKPDwKL0ZpbHRlciBbIC9BU0NJSTg1RGVjb2RlIC9GbGF0ZURlY29kZSBdIC9MZW5ndGggMjc4OQo+PgpzdHJlYW0KR2IhPFNDTiV0SSZyKzB1PSJJMUBuMG85SV1wJFpxIWJuMSVrckNJcj46Qm9kIzZAUUhNQCw4Pi1vbC9EST4+MHVnNTM8Wl1yJHI2P1I4UXNCNkpLal1sP0ZkLF5sYFVEblplQnFoYitCJW5cNiUtQzcnUGFHUyloYE8hXDZdLURJcToxR01ZXiVGXXInMDBoOlNPXEhIRjFAWVpEJiRUVlRLYkhvJFlScGFjVl5laEZOVDFcb0tBJms4WDVTLF1VSCNeaVxYalJydDpNW2A4bUNrcUlmWm1qQVFkYlBGPD5wbyZLPUtjTFlAWkFgRzBzZz5MXGM/PlY5blpGLy9LcD0hVGAwJkJrTUFfcGNNM18/KkRpPy9MXSg5OSJEb1NPVF9VLDksUzIsczVMRUZqP281UG81IURSR08kWC9PcDlwUm0/WmplY0sqWXU0KUtQODpPdF1JNC8taEhLY1tcNiopMWdUaUZlWXVJQnU9NE09aWJlJT5ULy9NSWBvTV1QKU4rLVdVKCc/ZCtBWz9OXzJEcEYjTVJGZyVtXkUmWHEqYGVAZW5GQTNLNTg3bipsW143Rzd0MjVKRzpVPztVKVJzcU90Wj0zayw0aGBJLD9PI11LNXNYNipSPGNYNnU7QFYlUE9XYmcvQUk8OixFbDcqMyFUUW4lIXFnSWkzIypjbFBFZCNuIkRvXzItOjpHJEBhdSlJLjE8RXNsOVdxPkM7Wy9ZP09aXT9VIjpuM2xdZzVTImEoI2M6ITNoO15pTmlpaGdHIytJLCpQX2RSRU9hVjo6RyRAYXN0VzQ5bTA0KHEvIiducFU9UFItPVM2XTwycG9HOi4yZ0llIWxSKi1YcEo1MyRCZWczImJpX0RSWT82Ozw1UU0tbzlnJWhydV9fTSIyK0loRTshOkBxI3E8Sjw7czc/THVlUGU4R1E6LGlRITcoXWAyVlhST21HZTZTRzk1YHMvOFRaZ3RnRkppPiQhVGJJX0QvZEhWXm8hPDBTMXJSdU45JkFGPXV0TXQnQEA/QUdfYC0wbTEmTmZtI3RXQzddPWtuZyhxXnVYSykpaiY/ZEhvKy89LFpbNWBTWyt1XGdYPl5NIkkwTWtrXEdeX1krLkwqZUBxUztrZUcybVpRIjNPbCc3c0RPVShmMjhVUXMwPGluTVFWay9MLzE+OW4mWUI0RzNiMkFxNSMtbyovPTQhJjIyNDxxbGJKVFdcLDlWa0ZjY0FDOmM0RjZPXCNsJz4pQ0w0YVQ6ajhnTCxlT2sqTTlJRjlwTzFcKGZFJEZSKzQxWzFaXzIwI10rJjlsYSlicmY3XlljMEg2a2pvXywwRVM7YSoyalEtREVXQFZMUUQjKClmMjViJGJyOzZGMSU6Z0dNPUlII20+JmgqNWNFTVxNSUFwSTNVL2dWNG5WbSlKOHEjKmNZJE83JSpfMFZDTl5wR01kamxXNVs3TVx1WCI3WWtHaiZnIm8/NDsyLWczQyVOYDlZZiFyP2lvV1A3SHMjOWhMUHRdRjI4alBrblpyWEgiXmxWJic4PSMwIi1LOC09RE1CPCVkOUxxXWJsITEzTjA2KWRJczJtX0xUTTUvP1s/TlJLVGouISQ3SWg8QzU2NV4/YVZlSzNwbmNKR0xHZyJPM0docFJHKFFdWGxRaFFBUW40VihqOGdhLGRHVnJ1NiRqRmcvZGdJNWlIKEVJK19NQTImMi5cYmRMJ3FlJD1vVlE7ITc/ajQ9TnBsVFU8Q0QqPGVTc1lcJjY2XmcoNkt0RGt1OF8oTSJhIzJvcDgsXy4sI2BAIXBcYEFGbkRRcDpeKilvVy9nOmZNXmtBXktXO3NmQVIpMCJqOVxndDQ6YkgxSFBXVjJyUi5WRzdHQG9FNV5gWF9aKCVJVCdpPSVlM2tFY2xXZHNYP1dbXDRDSUpIPylWJWA1SSw7ZlAtXmVcMCRlRnVSPjY0RTQxaTxIVSleMlNfJ0xYVlFeWVtOKj4tbzhbWmhydV9bTSI4QExQJmU+blxjXC8kWz1oWjcsTTxscWheZEByMGBbO2w9USxHTVcvJC4lLXVPOT8hbTRiJzdzRE5qJzJUX29kZkxVMWtmQDpOKV4tIWxcSU9HbD9GXlElITw+ZzMkNk1yLDRlMWc8S2FlUGQ1YWAjQmtZQVRwIW0zbDxDPl48PSpMTWYzWHMiU1VUM1hoNnBcTzRwQEs2QkFaLC1fWjpfLyYhJTE0JHFSIi1xLmJnRHUhXyQkIVheZFBJR0NHO1VYU0RiKVJnZUQ7QCZlZSFwb28/VCRyJSpdOk87MHNGaiFYN107OF9HYkUvRDNlNDVGcTZlP0csNzUnbT0rKXVgSDNXamk3MzBwXDInYzdWZ0knYW1cbEJAaiY9YFQ6YChmZmEjZy9zOSFLXidWXW4mcD1lUFlDIUtxPnNOWEIyXG8nOzRmX1NKWnJTUlFlXjYtNEc0Jmp1ajInL2M/MjBeRTQwUClQYFUqRk5nRlRCOUpmYDUrZ3NVc1BrITplQ2EwKU00YyVEa1BOXDd0NW8zY2pSMkU0YW8sYmFVJzUkYlU6O0VzRD5MJGEwZVVfaiNWN1BlOz9dJHRDZ0lLRlE3O18uIUFQXzgpXFdcOGU+bzpRbV43aXUlSlFGKSJLU0REKVptIV46N0oia2diTlpvaU5sQlYvPnM0TUhTcjkkcEsyUCUqXitlNFE7RV9lUGdZSmJeXUYwP1Y9Pjk+P1BGNmdgSCowOD1QKigzRCNPQjokTTA4bGZTRU8oJksrInMwKkgsaVtYPy9NXlFmJ0k2JixTYT9YQD1TLnJdZipSZTtXR1htXS5yYCZvYi5gJUppOmQ2KGZkJXMsKnUtMWE/LFpxXS9VTTJlRT5MZ0hmbD5JU0AhNHVtOSs8L24sPW1jTyxeIk1BKnB1RjdWUzQtLmYhLS9lQE5SODlvaU9xPFQ8PnJdTVpzNj5KSEskZiM0XzpjLGxJLFVsOGUya21XaWdgOU9qWEE8ZzNmXixGYzItVDEhIypWNSQiPDtlRiZdbExpOTcsYW5ONzdZaDxVWFhrPmowbWA8JUA0VVJTdDk4ImxTXD9NSCsnRVcmMT1Dam5fRylbXkNNZipMZGMna3JoKi5cUF4iOypQaCVwK2xHb1ZLVlhuMCNNP14yZz9OIjA1YEImS1EvLi5PLj8xI1gjZUVuTUM3YTZNPVY+Pi5UZmdeXG4zJT11PjdqT0BYKkAtJl5JQmYvWDJNIl5eb2hkN1JPKlVgY25vQjE6RGVjXDBFb1RpKFY4PFkyS1wiYXRMRl1AVV5oVF9RTklMN3M4KFJKUWRrN2VcSHBbdUA5cHFzSms/MjM0KVAvL0FUIkdLUDhwSV90NGw6VVM8VV1ENVNGaCNvJCFlOEQyYV9GLCM6UklUcnJjck9nT0s8SEMhYjpoQUdmIWs/VVxfKSMqQDElYFUoaXFQRWpVdVJMW0BKZEwqJT8nJ0dhYS10ZiRZTzJcXUUlSVFva1pIXy5jWD0zOEJHa1FTTVhtWzgtPURaaj5mQWIrbTomV21fOjtRWVM9NWtGOUYpcCN1TlBnZ18vIjFbPSRQSmttKzAzYzdjJTA3TGJfWEE2PyhjWWQzIURwaU1HbGNhVC9bIzhwUGkpbzlcNV5OVlYxJmZdOy1qT25EImM1RCouL0pSODA6IzBFIiJEYFNiWV0uOSlwWiclYklAPWMsMzgpb0d0WXAmfj5lbmRzdHJlYW0KZW5kb2JqCjE1IDAgb2JqCjw8Ci9GaWx0ZXIgWyAvQVNDSUk4NURlY29kZSAvRmxhdGVEZWNvZGUgXSAvTGVuZ3RoIDEzNzcKPj4Kc3RyZWFtCkdhdWFBRDApMSsmQkVdKjtzWzM4VW4nNS8rTWRWVEg6Y2wlMlNIT0JTW2swNmdyTFRXWzY0NEw6P2xiSSFdU2JHSC4iVkdgWl9TaHFRRXJzQGpQbjZAJmIkQkl0b0pnYjVlLUssIVtbYjxePFRMK2E9NllfPGclc3EvTjYqJUBhclkiaE8xNExZQjFPVmJXYFNsIWNmZj0ibkNubF4uO3RmT2RicWRXQGw3OFg0dSU1aVYta0tVKFh0I2VpWHBYOmtIMD8zYT5CKUNCR2QjSCohYD8pQnFcPz9HSzBZMlBjVihZU1FTZU9oKj04V2RZVig1UUg+ZTBJUW0oSk9CcEJvQXE7bkw4WCNfTy41YWlnc15YYTdZUFI0UTMhcCZWUGo3aiJGTjQqPmJmMmRxPTNmKWQiKkVnVl5zMz8+bVNZNnM9XTk9RSxqW0AlTFlPWiFEUnFQQDhubzo+RUprTDlcUSM+R2J1VjlsRWYpQDxPQCQvNTRbcVBgZlNpLyMkSSgwSUFbcyFuWGE5ZmlsQksrTyktO1cqOTlcOVpIbXNCLU4jUD43cEJWaj1jJmBHUiNyVlxxKm1MbDAubFopJChYPS47L3U3YGRyalVeJ0RuPDd0Pz9AZiopVHNNK3FcKU9dS1VLY2RxS1JZdVNfQ1hGcXJzaSQiXWg3U1BSQClsbl5VM2lfbjpRYS4kMGZuWlJiOWhscl48NTFBcD8jPDYiYztVJE86TyErQiZPJy9dX2ZUS2pOMC9pdUNCViROSTlnUyItQFhybV1AbDghJ0hRLSpFKDU1J2dOOGY9WjhhIj8oYSQrRl9cZ2VbJSY6I0opKEkmcFpmQ1U3cURDKGM6WV8jISlpNlhKREgqO24rZ1ZGcm9VLyxiQnBlUV8wVDBxJlEvQ2ApXUVoI1RvMD5hXzBvZ2clYEdMc15HbiFyckNcOl4mRS4mcUVuUlU2SUNLKic0ZERyLkolQTIzI3EqYiJOY1I2U2MoN3RrXGg0MD9WZEMrNDcjPzxRNVJaaF5SVCtYNT0kaThMIU4rY1hUZCs/NUhAOkNfUV1MZiZDOklsTUMiKVs2NTJLWTxSYUQydVRZVjZmM0Y7IVRlMlM+cTMlY01zc0U8bUxFYCQrMiFNKmtDNENoZk1xXC5fVz1WakxPNVNsVmJdPFdAUixyYCRxaVJHak9PRzciM0ZwWDxvI3FKTVV1aFVuXDMuNithUyosamZkKnR1L2VGY0xsMydfT1J0LzNHdGZQNFBvckdQNmItNDsrOGghU2BiUiY2QG1SWW5DSVM3RzVBYGU2Jy4iYkhPXCpCcFRLXUokTmY1N1R1UlNMbHA7aC0iNzpBLmpebm80XG8iSnAjWEwnUkEwMzFwQGUwIScuQ14ibTAmPE5Uc01ebyk2UCh0LSlfb29oXyw8MU9iVUpNS1E2XGJIS1ZqIiZdYnJYPls8WW8+OXIxMydHOyVEJFdZMy4xITxQYWZXckdHXltqJTFsPTdZNVAzY1NfRDRpbiFmaFU1cS9qWCNqKk5zMypAQWIjQ0hTUGVxXl0sZy9GODYsWzUkWFRfUVRfRTFxUC0jWjdpUy5KLSZRWlZjVnRxJkxgb0hWSC0xS1EpbiQ9OzNgVF5Eci06WENLcSUmKnArT2I+W0cwUGU1Qj8hKGlQTVA5L09GWSc+QmF0LjAyaUJXUWZ1VnJtTVArPG0hSiJiP1phNGxXXDpCKC4yWjw8WXMiTyRVRTEsPC4jLGVTM2NnZEwjYmVcUVBQREloYGAzZG1jU0Q5SVgxaXFuPlpJREI9MCZjVWtMZSlLMDM/P24rZkQjNi8nUnRwXiFISW1+PmVuZHN0cmVhbQplbmRvYmoKMTYgMCBvYmoKPDwKL0ZpbHRlciBbIC9BU0NJSTg1RGVjb2RlIC9GbGF0ZURlY29kZSBdIC9MZW5ndGggMjUyMQo+PgpzdHJlYW0KR2IhI109YGA9VyZxOVNZa2NLLE1bVlFGTCpJMTw7QSRUbXJBZV0wbEIkKytYVFwtJU9PZTxIaWpiXEtjMWdsMDkvVyxdb0YpOHNdOS1qRSNsZyUiQm8iXylnQjBZUF9fIyQ0Z3JsUD5oTFYiODVjakFcISJ0b0A+cmNkQD1TZFtxNSNZM2haSmwxR29AMVxNP2gwLzEmUkBTLis+YDdQL2FIJUo5Vm40XWpEJFl0NCJRO1J0MztucHBWO0IjRD0xSi4+IVc3ZFwlOz1yZFhyIShtQEclM1FcRFVQY2dsIkI7M0ZkN2cpSksjWzIhJGAxUls3S2UidHA9UmQuSVRYXDZwNkw2TWhmbUIsVjZoYz90MTMmLD1lJF9JdGJJI2BecGoyJ3QjRFNEcWxKPzlKdT5jZytMQERBPmlLcHNFTmkiT2dcaC4zZmtDXCpWXXVvJygiZmFSayhAclEvcD8xVmE2VDkhX1NSQlJnYFFwJi9yVUkuISZWVFs8YWUyRDtCOU9ya2xWMS0mI1REcG0kNj4lQSE8L2dXJTBfZTFQdUE6IWJdUGE4L2VAKV9jNGJZW2RoPmNyQChAWkdATT83NTZ1R0hiN3IzcydQMjNzQVFbJnBpIktSKFRCbjY1dVMibS9mUklaPDxhJWUhPjAoQSc9XEpZYm5MbzYqKnE0Z1wlM0FNXi0oIikoLyZnWTNwcWktcGJzcU0mQWZkT2BYMVArZyNaKmJkT3VxWy8zZTxPbV9CKzVvPkt0QCkzUnEqW2AzZztJakYlOGdZU2dPS3FZZVFQRVhQVyZZLSMnTFo4OjUiT286YnVwJCNGWVI1Oy8yblVuKEZfLVBDRmwmP1tvNkNkbiRAJU8vQ0xLY2haL0BfJDtSMm88dVAyK1tRVGpvOEorRV8tcVgxYS9oPjJ1I1teRCtlZUI6LTtKKiNQYkJtXy0kS10mLCJkO3JEVFo1ckIxNkVcYWlyYzk2UzdBR1RuVVg5bGB0aC9oM0tuTkEiajp0LU5yN20qTlZjTF0mTEk4XiZycWpOLCw8QC5ibUVZYy03LWM6PFJRYmdhK1U8KjwkRj5SVVRlYyhFZkVaRT9FNXFnO2VqNXFPb2BFZk89V1gjW3AzbiRPOysoNGVtV1tZVU9gQWBcTVgiNE9fXTQiMTNqKXVXUV9wODk2YGA+IUxNT2AkSytAOjRAK0ArOVdKVChHbzpNO09BcUJqQ0k6JHAtPiwoak8ycSlHaTZBQyU8JUAzKCFNOlZRRkpJS3UiLW9oXmBwKD9CMmRhcFNUalVTajRsU2QuNz8wPlNsM00yTVInXEo7N2NgVFRAXFZUXTcuTyZSUi0zJU4hXCsjUHAuc1hGJydaPlFiZEdKYFolPXMtOz5IRWtQOD8rJ1x0azNjJ0lMb0AzZD9eIlEnI3M8Y2RNb1AkUUZOKFBTVjtFPjt0Qi9FaVcjJGRZSDBbUTZbb1E8PyU/TTInWSJnWV4oV1YxMWZeTVEsImBhOV1qUk1YIXNtNFAlYS1QVyktJW1NJChMbCN0OTs5MkBKJjtTMzBmbEsrLnNHKHUkQS9hRG5JblhmWDRZOEVwTVRoMFooKzlnKVc9aXApTHBSQmdedVpFYyUwOXUuZDc6c2JBS050XHJuRWtSXldOYD4kUE1uMXJWOyg0cVJEVFwwK0EkU29dR1NiIXBiIVtAYEM9dENnR2JhSmBRb28mdXJwcUl0K1szUGJuZWUqMzQqYykiX2lyK1BIb2xXL0k+V1YkVk4ubSlZamooXXB1YzJBR1QnNyNcOWZuQzhCMl5zM0NwQGtBJyZuTE9PaDpgMjshPi9tUiRfaTNMZTlCcllbb1djMlJDcnAjIyphWjVVMkhXKWZzXldqVDZwRFBpS0c5VlldLjFIWC9NWWE+akohYFlJT0MwbD0iaVYyb1A0NTM4aWA7bk9wMCdCKCVhTlhPO0MpRVUyUG0tbFUyZT1aZzBXdXBYIVZpaTxfIyQmWlNYIjBKMiwzTl81Oi9fNkpnJkpyWlp0IWoubTI2Um9MLlRAQW5pLUFAPkRRZmxROi5MYTFUOVZBIjh0S0smMVolcFVlNXBqKkJDWixbUXQ3Yl5hIl9dViMqRnFwPGBfXC4nSjpfNWwxPiFCVEw/Vy0+YFUjL0p0K3BpLGFqJixNVWtkPEdaaU83KXNMVSwmIjFdP1MpRVMiUz4wOjNZL0dgTlpIS2dnJTZoKlNdSiNVaTE9Xzxiby1VQz5IZiVUVTIoO1UjKlE6ZXBSND02aT9pUEk9TVIrazUsLSFZO3BcQmlXPCclbzxhYlIsPlJfKChETz1kaEFkImFGTmFJbW81RUg0OkRAOlRMN3NfQ1pwXSlgMj0qIjM5dT1cQDQ6UWdHQlhvZXNKXl5LQDc1cSZUcilqW1w1MCIoQyUjaylhUUBeLV9IdFcidFNEKDVxRzwqX01fMGg/U2tIckcpamVGW1wpM1pNZVBdVig6ciNiUzFISyU+cTJdWzI1bylKJ0ZERWpXcyc1aTomIlttbkpgYWlvI2s0JSdgWnVhaD1gLnNJMikyQ19QXjNWSFllQEdAayxXMWdyVEloWUA+ZVNyZFEhMyFnalMzVVBwMFc3OW1nJmU7KypKXDtJaFlsRVgoS2g4XSJdQipNJWBgU1ZaWUsqWVwoYTZgQVBnaGxHcmMsLUk3WWtodClVYTJsJEEzJiUrVDkzUCpyRS51LShTUz5kSCltZ1AhTEpsN0pacFAtdWYuIUYnMjMiNWlWWTowQztKaTM0UVUlWHNjUWk1cidqaE1uQFZWS2hwSiREJ3JKbUk2K0lkYGk+ZSVVOTxvPyFLcURLV1FdJjVjQCo7cSlJYj1bJTkwZSZwb0lRRFNgck9GIypWIjM5b2VsYlgvXE9iaCJqKyQ0RCpSVD1qTjEzXzZKQ15BcVRSJlknS09fKkVnOWo8J21AO2htXFNWZD1vUGlmUiojZGJwOjdwIT5TUXNAJ3BLa0A5RmFuX1lrX25JRnRrOkVnTz9aOzxmUDBmWCJxJjoqOTFxQW03VU05cE1TL15YREYkci8iK09jQ1lsZm01cV5FMnRFT2tfJTFyUFgtYWd1I2pdV2p0PjdecS4zMTVDNWwuXVU+blBfMSdxYUpOS01BWT81NTFhK2NLbkFyNlQyWnRWRTI9ak1YY2MxaDUpODJvQV5jMlJcKyEnUDhEKjlVPkkpWF50LTViYllBQkJlZkFBTy4rT183ZUtWV0JQdHMjSDBnbzFkNzVpX2hOTDNnblZERDRBPkRJNC5jSlsxYG06ck8oKGdWOiM/LmZfbixzJUhZQFdxKjpGLStSSCZfTC4rJmdVSVZuNGwzO0YjdT9QLWB+PmVuZHN0cmVhbQplbmRvYmoKMTcgMCBvYmoKPDwKL0ZpbHRlciBbIC9BU0NJSTg1RGVjb2RlIC9GbGF0ZURlY29kZSBdIC9MZW5ndGggMjA0MAo+PgpzdHJlYW0KR2IhJEk+QmVkXCY6aVswLyo4U0IiNFZPZkRiN04zZ1hCY2hMQC51SUtJb0hLLzVdJnBqa29PSiZETG5hLTk9a2k2UEFtKjdQamx0Uk1rKztMRy1GPVMpc182JzZucmlLLS5tPiMoQUNiQC5GcC9TdCxeQG5UVDIzZDMrQzIuIlE+IkxuY1pybk4iOEs8TDhYPmFkaVI8T3E5YSM1KFIuTGs4RCNVTGxYVDxQUyldN0VWYSFUPXRHUzUwX2thNV5Zaz5rVTZ1Xj5hL0ojK14pQi9eQkZ0KCRBRi04Xyw+bCYiWzNFNy9SVXVmNHEtSC9ocjRwam1ZQjdiSV0lM2UrW1NlLEhRTT8qOyhXUzRnNl50QWhZSEE2XjExa1o3aTFvYlxVVz8xLzlmXklkYGxVN21JdSlBZ3FrPD9ObzotLzk6Y2NsZj9rbG1BXzVKW1FTLWgvPUwqZC9ZSkpXUVowQ0IoX0RMUmJyY21tci1WXVtRLnFPPFRjVE9mOUovPkhATzYmTExaVnAvWjUsVzFaRD09ZzZQW0E1N0AxIT87ajNENSszOWdwJmdkckBlW2VMW2dzXHRSKiNWNmpQZVw6Z2NjK0JmUE1gWFVmLj5MPmJsXWBDLW9jWCYvKTknNVtNP2xhVzcvSHJQdFJZOkFsMFxSb0dSbi43ZSQqLFdoVEZiSVBHTjAzY3BONiJzYC0xIzJvQl9QN2hRWkdQOCs3TCNqNUQqPGZ1YDM+LFxOVlo/N1NeL0hdJ2RNZHQ1JSUkaylEMypyZVZzN1FGKlBtZzFrRzAmakpTb3EhZS1dI1tBPyZBRCQhKypbO20tU0knQ1xsYGUubC5tMmYkLGEtb1ZCT1duaV8pakkpOilNVmshQ1FSNkxPSzdWJGtEN2o3YFZZbFZeWmsrblxPJElPSkQqKE0oWFAvcjJKMltedTcxIjVNUDxNWSoqXDEtYCdLYXVAU040cWNwOVlqUHA4T1E0KDxHQ3BscGBcLmEyKFEwQD9aQk5OTG9TUT1XSFRpOCw1R2hnaEBeKDtfVC5QKy5rI01EIj5HJUNMRk5WaFxESCdtbW1tJmFmWGV1KHU8MjYuODpIal9QRkFyX2hLbSoyUTVIN1JraCQnQnRjWmVzJEhkOWcpTThnYzc2TWhuaUQ0TDdhO2hsZTNhJl84VUhdY0xNX080U3JxWEciZyg6Xl9QIkQ6R0I9OyhqWVdjMTNbIjhvZVdLZ29ETV8kKlVqVk50K1tBTEYsTjhkMkcyUmloY09ZRyI6Zi5HcXBtJyE8I2k9Tlkzc1ghMyNuQj49cnQ9O0RcZSdJPzJaVyJeanUwcD4lZClZIjovVTdvSVVtaUo5Q1lLbj1zUis6JHEsJmdyUilbUmQkZyRVXEU1QCNvajhnVlksQWxyVGRsMVw4My1AVjFYRjRROjpfOm1bJ1A5bkE+JnFycyopSnNsKypST2otNkBnJWkmSlVUSTE7PmNEYGU1QzomI21jLWkpSEZaYzFEJkNrRU1KIWtnJ2tmQ2Bqc2tDcklzK0A4blY1ayU1OmBOST01NDJhZCU2PztdZW0uZmtCKTEyJHQzN0M/ZWVoMl8vR15ANVZdR1NOTmc+cSU0JjFLOWt0LGIlZ00nYmwoU1AoLm1Aals/KUpfREJaU1BJLTw4IiYjRXRQTlJqR2lRKm4pImFyJmdOY1xfJWROWTY/YEsuK082W01FITZJU1JEYSlwXCRpPWpkMjAhXlZwViFuM1ppLyJzLEddQGtnTW9DYCYyXSxeY2NpLGNaRiRXa0U4TU5oRTIwTiElLWUzazdAV1FePmZDbjI5OEgvVUctTz9qJ3FISlNmJkQ9RF1LOD1qSyctO18nXW1CUFhMXipSY3MyaV9cKFFWcDJcdFYqcVJtbjRRKkFtV2Q2Sz4lbFMsVic+LGBmIl5zK2xpbmFaUGM4LmE0KDFoblU1L1tbVGtHPzklQFssbml1MjNVTDImM01yRlZkTTdLLUhSLlNUQ0Y1Zj9dT1c1KGBSPjlyRG0rQllWWy1EXTFqU2dDYV8/WHNKInVvYE9cLjdoWF8uUklocC1SZk04X2tRSGlMYCxkR3QuXE0hUkglZixGLSNoaUJvWThUOWZPSjRDcVhuO2RSXixAdTMjIToySjZHTFZrTFJNNl5CRUxOUFA+a2Rbb2RzRTxUJVE1TktnP1w3aDJSbio3RCJkPi8oSiZUSm4jQmorPFBGQ2AjWVo5JF4lNiQ8VmViZmFBWzdGaSc3cUhEWWkpPyhaN1o2KiMiVzgkNTo1YC5vSVFXQ1JTQWphQ2BhYnQrI11GKEBAMjRwQm9iQz8ySmRIYVZALGNGaDM8NiRFYj4vJDBVJiRNMjEiWGFYL0ZJUz1cTFZAUEksJ3VDV2MtPS44azRbJWxkLiFnSDE3ZG86anFwbW9oV101IlE6OHBMVGVaNzpCQGE0bnM+TyMiMCQ6Oyt0ITcqZWNVXi5OdCxyREY9cUZtPDReLlZLa1ohQnRkTVJFWCVyO1NNcFs8VTFiWEBkIlVQUkZJQkNXJiEyVjZvc1BrRjNBa1krVlhoL0xdWjBMZ1JaLE5aSFpnSEJfQDIhYDdcJjxtVWhZYXE2RVw7OTdxO2BTTS1lN2BjOVs9bG1DbTJZI1E0Tz8xNUopUCEnXj5XcnEtVU9ZPjU7PDBGVUk1NlFBTEhhO1tZIitidU9aY0JmMihxJmZRdW0+Vn4+ZW5kc3RyZWFtCmVuZG9iagoxOCAwIG9iago8PAovRmlsdGVyIFsgL0FTQ0lJODVEZWNvZGUgL0ZsYXRlRGVjb2RlIF0gL0xlbmd0aCAyNDgxCj4+CnN0cmVhbQpHYXQ9LGdOKSUuJnEwTFVpNmc1QDNQPVY9TFQwaGpuVGAqckdUcSE6Q0otO2wjdVNkKiEhYE0jQllKcCs1YDJAUjhZMHMtT1g1U0JES01MbF0mQTI3cF4sX2s7QG1rMS1VMyJkOC5ec1tNP0wxI1BQR21mMzU+N1MsJiFSLEBQPFUvblZEa2dlL1FEKUtSSHRyaDZQMFVwKGkkZythZ1xJNyMiUy5IO0RsbCcjOCxcKXJaQC1iPT8hLi5iK2JacyVfX1YsKyRNTV9rbCI4TDYoNl5lK25oSmhDdD1XVlhKWCQ3KCk5LEQubTZRX3BYYiohZTlFZjYyOTxTSTpYQUNbXU1jUlpXNmsvWlZmWFRyU2BoXHJUQl0pN3QnMmJPbixpWCROb0ktM2YyYSxJb1wtL0RHW0ZgcDtdX1QxbDEhLUlvLm4uOjBMLXNLIVQoRCZrbVVQRGpmUDo1PSphW0NrbUhOPm06NC0mQU8zc0dXXDAqaGBwNkc7Jm9Eb1ppczoqakcnUWAqSFtEJiwwTy1gbl1gOCMrRkQuY0tldTJhL0UmKy5MLDlwcmhWbUlGJCRRQC9EMmNIL2lBb1oxbjxpYTFDI2xZLi9AZCwhMjpsQStPXkROJmhCbC02LFpoNzhqU1ZmPm4mV3EuTEllaCZcImpxQyZtcEpKaz8nQDRAUlJBVD1ZbUBIR3FRUVMkZV5tOFJXLkc/M1l0SixUUHRpPk91M3NsKXFbVEksYUg0S0xAZjQ0VipZVTgoOllybUc1TltsMyhFdCRAOWEzWmxRbFZxJCxoYz5NMFJkOkdDLDZMXj84OzRyY0NjcD5CM2tHXGAlLEZYPlM3RFNrKTM+OUhyUD9UYS03Lm9IdFZwOWpxLmk8VU44Q1g7KFE0QE5zSjtNWmZBI0QwaSNOU2BxX0JPSGFPOENqQltnKihPWDcobFhLP25CJHJtYy1sLyluaU1sWG9DJidJMD4vai1APFFtJWxtQmMwNyZXUlxxZypbWm1WZTxiPnNXazgzSEBYJW5tLltrOC1ZMGZvSUFGLVImPz5uTlIqbzJJJ2YuNFhKRiMyN0szdT9IRFk6K0YuJS8uInI+dGY6TlMkIzIsXFM/VC5US0FAJUFea1w9ZkFpX0ohaTxoM1UyZ1s8UG5YYzpfMmMxbTlTN0tvdCxaWVAvJkhdYzM1ckw2SzVULVQjJF0kOGlSPEJyR1YjZTEqcypOQCtWODA2KFlSS1RfJj1aPScrUC9tSW1QJy84KyMoRV5GXz1obUdKIUwmRSdnLktuUSg4KkksPTtubiVqSVhyLk5lU2ZZLFlaJkpZPmdjNUVbWEhhYjYuPE4vcXIqRzU6SmMkX1pCUiZmK3NoL2FPVk9WKiVhQCFtXlc1NStVbjIrS1NRayM7RkBSSmw+KVA4QjQlNjdNaTVkIXFlTXBKMWxgcFhMXCZAOywpWDhBSG5FMmA+WFgkb3BNcC5ZKjwnQiM3YClgZ2Y6OnNoYmVxOElndVZkZ1VcOzNtKyZGcnE2OjtyXVYhXkRLRWA0TWhyUTRPM0VxaCVAZ2VgaCIqTUJDdUpoNC5hNGM3MGxBYCkzTW83NTYvNEtmKVdkS1JFIlJaZVUnU0w3KjhIXjJzaUkuPG0/Y1pxZyxuXi4/PVVCQmgqUyxNby1DXEFiUGFCV3RBZ3NvdUxEXEUkRl5eYWFGUW1qVz8xPiMzWlEtdFFmQDN0QjxganJASWFRTF8kaG1PPFRVOyInVkJFOmlGLiUsOS1ZWzwuRGZMTS9sZCtWXCtwal9gZj1fWVtlbm1kWCgyKiMmdG0/WUdHS1NNKjEtNFNtOjktKk41N0wmKClpXi5VdFtTS0VAYUxOLkpUayg+ZWs/NURfS08iN05hRGFbMHA7Wig8bVokM2MzNSU4WEZvI2VJR0c/YldtInRbPD9ZPiM1QTJIPFdoZWZRXS82VFlIbjQuIVMoJSNXSnBnKm5aXj41RiJlai5JbmxsSlc+MDxUV1swbylrZ1wnbzViYVUwaz8sN2c0VnFyPmRxIissJC5hREEhN1g7JGNiJGsrTDlnVF9pa2dgRicqPlUzQFhEIUNkIkZVWzJELjVDKGdoOnUmbVdMXDheNihyWF1CTlZVXWlvOEQ2W1BOI2hBVnQnbEE6clgjUT4iPD01c0RQImkmN2deMm4jZnQ1bzVZYFtdWUNnU3RtbGtIKlFaJEVTWlhEb3UpVSYoOjVLazBPJ2pvJ3Anbz81YjkiJSZtOkghSUddYCw6cVotW0xuNVlPYkMnJnNCJlk6LiknMiNlK1xdPVU1Q0BnZistPjZUaGUpb2E0S3E0cS1LWTpGO2tUJk9aQVxnI0FrZFdTXXVTOUltS2JJPFJbRidzSC0iY1EsWHErZjp0dUpnaColT1dEOXBKbF9bOVtgVT9mMEJHTFVOL0tNaWQyWl5GYmhLOSk8S1pfYmY1T3NzUjowWy1VJzJUJW9jVklEJHEzVSlUY19UW1ApIVZ1OnRwQUZRLXBUXktoZWBxR2sqclZvYlcyTXIyXTkvQFhdJzstPyFMQXRSPGdgU3RhPlZpOTZsYztpJT44OTBfQkUha05TMDFbKW50MTxbYlFtW1xDb242TV5PY0pMYT5XZnBWIzxiLUQ2JHBtSSdFTjd0cS1XUzE+SChWRmtcTTx0JyomV1NbOGIvRFlEWS1aaEcnRjdkNztkNG1ocTUoZ2soZClbZj5RQmBWbzhnSStrcC5qb0ZvSyNDMlZZcStKNjBLZ3VbMyNnTkhdSFUiJkw8LClTOS8lJygpMVBCYjl0O3VKMzxJKTVjM1t1JTsnZnRnIm51WyUiaCxfITMhWmM2KiUrcls6cTlVLTI8JnVbWTA0S1ojPi02a29DVV4yci1LSWQwX0tcL19ESTQ7Kl9PbSo7R2RMR009N15tRlN0PlRWaixuTFIuVCUxSXRZcCVzXG1aajhUMG1nS28sW1NNMDIkQzJRIVVidHV0YkBALmE+VitCSDxcOiJOQ2k6MkAiVSgmMDUxSzJEMTNFamxANCdvciNkLlYmZ05KPXMnZyQ5VUJUZSEoLSVBOkUoPi40Y1JBJUAzVihVXCNPNXUoYT1TJSNBcTA4QkFWbjsqJjRQKz1AKSNJPiM0XDtWT0AicGNxRmdZRWtbJGpSR0xHXG4+Tz4uTypqSlNnNjU2OVM0bl8wLVhiInE2a1M/NmUhSUlJNUAzTHE2LVRMOkNgW2ZSTXJdcEJ0cCdqKkRUKVFiVTohQCFSKUJnZzs2UFVxZ2Q0YFZxXTsrIyphVjQyNS1hTXVObDoqKXM/fj5lbmRzdHJlYW0KZW5kb2JqCnhyZWYKMCAxOQowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwNzMgMDAwMDAgbiAKMDAwMDAwMDExNCAwMDAwMCBuIAowMDAwMDAwMjIxIDAwMDAwIG4gCjAwMDAwMDAzMzAgMDAwMDAgbiAKMDAwMDAwMDUzNSAwMDAwMCBuIAowMDAwMDAwNzQwIDAwMDAwIG4gCjAwMDAwMDA5NDUgMDAwMDAgbiAKMDAwMDAwMTE1MCAwMDAwMCBuIAowMDAwMDAxMzU1IDAwMDAwIG4gCjAwMDAwMDE1NjAgMDAwMDAgbiAKMDAwMDAwMTYzMCAwMDAwMCBuIAowMDAwMDAxOTE0IDAwMDAwIG4gCjAwMDAwMDIwMDQgMDAwMDAgbiAKMDAwMDAwMzg0NiAwMDAwMCBuIAowMDAwMDA2NzI3IDAwMDAwIG4gCjAwMDAwMDgxOTYgMDAwMDAgbiAKMDAwMDAxMDgwOSAwMDAwMCBuIAowMDAwMDEyOTQxIDAwMDAwIG4gCnRyYWlsZXIKPDwKL0lEIApbPDBjNzcyNzM4ZjRlZWQwZDY4NjBmNTFkMDgzNGQ2ZWJmPjwwYzc3MjczOGY0ZWVkMGQ2ODYwZjUxZDA4MzRkNmViZj5dCiUgUmVwb3J0TGFiIGdlbmVyYXRlZCBQREYgZG9jdW1lbnQgLS0gZGlnZXN0IChodHRwOi8vd3d3LnJlcG9ydGxhYi5jb20pCgovSW5mbyAxMSAwIFIKL1Jvb3QgMTAgMCBSCi9TaXplIDE5Cj4+CnN0YXJ0eHJlZgoxNTUxNAolJUVPRgo=',1,2),
	(196,3,52,'5','A random test classification','2022-09-07 03:00:00',_binary 'JVBERi0xLjMKJZOMi54gUmVwb3J0TGFiIEdlbmVyYXRlZCBQREYgZG9jdW1lbnQgaHR0cDovL3d3dy5yZXBvcnRsYWIuY29tCjEgMCBvYmoKPDwKL0YxIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9CYXNlRm9udCAvSGVsdmV0aWNhIC9FbmNvZGluZyAvV2luQW5zaUVuY29kaW5nIC9OYW1lIC9GMSAvU3VidHlwZSAvVHlwZTEgL1R5cGUgL0ZvbnQKPj4KZW5kb2JqCjMgMCBvYmoKPDwKL0NvbnRlbnRzIDcgMCBSIC9NZWRpYUJveCBbIDAgMCA1OTUuMjc1NiA4NDEuODg5OCBdIC9QYXJlbnQgNiAwIFIgL1Jlc291cmNlcyA8PAovRm9udCAxIDAgUiAvUHJvY1NldCBbIC9QREYgL1RleHQgL0ltYWdlQiAvSW1hZ2VDIC9JbWFnZUkgXQo+PiAvUm90YXRlIDAgL1RyYW5zIDw8Cgo+PiAKICAvVHlwZSAvUGFnZQo+PgplbmRvYmoKNCAwIG9iago8PAovUGFnZU1vZGUgL1VzZU5vbmUgL1BhZ2VzIDYgMCBSIC9UeXBlIC9DYXRhbG9nCj4+CmVuZG9iago1IDAgb2JqCjw8Ci9BdXRob3IgKGFub255bW91cykgL0NyZWF0aW9uRGF0ZSAoRDoyMDIyMDUzMDE0NTc0MC0wMScwMCcpIC9DcmVhdG9yIChSZXBvcnRMYWIgUERGIExpYnJhcnkgLSB3d3cucmVwb3J0bGFiLmNvbSkgL0tleXdvcmRzICgpIC9Nb2REYXRlIChEOjIwMjIwNTMwMTQ1NzQwLTAxJzAwJykgL1Byb2R1Y2VyIChSZXBvcnRMYWIgUERGIExpYnJhcnkgLSB3d3cucmVwb3J0bGFiLmNvbSkgCiAgL1N1YmplY3QgKHVuc3BlY2lmaWVkKSAvVGl0bGUgKHVudGl0bGVkKSAvVHJhcHBlZCAvRmFsc2UKPj4KZW5kb2JqCjYgMCBvYmoKPDwKL0NvdW50IDEgL0tpZHMgWyAzIDAgUiBdIC9UeXBlIC9QYWdlcwo+PgplbmRvYmoKNyAwIG9iago8PAovRmlsdGVyIFsgL0FTQ0lJODVEZWNvZGUgL0ZsYXRlRGVjb2RlIF0gL0xlbmd0aCAxODAKPj4Kc3RyZWFtCkdhcHBXWW4iVykmND8yQEt1XyYsKUg3T2pXQl5rY2teTUhTPmd1K2Q1dFAlKVQ+RkUtbyYrLlIyV3RzRl5ZOGFZJCttNmhmbjJFMmNqY1gwMCU7R189Zl1TMSVnbHVhZFhtbW5FaWNKdS9rKkhXWSpwUD5QKEsmTi1DdEMiL0ZTZz1bZkpXWD5JNHEiUDJaZE9uX2pOWTU6ZDouVmd0N0lFQjgtK0ZnLTZZbyoqPXExKkh+PmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDgKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDczIDAwMDAwIG4gCjAwMDAwMDAxMDQgMDAwMDAgbiAKMDAwMDAwMDIxMSAwMDAwMCBuIAowMDAwMDAwNDE0IDAwMDAwIG4gCjAwMDAwMDA0ODIgMDAwMDAgbiAKMDAwMDAwMDc3OCAwMDAwMCBuIAowMDAwMDAwODM3IDAwMDAwIG4gCnRyYWlsZXIKPDwKL0lEIApbPDY0ZjIyOTVkMzQzY2EyODdkNjU3MDA1MWRlYWY5Nzg0Pjw2NGYyMjk1ZDM0M2NhMjg3ZDY1NzAwNTFkZWFmOTc4ND5dCiUgUmVwb3J0TGFiIGdlbmVyYXRlZCBQREYgZG9jdW1lbnQgLS0gZGlnZXN0IChodHRwOi8vd3d3LnJlcG9ydGxhYi5jb20pCgovSW5mbyA1IDAgUgovUm9vdCA0IDAgUgovU2l6ZSA4Cj4+CnN0YXJ0eHJlZgoxMTA3CiUlRU9GCg==',1,2);
UNLOCK TABLES;


LOCK TABLES `consensus_classification_criteria_applied` WRITE;
INSERT INTO `consensus_classification_criteria_applied` VALUES 
	(1,195,2,4,'dsafds'),
	(2,195,3,6,'zjhdjhjh'),
	(3,195,2,5,'dsafds'),
	(4,196,2,4,'ev1'),
	(5,196,3,6,'ev2'),
	(6,196,2,5,'ev3');
UNLOCK TABLES;




--
-- Insert some transcripts 
--

LOCK TABLES `transcript` WRITE;
INSERT INTO `transcript` VALUES 
	(122155,2174,'ENST00000260947','protein coding',2323,1,0,0,1),
	(122156,2174,'ENST00000471590','processed transcript',918,0,0,0,0),
	(122157,2174,'ENST00000432456','protein coding',132,0,0,0,0),
	(122158,2174,'ENST00000619009','protein coding',790,1,0,0,0),
	(122159,2174,'ENST00000617164','protein coding',2267,1,0,0,0),
	(122160,2174,'ENST00000613374','protein coding',918,1,0,0,0),
	(122161,2174,'ENST00000650978','nonsense mediated decay',1293,0,0,0,0),
	(122162,2174,'ENST00000613706','protein coding',1915,1,0,0,0),
	(122163,2174,'ENST00000421162','protein coding',974,1,0,0,0),
	(122164,2174,'ENST00000613192','nonsense mediated decay',190,0,0,0,0),
	(122165,2174,'ENST00000620057','protein coding',380,1,0,0,0),
	(122166,2174,'ENST00000455743','nonsense mediated decay',228,0,0,0,0),
	(122167,2174,'ENST00000465841','retained intron',173,0,0,0,0),
	(122168,2174,'ENST00000471787','processed transcript',870,0,0,0,0),
	(122169,2174,'ENST00000479904','retained intron',571,0,0,0,0),
	(235730,2174,'NR_104215','misc RNA',5263,0,0,0,0),
	(235731,2174,'NR_104212','misc RNA',5319,0,0,0,0),
	(235732,2174,'NR_104216','misc RNA',4518,0,0,0,0),
	(235733,2174,'NM_001282548','mRNA',918,1,0,0,0),
	(235734,2174,'NM_001282543','mRNA',2267,1,0,0,0),
	(235735,2174,'NM_001282545','mRNA',974,1,0,0,0),
	(235736,2174,'NM_001282549','mRNA',790,1,0,0,0),
	(235737,2174,'NM_000465','mRNA',2323,1,1,0,1),
	(235738,2174,'XM_017004613','mRNA',2421,0,0,0,0),
	(235739,2174,'XM_047445350','mRNA',1919,0,0,0,0),
	(235740,2174,'XM_017004614','mRNA',2017,0,0,0,0),

	(5629,21541,'ENST00000529984','protein coding',645,1,0,0,0),
	(5630,21541,'ENST00000485271','nonsense mediated decay',131,0,0,0,0),
	(5631,21541,'ENST00000372104','protein coding',1551,1,0,0,0),
	(5632,21541,'ENST00000448481','protein coding',1584,1,0,0,0),
	(5633,21541,'ENST00000456914','protein coding',1551,1,1,0,1),
	(5634,21541,'ENST00000354383','protein coding',1554,1,0,0,0),
	(5635,21541,'ENST00000475516','nonsense mediated decay',121,0,0,0,0),
	(5636,21541,'ENST00000355498','protein coding',1551,1,0,0,0),
	(5637,21541,'ENST00000372110','protein coding',1595,1,0,0,0),
	(5638,21541,'ENST00000481571','nonsense mediated decay',162,0,0,0,0),
	(5639,21541,'ENST00000372098','protein coding',1625,1,0,0,0),
	(5640,21541,'ENST00000672818','protein coding',1625,1,0,0,0),
	(5641,21541,'ENST00000372115','protein coding',1592,1,0,0,0),
	(5642,21541,'ENST00000488731','protein coding',645,1,0,0,0),
	(5643,21541,'ENST00000531105','protein coding',187,1,0,0,0),
	(5644,21541,'ENST00000672011','nonsense mediated decay',631,0,0,0,0),
	(5645,21541,'ENST00000467459','nonsense mediated decay',550,0,0,0,0),
	(5646,21541,'ENST00000482094','retained intron',915,0,0,0,0),
	(5647,21541,'ENST00000529892','protein coding',635,0,0,0,0),
	(5648,21541,'ENST00000533178','nonsense mediated decay',297,0,0,0,0),
	(5649,21541,'ENST00000528013','protein coding',1593,1,0,0,0),
	(5650,21541,'ENST00000673134','nonsense mediated decay',121,0,0,0,0),
	(5651,21541,'ENST00000672314','protein coding',1384,0,0,0,0),
	(5652,21541,'ENST00000672593','nonsense mediated decay',121,0,0,0,0),
	(5653,21541,'ENST00000672764','nonsense mediated decay',623,0,0,0,0),
	(5654,21541,'ENST00000412971','protein coding',638,0,0,0,0),
	(5655,21541,'ENST00000462388','retained intron',875,0,0,0,0),
	(5656,21541,'ENST00000466231','retained intron',355,0,0,0,0),
	(5657,21541,'ENST00000470256','nonsense mediated decay',552,0,0,0,0),
	(5658,21541,'ENST00000461495','nonsense mediated decay',162,0,0,0,0),
	(5659,21541,'ENST00000435155','protein coding',864,0,0,0,0),
	(5660,21541,'ENST00000450313','nonsense mediated decay',673,0,0,0,0),
	(5661,21541,'ENST00000674679','nonsense mediated decay',121,0,0,0,0),
	(5662,21541,'ENST00000467940','nonsense mediated decay',136,0,0,0,0),
	(5663,21541,'ENST00000478796','retained intron',774,0,0,0,0),
	(5664,21541,'ENST00000525160','nonsense mediated decay',165,0,0,0,0),
	(5665,21541,'ENST00000479746','retained intron',966,0,0,0,0),
	(5666,21541,'ENST00000492494','retained intron',993,0,0,0,0),
	(5667,21541,'ENST00000671856','processed transcript',520,0,0,0,0),
	(5668,21541,'ENST00000483642','retained intron',1075,0,0,0,0),
	(5669,21541,'ENST00000481139','retained intron',1047,0,0,0,0),
	(5670,21541,'ENST00000485484','retained intron',805,0,0,0,0),
	(5671,21541,'ENST00000476789','retained intron',927,0,0,0,0),
	(5672,21541,'ENST00000462387','retained intron',817,0,0,0,0),
	(5673,21541,'ENST00000474703','retained intron',572,0,0,0,0),
	(5674,21541,'ENST00000483127','protein coding',279,0,0,0,0),
	(5675,21541,'ENST00000534453','retained intron',670,0,0,0,0),
	(215945,21541,'NR_146882','misc RNA',2021,0,0,0,0),
	(215946,21541,'NR_146883','misc RNA',1871,0,0,0,0),
	(215947,21541,'XM_017001332','mRNA',1593,0,0,0,0),
	(215948,21541,'NM_001350651','mRNA',1209,0,0,0,0),
	(215949,21541,'NM_001293192','mRNA',1277,0,0,0,0),
	(215950,21541,'NM_001350650','mRNA',1209,0,0,0,0),
	(215951,21541,'XM_047421200','mRNA',1551,0,0,0,0),
	(215952,21541,'NM_001048171','mRNA',1551,1,0,0,0),
	(215953,21541,'NM_001293190','mRNA',1595,1,0,0,0),
	(215954,21541,'XM_047421195','mRNA',1584,0,0,0,0),
	(215955,21541,'NM_012222','mRNA',1625,1,0,0,0),
	(215956,21541,'XM_011541503','mRNA',1593,0,0,0,0),
	(215957,21541,'NM_001128425','mRNA',1634,0,0,0,0),
	(215958,21541,'NM_001293196','mRNA',1277,0,0,0,0),
	(215959,21541,'NM_001048173','mRNA',1551,1,1,0,1),
	(215960,21541,'NM_001048172','mRNA',1554,1,0,0,0),
	(215961,21541,'XM_047421194','mRNA',1593,0,0,0,0),
	(215962,21541,'XM_047421199','mRNA',1560,0,0,0,0),
	(215963,21541,'XM_047421191','mRNA',1601,0,0,0,0),
	(215964,21541,'XM_047421201','mRNA',1510,0,0,0,0),
	(215965,21541,'NM_001048174','mRNA',1551,1,1,0,1),
	(215966,21541,'XM_017001334','mRNA',1554,0,0,0,0),
	(215967,21541,'NM_001293191','mRNA',1584,1,0,0,0),
	(215968,21541,'XM_011541499','mRNA',1593,0,0,0,0),
	(215969,21541,'XM_017001333','mRNA',1593,0,0,0,0),
	(215970,21541,'NM_001293195','mRNA',1551,1,1,0,1),
	(215971,21541,'XM_047421198','mRNA',1568,0,0,0,0),
	(215972,21541,'XM_047421196','mRNA',1571,0,0,0,0),
	(215973,21541,'XM_047421192','mRNA',1601,0,0,0,0),
	(215974,21541,'XM_011541502','mRNA',1593,0,0,0,0),
	(215975,21541,'XM_047421193','mRNA',1601,0,0,0,0),
	(215976,21541,'XM_047421197','mRNA',1568,0,0,0,0),
	(215977,21541,'XM_011541497','mRNA',1610,0,0,0,0),
	(215978,21541,'XM_047421203','mRNA',1177,0,0,0,0),
	(215979,21541,'XM_047421204','mRNA',1168,0,0,0,0),
	(215980,21541,'XM_047421202','mRNA',1505,0,0,0,0),

	(5628,11973,'ENST00000334815','protein coding',1115,1,1,0,1),
	(215944,11973,'NM_032756','mRNA',1115,1,1,0,1),
	
	(52018,42061,'ENST00000345108','protein coding',962,1,0,0,0),
	(52021,2566,'ENST00000380152','protein coding',10231,1,1,0,1),
	(52020,2566,'ENST00000530893','protein coding',1437,0,0,0,0),
	(52017,42061,'ENST00000533490','protein coding',962,1,1,0,1),
	(52019,2566,'ENST00000544455','protein coding',10231,1,0,0,0),
	(52023,2566,'ENST00000614259','nonsense mediated decay',7934,0,0,0,0),
	(52022,2566,'ENST00000680887','protein coding',10231,0,0,0,0),
	(311253,2566,'NM_000059','mRNA',10231,1,1,0,1),
	(311252,42061,'NM_001136571','mRNA',962,1,1,0,1);
UNLOCK TABLES;



LOCK TABLES `assay` WRITE;
/*!40000 ALTER TABLE `assay` DISABLE KEYS */;
INSERT INTO `assay` VALUES (1,52,'functional',_binary 'dA0KdGUNCnRlcw0KdGVzdA0KdGVzDQp0ZQ0KdA==','test.txt',12345,'2022-08-08'),(6,52,'functional',_binary 'dA0KdGUNCnRlcw0KdGVzdA0KdGVzDQp0ZQ0KdA==','test.txt',6565,'2022-08-09'),(14,52,'splicing',_binary 'dA0KdGUNCnRlcw0KdGVzdA0KdGVzDQp0ZQ0KdA==','test.txt',3654,'2022-08-09');
/*!40000 ALTER TABLE `assay` ENABLE KEYS */;
UNLOCK TABLES;