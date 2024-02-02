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
