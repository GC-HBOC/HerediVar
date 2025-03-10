-- CREATE TABLE `HerediVar`.`new_table` (
--   `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
--   `identifier` INT NOT NULL,
--   `requested_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(),
--   `finished_at` DATETIME NULL,
--   `celery_task_id` VARCHAR(45) NULL,
--   `status` ENUM('pending', 'success', 'error', 'retry', 'aborted', 'progress') NULL DEFAULT 'pending',
--   `type` ENUM('list_download') NOT NULL,
--   `filepath` TEXT NOT NULL,
--   `is_valid` TINYINT(1) NOT NULL DEFAULT 1,
--   `message` TEXT NULL,
--   PRIMARY KEY (`id`));
-- 
-- 
-- ALTER TABLE `HerediVar`.`new_table` 
-- CHARACTER SET = utf8 , RENAME TO  `HerediVar`.`download_queue` ;
-- 
-- GRANT SELECT,INSERT,UPDATE ON HerediVar.download_queue TO 'HerediVar_superuser';
-- GRANT SELECT,INSERT,UPDATE ON HerediVar.download_queue TO 'HerediVar_user';
-- GRANT SELECT,INSERT,UPDATE ON HerediVar.download_queue TO 'HerediVar_read_only';
-- GRANT SELECT,UPDATE ON HerediVar.download_queue TO 'HerediVar_annotation';
-- 
-- 
-- ALTER TABLE `HerediVar`.`download_queue` 
-- CHANGE COLUMN `filepath` `filename` TEXT CHARACTER SET 'utf8mb4' NOT NULL ;
-- 
-- 
-- ALTER TABLE `HerediVar`.`download_queue` 
-- CHANGE COLUMN `status` `status` ENUM('pending', 'success', 'error', 'retry', 'aborted', 'progress') CHARACTER SET 'utf8mb4' NOT NULL DEFAULT 'pending' ;
-- 
-- 
-- GRANT SELECT ON HerediVar.list_variants TO 'HerediVar_annotation';
-- 
-- 
-- INSERT INTO `HerediVar`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`, `is_deleted`) VALUES ('hci_prior', 'HCI prior', 'The prior probability of pathogenicity as reported in the priors HCI website. These range from 0.97 for variants with high probability to damage a donor or acceptor to 0.02 for exonic variants that do not impact a splice junction and are unlikely to create a de novo donor.', 'float', '1', '2024-08-23', 'Pathogenicity', '0', '0');


INSERT INTO `HerediVar`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`, `is_deleted`) VALUES ('heredicare_vid', 'HerediCare VID', 'The VID from HerediCare.The version_date is inaccurate. They are always up to date when reimporting from heredicare.', 'int', '-', '2024-08-23', 'ID', '0', '0');
INSERT INTO `HerediVar`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`, `is_deleted`) VALUES ('heredicare', 'HerediCare', 'The HerediCaRe annotation. Including LR scores and n_pat and n_fam', 'text', '-', '2024-08-23', 'None', '0', '0');
