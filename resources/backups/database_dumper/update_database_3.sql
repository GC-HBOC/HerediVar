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


ALTER TABLE `HerediVar_ahdoebm1`.`automatic_classification` 
ADD COLUMN `tool_version` VARCHAR(45) NOT NULL AFTER `date`;


ALTER TABLE `HerediVar_ahdoebm1`.`automatic_classification` 
ADD COLUMN `classification_protein` ENUM('1', '2', '3', '4', '5') NOT NULL AFTER `classification_splicing`,
CHANGE COLUMN `classification` `classification_splicing` ENUM('1', '2', '3', '4', '5') NOT NULL ;


ALTER TABLE `HerediVar_ahdoebm1`.`user_classification_criteria_applied` 
ADD COLUMN `is_selected` TINYINT(1) NOT NULL DEFAULT 1 AFTER `evidence`;

ALTER TABLE `HerediVar_ahdoebm1`.`consensus_classification_criteria_applied` 
ADD COLUMN `is_selected` TINYINT(1) NOT NULL DEFAULT 1 AFTER `evidence`;





CREATE TABLE `HerediVar_ahdoebm1`.`mutually_inclusive_criteria` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `source` INT UNSIGNED NOT NULL,
  `target` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

ALTER TABLE `HerediVar_ahdoebm1`.`mutually_inclusive_criteria` 
ADD INDEX `FK_mutually_inclusive_criteria_criteria_idx` (`source` ASC),
ADD INDEX `FK_mutually_inlusive_criteria_target_idx` (`target` ASC);
;
ALTER TABLE `HerediVar_ahdoebm1`.`mutually_inclusive_criteria` 
ADD CONSTRAINT `FK_mutually_inclusive_criteria_source`
  FOREIGN KEY (`source`)
  REFERENCES `HerediVar_ahdoebm1`.`classification_criterium` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION,
ADD CONSTRAINT `FK_mutually_inlusive_criteria_target`
  FOREIGN KEY (`target`)
  REFERENCES `HerediVar_ahdoebm1`.`classification_criterium` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;

GRANT SELECT ON HerediVar_ahdoebm1.mutually_inclusive_criteria TO 'HerediVar_user';
GRANT SELECT ON HerediVar_ahdoebm1.mutually_inclusive_criteria TO 'HerediVar_superuser';
GRANT DELETE,INSERT ON HerediVar_ahdoebm1.mutually_inclusive_criteria TO 'HerediVar_superuser';



ALTER TABLE `HerediVar_ahdoebm1`.`mutually_inclusive_criteria` 
ADD UNIQUE INDEX `UNIQUE_mutually_inclusive_criteria` (`source` ASC, `target` ASC);
;


ALTER TABLE `HerediVar_ahdoebm1`.`classification_scheme` 
ADD COLUMN `version` VARCHAR(45) NOT NULL AFTER DEFAULT 'v1.0.0' `name`;
UPDATE classification_scheme SET version = "v1.4.0" WHERE name = "enigma-tp53";
UPDATE classification_scheme SET version = "v1.1.0" WHERE name = "enigma-ATM";

ALTER TABLE `HerediVar_ahdoebm1`.`classification_scheme` 
CHANGE COLUMN `name` `name` VARCHAR(45) NOT NULL ;


ALTER TABLE `HerediVar_ahdoebm1`.`classification_scheme` 
ADD UNIQUE INDEX `UNIQUE_classification_scheme` (`name` ASC, `version` ASC);
;


ALTER TABLE `HerediVar_ahdoebm1`.`mutually_inclusive_criteria` 
DROP FOREIGN KEY `FK_mutually_inclusive_criteria_source`,
DROP FOREIGN KEY `FK_mutually_inlusive_criteria_target`;
ALTER TABLE `HerediVar_ahdoebm1`.`mutually_inclusive_criteria` 
ADD CONSTRAINT `FK_mutually_inclusive_criteria_source`
  FOREIGN KEY (`source`)
  REFERENCES `HerediVar_ahdoebm1`.`classification_criterium` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION,
ADD CONSTRAINT `FK_mutually_inlusive_criteria_target`
  FOREIGN KEY (`target`)
  REFERENCES `HerediVar_ahdoebm1`.`classification_criterium` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;


CREATE TABLE `HerediVar_ahdoebm1`.`classification_scheme_alias` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `classification_scheme_id` INT UNSIGNED NOT NULL,
  `alias` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


ALTER TABLE `HerediVar_ahdoebm1`.`classification_scheme_alias` 
ADD INDEX `FK_classification_scheme_alias_classification_scheme_idx` (`classification_scheme_id` ASC);
;
ALTER TABLE `HerediVar_ahdoebm1`.`classification_scheme_alias` 
ADD CONSTRAINT `FK_classification_scheme_alias_classification_scheme`
  FOREIGN KEY (`classification_scheme_id`)
  REFERENCES `HerediVar_ahdoebm1`.`classification_scheme` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


GRANT SELECT ON HerediVar_ahdoebm1.classification_scheme_alias TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1.classification_scheme TO 'HerediVar_annotation';
GRANT SELECT,INSERT,UPDATE,DELETE ON HerediVar_ahdoebm1.classification_scheme_alias TO 'HerediVar_superuser';



ALTER TABLE `HerediVar_ahdoebm1`.`automatic_classification` 
DROP COLUMN `scheme_name`;

ALTER TABLE `HerediVar_ahdoebm1`.`automatic_classification` 
ADD COLUMN `classification_scheme_id` INT UNSIGNED NOT NULL AFTER `variant_id`;

ALTER TABLE `HerediVar_ahdoebm1`.`automatic_classification` 
ADD INDEX `FK_autoclass_classification_scheme_idx` (`classification_scheme_id` ASC);
;
ALTER TABLE `HerediVar_ahdoebm1`.`automatic_classification` 
ADD CONSTRAINT `FK_autoclass_classification_scheme`
  FOREIGN KEY (`classification_scheme_id`)
  REFERENCES `HerediVar_ahdoebm1`.`classification_scheme` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;



