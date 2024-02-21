-- ALTER TABLE `HerediVar`.`variant_heredicare_annotation` 
-- ADD COLUMN `lr_cooc` FLOAT NULL AFTER `date`,
-- ADD COLUMN `lr_coseg` FLOAT NULL AFTER `lr_cooc`,
-- ADD COLUMN `lr_family` VARCHAR(45) NULL AFTER `lr_coseg`;
-- 
-- 
-- ALTER TABLE `HerediVar`.`annotation_type` 
-- ADD COLUMN `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 AFTER `is_transcript_specific`;


-- UPDATE `HerediVar`.`annotation_type` SET is_deleted = 1 WHERE title = "tp53db_bayes_del";
-- 
-- 
-- CREATE TABLE `HerediVar`.`variant_cancerhotspots_annotation` (
--   `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
--   `variant_id` INT UNSIGNED NOT NULL,
--   `oncotree_symbol` VARCHAR(45) NOT NULL,
--   `cancertype` TEXT NOT NULL,
--   `tissue` TEXT NOT NULL,
--   `occurances` INT NOT NULL,
--   PRIMARY KEY (`id`),
--   UNIQUE INDEX `id_UNIQUE` (`id` ASC) );
-- 
-- 
-- ALTER TABLE `HerediVar`.`variant_cancerhotspots_annotation` 
-- ADD COLUMN `annotation_type_id` INT UNSIGNED NOT NULL AFTER `occurances`;
-- 
-- 
-- INSERT INTO `HerediVar`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`, `is_deleted`) VALUES ('cancerhotspots', 'cancerhotspots', 'The oncotree symbol, cancertype, tissue and number of occurances form the cancerhotspots database', 'text', 'v2', '2017-12-15', 'None', '0', '0');
-- 
-- 
-- UPDATE `HerediVar`.`annotation_type` SET is_deleted = 1 WHERE title = "cancerhotspots_cancertypes";
-- 
-- GRANT SELECT, INSERT, UPDATE, DELETE ON HerediVar.variant_cancerhotspots_annotation TO 'HerediVar_annotation';
-- GRANT SELECT ON HerediVar.variant_cancerhotspots_annotation TO 'HerediVar_user';
-- GRANT SELECT ON HerediVar.variant_cancerhotspots_annotation TO 'HerediVar_superuser';
-- GRANT SELECT ON HerediVar.variant_cancerhotspots_annotation TO 'HerediVar_read_only';
-- 
-- 
-- ALTER TABLE `HerediVar`.`variant_cancerhotspots_annotation` 
-- CHARACTER SET = utf8 ;
-- 
-- 
-- ALTER TABLE `HerediVar`.`variant_cancerhotspots_annotation` 
-- CHANGE COLUMN `cancertype` `cancertype` VARCHAR(500) CHARACTER SET 'utf8mb4' NOT NULL ,
-- CHANGE COLUMN `tissue` `tissue` VARCHAR(45) CHARACTER SET 'utf8mb4' NOT NULL ;
-- 
-- 
-- UPDATE `HerediVar`.`annotation_type` SET group_name = "None" WHERE title = "cancerhotspots_ac";
-- UPDATE `HerediVar`.`annotation_type` SET group_name = "None" WHERE title = "cancerhotspots_af";
-- 
-- 
-- ALTER TABLE `HerediVar`.`variant_heredicare_annotation` 
-- CHANGE COLUMN `lr_family` `lr_family` FLOAT NULL DEFAULT NULL ;
-- 
-- 
-- UPDATE `HerediVar`.`annotation_type` SET is_deleted=1 WHERE title="arup_classification";
-- 
-- 
-- 
-- 
-- CREATE TABLE `HerediVar`.`assay_metadata` (
--   `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
--   `assay_id` INT UNSIGNED NOT NULL,
--   `metadata_type` VARCHAR(45) NOT NULL,
--   `value` VARCHAR(45) NULL,
--   PRIMARY KEY (`id`))
-- ENGINE = InnoDB
-- DEFAULT CHARACTER SET = utf8;
-- 
-- 
-- CREATE TABLE `HerediVar`.`assay_metadata_type` (
--   `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
--   `title` VARCHAR(45) NOT NULL,
--   `display_title` VARCHAR(45) NOT NULL,
--   `assay_type_id` INT NOT NULL,
--   `value_type` ENUM('int', 'float', 'text', 'bool') NOT NULL,
--   PRIMARY KEY (`id`))
-- ENGINE = InnoDB
-- DEFAULT CHARACTER SET = utf8;
-- 
-- ALTER TABLE `HerediVar`.`assay_metadata` 
-- CHANGE COLUMN `metadata_type` `metadata_type_id` INT NOT NULL ;
-- 
-- 
-- ALTER TABLE `HerediVar`.`assay_metadata_type` 
-- ADD COLUMN `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 AFTER `value_type`;
-- 
-- CREATE TABLE `HerediVar`.`assay_type` (
--   `id` INT NOT NULL,
--   `title` VARCHAR(45) NOT NULL,
--   PRIMARY KEY (`id`))
-- ENGINE = InnoDB
-- DEFAULT CHARACTER SET = utf8;
-- 
-- ALTER TABLE `HerediVar`.`assay_type` 
-- CHANGE COLUMN `id` `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT ;
-- 
-- INSERT INTO `HerediVar`.`assay_type` (`title`) VALUES ('functional');
-- INSERT INTO `HerediVar`.`assay_type` (`title`) VALUES ('splicing');
-- 
-- ALTER TABLE `HerediVar`.`assay` 
-- ADD COLUMN `paper` TEXT NULL AFTER `filename`,
-- CHANGE COLUMN `report` `report` MEDIUMBLOB NULL ,
-- CHANGE COLUMN `filename` `filename` TEXT NULL ;
-- 
-- ALTER TABLE `HerediVar`.`assay_metadata_type` 
-- CHANGE COLUMN `value_type` `value_type` TEXT NOT NULL ;

ALTER TABLE `HerediVar_ahdoebm1`.`assay_metadata_type` 
ADD COLUMN `is_required` TINYINT(1) NOT NULL DEFAULT 1 AFTER `is_deleted`;


-- INSERT INTO `HerediVar`.`assay_metadata_type` (title, display_title, assay_type_id, value_type) VALUES ('patient_rna', 'Patient RNA', (SELECT id FROM `HerediVar`.`assay_type` WHERE title='splicing'), 'bool');
-- INSERT INTO `HerediVar`.`assay_metadata_type` (title, display_title, assay_type_id, value_type) VALUES ('minigene', 'Minigene', (SELECT id FROM `HerediVar`.`assay_type` WHERE title='splicing'), 'bool');
-- INSERT INTO `HerediVar`.`assay_metadata_type` (title, display_title, assay_type_id, value_type) VALUES ('allele_specific', 'Allele-Specific', (SELECT id FROM `HerediVar`.`assay_type` WHERE title='splicing'), 'ENUM:True,False,Construct');
-- INSERT INTO `HerediVar`.`assay_metadata_type` (title, display_title, assay_type_id, value_type) VALUES ('comment', 'Comment', (SELECT id FROM `HerediVar`.`assay_type` WHERE title='splicing'), 'text');
-- INSERT INTO `HerediVar`.`assay_metadata_type` (title, display_title, assay_type_id, value_type) VALUES ('score', 'Score', (SELECT id FROM `HerediVar`.`assay_type` WHERE title='splicing'), 'float');
-- INSERT INTO `HerediVar`.`assay_metadata_type` (title, display_title, assay_type_id, value_type) VALUES ('minimal_percentage', 'Percent aberrant transcript', (SELECT id FROM `HerediVar`.`assay_type` WHERE title='splicing'), 'float');
-- 
-- INSERT INTO `HerediVar`.`assay_metadata_type` (title, display_title, assay_type_id, value_type) VALUES ('functional_category', 'Functional category', (SELECT id FROM `HerediVar`.`assay_type` WHERE title='functional'), 'ENUM:Pathogenic,Benign,Ambigous');
-- INSERT INTO `HerediVar`.`assay_metadata_type` (title, display_title, assay_type_id, value_type) VALUES ('score', 'Score', (SELECT id FROM `HerediVar`.`assay_type` WHERE title='functional'), 'float');


UPDATE `HerediVar`.`assay_metadata_type` SET `is_required` = '0' WHERE (`title` = 'comment');
UPDATE `HerediVar`.`assay_metadata_type` SET `is_required` = '0' WHERE (`title` = 'score');



ALTER TABLE `HerediVar`.`assay` 
ADD COLUMN `assay_type_id` INT UNSIGNED NOT NULL AFTER `assay_type`;

UPDATE `HerediVar`.`assay` SET assay_type_id = (SELECT id FROM `HerediVar`.`assay_type` WHERE title = 'functional') WHERE assay_type = 'functional';
UPDATE `HerediVar`.`assay` SET assay_type_id = (SELECT id FROM `HerediVar`.`assay_type` WHERE title = 'splicing') WHERE assay_type = 'splicing';

ALTER TABLE `HerediVar`.`assay` 
DROP COLUMN `assay_type`;

INSERT INTO `HerediVar`.`assay_metadata` (assay_id, metadata_type_id, value) SELECT id, (SELECT id FROM `HerediVar`.assay_metadata_type WHERE assay_metadata_type.title = 'score' AND assay_metadata_type.assay_type_id = assay.assay_type_id), score FROM assay

ALTER TABLE `HerediVar`.`assay` 
DROP COLUMN `score`;

ALTER TABLE `HerediVar`.`assay` 
CHANGE COLUMN `paper` `link` TEXT NULL DEFAULT NULL ;

ALTER TABLE `HerediVar`.`assay_metadata_type` 
ADD COLUMN `is_required` TINYINT(1) NOT NULL DEFAULT 1 AFTER `is_deleted`;

ALTER TABLE `HerediVar`.`assay_metadata` 
CHANGE COLUMN `metadata_type_id` `assay_metadata_type_id` INT(11) NOT NULL ;


GRANT SELECT ON HerediVar.assay_type TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar.assay_type TO 'HerediVar_user';
GRANT SELECT ON HerediVar.assay_type TO 'HerediVar_superuser';
GRANT SELECT ON HerediVar.assay_type TO 'HerediVar_read_only';


GRANT SELECT ON HerediVar.assay_metadata_type TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar.assay_metadata_type TO 'HerediVar_user';
GRANT SELECT ON HerediVar.assay_metadata_type TO 'HerediVar_superuser';
GRANT SELECT ON HerediVar.assay_metadata_type TO 'HerediVar_read_only';


GRANT SELECT, INSERT ON HerediVar.assay_metadata TO 'HerediVar_annotation';
GRANT SELECT, INSERT ON HerediVar.assay_metadata TO 'HerediVar_user';
GRANT SELECT, INSERT ON HerediVar.assay_metadata TO 'HerediVar_superuser';
GRANT SELECT ON HerediVar.assay_metadata TO 'HerediVar_read_only';

GRANT INSERT ON HerediVar.assay TO 'HerediVar_annotation';
GRANT DELETE ON HerediVar.assay TO 'HerediVar_annotation';


ALTER TABLE `HerediVar`.`assay` 
ADD COLUMN `user_id` INT UNSIGNED NULL AFTER `date`;


ALTER TABLE `HerediVar`.`assay` 
ADD INDEX `FK_assay_assay_type_idx` (`assay_type_id` ASC);
;
ALTER TABLE `HerediVar`.`assay` 
ADD CONSTRAINT `FK_assay_assay_type`
  FOREIGN KEY (`assay_type_id`)
  REFERENCES `HerediVar`.`assay_type` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


ALTER TABLE `HerediVar`.`assay` 
ADD INDEX `FK_assay_user_idx` (`user_id` ASC);
;
ALTER TABLE `HerediVar`.`assay` 
ADD CONSTRAINT `FK_assay_user`
  FOREIGN KEY (`user_id`)
  REFERENCES `HerediVar`.`user` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;

ALTER TABLE `HerediVar`.`assay` 
DROP FOREIGN KEY `FK_assay_variant`;
ALTER TABLE `HerediVar`.`assay` 
ADD CONSTRAINT `FK_assay_variant`
  FOREIGN KEY (`variant_id`)
  REFERENCES `HerediVar`.`variant` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


ALTER TABLE `HerediVar`.`assay_metadata` 
CHANGE COLUMN `assay_metadata_type_id` `assay_metadata_type_id` INT(11) UNSIGNED NOT NULL ,
ADD INDEX `FK_assay_metadata_assay_idx` (`assay_id` ASC),
ADD INDEX `FK_assay_metadata_assay_metadata_type_idx` (`assay_metadata_type_id` ASC);
;
ALTER TABLE `HerediVar`.`assay_metadata` 
ADD CONSTRAINT `FK_assay_metadata_assay`
  FOREIGN KEY (`assay_id`)
  REFERENCES `HerediVar`.`assay` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION,
ADD CONSTRAINT `FK_assay_metadata_assay_metadata_type`
  FOREIGN KEY (`assay_metadata_type_id`)
  REFERENCES `HerediVar`.`assay_metadata_type` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


ALTER TABLE `HerediVar`.`assay_metadata` 
DROP FOREIGN KEY `FK_assay_metadata_assay_metadata_type`;
ALTER TABLE `HerediVar`.`assay_metadata` 
ADD CONSTRAINT `FK_assay_metadata_assay_metadata_type`
  FOREIGN KEY (`assay_metadata_type_id`)
  REFERENCES `HerediVar`.`assay_metadata_type` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;




CREATE TABLE `HerediVar`.`heredicare_ZID` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `ZID` INT NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

ALTER TABLE `HerediVar`.`heredicare_ZID` 
DROP COLUMN `id`,
CHANGE COLUMN `ZID` `ZID` INT(11) UNSIGNED NOT NULL ,
DROP PRIMARY KEY,
ADD PRIMARY KEY (`ZID`);
;

INSERT INTO `HerediVar`.`heredicare_ZID` (ZID, name) VALUES
(1, "Berlin"),
(2, "Leipzig"),
(3, "Dresden"),
(4, "München-LMU"),
(5, "Würzburg"),
(6, "Ulm"),
(7, "Heidelberg"),
(8, "Frankfurt"),
(9, "Köln"),
(10, "Düsseldorf"),
(11, "Münster"),
(12, "Kiel"),
(13, "Wiesbaden"),
(14, "München-TU"),
(15, "Hannover"),
(16, "Regensburg"),
(17, "Tübingen"),
(18, "Göttingen"),
(19, "Hamburg"),
(20, "Greifswald"),
(21, "Freiburg"),
(22, "Erlangen"),
(23, "Halle"),
(24, "Mainz"),
(25, "Lübeck");


-- ALTER TABLE `HerediVar`.`heredicare_center_classification` 
-- DROP FOREIGN KEY `FK_heredicare_center_classification_variant`;
-- ALTER TABLE `HerediVar`.`heredicare_center_classification` 
-- DROP COLUMN `date`,
-- CHANGE COLUMN `variant_id` `variant_heredicare_annotation_id` INT(10) UNSIGNED NOT NULL ,
-- CHANGE COLUMN `center_name` `heredicare_ZID` INT UNSIGNED NOT NULL ,
-- CHANGE COLUMN `comment` `comment` TEXT NULL ,
-- DROP INDEX `FK_classification_center_heredicare_variant_idx` ;
-- ;
-- ALTER TABLE `HerediVar`.`heredicare_center_classification` 
-- ADD INDEX `FK_heredicare_center_classification_heredicare_ZID_idx` (`heredicare_ZID` ASC);
-- ;
-- ALTER TABLE `HerediVar`.`heredicare_center_classification` 
-- ADD CONSTRAINT `FK_heredicare_center_classification_heredicare_ZID`
--   FOREIGN KEY (`heredicare_ZID`)
--   REFERENCES `HerediVar`.`heredicare_ZID` (`ZID`)
--   ON DELETE NO ACTION
--   ON UPDATE NO ACTION;
-- 
-- ALTER TABLE `HerediVar`.`heredicare_center_classification` 
-- ADD CONSTRAINT `FK_center_classification_heredicare_annotation`
--   FOREIGN KEY (`heredicare_ZID`)
--   REFERENCES `HerediVar`.`variant_heredicare_annotation` (`id`)
--   ON DELETE NO ACTION
--   ON UPDATE NO ACTION;
-- 
-- ALTER TABLE `HerediVar`.`heredicare_center_classification` 
-- CHANGE COLUMN `classification` `classification` ENUM('1', '2', '3', '11', '12', '32', '13', '34', '14', '15', '20', '21', '4') NOT NULL AFTER `heredicare_ZID`;
-- 
-- ALTER TABLE `HerediVar`.`heredicare_center_classification` 
-- DROP FOREIGN KEY `FK_center_classification_heredicare_annotation`;
-- 
-- ALTER TABLE `HerediVar`.`heredicare_center_classification` 
-- DROP INDEX `FK_center_classification_heredicare_annotation_idx` ;
-- ;
-- 
-- ALTER TABLE `HerediVar`.`heredicare_center_classification` 
-- ADD INDEX `FK_center_classification_heredicare_annotation_idx` (`variant_heredicare_annotation_id` ASC);
-- ;
-- ALTER TABLE `HerediVar`.`heredicare_center_classification` 
-- ADD CONSTRAINT `FK_center_classification_heredicare_annotation`
--   FOREIGN KEY (`variant_heredicare_annotation_id`)
--   REFERENCES `HerediVar`.`variant_heredicare_annotation` (`id`)
--   ON DELETE NO ACTION
--   ON UPDATE NO ACTION;
-- 
-- ALTER TABLE `HerediVar`.`heredicare_center_classification` 
-- DROP FOREIGN KEY `FK_center_classification_heredicare_annotation`;
-- ALTER TABLE `HerediVar`.`heredicare_center_classification` 
-- ADD CONSTRAINT `FK_center_classification_heredicare_annotation`
--   FOREIGN KEY (`variant_heredicare_annotation_id`)
--   REFERENCES `HerediVar`.`variant_heredicare_annotation` (`id`)
--   ON DELETE CASCADE
--   ON UPDATE NO ACTION;
-- 

DROP TABLE IF EXISTS `HerediVar`.`heredicare_center_classification` 
CREATE TABLE `HerediVar`.`heredicare_center_classification`  (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `variant_heredicare_annotation_id` int(10) unsigned NOT NULL,
  `heredicare_ZID` int(10) unsigned NOT NULL,
  `classification` enum('1','2','3','11','12','32','13','34','14','15','20','21','4') NOT NULL,
  `comment` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_heredicare_center_classification_heredicare_ZID_idx` (`heredicare_ZID`),
  KEY `FK_center_classification_heredicare_annotation_idx` (`variant_heredicare_annotation_id`),
  CONSTRAINT `FK_center_classification_heredicare_annotation` FOREIGN KEY (`variant_heredicare_annotation_id`) REFERENCES `variant_heredicare_annotation` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `FK_heredicare_center_classification_heredicare_ZID` FOREIGN KEY (`heredicare_ZID`) REFERENCES `heredicare_ZID` (`ZID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

