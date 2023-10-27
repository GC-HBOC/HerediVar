DROP TABLE IF EXISTS `HerediVar`.`import_variant_queue`;

DROP TABLE IF EXISTS `HerediVar`.`import_queue`;
CREATE TABLE `HerediVar`.`import_queue` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(10) unsigned NOT NULL,
  `requested_at` datetime NOT NULL DEFAULT current_timestamp(),
  `status` enum('pending','progress','success','error','retry') NOT NULL DEFAULT 'pending',
  `finished_at` datetime DEFAULT NULL,
  `message` text DEFAULT '',
  `celery_task_id` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_import_queue_user_id_idx` (`user_id`),
  CONSTRAINT `FK_import_queue_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=281 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;




DROP TABLE IF EXISTS `HerediVar`.`import_variant_queue`;
CREATE TABLE `HerediVar`.`import_variant_queue` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `import_queue_id` int(10) unsigned DEFAULT NULL,
  `status` enum('pending','success','error','progress','deleted','update','retry') NOT NULL DEFAULT 'pending',
  `requested_at` datetime NOT NULL DEFAULT current_timestamp(),
  `finished_at` datetime DEFAULT NULL,
  `message` text DEFAULT '',
  `celery_task_id` varchar(45) DEFAULT NULL,
  `vid` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `fk_import_variant_queue_import_queue_idx` (`import_queue_id`),
  CONSTRAINT `fk_import_variant_queue_import_queue` FOREIGN KEY (`import_queue_id`) REFERENCES `import_queue` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=42036 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
-- 
-- ALTER TABLE `HerediVar`.`classification_criterium` 
-- CHANGE COLUMN `relevant_info` `relevant_info` TEXT NOT NULL DEFAULT '' ;
-- 
-- 
-- 
-- 
-- 
-- ALTER TABLE `HerediVar`.`variant` 
-- ADD COLUMN `is_hidden` TINYINT(1) NOT NULL DEFAULT 0 AFTER `orig_alt`;
-- 
-- 
-- 
-- 
-- 
-- 
-- 
-- 
-- CREATE TABLE `HerediVar`.`variant_heredicare_annotation` (
--   `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
--   `variant_id` INT UNSIGNED NOT NULL,
--   `vid` VARCHAR(45) NOT NULL,
--   `n_fam` INT NOT NULL DEFAULT 0 COMMENT 'consensus class: 1:pathogen, 2: vus, 3: polymorphismus/neutral, 11: class1, 12: class2, 32: class3-, 13: class3, 34: class3+, 14: class4, 15: class5, 20: artefakt, 21: nicht klassifiziert, 4: unbekannt',
--   `n_pat` INT NOT NULL DEFAULT 0,
--   `consensus_class` ENUM('1', '2', '3', '11', '12', '32', '13', '34', '14', '15', '20', '21', '4') NOT NULL,
--   `comment` TEXT NOT NULL,
--   PRIMARY KEY (`id`),
--   UNIQUE INDEX `id_UNIQUE` (`id` ASC));
-- 
-- ALTER TABLE `HerediVar`.`variant_heredicare_annotation` 
-- ADD COLUMN `date` DATE NULL AFTER `comment`;
-- 
-- 
-- GRANT INSERT, DELETE ON HerediVar.variant_heredicare_annotation TO 'HerediVar_annotation';
-- GRANT SELECT ON HerediVar.variant_heredicare_annotation TO 'HerediVar_annotation';
-- GRANT SELECT ON HerediVar.variant_heredicare_annotation TO 'HerediVar_superuser';
-- GRANT SELECT ON HerediVar.variant_heredicare_annotation TO 'HerediVar_read_only';
-- GRANT SELECT ON HerediVar.variant_ids TO 'HerediVar_annotation';
-- 
-- 
-- 
-- 
-- DELETE FROM `HerediVar`.`annotation_type` WHERE (`id` = '34');
-- DELETE FROM `HerediVar`.`annotation_type` WHERE (`id` = '35');
-- 
-- ALTER TABLE `HerediVar`.`import_queue` 
-- CHANGE COLUMN `status` `status` ENUM('pending', 'progress', 'success', 'error', 'retry') NOT NULL DEFAULT 'pending' ;
-- 
-- 
-- 
-- GRANT DELETE ON HerediVar.variant_ids TO 'HerediVar_superuser';
-- 
-- 
-- ALTER TABLE `HerediVar`.`variant_consequence` 
-- CHANGE COLUMN `exon_nr` `exon_nr` VARCHAR(45) NULL DEFAULT NULL ,
-- CHANGE COLUMN `intron_nr` `intron_nr` VARCHAR(45) NULL DEFAULT NULL ;
-- 
-- 
-- 
-- ALTER TABLE `HerediVar`.`consensus_classification` 
-- CHANGE COLUMN `classification` `classification` ENUM('1', '2', '3', '4', '5', '3+', '3-', 'M') NOT NULL ;
-- 
-- ALTER TABLE `HerediVar`.`user_classification` 
-- CHANGE COLUMN `classification` `classification` ENUM('1', '2', '3', '4', '5', '3-', '3+', 'M') NOT NULL ;
-- 
-- 
-- GRANT INSERT,UPDATE ON HerediVar.classification_scheme TO 'HerediVar_superuser';
-- GRANT INSERT,UPDATE,DELETE ON HerediVar.classification_criterium TO 'HerediVar_superuser';
-- GRANT INSERT,UPDATE,DELETE ON HerediVar.classification_criterium_strength TO 'HerediVar_superuser';
-- GRANT INSERT,UPDATE,DELETE ON HerediVar.mutually_exclusive_criteria TO 'HerediVar_superuser';
-- 
-- 
-- ALTER TABLE `HerediVar`.`classification_criterium_strength` 
-- CHANGE COLUMN `name` `name` VARCHAR(32) NOT NULL;
-- ALTER TABLE `HerediVar`.`classification_criterium_strength` 
-- ADD UNIQUE INDEX `UNIQUE_strength_key` (`classification_criterium_id` ASC, `name` ASC);
-- ALTER TABLE `HerediVar`.`mutually_exclusive_criteria` 
-- ADD UNIQUE INDEX `UNIQUE_mutually_exclusive` (`source` ASC, `target` ASC);
-- 
-- 
-- ALTER TABLE `HerediVar`.`classification_criterium` 
-- DROP INDEX `UNIQUE_scheme_id_name` ;
-- 
-- ALTER TABLE `HerediVar`.`classification_criterium` 
-- ADD UNIQUE INDEX `UNIQUE_classification_criterium` (`classification_scheme_id` ASC, `name` ASC);
-- 
-- 
-- ALTER TABLE `HerediVar`.`classification_criterium_strength` 
-- DROP FOREIGN KEY `FK_criterium_strength_classification_criterium`;
-- ALTER TABLE `HerediVar`.`classification_criterium_strength` 
-- ADD CONSTRAINT `FK_criterium_strength_classification_criterium`
--   FOREIGN KEY (`classification_criterium_id`)
--   REFERENCES `HerediVar`.`classification_criterium` (`id`)
--   ON DELETE CASCADE
--   ON UPDATE NO ACTION;
-- 
-- 
-- ALTER TABLE `HerediVar`.`mutually_exclusive_criteria` 
-- DROP FOREIGN KEY `FK_mutually_exclusive_criteria_classification_criteria_1`,
-- DROP FOREIGN KEY `FK_mutually_exclusive_criteria_classification_criterium`;
-- ALTER TABLE `HerediVar`.`mutually_exclusive_criteria` 
-- ADD CONSTRAINT `FK_mutually_exclusive_criteria_classification_criteria_1`
--   FOREIGN KEY (`source`)
--   REFERENCES `HerediVar`.`classification_criterium` (`id`)
--   ON DELETE CASCADE
--   ON UPDATE NO ACTION,
-- ADD CONSTRAINT `FK_mutually_exclusive_criteria_classification_criterium`
--   FOREIGN KEY (`target`)
--   REFERENCES `HerediVar`.`classification_criterium` (`id`)
--   ON DELETE CASCADE
--   ON UPDATE NO ACTION;







