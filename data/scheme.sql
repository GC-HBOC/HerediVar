CREATE DATABASE  IF NOT EXISTS `bioinf_heredivar_ahdoebm1_2` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `bioinf_heredivar_ahdoebm1_2`;
-- MySQL dump 10.13  Distrib 8.0.20, for Win64 (x86_64)
--
-- Host: SRV018.img.med.uni-tuebingen.de    Database: bioinf_heredivar_ahdoebm1
-- ------------------------------------------------------
-- Server version	5.7.37-0ubuntu0.18.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `annotation_queue`
--

DROP TABLE IF EXISTS `annotation_queue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `annotation_queue` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `variant_id` int(10) unsigned NOT NULL,
  `user_id` int(10) unsigned NOT NULL,
  `requested` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('pending','success','error') NOT NULL DEFAULT 'pending',
  `finished_at` datetime DEFAULT NULL,
  `error_message` longtext,
  PRIMARY KEY (`id`),
  KEY `annotation_log_variant_idx` (`variant_id`),
  KEY `annotation_log_user_idx` (`user_id`),
  CONSTRAINT `FK_annotation_log_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_annotation_log_variant` FOREIGN KEY (`variant_id`) REFERENCES `variant` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `annotation_type`
--

DROP TABLE IF EXISTS `annotation_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `annotation_type` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` text NOT NULL,
  `description` text NOT NULL,
  `value_type` enum('int','float','text') NOT NULL,
  `version` text NOT NULL COMMENT 'Either the version name of the resource or, if there is no versioning, the date when the resource was accessed.',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `classification`
--

DROP TABLE IF EXISTS `classification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `classification` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `classification` enum('1','2','3','4','5') NOT NULL,
  `variant_id` int(10) unsigned NOT NULL,
  `user_id` int(10) unsigned NOT NULL,
  `comment` text NOT NULL,
  `date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `classification_variant_idx` (`variant_id`),
  KEY `classification_user_idx` (`user_id`),
  CONSTRAINT `FK_user_classification` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_variant_classification` FOREIGN KEY (`variant_id`) REFERENCES `variant` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `consensus_classification`
--

DROP TABLE IF EXISTS `consensus_classification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `consensus_classification` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `variant_id` int(10) unsigned NOT NULL,
  `classification` enum('1','2','3','4','5') NOT NULL,
  `comment` text NOT NULL,
  `date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `evidence_document` blob NOT NULL,
  PRIMARY KEY (`id`),
  KEY `consensus_classification_variant_idx` (`variant_id`),
  CONSTRAINT `FK_variant_consensus_classification` FOREIGN KEY (`variant_id`) REFERENCES `variant` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gene`
--

DROP TABLE IF EXISTS `gene`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gene` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `hgnc_id` text NOT NULL,
  `symbol` text NOT NULL,
  `description` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `first_name` text NOT NULL,
  `last_name` text NOT NULL,
  `affilitation` text NOT NULL,
  `mail` text NOT NULL,
  `secret` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `variant`
--

DROP TABLE IF EXISTS `variant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `variant` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `chr` enum('chr1','chr2','chr3','chr4','chr5','chr6','chr7','chr8','chr9','chr10','chr11','chr12','chr13','chr14','chr15','chr16','chr17','chr18','chr19','chr20','chr21','chr22','chrX','chrY','chrMT') NOT NULL,
  `pos` int(10) unsigned NOT NULL,
  `ref` text NOT NULL,
  `alt` text NOT NULL,
  `heredicare_seqid` int(10) unsigned DEFAULT NULL COMMENT '-1 if there is no heredicare_seqid (eg. if it was put in by hand through the web interface)',
  `error` tinyint(1) NOT NULL DEFAULT '0',
  `error_description` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `variant_annotation`
--

DROP TABLE IF EXISTS `variant_annotation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `variant_annotation` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `variant_id` int(11) unsigned NOT NULL,
  `annotation_type_id` int(11) unsigned NOT NULL,
  `vlaue` text NOT NULL,
  `supplementary_document` blob,
  PRIMARY KEY (`id`),
  KEY `variant_annotation_variant_idx` (`variant_id`),
  KEY `variant_annotation_variant_type_idx` (`annotation_type_id`),
  CONSTRAINT `variant` FOREIGN KEY (`variant_id`) REFERENCES `variant` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `variant_type` FOREIGN KEY (`annotation_type_id`) REFERENCES `annotation_type` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `variant_consequence`
--

DROP TABLE IF EXISTS `variant_consequence`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `variant_consequence` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `variant_id` int(11) unsigned NOT NULL,
  `transcript_name` text NOT NULL,
  `hgvs_c` text,
  `hgvs_p` text,
  `consequence` text NOT NULL,
  `impact` enum('high','moderate','low','modifier') NOT NULL,
  `exon_nr` int(11) unsigned DEFAULT NULL,
  `intron_nr` int(11) unsigned DEFAULT NULL,
  `gene_id` int(11) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `variant_idx` (`variant_id`),
  KEY `gene_idx` (`gene_id`),
  KEY `variant_consequence_variant_idx` (`variant_id`),
  KEY `variant_consequence_gene_idx` (`gene_id`),
  CONSTRAINT `FK_gene_variant_consequence` FOREIGN KEY (`gene_id`) REFERENCES `gene` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_variant_variant_consequence` FOREIGN KEY (`variant_id`) REFERENCES `variant` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Final view structure for view `variant_view`
--

/*!50001 DROP VIEW IF EXISTS `variant_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`ahdoebm1`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `variant_view` AS select `variant`.`id` AS `id`,`variant`.`chr` AS `chr`,`variant`.`pos` AS `pos`,`variant`.`ref` AS `ref`,`variant`.`alt` AS `alt`,`variant`.`heredicare_seqid` AS `heredicare_seqid`,`variant`.`error` AS `error`,`variant`.`error_description` AS `error_description` from `variant` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-03-10 15:14:52
