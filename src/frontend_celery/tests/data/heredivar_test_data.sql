--
-- All Annotation types
--

LOCK TABLES `annotation_type` WRITE;
/*!40000 ALTER TABLE `annotation_type` DISABLE KEYS */;
INSERT INTO `annotation_type` VALUES 
	(3,'rsid','The rs-number of a variant from dbSNP (version summary: https://www.ncbi.nlm.nih.gov/projects/SNP/snp_summary.cgi)','text','155','2021-06-16','None'),
	(4,'phylop_100way','PhyloP 100 vertebrates (100-way) conservation scores. These scores measure evolutionary conservation at individual alignment sites. Interpretations of the scores are compared to the evolution that is expected under neutral drift. Positive scores: Measure conservation, which is slower evolution than expected, at sites that are predicted to be conserved. Negative scores: Measure acceleration, which is faster evolution than expected, at sites that are predicted to be fast-evolving. ','float',NULL,'2013-12-01','Change tolerance'),
	(5,'cadd_scaled','The scaled CADD scores: PHRED-like (-10*log10(rank/total)) scaled C-score ranking a variant relative to all possible substitutions of the human genome (8.6x10^9). These scores range from 1 to 99. A cutoff for deleteriousness can be set to 10-15, but the choice remains arbitrary.','float','v1.6','2020-04-11','Change tolerance'),
	(6,'revel','The REVEL pathogenicity score of this variant. This score can range from 0 to 1, which reflects the number of trees in the random forest that classified the variant as pathogenic. Thus, higher values represent a more \"certain\" decision. When choosing a cutoff one should keep in mind that higher cutoffs will result in a higher specificity, but lower sensitivity.','float','v1.3','2021-05-03','Change tolerance'),
	(7,'spliceai_details','Details about the SpliceAI predictions: These include delta scores (DS) and delta positions (DP) for acceptor gain (AG), acceptor loss (AL), donor gain (DG), and donor loss (DL). Format: GENE|DS_AG|DS_AL|DS_DG|DS_DL|DP_AG|DP_AL|DP_DG|DP_DL','text','v1.3.1','2021-09-07','Splicing'),
	(8,'spliceai_max_delta','Max of delta scores for acceptor gain, acceptor loss, donor gain and donor loss. A value of 0.5 or more can be assumed to have an impact on splicing.','float','v1.3.1','2021-09-07','Splicing'),
	(9,'maxentscan_ref','MaxEntScan reference sequence score. The lower the score, the more difference one would expect the input (ie mutated) sequence is from the reference. Whenever the difference between ref and alt is positive it predicts a functional splice site. A negative difference predicts that this position is not a functional splice site.','float',NULL,'2018-08-29','Splicing'),
	(10,'maxentscan_alt','MaxEntScan alternate sequence score calculated though VEP release-104.3 using the MaxEntScan plugin','float',NULL,'2018-08-29','Splicing'),
	(11,'gnomad_ac','gnomAD alternate allele count for samples','int','v3.1.2','2021-10-22','GnomAD'),
	(12,'gnomad_af','gnomAD frequency of alternate allele in samples','float','v3.1.2','2021-10-22','GnomAD'),
	(13,'gnomad_hom','gnomAD number of homozygous individuals in samples','int','v3.1.2','2021-10-22','GnomAD'),
	(14,'gnomad_hemi','gnomAD number of hemizygous individuals in samples','int','v3.1.2','2021-10-22','GnomAD'),
	(15,'gnomad_het','gnomAD number of heterozygous individuals in samples','int','v3.1.2','2021-10-22','GnomAD'),
	(16,'gnomad_popmax','gnomAD population with maximum allele frequency (AF)','text','v3.1.2','2021-10-22','GnomAD'),
	(17,'gnomadm_ac_hom','Allele count restricted to variants with a heteroplasmy level >= 0.95 from the GnomAD mitochondrial genome data. These variants are (almost) homozygous among all mitochondria in an individual','int','v3.1','2020-11-17','GnomAD'),
	(18,'brca_exchange_clinical_significance','Variant pathogenicity as displayed in the Summary view','text','54','2022-02-22','None'),
	(19,'flossies_num_afr','Number of individuals with this variant in the african american cohort. (n=2559)','int',NULL,'2022-03-25','FLOSSIES'),
	(20,'flossies_num_eur','Number of individuals with this variant in the european american cohort. (n=7325)','int',NULL,'2022-03-25','FLOSSIES'),
	(21,'arup_classification','Pathogenicity classification from the ARUP database (1: not pathogenic or of no clinical significance; 2: likely not pathogenic or of little clinical significance; 3: uncertain; 4: likely pathogenic; 5: definitely pathogenic)','int',NULL,'2022-04-01','None'),
	(22,'cancerhotspots_cancertypes','A | delimited list of all cancertypes associated to this variant according to cancerhotspots. FORMAT: tumortype:tissue','text','v2','2017-12-15','Cancerhotspots'),
	(23,'cancerhotspots_ac','Number of samples showing the variant from cancerhotspots','int','v2','2017-12-15','Cancerhotspots'),
	(24,'cancerhotspots_af','Allele Frequency of the variant (AC / num samples cancerhotspots)','float','v2','2017-12-15','Cancerhotspots'),
	(25,'rsid','https://www.ncbi.nlm.nih.gov/projects/SNP/snp_summary.cgi)','text','0','2020-07-01','None'),
	(26,'rsid','atests','text','0','2022-01-01','None'),
	(27,'tp53db_class','Family classification: LFS = strict clinical definition of Li-Fraumeni syndrome, LFL = Li-Fraumeni like for the extended clinical definition of Li-Fraumeni, FH: family history of cancer which does not fulfil LFS or any of the LFL definitions, No FH: no family history of cancer, FH= Family history of cancer (not fulfilling the definition of LFS/LFL),  No= no family history of cancer, ?= unknown','text','r20','2019-07-01','TP53 database'),
	(29,'tp53db_DNE_LOF_class','Functional classification for loss of growth-suppression and dominant-negative activities based on Z-scores','text','r20','2019-07-01','TP53 database'),
	(30,'tp53db_bayes_del','Missense variant functional predictions by BayesDel tool (Feng 2017) used without allele frequency. Score bigger or equal to 0.16: damaging; Score smaller than 0.16: tolerated','float','r20','2019-07-01','TP53 database'),
	(31,'tp53db_DNE_class','Dominant-negative effect on transactivation by wild-type p53. Yes: dominant-negative activity on WAF1 and RGC promoters, Moderate: dominant-negative activity on some but not all promoters, No: no dominant-negative activity on both WAF1 and RGC promoters, or none of the promoters in the large studies.','text','r20','2019-07-01','TP53 database'),
	(32,'tp53db_domain_function','Function of the domain in which the mutated residue is located.','text','r20','2019-07-01','TP53 database'),
	(33,'tp53db_transactivation_class','Functional classification based on the overall transcriptional activity','text','r20','2019-07-01','TP53 database'),
	(34,'heredicare_cases_count','Number of cases the variant occurs in','int',NULL,'2022-05-23','HerediCare'),
	(35,'heredicare_family_count','Number of families the variant occurs in','int',NULL,'2022-05-23','HerediCare'),
	(36,'task_force_protein_domain','The description of the protein domain from a hand-crafted table by the VUS-Task-Force.','text',NULL,'2022-06-01','Task-Force protein domains'),
	(37,'task_force_protein_domain_source','The source of the task force protein domain.','text',NULL,'2022-06-01','Task-Force protein domains'),
	(39,'hexplorer','The HEXplorer delta score (HZEI mutant - HZEI wildtype). HZEI scores were normalized by the total number of nucleotide positions which contribute to the score.','float','1.0','2022-06-30','Splicing'),
	(40,'hexplorer_mut','The HEXplorer score for the mutant sequence. HZEI scores were normalized by the total number of nucleotide positions which contribute to the score.','float','1.0','2022-06-30','Splicing'),
	(41,'hexplorer_wt','The HEXplorer score for the reference sequence. HZEI scores were normalized by the total number of nucleotide positions which contribute to the score.','float','1.0','2022-06-30','Splicing'),
	(42,'hexplorer_rev','The HEXplorer delta score for the reverse complement of the original sequence (HZEI mutant rev - HZEI wildtype rev). HZEI scores were normalized by the total number of nucleotide positions which contribute to the score.','float','1.0','2022-06-30','Splicing'),
	(43,'hexplorer_rev_mut','The HEXplorer score for the reverse complement of the mutant sequence. HZEI scores were normalized by the total number of nucleotide positions which contribute to the score.','float','1.0','2022-06-30','Splicing'),
	(44,'hexplorer_rev_wt','The HEXplorer score for the reverse complement of the reference sequence. HZEI scores were normalized by the total number of nucleotide positions which contribute to the score.','float','1.0','2022-06-30','Splicing'),
	(45,'max_hbond','The HBond delta score (max HBond mutant - max HBond wildtype). This score shows the change in binding affinity of the U1 snRNA to the splice site motiv, i. e. its ability to form hbonds with the sequence motiv. Negative values show that the mutant sequence is less probable to bind the U1 snRNA (This is a \"worse\" binding site). Positive values mean that the mutant sequence is more likely to bind the U1 snRNA. If there are multiple possible splice sites only the max values are considered.','float','1.0','2022-06-30','Splicing'),
	(46,'max_hbond_mut','The max HBond score for the mutant sequence. ','float','1.0','2022-06-30','Splicing'),
	(47,'max_hbond_wt','This is the max HBond score for the reference sequence.','float','1.0','2022-06-30','Splicing'),
	(48,'max_hbond_rev','The max HBond delta score for the reverse complement of the original sequence (HZEI mutant rev - HZEI wildtype rev). This score shows the change in binding affinity of the U1 snRNA to the splice site motiv, i. e. its ability to form hbonds with the sequence motiv. Negative values show that the mutant sequence is less probable to bind the U1 snRNA (This is a \"worse\" binding site). Positive values mean that the mutant sequence is more likely to bind the U1 snRNA. If there are multiple possible splice sites only the max values are considered.','float','1.0','2022-06-30','Splicing'),
	(49,'max_hbond_rev_mut','This is the max HBond score for the reverse complement of the mutant sequence.','float','1.0','2022-06-30','Splicing'),
	(50,'max_hbond_rev_wt','This is the max HBond score for the reverse complement of the reference sequence.','float','1.0','2022-06-30','Splicing'),
	(51,'gnomad_popmax_AF','The allele frequency of the \"popmax\" population','float','v3.1.2','2021-10-22','GnomAD');
/*!40000 ALTER TABLE `annotation_type` ENABLE KEYS */;
UNLOCK TABLES;



--
-- Dumping data for table `task_force_protein_domains`
--

LOCK TABLES `task_force_protein_domains` WRITE;
/*!40000 ALTER TABLE `task_force_protein_domains` DISABLE KEYS */;
INSERT INTO `task_force_protein_domains` VALUES (1,'chr11',108229263,108229283,'Substrate binding','BWRL'),(2,'chr11',108249020,108249031,'NLS','BWRL'),(3,'chr11',108282785,108282847,'Leucine zipper','BWRL'),(4,'chr11',108288984,108289013,'Proline rich','BWRL'),(5,'chr11',108307899,108365505,'FATKIN','BWRL'),(6,'chr2',214792346,214809449,'RING','PMID: 32726901'),(7,'chr2',214752552,214780595,'ANK','PMID: 32726901'),(8,'chr2',214728709,214745830,'BRCT Domains','PMID: 32726901'),(9,'chr17',43104260,43124096,'RING','BWRL/ENIGMA'),(10,'chr17',41256889,43104928,'NES','BWRL/ENIGMA'),(11,'chr17',41246024,41246041,'NLS1','BWRL/ENIGMA'),(12,'chr17',41245706,41245729,'NLS2','BWRL/ENIGMA'),(13,'chr17',41245580,41245597,'NLS3','BWRL/ENIGMA'),(14,'chr17',41234506,41242975,'COILED-COIL','BWRL/ENIGMA'),(15,'chr17',41197698,41222983,'BRCT DOMAINS','BWRL/ENIGMA'),(16,'chr13',32316488,32319129,'PALB2 Binding','BWRL/ENIGMA'),(17,'chr13',32337362,32340601,'Interaction with RAD51 (BRC-1 bis BRC-8)','Uniprot'),(18,'chr13',32354901,32357757,'Interaction with FANCD2','Uniprot'),(19,'chr13',32356433,32396954,'DBD (DNA/DSS1 binding domain- helical OB1, OB2, OB3)','BWRL/ENIGMA'),(20,'chr13',32363246,32363296,'Nuclear export signal; masked by interaction with SEM1','Uniprot'),(21,'chr13',32298300,32398506,'C-terminal RAD51 binding domain (inkl. NLS1 und BRC-) ','BWRL/ENIGMA'),(22,'chr17',61686080,61861539,'ATPase/Helicase domain','PMID: 33619228'),(23,'chr17',61683857,61686079,'BRCA1 Interaction','PMID: 33619228'),(24,'chr1',68737416,68833496,'Bisher bekannten pathogenen CDH1-Varianten sind über den gesamten Locus verteilt und es kann daher keine klinisch relevante funktionelle Proteindomäne definiert werden.','BWRL'),(25,'chr22',28734515,28734667,'SQ/TQ-rich','BWRL'),(26,'chr22',28719463,28734448,'FHA','BWRL'),(27,'chr22',28689174,28719444,'Kinase','BWRL'),(28,'chr22',28687915,28687986,'NLS','BWRL'),(29,'chr16',23637932,23641133,'BRCA1 interaction domain','BWRL'),(30,'chr16',23635827,23641157,'DNA binding and Interaction with BRCA1','https://pubmed.ncbi.nlm.nih.gov/19369211/'),(31,'chr16',23635994,23636245,'RAD51 binding site','BWRL'),(32,'chr16',23634863,23635432,'DNA binding site','BWRL'),(33,'chr16',23629862,23630323,'MRG15 (MORF4L1) interaction domain','BWRL'),(34,'chr16',23603462,23629233,'WD40 repeat','BWRL'),(35,'chr17',58692644,58694983,'N-terminal region','BWRL'),(36,'chr17',58695020,58734219,'ATPase domain and RAD51B, XRCC3, and RAD51D binding','BWRL'),(37,'chr17',58734187,58734201,'Nuclear localization signal','BWRL'),(38,'chr17',35118515,35119613,'N-terminal region','BWRL https://www.sciencedirect.com/science/article/abs/pii/S1357272510003924'),(39,'chr17',35118530,35118586,'Linker','BWRL'),(40,'chr17',35101282,35107416,'ATPase domain and RAD51B, RAD51C, and XRCC2 binding','BWRL (PMID 10749867, 14704354, 19327148)'),(41,'chr17',7676204,7676594,'Transcription activation (TAD1+TAD2)','https://pubmed.ncbi.nlm.nih.gov/27145840/'),(42,'chr17',7676087,7676188,'Proline rich domain','BWRL'),(43,'chr17',7673744,7676065,'DNA binding region ','BWRL'),(44,'chr17',7673559,7673719,'NLS ','https://pubmed.ncbi.nlm.nih.gov/10321742/'),(45,'chr17',7670641,7673555,'Oligomerization region','BWRL'),(46,'chr17',7669612,7670643,'CTD (repression of DNA-binding region)','https://pubmed.ncbi.nlm.nih.gov/27145840/'),(47,'chr3',36993548,37020439,'N-terminal domain (MutSa interaction)','Insight Richtlinien und PMID: 26249686'),(48,'chr3',36993605,37007051,'ATPase domain','Insight Richtlinien und PMID: 26249686'),(49,'chr3',37025826,37048570,'EXO1 interaction','Insight Richtlinien und PMID: 28765196'),(50,'chr3',37028848,37050611,'PMS2/MLH3/PMS1 interaction','Insight Richtlinien und PMID: 28765196'),(51,'chr3',37026003,37028808,'NLS ','Insight Richtlinien und PMID: 28765196'),(52,'chr3',37047540,37047572,'NES1','Insight Richtlinien'),(53,'chr3',37048568,37048609,'NES2','Insight Richtlinien'),(54,'chr2',47403192,47410099,'DNA mismatch binding domain','Insight Richtlinien und PMID: 23391514'),(55,'chr2',47410100,47414367,'Connector domain','Insight Richtlinien und PMID: 28765196'),(56,'chr2',47410337,47412443,'MutLa interaction','Insight Richtlinien'),(57,'chr2',47414374,47445639,'Lever domain','Insight Richtlinien und PMID: 28765196'),(58,'chr2',47466807,47475122,'Lever domain','Insight Richtlinien und PMID: 28765196'),(59,'chr2',47445640,47466806,'Clamp domain','Insight Richtlinien und PMID: 28765196 PMID: 28765196'),(60,'chr2',47475123,47482946,'ATPase and  Helix-Turn-Helix','Insight Richtinien und PMID: 23391514;PMID: 28765196'),(61,'chr2',47429797,47475140,'MSH6/MSH3 interaction','Insight Richtlinien und PMID: 28765196'),(62,'chr2',47463061,47476419,'MutLa interaction','InSiGHT Richtlinien'),(63,'chr2',47480860,47482946,'MSH6/MSH3 interaction','Insight Richtlinien und PMID: 28765196'),(64,'chr2',47414272,47476374,'EXO1 stabilisation and interaction','InSiGHT Richtlinien und PMID: 28765196 PMID: 28765196'),(65,'chr2',47783243,47783266,'PCNA binding domain','PMID: 23391514; PMID: 28765196; InSiGHT-Richtlinien'),(66,'chr2',47790931,47796018,'PWWP domain','PMID: 23391514; PMID: 28765196; InSiGHT-Richtlinien'),(67,'chr2',47799067,47799540,'DNA mismatch /MMR binding domain','PMID: 23391514;PMID: 28765196'),(68,'chr2',47799499,47800134,'Connector domain','Insight Richtlinien;PMID: 23391514; PMID: 28765196'),(69,'chr2',47800135,47800785,'Lever domain','PMID: 23391514; PMID: 28765196'),(70,'chr2',47801008,47803472,'Lever domain','PMID: 23391514; PMID: 28765196'),(71,'chr2',47800786,47801007,'Clamp domain','PMID: 23391514; PMID: 28765196'),(72,'chr2',47803473,47806857,'ATPase/ATP binding','Insight und PMID: 23391514; PMID: 28765196'),(73,'chr2',47806554,47806857,'MSH2 interaction','Insight Richtlinien'),(74,'chr7',5969849,6009019,'ATPase/ATP binding','InSiGHT Richtlinien'),(75,'chr7',5973423,5982975,'Dimerisation/MLH1 interaction','P54278 (P54278) - protein - InterPro (ebi.ac.uk); PMID: 28765196; InSiGHT-Richtlinien'),(76,'chr7',5982853,5982906,'Exonuclease active site','PMID: 28765196'),(77,'chr7',5986869,5986892,'NLS ','Insight Richtlinien'),(78,'chr19',1207076,1207102,'Nucleotide binding ATP','STK11 - Serine/threonine-protein kinase STK11 precursor - Homo sapiens (Human) - STK11 gene & protein (uniprot.org)'),(79,'chr19',1207058,1222991,'Protein kinase domain','STK11 - Serine/threonine-protein kinase STK11 precursor - Homo sapiens (Human) - STK11 gene & protein (uniprot.org)'),(80,'chr19',1207046,1207183,'SIRT1 interaction','STK11 - Serine/threonine-protein kinase STK11 precursor - Homo sapiens (Human) - STK11 gene & protein (uniprot.org)'),(81,'chr10',87864470,87864511,'N-terminal phosphatidylinositol (Ptdlnsf4, 5) P2-binding domain (PBD)','PMID: 24656806, PMID: 34140896'),(82,'chr10',87864512,87952177,'phosphatase domain','PMID: 24656806, PMID: 34140896'),(83,'chr10',87952178,87965310,'C2 lipid or membrane-binding domain','PMID: 24656806, PMID: 34140896'),(84,'chr10',87965311,87965469,'carboxy-terminal tail','PMID: 24656806, PMID: 34140896'),(85,'chr10',87965461,87965469,'class I PDZ-binding (PDZ-BD) motif','PMID: 24656806, PMID: 34140896');
/*!40000 ALTER TABLE `task_force_protein_domains` ENABLE KEYS */;
UNLOCK TABLES;



	
--
-- Insert relevant genes
--

LOCK TABLES `gene` WRITE;
/*!40000 ALTER TABLE `gene` DISABLE KEYS */;
INSERT INTO `gene` VALUES 
	(2174,952,'BARD1','BRCA1 associated RING domain 1','protein-coding gene',601593,18430),
	(2566,1101,'BRCA2','BRCA2 DNA repair associated','protein-coding gene',600185,15378),
	(4004,1748,'CDH1','cadherin 1','protein-coding gene',192090,15419),
	(2564,1100,'BRCA1','BRCA1 DNA repair associated','protein-coding gene',113705,15377),
	(13764,16636,'KIF1B','kinesin family member 1B','protein-coding gene',605995,16304),
	(21914,20691,'NBR2','neighbor of BRCA1 lncRNA 2','non-coding RNA',618708,NULL),
	(38963,11998,'TP53','tumor protein p53','protein-coding gene',191170,15644),
	(30030,34281,'RNU6-37P','RNA, U6 small nuclear 37, pseudogene','pseudogene',NULL,NULL);
/*!40000 ALTER TABLE `gene` ENABLE KEYS */;
UNLOCK TABLES;



--
-- Insert relevant gene aliases
--

LOCK TABLES `gene_alias` WRITE;
/*!40000 ALTER TABLE `gene_alias` DISABLE KEYS */;
INSERT INTO `gene_alias` VALUES 
	(4430,2564,'RNF53'),
	(4432,2564,'PPP1R53'),
	(4433,2564,'FANCS'),
	(4440,2566,'XRCC11'),
	(4441,2566,'FANCD1'),
	(6845,4004,'uvomorulin'),
	(6846,4004,'CD324'),
	(6847,4004,'UVO'),
	(22212,13764,'KIAA0591'),
	(22213,13764,'KLP'),
	(22214,13764,'HMSNII'),
	(22215,13764,'CMT2A'),
	(41734,30030,'RNU6-37'),
	(51290,38963,'p53'),
	(51291,38963,'LFS1');
/*!40000 ALTER TABLE `gene_alias` ENABLE KEYS */;
UNLOCK TABLES;


--
-- Dumping data for table `variant`
--

LOCK TABLES `variant` WRITE;
/*!40000 ALTER TABLE `variant` DISABLE KEYS */;
INSERT INTO `variant` VALUES 
	(15,'chr2',214730440,'G','A',0,NULL,'chr1',0,'',''),
	(52,'chr13',32314943,'A','G',0,'dummy BRCA variant','chr1',0,'',''),
	(55,'chr16',68822185,'C','T',0,'PFAM annotation consequences','chr1',0,'',''),
	(71,'chr17',43124032,'AAGATTTTCTGCAT','A',0,NULL,'chr1',0,'',''),
	(72,'chr17',7670685,'G','A',0,'dummy TP53 variant','chr1',0,'',''),
	(119,'chr1',10295758,'G','A',0,NULL,'chr1',10355816,'G','A'),
	(139,'chr1',10304277,'T','C',0,NULL,'chr1',10364335,'T','C');
/*!40000 ALTER TABLE `variant` ENABLE KEYS */;
UNLOCK TABLES;




--
-- Dumping data for table `heredicare_center_classification`
--

LOCK TABLES `heredicare_center_classification` WRITE;
/*!40000 ALTER TABLE `heredicare_center_classification` DISABLE KEYS */;
INSERT INTO `heredicare_center_classification` VALUES 
	(46,'5',119,'Uniklinik Tübingen','this is a test','1999-01-01'),
	(47,'5',119,'Hamburger Hähnchenfabrik','this is a test for the second classificatoin center','2020-05-01'),
	(60,'5',139,'Uniklinik Tübingen','this is a test','1999-01-01'),
	(61,'5',139,'Hamburger Hähnchenfabrik','this is a test for the second classificatoin center','2020-05-01');
/*!40000 ALTER TABLE `heredicare_center_classification` ENABLE KEYS */;
UNLOCK TABLES;




--
-- Dumping data for table `pfam_id_mapping`
--

LOCK TABLES `pfam_id_mapping` WRITE;
/*!40000 ALTER TABLE `pfam_id_mapping` DISABLE KEYS */;
INSERT INTO `pfam_id_mapping` VALUES 
	(1711,'PF00028','Cadherin domain'),
	(9095,'PF00498','FHA domain'),
	(13575,'PF07710','P53 tetramerisation motif');
/*!40000 ALTER TABLE `pfam_id_mapping` ENABLE KEYS */;
UNLOCK TABLES;



--
-- Dumping data for table `variant_consequence`
--

LOCK TABLES `variant_consequence` WRITE;
/*!40000 ALTER TABLE `variant_consequence` DISABLE KEYS */;
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

	(1111,55,'ENST00000261769','c.1896C>T','p.His632%3D','synonymous variant','low',12,NULL,4004,'ensembl','PF00028','Cadherin domain'),
	(1112,55,'ENST00000422392','c.1713C>T','p.His571%3D','synonymous variant','low',11,NULL,4004,'ensembl','PF00028','Cadherin domain'),
	(1113,55,'ENST00000562087',NULL,NULL,'upstream gene variant','modifier',NULL,NULL,9549,'ensembl',NULL,NULL),
	(1114,55,'ENST00000562118',NULL,NULL,'upstream gene variant','modifier',NULL,NULL,4004,'ensembl',NULL,NULL),
	(1115,55,'ENST00000562836','n.1967C>T',NULL,'non coding transcript exon variant','modifier',11,NULL,4004,'ensembl',NULL,NULL),
	(1116,55,'ENST00000563916','n.263+1079G>A',NULL,'intron variant & non coding transcript variant','modifier',NULL,1,NULL,'ensembl',NULL,NULL),
	(1117,55,'ENST00000566510','c.*562C>T',NULL,'3 prime UTR variant & NMD transcript variant','modifier',11,NULL,4004,'ensembl',NULL,NULL),
	(1118,55,'ENST00000566612','c.*136C>T',NULL,'3 prime UTR variant & NMD transcript variant','modifier',11,NULL,4004,'ensembl',NULL,NULL),
	(1119,55,'NM_001317184','c.1713C>T','p.His571%3D','synonymous variant','low',11,NULL,4004,'refseq',NULL,NULL),
	(1120,55,'NM_001317185','c.348C>T','p.His116%3D','synonymous variant','low',12,NULL,4004,'refseq',NULL,NULL),
	(1121,55,'NM_001317186','c.-70C>T',NULL,'5 prime UTR variant','modifier',11,NULL,4004,'refseq',NULL,NULL),
	(1122,55,'NM_004360','c.1896C>T','p.His632%3D','synonymous variant','low',12,NULL,4004,'refseq',NULL,NULL),

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
	(2339,52,'NM_001136571','c.-390+372T>C',NULL,'intron variant','modifier',NULL,1,42061,'refseq',NULL,NULL),

	(2448,119,'ENST00000263934','c.1631G>A','p.Ser544Asn','missense variant','moderate',17,NULL,13764,'ensembl','PF00498','FHA domain'),
	(2450,119,'ENST00000362692',NULL,NULL,'upstream gene variant','modifier',NULL,NULL,30030,'ensembl',NULL,NULL),
	(2453,119,'ENST00000377081','c.1769G>A','p.Ser590Asn','missense variant','moderate',18,NULL,13764,'ensembl','PF00498','FHA domain'),
	(2457,119,'ENST00000377083','c.1631G>A','p.Ser544Asn','missense variant','moderate',17,NULL,13764,'ensembl','PF00498','FHA domain'),
	(2460,119,'ENST00000377086','c.1769G>A','p.Ser590Asn','missense variant','moderate',19,NULL,13764,'ensembl','PF00498','FHA domain'),
	(2461,119,'ENST00000377093','c.1631G>A','p.Ser544Asn','missense variant','moderate',17,NULL,13764,'ensembl','PF00498','FHA domain'),
	(2463,119,'ENST00000497835',NULL,NULL,'downstream gene variant','modifier',NULL,NULL,13764,'ensembl',NULL,NULL),
	(2464,119,'ENST00000620295','c.1727G>A','p.Ser576Asn','missense variant','moderate',17,NULL,13764,'ensembl','PF00498','FHA domain'),
	(2466,119,'ENST00000622724','c.1691G>A','p.Ser564Asn','missense variant','moderate',18,NULL,13764,'ensembl','PF00498','FHA domain'),
	(2468,119,'ENST00000676179','c.1769G>A','p.Ser590Asn','missense variant','moderate',19,NULL,13764,'ensembl','PF00498','FHA domain'),
	(2469,119,'ENSR00000919611',NULL,NULL,'regulatory region variant','modifier',NULL,NULL,NULL,'ensembl',NULL,NULL),
	(2471,119,'NM_001365951','c.1769G>A','p.Ser590Asn','missense variant','moderate',19,NULL,13764,'refseq',NULL,NULL),
	(2472,119,'NM_001365952','c.1769G>A','p.Ser590Asn','missense variant','moderate',19,NULL,13764,'refseq',NULL,NULL),
	(2474,119,'NM_001365953','c.1631G>A','p.Ser544Asn','missense variant','moderate',17,NULL,13764,'refseq',NULL,NULL),
	(2475,119,'NM_015074','c.1631G>A','p.Ser544Asn','missense variant','moderate',17,NULL,13764,'refseq',NULL,NULL),
	(2476,119,'NM_183416','c.1631G>A','p.Ser544Asn','missense variant','moderate',17,NULL,13764,'refseq',NULL,NULL);
/*!40000 ALTER TABLE `variant_consequence` ENABLE KEYS */;
UNLOCK TABLES;






--
-- Dumping data for table `variant_ids`
--

LOCK TABLES `variant_ids` WRITE;
/*!40000 ALTER TABLE `variant_ids` DISABLE KEYS */;
INSERT INTO `variant_ids` VALUES 
	(57,119,'SCV002541050','clinvar_accession'),
	(55,119,'SUB11823131','clinvar_submission'),
	(40,119,'11740058','heredicare'),

	(51,139,'11334923','heredicare'),
	(52,139,'11509431','heredicare');
/*!40000 ALTER TABLE `variant_ids` ENABLE KEYS */;
UNLOCK TABLES;






--
-- insert some literature entries
--

LOCK TABLES `variant_literature` WRITE;
/*!40000 ALTER TABLE `variant_literature` DISABLE KEYS */;
INSERT INTO `variant_literature` VALUES 
	(16,15,25741868,'Standards and guidelines for the interpretation of sequence variants: a joint consensus recommendation of the American College of Medical Genetics and Genomics and the Association for Molecular Pathology.','Sue Richards, Nazneen Aziz, Sherri Bale, David Bick, Soma Das, Julie Gastier-Foster, Wayne W Grody, Madhuri Hegde, Elaine Lyon, Elaine Spector, Karl Voelkerding, Heidi L Rehm, ACMG Laboratory Quality Assurance Committee','Genetics in medicine : official journal of the American College of Medical Genetics',2015),
	(17,15,29458332,'Identification of genetic variants for clinical management of familial colorectal tumors.','Mev Dominguez-Valentin, Sigve Nakken, Hélène Tubeuf, Daniel Vodak, Per Olaf Ekstrøm, Anke M Nissen, Monika Morak, Elke Holinski-Feder, Alexandra Martins, Pål Møller, Eivind Hovig','BMC medical genetics',2018),
	(18,15,32039725,'Germline variants in DNA repair genes associated with hereditary breast and ovarian cancer syndrome: analysis of a 21 gene panel in the Brazilian population.','Simone da Costa E Silva Carvalho, Nathalia Moreno Cury, Danielle Barbosa Brotto, Luiza Ferreira de Araujo, Reginaldo Cruz Alves Rosa, Lorena Alves Texeira, Jessica Rodrigues Plaça, Adriana Aparecida Marques, Kamila Chagas Peronni, Patricia de Cássia Ruy, Greice Andreotti Molfetta, Julio Cesar Moriguti, Dirce Maria Carraro, Edenir Inêz Palmero, Patricia Ashton-Prolla, Victor Evangelista de Faria Ferraz, Wilson Araujo Silva','BMC medical genomics',2020),
	(19,15,16741161,'Variants in the GH-IGF axis confer susceptibility to lung cancer.','Matthew F Rudd, Emily L Webb, Athena Matakidou, Gabrielle S Sellick, Richard D Williams, Helen Bridle, Tim Eisen, Richard S Houlston, GELCAPS Consortium','Genome research',2006),
	(20,15,19584272,'Modification of ovarian cancer risk by BRCA1/2-interacting genes in a multicenter cohort of BRCA1/2 mutation carriers.','Timothy R Rebbeck, Nandita Mitra, Susan M Domchek, Fei Wan, Shannon Chuai, Tara M Friebel, Saarene Panossian, Amanda Spurdle, Georgia Chenevix-Trench, kConFab, Christian F Singer, Georg Pfeiler, Susan L Neuhausen, Henry T Lynch, Judy E Garber, Jeffrey N Weitzel, Claudine Isaacs, Fergus Couch, Steven A Narod, Wendy S Rubinstein, Gail E Tomlinson, Patricia A Ganz, Olufunmilayo I Olopade, Nadine Tung, Joanne L Blum, Roger Greenberg, Katherine L Nathanson, Mary B Daly','Cancer research',2009),
	(21,15,26315354,'Germline Mutations in the BRIP1, BARD1, PALB2, and NBN Genes in Women With Ovarian Cancer.','Susan J Ramus, Honglin Song, Ed Dicks, Jonathan P Tyrer, Adam N Rosenthal, Maria P Intermaggio, Lindsay Fraser, Aleksandra Gentry-Maharaj, Jane Hayward, Susan Philpott, Christopher Anderson, Christopher K Edlund, David Conti, Patricia Harrington, Daniel Barrowdale, David D Bowtell, Kathryn Alsop, Gillian Mitchell, AOCS Study Group, Mine S Cicek, Julie M Cunningham, Brooke L Fridley, Jennifer Alsop, Mercedes Jimenez-Linan, Samantha Poblete, Shashi Lele, Lara Sucheston-Campbell, Kirsten B Moysich, Weiva Sieh, Valerie McGuire, Jenny Lester, Natalia Bogdanova, Matthias Dürst, Peter Hillemanns, Ovarian Cancer Association Consortium, Kunle Odunsi, Alice S Whittemore, Beth Y Karlan, Thilo Dörk, Ellen L Goode, Usha Menon, Ian J Jacobs, Antonis C Antoniou, Paul D P Pharoah, Simon A Gayther','Journal of the National Cancer Institute',2015),
	(22,15,19412175,'Common variations in BARD1 influence susceptibility to high-risk neuroblastoma.','Mario Capasso, Marcella Devoto, Cuiping Hou, Shahab Asgharzadeh, Joseph T Glessner, Edward F Attiyeh, Yael P Mosse, Cecilia Kim, Sharon J Diskin, Kristina A Cole, Kristopher Bosse, Maura Diamond, Marci Laudenslager, Cynthia Winter, Jonathan P Bradfield, Richard H Scott, Jayanti Jagannathan, Maria Garris, Carmel McConville, Wendy B London, Robert C Seeger, Struan F A Grant, Hongzhe Li, Nazneen Rahman, Eric Rappaport, Hakon Hakonarson, John M Maris','Nature genetics',2009),
	(23,15,31258718,'Functional Polymorphisms in <i>BARD1</i> Association with Neuroblastoma in a regional Han Chinese Population.','Jin Shi, Yongbo Yu, Yaqiong Jin, Jie Lu, Jie Zhang, Huanmin Wang, Wei Han, Ping Chu, Jun Tai, Feng Chen, Huimin Ren, Yongli Guo, Xin Ni','Journal of Cancer',2019),
	(24,15,16061562,'Identification and characterization of missense alterations in the BRCA1 associated RING domain (BARD1) gene in breast and ovarian cancer.','M K Sauer, I L Andrulis','Journal of medical genetics',2005),
	(25,15,20077502,'Cancer predisposing missense and protein truncating BARD1 mutations in non-BRCA1 or BRCA2 breast cancer families.','Sylvia De Brakeleer, Jacques De Grève, Remy Loris, Nicolas Janin, Willy Lissens, Erica Sermijn, Erik Teugels','Human mutation',2010),
	(26,15,9425226,'Mutations in the BRCA1-associated RING domain (BARD1) gene in primary breast, ovarian and uterine cancers.','T H Thai, F Du, J T Tsan, Y Jin, A Phung, M A Spillman, H F Massa, C Y Muller, R Ashfaq, J M Mathis, D S Miller, B J Trask, R Baer, A M Bowcock','Human molecular genetics',1998),
	(27,15,15342711,'Mutation screening of the BARD1 gene: evidence for involvement of the Cys557Ser allele in hereditary susceptibility to breast cancer.','S-M Karppinen, K Heikkinen, K Rapakko, R Winqvist','Journal of medical genetics',2004),
	(28,15,16333312,'BARD1 variants Cys557Ser and Val507Met in breast cancer predisposition.','Pia Vahteristo, Kirsi Syrjäkoski, Tuomas Heikkinen, Hannaleena Eerola, Kristiina Aittomäki, Karl von Smitten, Kaija Holli, Carl Blomqvist, Olli-Pekka Kallioniemi, Heli Nevanlinna','European journal of human genetics : EJHG',2006),
	(29,15,25994375,'Analysis of large mutations in BARD1 in patients with breast and/or ovarian cancer: the Polish population as an example.','Katarzyna Klonowska, Magdalena Ratajska, Karol Czubak, Alina Kuzniacka, Izabela Brozek, Magdalena Koczkowska, Marcin Sniadecki, Jaroslaw Debniak, Dariusz Wydra, Magdalena Balut, Maciej Stukan, Agnieszka Zmienko, Beata Nowakowska, Irmgard Irminger-Finger, Janusz Limon, Piotr Kozlowski','Scientific reports',2015),
	(30,15,26350354,'Functional Analysis of BARD1 Missense Variants in Homology-Directed Repair of DNA Double Strand Breaks.','Cindy Lee, Tapahsama Banerjee, Jessica Gillespie, Amanda Ceravolo, Matthew R Parvinsmith, Lea M Starita, Stanley Fields, Amanda E Toland, Jeffrey D Parvin','Human mutation',2015);
/*!40000 ALTER TABLE `variant_literature` ENABLE KEYS */;
UNLOCK TABLES;




--
-- Dumping data for table `clinvar_submission`
--

LOCK TABLES `clinvar_submission` WRITE;
/*!40000 ALTER TABLE `clinvar_submission` DISABLE KEYS */;
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
	(7901,702,'Likely benign','2017-04-27','criteria provided, single submitter','C0346153:Familial cancer of breast','Illumina Laboratory Services, Illumina','description: This variant was observed as part of a predisposition screen in an ostensibly healthy population. A literature search was performed for the gene, cDNA change, and amino acid change (where applicable). Publications were found based on this search. The evidence from the literature, in combination with allele frequency data from public databases where available, was sufficient to determine this variant is unlikely to cause disease. Therefore, this variant is classified as likely benign.');
/*!40000 ALTER TABLE `clinvar_submission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `clinvar_variant_annotation`
--

LOCK TABLES `clinvar_variant_annotation` WRITE;
/*!40000 ALTER TABLE `clinvar_variant_annotation` DISABLE KEYS */;
INSERT INTO `clinvar_variant_annotation` VALUES 
	(702,15,136500,'Conflicting_interpretations_of_pathogenicity|Uncertain_significance(1)|_Benign(8)|_Likely_benign(4)','criteria_provided,_conflicting_interpretations');
/*!40000 ALTER TABLE `clinvar_variant_annotation` ENABLE KEYS */;
UNLOCK TABLES;
