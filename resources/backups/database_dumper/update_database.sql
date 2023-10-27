ALTER TABLE `HerediVar_ahdoebm1`.`classification_criterium` 
CHANGE COLUMN `relevant_info` `relevant_info` TEXT NOT NULL DEFAULT '' ;






ALTER TABLE `HerediVar_ahdoebm1`.`import_variant_queue` 
ADD INDEX `fk_import_variant_queue_import_queue_idx` (`import_queue_id` ASC);
;
ALTER TABLE `HerediVar_ahdoebm1`.`import_variant_queue` 
ADD CONSTRAINT `fk_import_variant_queue_import_queue`
  FOREIGN KEY (`import_queue_id`)
  REFERENCES `HerediVar_ahdoebm1`.`import_queue` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;











CREATE TABLE `HerediVar_ahdoebm1`.`variant_heredicare_annotation` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `variant_id` INT UNSIGNED NOT NULL,
  `vid` VARCHAR(45) NOT NULL,
  `n_fam` INT NOT NULL DEFAULT 0 COMMENT 'consensus class: 1:pathogen, 2: vus, 3: polymorphismus/neutral, 11: class1, 12: class2, 32: class3-, 13: class3, 34: class3+, 14: class4, 15: class5, 20: artefakt, 21: nicht klassifiziert, 4: unbekannt',
  `n_pat` INT NOT NULL DEFAULT 0,
  `consensus_class` ENUM('1', '2', '3', '11', '12', '32', '13', '34', '14', '15', '20', '21', '4') NOT NULL,
  `comment` TEXT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC));

ALTER TABLE `HerediVar_ahdoebm1`.`variant_heredicare_annotation` 
ADD COLUMN `date` DATE NULL AFTER `comment`;


GRANT INSERT, DELETE ON HerediVar_ahdoebm1.variant_heredicare_annotation TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1.variant_heredicare_annotation TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1.variant_heredicare_annotation TO 'HerediVar_superuser';
GRANT SELECT ON HerediVar_ahdoebm1.variant_heredicare_annotation TO 'HerediVar_read_only';
GRANT SELECT ON HerediVar_ahdoebm1.variant_ids TO 'HerediVar_annotation';




DELETE FROM `HerediVar_ahdoebm1`.`annotation_type` WHERE (`id` = '34');
DELETE FROM `HerediVar_ahdoebm1`.`annotation_type` WHERE (`id` = '35');

ALTER TABLE `HerediVar_ahdoebm1`.`import_queue` 
CHANGE COLUMN `status` `status` ENUM('pending', 'progress', 'success', 'error', 'retry') NOT NULL DEFAULT 'pending' ;



GRANT DELETE ON HerediVar_ahdoebm1.variant_ids TO 'HerediVar_superuser';


ALTER TABLE `HerediVar_ahdoebm1`.`variant_consequence` 
CHANGE COLUMN `exon_nr` `exon_nr` VARCHAR(45) NULL DEFAULT NULL ,
CHANGE COLUMN `intron_nr` `intron_nr` VARCHAR(45) NULL DEFAULT NULL ;


ALTER TABLE `HerediVar_ahdoebm1`.`import_variant_queue` 
DROP FOREIGN KEY `fk_import_variant_queue_import_queue`;
ALTER TABLE `HerediVar_ahdoebm1`.`import_variant_queue` 
CHANGE COLUMN `import_queue_id` `import_queue_id` INT(10) UNSIGNED NULL DEFAULT NULL ;
ALTER TABLE `HerediVar_ahdoebm1`.`import_variant_queue` 
ADD CONSTRAINT `fk_import_variant_queue_import_queue`
  FOREIGN KEY (`import_queue_id`)
  REFERENCES `HerediVar_ahdoebm1`.`import_queue` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;


ALTER TABLE `HerediVar_ahdoebm1`.`consensus_classification` 
CHANGE COLUMN `classification` `classification` ENUM('1', '2', '3', '4', '5', '3+', '3-', 'M') NOT NULL ;

ALTER TABLE `HerediVar_ahdoebm1`.`user_classification` 
CHANGE COLUMN `classification` `classification` ENUM('1', '2', '3', '4', '5', '3-', '3+', 'M') NOT NULL ;


GRANT INSERT,UPDATE ON HerediVar_ahdoebm1.classification_scheme TO 'HerediVar_superuser';
GRANT INSERT,UPDATE,DELETE ON HerediVar_ahdoebm1.classification_criterium TO 'HerediVar_superuser';
GRANT INSERT,UPDATE,DELETE ON HerediVar_ahdoebm1.classification_criterium_strength TO 'HerediVar_superuser';
GRANT INSERT,UPDATE,DELETE ON HerediVar_ahdoebm1.mutually_exclusive_criteria TO 'HerediVar_superuser';


ALTER TABLE `HerediVar_ahdoebm1`.`classification_criterium_strength` 
CHANGE COLUMN `name` `name` VARCHAR(32) NOT NULL ,
ADD UNIQUE INDEX `UNIQUE_strength_key` (`classification_criterium_id` ASC, `name` ASC);
ALTER TABLE `HerediVar_ahdoebm1`.`mutually_exclusive_criteria` 
ADD UNIQUE INDEX `UNIQUE_mutually_exclusive` (`source` ASC, `target` ASC);


ALTER TABLE `HerediVar_ahdoebm1`.`classification_criterium` 
DROP INDEX `UNIQUE_scheme_id_name` ;

ALTER TABLE `HerediVar_ahdoebm1`.`classification_criterium` 
ADD UNIQUE INDEX `UNIQUE_classification_criterium` (`classification_scheme_id` ASC, `name` ASC);


ALTER TABLE `HerediVar_ahdoebm1`.`classification_criterium_strength` 
DROP FOREIGN KEY `FK_criterium_strength_classification_criterium`;
ALTER TABLE `HerediVar_ahdoebm1`.`classification_criterium_strength` 
ADD CONSTRAINT `FK_criterium_strength_classification_criterium`
  FOREIGN KEY (`classification_criterium_id`)
  REFERENCES `HerediVar_ahdoebm1`.`classification_criterium` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;


ALTER TABLE `HerediVar_ahdoebm1`.`mutually_exclusive_criteria` 
DROP FOREIGN KEY `FK_mutually_exclusive_criteria_classification_criteria_1`,
DROP FOREIGN KEY `FK_mutually_exclusive_criteria_classification_criterium`;
ALTER TABLE `HerediVar_ahdoebm1`.`mutually_exclusive_criteria` 
ADD CONSTRAINT `FK_mutually_exclusive_criteria_classification_criteria_1`
  FOREIGN KEY (`source`)
  REFERENCES `HerediVar_ahdoebm1`.`classification_criterium` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION,
ADD CONSTRAINT `FK_mutually_exclusive_criteria_classification_criterium`
  FOREIGN KEY (`target`)
  REFERENCES `HerediVar_ahdoebm1`.`classification_criterium` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;
