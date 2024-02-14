ALTER TABLE `HerediVar_ahdoebm1`.`variant_heredicare_annotation` 
ADD COLUMN `lr_cooc` FLOAT NULL AFTER `date`,
ADD COLUMN `lr_coseg` FLOAT NULL AFTER `lr_cooc`,
ADD COLUMN `lr_family` VARCHAR(45) NULL AFTER `lr_coseg`;


ALTER TABLE `HerediVar_ahdoebm1`.`annotation_type` 
ADD COLUMN `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 AFTER `is_transcript_specific`;


UPDATE annotation_type SET is_deleted = 1 WHERE title = "tp53db_bayes_del";


CREATE TABLE `HerediVar_ahdoebm1`.`variant_cancerhotspots_annotation` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `variant_id` INT UNSIGNED NOT NULL,
  `oncotree_symbol` VARCHAR(45) NOT NULL,
  `cancertype` TEXT NOT NULL,
  `tissue` TEXT NOT NULL,
  `occurances` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) );


ALTER TABLE `HerediVar_ahdoebm1`.`variant_cancerhotspots_annotation` 
ADD COLUMN `annotation_type_id` INT UNSIGNED NOT NULL AFTER `occurances`;


INSERT INTO `HerediVar_ahdoebm1`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`, `is_deleted`) VALUES ('cancerhotspots', 'cancerhotspots', 'The oncotree symbol, cancertype, tissue and number of occurances form the cancerhotspots database', 'text', 'v2', '2017-12-15', 'None', '0', '0');


UPDATE annotation_type SET is_deleted = 1 WHERE title = "cancerhotspots_cancertypes";

GRANT SELECT, INSERT, UPDATE, DELETE ON HerediVar_ahdoebm1.variant_cancerhotspots_annotation TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1.variant_cancerhotspots_annotation TO 'HerediVar_user';
GRANT SELECT ON HerediVar_ahdoebm1.variant_cancerhotspots_annotation TO 'HerediVar_superuser';
GRANT SELECT ON HerediVar_ahdoebm1.variant_cancerhotspots_annotation TO 'HerediVar_read_only';


ALTER TABLE `HerediVar_ahdoebm1`.`variant_cancerhotspots_annotation` 
CHARACTER SET = utf8 ;


ALTER TABLE `HerediVar_ahdoebm1`.`variant_cancerhotspots_annotation` 
CHANGE COLUMN `cancertype` `cancertype` VARCHAR(500) CHARACTER SET 'utf8mb4' NOT NULL ,
CHANGE COLUMN `tissue` `tissue` VARCHAR(45) CHARACTER SET 'utf8mb4' NOT NULL ;


UPDATE annotation_type SET group_name = "None" WHERE title = "cancerhotspots_ac";
UPDATE annotation_type SET group_name = "None" WHERE title = "cancerhotspots_af";


ALTER TABLE `HerediVar_ahdoebm1`.`variant_heredicare_annotation` 
CHANGE COLUMN `lr_family` `lr_family` FLOAT NULL DEFAULT NULL ;


UPDATE annotation_type SET is_deleted=1 WHERE title="arup_classification"




CREATE TABLE `HerediVar_ahdoebm1`.`assay_metadata` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `assay_id` INT UNSIGNED NOT NULL,
  `metadata_type` VARCHAR(45) NOT NULL,
  `value` VARCHAR(45) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


CREATE TABLE `HerediVar_ahdoebm1`.`assay_metadata_type` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(45) NOT NULL,
  `display_title` VARCHAR(45) NOT NULL,
  `assay_type_id` INT NOT NULL,
  `value_type` ENUM('int', 'float', 'text', 'bool') NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

ALTER TABLE `HerediVar_ahdoebm1`.`assay_metadata` 
CHANGE COLUMN `metadata_type` `metadata_type_id` INT NOT NULL ;


ALTER TABLE `HerediVar_ahdoebm1`.`assay_metadata_type` 
ADD COLUMN `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 AFTER `value_type`;

CREATE TABLE `HerediVar_ahdoebm1`.`assay_type` (
  `id` INT NOT NULL,
  `title` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

ALTER TABLE `HerediVar_ahdoebm1`.`assay_type` 
CHANGE COLUMN `id` `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT ;

INSERT INTO `HerediVar_ahdoebm1`.`assay_type` (`title`) VALUES ('functional');
INSERT INTO `HerediVar_ahdoebm1`.`assay_type` (`title`) VALUES ('splicing');

ALTER TABLE `HerediVar_ahdoebm1`.`assay` 
ADD COLUMN `paper` TEXT NULL AFTER `filename`,
CHANGE COLUMN `report` `report` MEDIUMBLOB NULL ,
CHANGE COLUMN `filename` `filename` TEXT NULL ;

ALTER TABLE `HerediVar_ahdoebm1`.`assay_metadata_type` 
CHANGE COLUMN `value_type` `value_type` TEXT NOT NULL ;


INSERT INTO `HerediVar_ahdoebm1`.assay_metadata_type (title, display_title, assay_type_id, value_type) VALUES ('patient_rna', 'Patient RNA', (SELECT id FROM assay_type WHERE title='splicing'), 'bool')
INSERT INTO `HerediVar_ahdoebm1`.assay_metadata_type (title, display_title, assay_type_id, value_type) VALUES ('minigene', 'Minigene', (SELECT id FROM assay_type WHERE title='splicing'), 'bool')
INSERT INTO `HerediVar_ahdoebm1`.assay_metadata_type (title, display_title, assay_type_id, value_type) VALUES ('allele_specific', 'Allele-Specific', (SELECT id FROM assay_type WHERE title='splicing'), 'ENUM:True,False,Construct')
INSERT INTO `HerediVar_ahdoebm1`.assay_metadata_type (title, display_title, assay_type_id, value_type) VALUES ('comment', 'Comment', (SELECT id FROM assay_type WHERE title='splicing'), 'text')
INSERT INTO `HerediVar_ahdoebm1`.assay_metadata_type (title, display_title, assay_type_id, value_type) VALUES ('score', 'Score', (SELECT id FROM assay_type WHERE title='splicing'), 'float')
INSERT INTO `HerediVar_ahdoebm1`.assay_metadata_type (title, display_title, assay_type_id, value_type) VALUES ('minimal_percentage', 'Percent aberrant transcript', (SELECT id FROM assay_type WHERE title='splicing'), 'float')

INSERT INTO `HerediVar_ahdoebm1`.assay_metadata_type (title, display_title, assay_type_id, value_type) VALUES ('functional_category', 'Functional category', (SELECT id FROM assay_type WHERE title='functional'), 'ENUM:Pathogenic,Benign,Ambigous')
INSERT INTO `HerediVar_ahdoebm1`.assay_metadata_type (title, display_title, assay_type_id, value_type) VALUES ('score', 'Score', (SELECT id FROM assay_type WHERE title='functional'), 'float')



ALTER TABLE `HerediVar_ahdoebm1`.`assay` 
ADD COLUMN `assay_type_id` INT UNSIGNED NOT NULL AFTER `assay_type`;

UPDATE assay SET assay_type_id = (SELECT id FROM assay_type WHERE title = 'functional') WHERE assay_type = 'functional'
UPDATE assay SET assay_type_id = (SELECT id FROM assay_type WHERE title = 'splicing') WHERE assay_type = 'splicing'

ALTER TABLE `HerediVar_ahdoebm1`.`assay` 
DROP COLUMN `assay_type`;

INSERT INTO assay_metadata (assay_id, metadata_type_id, value) SELECT id, (SELECT id FROM assay_metadata_type WHERE assay_metadata_type.title = 'score' AND assay_metadata_type.assay_type_id = assay.assay_type_id), score FROM assay

ALTER TABLE `HerediVar_ahdoebm1`.`assay` 
DROP COLUMN `score`;

ALTER TABLE `HerediVar_ahdoebm1`.`assay` 
CHANGE COLUMN `paper` `link` TEXT NULL DEFAULT NULL ;

ALTER TABLE `HerediVar_ahdoebm1`.`assay_metadata_type` 
ADD COLUMN `is_required` TINYINT(1) NOT NULL DEFAULT 1 AFTER `is_deleted`;

ALTER TABLE `HerediVar_ahdoebm1`.`assay_metadata` 
CHANGE COLUMN `metadata_type_id` `assay_metadata_type_id` INT(11) NOT NULL ;


GRANT SELECT ON HerediVar_ahdoebm1.assay_type TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1.assay_type TO 'HerediVar_user';
GRANT SELECT ON HerediVar_ahdoebm1.assay_type TO 'HerediVar_superuser';
GRANT SELECT ON HerediVar_ahdoebm1.assay_type TO 'HerediVar_read_only';


GRANT SELECT ON HerediVar_ahdoebm1.assay_metadata_type TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1.assay_metadata_type TO 'HerediVar_user';
GRANT SELECT ON HerediVar_ahdoebm1.assay_metadata_type TO 'HerediVar_superuser';
GRANT SELECT ON HerediVar_ahdoebm1.assay_metadata_type TO 'HerediVar_read_only';


GRANT SELECT, INSERT ON HerediVar_ahdoebm1.assay_metadata TO 'HerediVar_annotation';
GRANT SELECT, INSERT ON HerediVar_ahdoebm1.assay_metadata TO 'HerediVar_user';
GRANT SELECT, INSERT ON HerediVar_ahdoebm1.assay_metadata TO 'HerediVar_superuser';
GRANT SELECT ON HerediVar_ahdoebm1.assay_metadata TO 'HerediVar_read_only';

GRANT INSERT ON HerediVar_ahdoebm1.assay TO 'HerediVar_annotation';
GRANT DELETE ON HerediVar_ahdoebm1.assay TO 'HerediVar_annotation';


ALTER TABLE `HerediVar_ahdoebm1`.`assay` 
ADD COLUMN `user_id` INT UNSIGNED NULL AFTER `date`;


ALTER TABLE `HerediVar_ahdoebm1`.`assay` 
ADD INDEX `FK_assay_assay_type_idx` (`assay_type_id` ASC);
;
ALTER TABLE `HerediVar_ahdoebm1`.`assay` 
ADD CONSTRAINT `FK_assay_assay_type`
  FOREIGN KEY (`assay_type_id`)
  REFERENCES `HerediVar_ahdoebm1`.`assay_type` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


ALTER TABLE `HerediVar_ahdoebm1`.`assay` 
ADD INDEX `FK_assay_user_idx` (`user_id` ASC);
;
ALTER TABLE `HerediVar_ahdoebm1`.`assay` 
ADD CONSTRAINT `FK_assay_user`
  FOREIGN KEY (`user_id`)
  REFERENCES `HerediVar_ahdoebm1`.`user` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;

ALTER TABLE `HerediVar_ahdoebm1`.`assay` 
DROP FOREIGN KEY `FK_assay_variant`;
ALTER TABLE `HerediVar_ahdoebm1`.`assay` 
ADD CONSTRAINT `FK_assay_variant`
  FOREIGN KEY (`variant_id`)
  REFERENCES `HerediVar_ahdoebm1`.`variant` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


ALTER TABLE `HerediVar_ahdoebm1`.`assay_metadata` 
CHANGE COLUMN `assay_metadata_type_id` `assay_metadata_type_id` INT(11) UNSIGNED NOT NULL ,
ADD INDEX `FK_assay_metadata_assay_idx` (`assay_id` ASC),
ADD INDEX `FK_assay_metadata_assay_metadata_type_idx` (`assay_metadata_type_id` ASC);
;
ALTER TABLE `HerediVar_ahdoebm1`.`assay_metadata` 
ADD CONSTRAINT `FK_assay_metadata_assay`
  FOREIGN KEY (`assay_id`)
  REFERENCES `HerediVar_ahdoebm1`.`assay` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION,
ADD CONSTRAINT `FK_assay_metadata_assay_metadata_type`
  FOREIGN KEY (`assay_metadata_type_id`)
  REFERENCES `HerediVar_ahdoebm1`.`assay_metadata_type` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


ALTER TABLE `HerediVar_ahdoebm1`.`assay_metadata` 
DROP FOREIGN KEY `FK_assay_metadata_assay_metadata_type`;
ALTER TABLE `HerediVar_ahdoebm1`.`assay_metadata` 
ADD CONSTRAINT `FK_assay_metadata_assay_metadata_type`
  FOREIGN KEY (`assay_metadata_type_id`)
  REFERENCES `HerediVar_ahdoebm1`.`assay_metadata_type` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;
