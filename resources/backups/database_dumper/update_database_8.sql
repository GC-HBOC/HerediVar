ALTER TABLE `HerediVar_ahdoebm1`.`import_variant_queue` 
CHANGE COLUMN `vid` `vid` TEXT NULL ;



CREATE TABLE `HerediVar_ahdoebm1`.`list_variant_import_queue` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `list_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `requested_at` DATETIME NOT NULL,
  `status` ENUM('pending', 'success', 'error', 'retry', 'aborted') NOT NULL DEFAULT 'pending',
  `finished_at` DATETIME NULL,
  `message` TEXT NULL,
  `celery_task_id` TEXT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

ALTER TABLE `HerediVar_ahdoebm1`.`list_variant_import_queue` 
CHANGE COLUMN `requested_at` `requested_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP() ;


GRANT SELECT,INSERT,UPDATE ON HerediVar_ahdoebm1.list_variant_import_queue TO 'HerediVar_user';
GRANT SELECT,INSERT,UPDATE ON HerediVar_ahdoebm1.list_variant_import_queue TO 'HerediVar_superuser';
GRANT SELECT,INSERT,UPDATE ON HerediVar_ahdoebm1.list_variant_import_queue TO 'HerediVar_read_only';

ALTER TABLE `HerediVar_ahdoebm1`.`list_variant_import_queue` 
CHANGE COLUMN `status` `status` ENUM('progress', 'pending', 'success', 'error', 'retry', 'aborted') NOT NULL DEFAULT 'pending' ;


ALTER TABLE `HerediVar_ahdoebm1`.`import_queue` 
ADD COLUMN `source` ENUM('heredicare', 'vcf') NOT NULL DEFAULT 'heredicare' AFTER `celery_task_id`;
