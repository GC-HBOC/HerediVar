ALTER TABLE `HerediVar_ahdoebm1`.`classification_scheme` 
ADD COLUMN `is_active` TINYINT(1) NOT NULL DEFAULT 1 AFTER `reference`;


ALTER TABLE `HerediVar_ahdoebm1`.`classification_scheme` 
ADD COLUMN `is_default` TINYINT(1) NOT NULL DEFAULT 0 AFTER `is_active`;


ALTER TABLE `HerediVar_ahdoebm1`.`classification_criterium_strength` 
ADD COLUMN `display_name` VARCHAR(45) NOT NULL AFTER `name`;


UPDATE classification_criterium_strength SET display_name = "vstr" WHERE name = "pvs";
UPDATE classification_criterium_strength SET display_name = "str" WHERE name = "ps" or name = "bs";
UPDATE classification_criterium_strength SET display_name = "mod" WHERE name = "pm" or name = "bm";
UPDATE classification_criterium_strength SET display_name = "sup" WHERE name = "pp" or name = "bp";
UPDATE classification_criterium_strength SET display_name = "alo" WHERE name = "ba";


ALTER TABLE `HerediVar_ahdoebm1`.`annotation_queue` 
CHANGE COLUMN `status` `status` ENUM('pending', 'success', 'error', 'retry', 'aborted') NOT NULL DEFAULT 'pending' ;



CREATE TABLE `HerediVar_ahdoebm1`.`automatic_classification` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `variant_id` INT UNSIGNED NOT NULL,
  `classification` ENUM('1', '2', '3', '4', '5') NOT NULL,
  `date` DATETIME NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

ALTER TABLE `HerediVar_ahdoebm1`.`automatic_classification` 
ADD COLUMN `scheme_name` VARCHAR(45) NOT NULL AFTER `variant_id`;


ALTER TABLE `HerediVar_ahdoebm1`.`automatic_classification` 
ADD INDEX `FK_autoclass_variant_idx` (`variant_id` ASC);
;
ALTER TABLE `HerediVar_ahdoebm1`.`automatic_classification` 
ADD CONSTRAINT `FK_autoclass_variant`
  FOREIGN KEY (`variant_id`)
  REFERENCES `HerediVar_ahdoebm1`.`variant` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;



CREATE TABLE `HerediVar_ahdoebm1`.`automatic_classification_criteria_applied` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `automatic_classification_id` INT UNSIGNED NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `rule_type` ENUM('splicing', 'protein', 'general') NOT NULL,
  `evidence_type` ENUM('benign', 'pathogenic') NOT NULL,
  `is_selected` TINYINT(1) NOT NULL,
  `strength` VARCHAR(45) NOT NULL,
  `comment` TEXT NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

ALTER TABLE `HerediVar_ahdoebm1`.`automatic_classification_criteria_applied` 
ADD INDEX `FK_autoclass_criteria_autoclass_idx` (`automatic_classification_id` ASC);
;
ALTER TABLE `HerediVar_ahdoebm1`.`automatic_classification_criteria_applied` 
ADD CONSTRAINT `FK_autoclass_criteria_autoclass`
  FOREIGN KEY (`automatic_classification_id`)
  REFERENCES `HerediVar_ahdoebm1`.`automatic_classification` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


ALTER TABLE `HerediVar_ahdoebm1`.`automatic_classification_criteria_applied` 
DROP FOREIGN KEY `FK_autoclass_criteria_autoclass`;
ALTER TABLE `HerediVar_ahdoebm1`.`automatic_classification_criteria_applied` 
ADD CONSTRAINT `FK_autoclass_criteria_autoclass`
  FOREIGN KEY (`automatic_classification_id`)
  REFERENCES `HerediVar_ahdoebm1`.`automatic_classification` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;




GRANT SELECT, INSERT, UPDATE, DELETE ON HerediVar_ahdoebm1.automatic_classification TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1.automatic_classification TO 'HerediVar_user';
GRANT SELECT ON HerediVar_ahdoebm1.automatic_classification TO 'HerediVar_superuser';
GRANT SELECT ON HerediVar_ahdoebm1.automatic_classification TO 'HerediVar_read_only';

GRANT SELECT, INSERT, UPDATE, DELETE ON HerediVar_ahdoebm1.automatic_classification_criteria_applied TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1.automatic_classification_criteria_applied TO 'HerediVar_user';
GRANT SELECT ON HerediVar_ahdoebm1.automatic_classification_criteria_applied TO 'HerediVar_superuser';
GRANT SELECT ON HerediVar_ahdoebm1.automatic_classification_criteria_applied TO 'HerediVar_read_only';



GRANT SELECT ON HerediVar_ahdoebm1.assay TO 'HerediVar_annotation';


ALTER TABLE `HerediVar_ahdoebm1`.`task_force_protein_domains` 
ADD COLUMN `gene_id` INT UNSIGNED NOT NULL AFTER `source`;
ALTER TABLE `HerediVar_ahdoebm1`.`task_force_protein_domains` 
CHANGE COLUMN `gene_id` `gene_id` INT(10) UNSIGNED NOT NULL AFTER `id`;


SET FOREIGN_KEY_CHECKS = 0; 
TRUNCATE table task_force_protein_domains; 
SET FOREIGN_KEY_CHECKS = 1;


ALTER TABLE `HerediVar_ahdoebm1`.`task_force_protein_domains` 
ADD INDEX `FK_task_force_protein_domain_gene_idx` (`gene_id` ASC);
;
ALTER TABLE `HerediVar_ahdoebm1`.`task_force_protein_domains` 
ADD CONSTRAINT `FK_task_force_protein_domain_gene`
  FOREIGN KEY (`gene_id`)
  REFERENCES `HerediVar_ahdoebm1`.`gene` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


ALTER TABLE `HerediVar_ahdoebm1`.`automatic_classification_criteria_applied` 
ADD COLUMN `type` VARCHAR(45) NOT NULL AFTER `strength`;
