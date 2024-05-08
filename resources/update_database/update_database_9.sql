ALTER TABLE `HerediVar_ahdoebm1`.`annotation_queue` 
CHANGE COLUMN `status` `status` ENUM('pending', 'success', 'error', 'retry', 'aborted', 'progress') NOT NULL DEFAULT 'pending' ;

UPDATE HerediVar_ahdoebm1.annotation_type SET is_deleted = 1 WHERE title = "maxentscan_ref" OR title = "maxentscan_alt";

ALTER TABLE `HerediVar_ahdoebm1`.`consensus_classification` 
ADD COLUMN `needs_heredicare_upload` TINYINT(1) NOT NULL DEFAULT 1 AFTER `scheme_class`;
UPDATE `consensus_classification` SET `needs_heredicare_upload` = `is_recent` WHERE `id`=`id`;



CREATE TABLE `HerediVar_ahdoebm1`.`upload_queue` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `requested_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  `status` ENUM('pending', 'progress', 'success', 'error', 'retry') NOT NULL DEFAULT 'pending',
  `finished_at` DATETIME NULL,
  `message` TEXT NULL,
  `celery_task_id` VARCHAR(45) NULL,
  PRIMARY KEY (`id`));

CREATE TABLE `HerediVar_ahdoebm1`.`upload_variant_queue` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `upload_queue_id` INT UNSIGNED NOT NULL,
  `status` ENUM('pending', 'success', 'error', 'progress', 'retry') NOT NULL DEFAULT 'pending',
  `requested_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  `finished_at` DATETIME NULL,
  `message` TEXT NULL,
  `celery_task_id` VARCHAR(45) NULL,
  `vid` TEXT NOT NULL,
  `submission_id` INT NOT NULL,
  PRIMARY KEY (`id`));

ALTER TABLE `HerediVar_ahdoebm1`.`upload_variant_queue` 
CHANGE COLUMN `upload_queue_id` `upload_queue_id` INT(10) UNSIGNED NULL ;
ALTER TABLE `HerediVar_ahdoebm1`.`upload_variant_queue` 
ADD COLUMN `variant_id` INT UNSIGNED NOT NULL AFTER `vid`;
ALTER TABLE `HerediVar_ahdoebm1`.`upload_variant_queue` 
ADD COLUMN `user_id` INT UNSIGNED NOT NULL AFTER `submission_id`;
ALTER TABLE `HerediVar_ahdoebm1`.`upload_variant_queue` 
CHANGE COLUMN `submission_id` `submission_id` INT(11) NULL ;
