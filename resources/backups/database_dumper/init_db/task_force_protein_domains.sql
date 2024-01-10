-- MySQL dump 10.13  Distrib 8.0.35, for Linux (x86_64)
--

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `task_force_protein_domains`
--

DROP TABLE IF EXISTS `task_force_protein_domains`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `task_force_protein_domains` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `gene_id` int(10) unsigned NOT NULL,
  `chr` enum('chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9','chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17','chr18','chr19','chr20','chr21','chr22','chrX','chrY','chrMT') NOT NULL,
  `start` int(11) NOT NULL,
  `end` int(11) NOT NULL,
  `description` text NOT NULL,
  `source` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_task_force_protein_domain_gene_idx` (`gene_id`),
  CONSTRAINT `FK_task_force_protein_domain_gene` FOREIGN KEY (`gene_id`) REFERENCES `gene` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=86 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task_force_protein_domains`
--

LOCK TABLES `task_force_protein_domains` WRITE;
/*!40000 ALTER TABLE `task_force_protein_domains` DISABLE KEYS */;
INSERT INTO `task_force_protein_domains` VALUES (1,1856,'chr11',108229263,108229283,'Substrate binding','BWRL'),(2,1856,'chr11',108249020,108249031,'NLS','BWRL'),(3,1856,'chr11',108282785,108282847,'Leucine zipper','BWRL'),(4,1856,'chr11',108288984,108289013,'Proline rich','BWRL'),(5,1856,'chr11',108307899,108365505,'FATKIN','BWRL'),(6,2218,'chr2',214792346,214809449,'RING','PMID: 32726901'),(7,2218,'chr2',214752552,214780595,'ANK','PMID: 32726901'),(8,2218,'chr2',214728709,214745830,'BRCT Domains','PMID: 32726901'),(9,2626,'chr17',43104260,43124096,'RING','BWRL/ENIGMA'),(10,2626,'chr17',43104872,43104928,'NES','BWRL/ENIGMA'),(11,2626,'chr17',43094007,43094024,'NLS1','BWRL/ENIGMA'),(12,2626,'chr17',43093689,43093712,'NLS2','BWRL/ENIGMA'),(13,2626,'chr17',43093563,43093580,'NLS3','BWRL/ENIGMA'),(14,2626,'chr17',43082489,43090958,'COILED-COIL','BWRL/ENIGMA'),(15,2626,'chr17',43045681,43070966,'BRCT DOMAINS','BWRL/ENIGMA'),(16,2628,'chr13',32316488,32319129,'PALB2 Binding','BWRL/ENIGMA'),(17,2628,'chr13',32337362,32340601,'Interaction with RAD51 (BRC-1 bis BRC-8)','Uniprot'),(18,2628,'chr13',32354901,32357757,'Interaction with FANCD2','Uniprot'),(19,2628,'chr13',32356433,32396954,'DBD (DNA/DSS1 binding domain- helical OB1, OB2, OB3)','BWRL/ENIGMA'),(20,2628,'chr13',32363246,32363296,'Nuclear export signal; masked by interaction with SEM1','Uniprot'),(21,2628,'chr13',32298300,32398506,'C-terminal RAD51 binding domain (inkl. NLS1 und BRC-) ','BWRL/ENIGMA'),(22,2663,'chr17',61686080,61861539,'ATPase/Helicase domain','PMID: 33619228'),(23,2663,'chr17',61683857,61686079,'BRCA1 Interaction','PMID: 33619228'),(24,4061,'chr1',68737416,68833496,'Bisher bekannten pathogenen CDH1-Varianten sind über den gesamten Locus verteilt und es kann daher keine klinisch relevante funktionelle Proteindomäne definiert werden.','BWRL'),(25,4575,'chr22',28734515,28734667,'SQ/TQ-rich','BWRL'),(26,4575,'chr22',28719463,28734448,'FHA','BWRL'),(27,4575,'chr22',28689174,28719444,'Kinase','BWRL'),(28,4575,'chr22',28687915,28687986,'NLS','BWRL'),(29,24639,'chr16',23637932,23641133,'BRCA1 interaction domain','BWRL'),(30,24639,'chr16',23635827,23641157,'DNA binding and Interaction with BRCA1','https://pubmed.ncbi.nlm.nih.gov/19369211/'),(31,24639,'chr16',23635994,23636245,'RAD51 binding site','BWRL'),(32,24639,'chr16',23634863,23635432,'DNA binding site','BWRL'),(33,24639,'chr16',23629862,23630323,'MRG15 (MORF4L1) interaction domain','BWRL'),(34,24639,'chr16',23603462,23629233,'WD40 repeat','BWRL'),(35,27567,'chr17',58692644,58694983,'N-terminal region','BWRL'),(36,27567,'chr17',58695020,58734219,'ATPase domain and RAD51B, XRCC3, and RAD51D binding','BWRL'),(37,27567,'chr17',58734187,58734201,'Nuclear localization signal','BWRL'),(38,27568,'chr17',35118515,35119613,'N-terminal region','BWRL https://www.sciencedirect.com/science/article/abs/pii/S1357272510003924'),(39,27568,'chr17',35118530,35118586,'Linker','BWRL'),(40,27568,'chr17',35101282,35107416,'ATPase domain and RAD51B, RAD51C, and XRCC2 binding','BWRL (PMID 10749867, 14704354, 19327148)'),(41,39407,'chr17',7676204,7676594,'Transcription activation (TAD1+TAD2)','https://pubmed.ncbi.nlm.nih.gov/27145840/'),(42,39407,'chr17',7676087,7676188,'Proline rich domain','BWRL'),(43,39407,'chr17',7673744,7676065,'DNA binding region ','BWRL'),(44,39407,'chr17',7673559,7673719,'NLS ','https://pubmed.ncbi.nlm.nih.gov/10321742/'),(45,39407,'chr17',7670641,7673555,'Oligomerization region','BWRL'),(46,39407,'chr17',7669612,7670643,'CTD (repression of DNA-binding region)','https://pubmed.ncbi.nlm.nih.gov/27145840/'),(47,20574,'chr3',36993548,37020439,'N-terminal domain (MutSa interaction)','Insight Richtlinien und PMID: 26249686'),(48,20574,'chr3',36993605,37007051,'ATPase domain','Insight Richtlinien und PMID: 26249686'),(49,20574,'chr3',37025826,37048570,'EXO1 interaction','Insight Richtlinien und PMID: 28765196'),(50,20574,'chr3',37028848,37050611,'PMS2/MLH3/PMS1 interaction','Insight Richtlinien und PMID: 28765196'),(51,20574,'chr3',37026003,37028808,'NLS ','Insight Richtlinien und PMID: 28765196'),(52,20574,'chr3',37047540,37047572,'NES1','Insight Richtlinien'),(53,20574,'chr3',37048568,37048609,'NES2','Insight Richtlinien'),(54,21060,'chr2',47403192,47410099,'DNA mismatch binding domain','Insight Richtlinien und PMID: 23391514'),(55,21060,'chr2',47410100,47414367,'Connector domain','Insight Richtlinien und PMID: 28765196'),(56,21060,'chr2',47410337,47412443,'MutLa interaction','Insight Richtlinien'),(57,21060,'chr2',47414374,47445639,'Lever domain','Insight Richtlinien und PMID: 28765196'),(58,21060,'chr2',47466807,47475122,'Lever domain','Insight Richtlinien und PMID: 28765196'),(59,21060,'chr2',47445640,47466806,'Clamp domain','Insight Richtlinien und PMID: 28765196 PMID: 28765196'),(60,21060,'chr2',47475123,47482946,'ATPase and  Helix-Turn-Helix','Insight Richtinien und PMID: 23391514;PMID: 28765196'),(61,21060,'chr2',47429797,47475140,'MSH6/MSH3 interaction','Insight Richtlinien und PMID: 28765196'),(62,21060,'chr2',47463061,47476419,'MutLa interaction','InSiGHT Richtlinien'),(63,21060,'chr2',47480860,47482946,'MSH6/MSH3 interaction','Insight Richtlinien und PMID: 28765196'),(64,21060,'chr2',47414272,47476374,'EXO1 stabilisation and interaction','InSiGHT Richtlinien und PMID: 28765196 PMID: 28765196'),(65,21066,'chr2',47783243,47783266,'PCNA binding domain','PMID: 23391514; PMID: 28765196; InSiGHT-Richtlinien'),(66,21066,'chr2',47790931,47796018,'PWWP domain','PMID: 23391514; PMID: 28765196; InSiGHT-Richtlinien'),(67,21066,'chr2',47799067,47799540,'DNA mismatch /MMR binding domain','PMID: 23391514;PMID: 28765196'),(68,21066,'chr2',47799499,47800134,'Connector domain','Insight Richtlinien;PMID: 23391514; PMID: 28765196'),(69,21066,'chr2',47800135,47800785,'Lever domain','PMID: 23391514; PMID: 28765196'),(70,21066,'chr2',47801008,47803472,'Lever domain','PMID: 23391514; PMID: 28765196'),(71,21066,'chr2',47800786,47801007,'Clamp domain','PMID: 23391514; PMID: 28765196'),(72,21066,'chr2',47803473,47806857,'ATPase/ATP binding','Insight und PMID: 23391514; PMID: 28765196'),(73,21066,'chr2',47806554,47806857,'MSH2 interaction','Insight Richtlinien'),(74,25975,'chr7',5969849,6009019,'ATPase/ATP binding','InSiGHT Richtlinien'),(75,25975,'chr7',5973423,5982975,'Dimerisation/MLH1 interaction','P54278 (P54278) - protein - InterPro (ebi.ac.uk); PMID: 28765196; InSiGHT-Richtlinien'),(76,25975,'chr7',5982853,5982906,'Exonuclease active site','PMID: 28765196'),(77,25975,'chr7',5986869,5986892,'NLS ','Insight Richtlinien'),(78,37614,'chr19',1207076,1207102,'Nucleotide binding ATP','STK11 - Serine/threonine-protein kinase STK11 precursor - Homo sapiens (Human) - STK11 gene & protein (uniprot.org)'),(79,37614,'chr19',1207058,1222991,'Protein kinase domain','STK11 - Serine/threonine-protein kinase STK11 precursor - Homo sapiens (Human) - STK11 gene & protein (uniprot.org)'),(80,37614,'chr19',1207046,1207183,'SIRT1 interaction','STK11 - Serine/threonine-protein kinase STK11 precursor - Homo sapiens (Human) - STK11 gene & protein (uniprot.org)'),(81,27137,'chr10',87864470,87864511,'N-terminal phosphatidylinositol (Ptdlnsf4, 5) P2-binding domain (PBD)','PMID: 24656806, PMID: 34140896'),(82,27137,'chr10',87864512,87952177,'phosphatase domain','PMID: 24656806, PMID: 34140896'),(83,27137,'chr10',87952178,87965310,'C2 lipid or membrane-binding domain','PMID: 24656806, PMID: 34140896'),(84,27137,'chr10',87965311,87965469,'carboxy-terminal tail','PMID: 24656806, PMID: 34140896'),(85,27137,'chr10',87965461,87965469,'class I PDZ-binding (PDZ-BD) motif','PMID: 24656806, PMID: 34140896');
/*!40000 ALTER TABLE `task_force_protein_domains` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-01-10 10:23:48
