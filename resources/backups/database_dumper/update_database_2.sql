-- CREATE TABLE `HerediVar`.`variant_transcript_annotation` (
--   `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
--   `variant_id` INT UNSIGNED NOT NULL,
--   `annotation_type_id` INT UNSIGNED NOT NULL,
--   `transcript` VARCHAR(45) NOT NULL,
--   `value` TEXT NOT NULL,
--   UNIQUE INDEX `id_UNIQUE` (`id` ASC),
--   PRIMARY KEY (`id`),
--   INDEX `FK_variant_transcript_annotation_variant_idx` (`variant_id` ASC),
--   INDEX `FK_variant_transcript_annotation_annotation_type_idx` (`annotation_type_id` ASC),
--   CONSTRAINT `FK_variant_transcript_annotation_variant`
--     FOREIGN KEY (`variant_id`)
--     REFERENCES `HerediVar`.`variant` (`id`)
--     ON DELETE CASCADE
--     ON UPDATE NO ACTION,
--   CONSTRAINT `FK_variant_transcript_annotation_annotation_type`
--     FOREIGN KEY (`annotation_type_id`)
--     REFERENCES `HerediVar`.`annotation_type` (`id`)
--     ON DELETE NO ACTION
--     ON UPDATE NO ACTION)
-- ENGINE = InnoDB
-- DEFAULT CHARACTER SET = utf8;
-- 
-- 
-- ALTER TABLE `HerediVar`.`variant_transcript_annotation` 
-- ADD UNIQUE INDEX `UNIQUE_variant_transcript_annotation` (`variant_id` ASC, `annotation_type_id` ASC, `transcript` ASC),
-- DROP INDEX `id_UNIQUE` ;

-- ALTER TABLE `HerediVar`.`annotation_type` 
-- ADD COLUMN `is_transcript_specific` TINYINT(1) NOT NULL DEFAULT 0 AFTER `group_name`;
-- 
-- INSERT INTO `HerediVar`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`) VALUES ('maxentscan', 'MaxEntScan', 'The transcript specific MaxEntScan scores calculated from ngs-bits. Each value is of the form: ref|alt', 'text', 'v1.0.0', '2023-09-27', 'Splicing', 1);
-- INSERT INTO `HerediVar`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`) VALUES ('maxentscan_swa', 'MaxEntScan SWA', 'The transcript specific MaxEntScan SWA scores calculated from ngs-bits. A special application of the MaxEntScan algorithm to discover de-novo spliceing variants. Each value is of the form maxentscan_ref_donor|maxentscan_alt_donor|maxentscan_donor_comp|maxentscan_ref_acceptor|maxentscan_alt_acceptor|maxentscan_acceptor_comp', 'text', 'v1.0.0', '2023-09-27', 'Splicing', 1);
-- 
-- 
-- 
-- 
-- GRANT SELECT, INSERT, UPDATE ON HerediVar.variant_transcript_annotation TO 'HerediVar_annotation';
-- GRANT SELECT ON HerediVar.variant_transcript_annotation TO 'HerediVar_user';
-- GRANT SELECT ON HerediVar.variant_transcript_annotation TO 'HerediVar_superuser';
-- GRANT SELECT ON HerediVar.variant_transcript_annotation TO 'HerediVar_read_only';
-- 
-- 
-- 
-- 
-- UPDATE `HerediVar`.`annotation_type` SET `group_name` = 'Protein Domain' WHERE (`id` = '36');
-- UPDATE `HerediVar`.`annotation_type` SET `group_name` = 'Protein Domain' WHERE (`id` = '37');
-- UPDATE `HerediVar`.`annotation_type` SET `group_name` = 'None' WHERE (`id` = '9');
-- UPDATE `HerediVar`.`annotation_type` SET `group_name` = 'None' WHERE (`id` = '10');
-- 
-- 
-- 
-- 
-- ALTER TABLE `HerediVar`.`variant_heredicare_annotation` 
-- ADD INDEX `FK_variant_heredicare_annotation_variant_idx` (`variant_id` ASC);
-- ;
-- ALTER TABLE `HerediVar`.`variant_heredicare_annotation` 
-- ADD CONSTRAINT `FK_variant_heredicare_annotation_variant`
--   FOREIGN KEY (`variant_id`)
--   REFERENCES `HerediVar`.`variant` (`id`)
--   ON DELETE NO ACTION
--   ON UPDATE NO ACTION;
-- 
-- 
-- ALTER TABLE `HerediVar`.`annotation_queue` 
-- CHANGE COLUMN `error_message` `error_message` TEXT NULL DEFAULT '' ;
-- 
-- 
-- ALTER TABLE `HerediVar`.`variant_ids` 
-- ADD COLUMN `annotation_type_id` INT UNSIGNED NOT NULL AFTER `id_source`;
-- 
-- 
-- INSERT INTO `HerediVar`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`) VALUES ('heredicare_vid', 'HerediCare VID', 'The VID from HerediCare.The version_date is inaccurate. They are always up to date when reimporting from heredicare.', 'int', '-', '2023-01-01', 'ID', '0');

UPDATE variant_ids SET annotation_type_id = (SELECT id FROM annotation_type WHERE title = 'heredicare_vid') WHERE id_source = 'heredicare';


ALTER TABLE `HerediVar`.`variant_ids` 
ADD INDEX `FK_variant_ids_annotation_type_idx` (`annotation_type_id` ASC);
;
ALTER TABLE `HerediVar`.`variant_ids` 
ADD CONSTRAINT `FK_variant_ids_annotation_type`
  FOREIGN KEY (`annotation_type_id`)
  REFERENCES `HerediVar`.`annotation_type` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


ALTER TABLE `HerediVar`.`variant_ids` 
DROP COLUMN `id_source`,
DROP INDEX `variant_id_external_id_id_source_key` ,
ADD UNIQUE INDEX `variant_id_external_id_id_source_key` (`variant_id` ASC, `external_id` ASC);
;

ALTER TABLE `HerediVar`.`variant_ids` 
DROP INDEX `variant_id_external_id_id_source_key`;
ALTER TABLE `HerediVar`.`variant_ids` 
ADD UNIQUE INDEX `unique_variant_ids` (`variant_id` ASC, `external_id` ASC, `annotation_type_id` ASC);
;
UPDATE annotation_type SET group_name = "ID" WHERE title = 'rsid'



INSERT INTO `HerediVar`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`) VALUES ('clinvar', 'ClinVar variation ID', 'The Variation ID from ClinVar', 'int', '-', '2023-02-26', 'ID', '0');





SET FOREIGN_KEY_CHECKS = 0; 
TRUNCATE table gene_alias; 
SET FOREIGN_KEY_CHECKS = 1;

SET FOREIGN_KEY_CHECKS = 0; 
TRUNCATE table gene; 
SET FOREIGN_KEY_CHECKS = 1;

SET FOREIGN_KEY_CHECKS = 0; 
TRUNCATE table transcript; 
SET FOREIGN_KEY_CHECKS = 1;


ALTER TABLE `HerediVar`.`transcript` 
ADD COLUMN `start` INT NOT NULL AFTER `length`,
ADD COLUMN `end` INT NOT NULL AFTER `start`;


ALTER TABLE `HerediVar`.`transcript` 
ADD COLUMN `chrom` ENUM('chr1', 'chr2', 'chr3', 'chr4', 'chr5', 'chr6', 'chr7', 'chr8', 'chr9', 'chr10', 'chr11', 'chr12', 'chr13', 'chr14', 'chr15', 'chr16', 'chr17', 'chr18', 'chr19', 'chr20', 'chr21', 'chr22', 'chrX', 'chrY', 'chrMT') NOT NULL AFTER `length`;


ALTER TABLE `HerediVar`.`transcript` 
ADD COLUMN `orientation` ENUM('+', '-') NOT NULL AFTER `end`;


CREATE TABLE `HerediVar`.`new_table` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `transcript_id` INT UNSIGNED NOT NULL,
  `start` INT NOT NULL,
  `end` INT NOT NULL,
  `cdna_start` INT NULL,
  `cdna_end` INT NULL,
  `is_cds` TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`));

ALTER TABLE `HerediVar`.`new_table` 
RENAME TO  `HerediVar`.`exon` ;

ALTER TABLE `HerediVar`.`exon` 
ADD INDEX `FK_exon_transcript_idx` (`transcript_id` ASC);
;
ALTER TABLE `HerediVar`.`exon` 
ADD CONSTRAINT `FK_exon_transcript`
  FOREIGN KEY (`transcript_id`)
  REFERENCES `HerediVar`.`transcript` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;

ALTER TABLE `HerediVar`.`exon` 
DROP FOREIGN KEY `FK_exon_transcript`;
ALTER TABLE `HerediVar`.`exon` 
ADD CONSTRAINT `FK_exon_transcript`
  FOREIGN KEY (`transcript_id`)
  REFERENCES `HerediVar`.`transcript` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;


INSERT INTO `HerediVar`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`) VALUES ('gnomad_popmax_AC', 'popmax AC', 'The allele count from the popmax population from GnomAD', 'int', 'v3.1.2', '2021-10-22', 'gnomAD', '0');



INSERT INTO `HerediVar`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`) VALUES ('bayesdel', 'BayesDEL', 'Missense variant functional predictions by BayesDel tool (Feng 2017) used without allele frequency. Score bigger or equal to 0.16: damaging; Score smaller than 0.16: tolerated. Scores were imported from dbNSFP.', 'float', '4.4', '2023-05-06', 'Pathogenicity', 0);



UPDATE annotation_type SET is_transcript_specific = 1 WHERE title = 'revel'
DELETE FROM variant_annotation WHERE annotation_type_id = 6



ALTER TABLE `HerediVar`.`user_classification` 
ADD COLUMN `deleted_date` DATETIME NULL AFTER `scheme_class`;


ALTER TABLE `HerediVar`.`user_classification` 
CHANGE COLUMN `classification` `classification` ENUM('1', '2', '3', '4', '5', '3-', '3+', 'M', '4M') NOT NULL ;
UPDATE user_classification SET classification = '4M' WHERE classification = 'M';
ALTER TABLE `HerediVar`.`user_classification` 
CHANGE COLUMN `classification` `classification` ENUM('1', '2', '3', '4', '5', '3-', '3+', '4M') NOT NULL ;


ALTER TABLE `HerediVar`.`consensus_classification` 
CHANGE COLUMN `classification` `classification` ENUM('1', '2', '3', '4', '5', '3+', '3-', 'M', '4M') NOT NULL ;
UPDATE consensus_classification SET classification = '4M' WHERE classification = 'M';
ALTER TABLE `HerediVar`.`consensus_classification` 
CHANGE COLUMN `classification` `classification` ENUM('1', '2', '3', '4', '5', '3+', '3-', '4M') NOT NULL ;




