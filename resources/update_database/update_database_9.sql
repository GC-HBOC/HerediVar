-- ALTER TABLE `HerediVar`.`annotation_queue` 
-- CHANGE COLUMN `status` `status` ENUM('pending', 'success', 'error', 'retry', 'aborted', 'progress') NOT NULL DEFAULT 'pending' ;
-- 
-- UPDATE HerediVar.annotation_type SET is_deleted = 1 WHERE title = "maxentscan_ref" OR title = "maxentscan_alt";
-- 
-- ALTER TABLE `HerediVar`.`consensus_classification` 
-- ADD COLUMN `needs_heredicare_upload` TINYINT(1) NOT NULL DEFAULT 1 AFTER `scheme_class`;
-- UPDATE `consensus_classification` SET `needs_heredicare_upload` = `is_recent` WHERE `id`=`id`;
-- 
-- 
-- 
-- CREATE TABLE `HerediVar`.`upload_queue` (
--   `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
--   `user_id` INT NOT NULL,
--   `requested_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(),
--   `status` ENUM('pending', 'progress', 'success', 'error', 'retry') NOT NULL DEFAULT 'pending',
--   `finished_at` DATETIME NULL,
--   `message` TEXT NULL,
--   `celery_task_id` VARCHAR(45) NULL,
--   PRIMARY KEY (`id`));
-- 
-- CREATE TABLE `HerediVar`.`upload_variant_queue` (
--   `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
--   `upload_queue_id` INT UNSIGNED NOT NULL,
--   `status` ENUM('pending', 'success', 'error', 'progress', 'retry') NOT NULL DEFAULT 'pending',
--   `requested_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(),
--   `finished_at` DATETIME NULL,
--   `message` TEXT NULL,
--   `celery_task_id` VARCHAR(45) NULL,
--   `vid` TEXT NOT NULL,
--   `submission_id` INT NOT NULL,
--   PRIMARY KEY (`id`));
-- 
-- ALTER TABLE `HerediVar`.`upload_variant_queue` 
-- CHANGE COLUMN `upload_queue_id` `upload_queue_id` INT(10) UNSIGNED NULL ;
-- ALTER TABLE `HerediVar`.`upload_variant_queue` 
-- ADD COLUMN `variant_id` INT UNSIGNED NOT NULL AFTER `vid`;
-- ALTER TABLE `HerediVar`.`upload_variant_queue` 
-- ADD COLUMN `user_id` INT UNSIGNED NOT NULL AFTER `submission_id`;
-- ALTER TABLE `HerediVar`.`upload_variant_queue` 
-- CHANGE COLUMN `submission_id` `submission_id` INT(11) NULL ;
-- 
-- 
-- ALTER TABLE `HerediVar`.`upload_queue` 
-- RENAME TO  `HerediVar`.`publish_queue` ;

-- ALTER TABLE `HerediVar`.`upload_variant_queue` 
-- RENAME TO  `HerediVar`.`publish_heredicare_queue` ;
-- 
-- GRANT SELECT,INSERT,UPDATE ON HerediVar.publish_queue TO 'HerediVar_superuser';
-- GRANT SELECT ON HerediVar.publish_queue TO 'HerediVar_user';
-- GRANT SELECT ON HerediVar.publish_queue TO 'HerediVar_read_only';
-- 
-- GRANT SELECT,INSERT,UPDATE ON HerediVar.publish_heredicare_queue TO 'HerediVar_superuser';
-- GRANT SELECT,UPDATE ON HerediVar.publish_heredicare_queue TO 'HerediVar_user';
-- GRANT SELECT,UPDATE ON HerediVar.publish_heredicare_queue TO 'HerediVar_read_only';


ALTER TABLE `HerediVar`.`publish_heredicare_queue` 
DROP COLUMN `user_id`,
CHANGE COLUMN `upload_queue_id` `publish_queue_id` INT(10) UNSIGNED NULL DEFAULT NULL , RENAME TO  `HerediVar`.`publish_heredicare_queue` ;



ALTER TABLE `HerediVar`.`heredivar_clinvar_submissions` 
RENAME TO  `HerediVar`.`publish_clinvar_queue` ;

ALTER TABLE `HerediVar`.`publish_heredicare_queue` 
CHANGE COLUMN `status` `status` ENUM('pending', 'success', 'error', 'progress', 'retry', 'skipped') NOT NULL DEFAULT 'pending' ;

ALTER TABLE `HerediVar`.`publish_heredicare_queue` 
CHANGE COLUMN `vid` `vid` TEXT NULL ;


ALTER TABLE `HerediVar`.`publish_heredicare_queue` 
CHANGE COLUMN `status` `status` ENUM('pending', 'success', 'error', 'progress', 'retry', 'skipped', 'submitted', 'api_error') NOT NULL DEFAULT 'pending' ;

ALTER TABLE `HerediVar`.`publish_heredicare_queue` 
ADD COLUMN `consensus_classification_id` INT UNSIGNED NULL AFTER `submission_id`;


ALTER TABLE `HerediVar`.`publish_clinvar_queue` 
ADD COLUMN `publish_queue_id` INT UNSIGNED NOT NULL AFTER `id`,
ADD COLUMN `requested_at` DATETIME NOT NULL AFTER `variant_id`,
ADD COLUMN `celery_task_id` VARCHAR(45) NULL AFTER `last_updated`,
ADD COLUMN `consensus_classification_id` INT UNSIGNED NULL AFTER `celery_task_id`;

ALTER TABLE `HerediVar`.`publish_clinvar_queue` 
CHANGE COLUMN `status` `status` TEXT NOT NULL AFTER `requested_at`,
CHANGE COLUMN `message` `message` TEXT NULL AFTER `status`,
CHANGE COLUMN `submission_id` `submission_id` TEXT NULL ,
CHANGE COLUMN `last_updated` `last_updated` DATETIME NULL ;

ALTER TABLE `HerediVar`.`publish_clinvar_queue` 
CHANGE COLUMN `status` `status` TEXT NOT NULL DEFAULT 'pending' ;

ALTER TABLE `HerediVar`.`publish_clinvar_queue` 
CHANGE COLUMN `requested_at` `requested_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP() ;

ALTER TABLE `HerediVar`.`consensus_classification` 
ADD COLUMN `needs_clinvar_upload` TINYINT(1) NULL DEFAULT 1 AFTER `needs_heredicare_upload`;
UPDATE `consensus_classification` SET `needs_clinvar_upload` = `is_recent` WHERE `id`=`id`;

GRANT SELECT,INSERT,UPDATE ON HerediVar.publish_clinvar_queue TO 'HerediVar_superuser';
GRANT SELECT,UPDATE ON HerediVar.publish_clinvar_queue TO 'HerediVar_user';
GRANT SELECT,UPDATE ON HerediVar.publish_clinvar_queue TO 'HerediVar_read_only';

ALTER TABLE `HerediVar`.`publish_clinvar_queue` 
DROP INDEX `unique_heredivar_clinvar_submissions_variant_id` ;
;

INSERT INTO `HerediVar`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`, `is_deleted`) VALUES ('pfam_domains', 'Pfam protein domains', 'The Pfam protein domain accession ids of all transcripts. Multiple values are separated with , - symbols. This data is generated by VEP.', 'text', '110', '2023-07-18', 'Protein Domain', '1', '0');


ALTER TABLE `HerediVar`.`variant_consequence` 
DROP COLUMN `pfam_description`,
DROP COLUMN `pfam_accession`;



ALTER TABLE `HerediVar`.`publish_queue` 
ADD COLUMN `upload_clinvar` TINYINT(1) NOT NULL AFTER `celery_task_id`,
ADD COLUMN `upload_heredicare` TINYINT(1) NOT NULL AFTER `upload_clinvar`,
ADD COLUMN `variant_ids` TEXT NOT NULL AFTER `upload_heredicare`;



CREATE TABLE `HerediVar`.`classification_final_class` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `classification_scheme_id` INT UNSIGNED NOT NULL,
  `classification` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`));

ALTER TABLE `HerediVar`.`classification_final_class` 
ADD INDEX `FK_classification_final_class_classification_scheme_idx` (`classification_scheme_id` ASC);
;
ALTER TABLE `HerediVar`.`classification_final_class` 
ADD CONSTRAINT `FK_classification_final_class_classification_scheme`
  FOREIGN KEY (`classification_scheme_id`)
  REFERENCES `HerediVar`.`classification_scheme` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


GRANT SELECT ON HerediVar.classification_final_class TO 'HerediVar_superuser';
GRANT SELECT ON HerediVar.classification_final_class TO 'HerediVar_user';
GRANT SELECT ON HerediVar.classification_final_class TO 'HerediVar_read_only';


ALTER TABLE `HerediVar`.`consensus_classification` 
CHANGE COLUMN `classification` `classification` ENUM('1', '2', '3', '4', '5', '3+', '3-', '4M', 'R') NOT NULL ;
ALTER TABLE `HerediVar`.`user_classification` 
CHANGE COLUMN `classification` `classification` ENUM('1', '2', '3', '4', '5', '3-', '3+', '4M', 'R') NOT NULL ;
ALTER TABLE `HerediVar`.`consensus_classification` 
CHANGE COLUMN `scheme_class` `scheme_class` ENUM('1', '2', '3', '4', '5', '-') NOT NULL ;

ALTER TABLE `HerediVar`.`publish_clinvar_queue` 
DROP FOREIGN KEY `FK_heredivar_clinvar_submissions_variant`;
ALTER TABLE `HerediVar`.`publish_clinvar_queue` 
ADD CONSTRAINT `FK_publish_clinvar_queue_variant`
  FOREIGN KEY (`variant_id`)
  REFERENCES `HerediVar`.`variant` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;
