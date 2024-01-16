
CREATE TABLE `HerediVar_ahdoebm1`.`sv_variant` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `chrom` ENUM('chr1', 'chr2', 'chr3', 'chr4', 'chr5', 'chr6', 'chr7', 'chr8', 'chr9', 'chr10', 'chr11', 'chr12', 'chr13', 'chr14', 'chr15', 'chr16', 'chr17', 'chr18', 'chr19', 'chr20', 'chr21', 'chr22', 'chrX', 'chrY', 'chrMT') NOT NULL,
  `start` INT NOT NULL,
  `end` INT NOT NULL,
  `sv_type` ENUM('DEL', 'DUP', 'INV') NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC));

CREATE TABLE `HerediVar_ahdoebm1`.`sv_variant_hgvs` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `sv_variant_id` INT UNSIGNED NOT NULL,
  `hgvs` VARCHAR(45) NOT NULL,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

GRANT SELECT, INSERT ON HerediVar_ahdoebm1.sv_variant TO 'HerediVar_user';
GRANT SELECT, INSERT ON HerediVar_ahdoebm1.sv_variant TO 'HerediVar_superuser';
GRANT SELECT ON HerediVar_ahdoebm1.sv_variant TO 'HerediVar_read_only';

GRANT SELECT, INSERT, UPDATE, DELETE ON HerediVar_ahdoebm1.sv_variant_hgvs TO 'HerediVar_user';
GRANT SELECT, INSERT, UPDATE, DELETE ON HerediVar_ahdoebm1.sv_variant_hgvs TO 'HerediVar_superuser';
GRANT SELECT ON HerediVar_ahdoebm1.sv_variant_hgvs TO 'HerediVar_read_only';




ALTER TABLE `HerediVar_ahdoebm1`.`variant` 
DROP COLUMN `error_description`,
DROP COLUMN `error`,
ADD COLUMN `variant_type` ENUM('sv', 'small') NOT NULL DEFAULT 'small' AFTER `is_hidden`,
ADD COLUMN `sv_variant_id` INT UNSIGNED NULL AFTER `variant_type`,
CHANGE COLUMN `chr` `chr` ENUM('chr1', 'chr2', 'chr3', 'chr4', 'chr5', 'chr6', 'chr7', 'chr8', 'chr9', 'chr10', 'chr11', 'chr12', 'chr13', 'chr14', 'chr15', 'chr16', 'chr17', 'chr18', 'chr19', 'chr20', 'chr21', 'chr22', 'chrX', 'chrY', 'chrMT') NULL ,
CHANGE COLUMN `pos` `pos` INT(10) UNSIGNED NULL ,
CHANGE COLUMN `ref` `ref` TEXT NULL ,
CHANGE COLUMN `alt` `alt` TEXT NULL ,
CHANGE COLUMN `orig_chr` `orig_chr` ENUM('chr1', 'chr2', 'chr3', 'chr4', 'chr5', 'chr6', 'chr7', 'chr8', 'chr9', 'chr10', 'chr11', 'chr12', 'chr13', 'chr14', 'chr15', 'chr16', 'chr17', 'chr18', 'chr19', 'chr20', 'chr21', 'chr22', 'chrX', 'chrY', 'chrMT') NULL ,
CHANGE COLUMN `orig_pos` `orig_pos` INT(10) UNSIGNED NULL DEFAULT 0 ,
CHANGE COLUMN `orig_ref` `orig_ref` TEXT NULL ,
CHANGE COLUMN `orig_alt` `orig_alt` TEXT NULL ,
ADD UNIQUE INDEX `sv_variant_id_UNIQUE` (`sv_variant_id` ASC);
;

ALTER TABLE `HerediVar_ahdoebm1`.`sv_variant_hgvs` 
ADD INDEX `FK_sv_variant_hgvs_sv_variant_idx` (`sv_variant_id` ASC);
;
ALTER TABLE `HerediVar_ahdoebm1`.`sv_variant_hgvs` 
ADD CONSTRAINT `FK_sv_variant_hgvs_sv_variant`
  FOREIGN KEY (`sv_variant_id`)
  REFERENCES `HerediVar_ahdoebm1`.`sv_variant` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;

ALTER TABLE `HerediVar_ahdoebm1`.`sv_variant_hgvs` 
CHANGE COLUMN `` `transcript` VARCHAR(45) NULL ,
CHANGE COLUMN `` `hgvs_type` ENUM('c', 'p', 'o') NOT NULL ;


ALTER TABLE `HerediVar_ahdoebm1`.`sv_variant_hgvs` 
ADD UNIQUE INDEX `sv_variant_hgvs_unique` (`transcript` ASC, `hgvs` ASC);

ALTER TABLE `HerediVar_ahdoebm1`.`sv_variant` 
ADD COLUMN `imprecise` TINYINT(1) NOT NULL AFTER `sv_type`;


ALTER TABLE `HerediVar_ahdoebm1`.`variant` 
ADD CONSTRAINT `FK_variant_sv_variant`
  FOREIGN KEY (`sv_variant_id`)
  REFERENCES `HerediVar_ahdoebm1`.`sv_variant` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;


CREATE TABLE `HerediVar_ahdoebm1`.`coldspots` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `chrom` ENUM('chr1', 'chr2', 'chr3', 'chr4', 'chr5', 'chr6', 'chr7', 'chr8', 'chr9', 'chr10', 'chr11', 'chr12', 'chr13', 'chr14', 'chr15', 'chr16', 'chr17', 'chr18', 'chr19', 'chr20', 'chr21', 'chr22', 'chrX', 'chrY', 'chrMT') NOT NULL,
  `start` INT NOT NULL,
  `end` INT NOT NULL,
  `source` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


ALTER TABLE `HerediVar_ahdoebm1`.`annotation_type` 
CHANGE COLUMN `value_type` `value_type` ENUM('int', 'float', 'text', 'bool') NOT NULL ;

INSERT INTO `HerediVar_ahdoebm1`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`) VALUES ('coldspot', 'in coldspot', 'Whether the variant is in a coldspot region or not', 'bool', '-', '2024-01-12', 'Protein Domain', '0');


GRANT SELECT ON HerediVar_ahdoebm1.coldspots TO 'HerediVar_user';
GRANT SELECT ON HerediVar_ahdoebm1.coldspots TO 'HerediVar_superuser';
GRANT SELECT ON HerediVar_ahdoebm1.coldspots TO 'HerediVar_read_only';
GRANT SELECT ON HerediVar_ahdoebm1.coldspots TO 'HerediVar_annotation';

ALTER TABLE `HerediVar_ahdoebm1`.`heredicare_center_classification` 
CHANGE COLUMN `classification` `classification` ENUM('1', '2', '3', '11', '12', '32', '13', '34', '14', '15', '20', '21', '4') NOT NULL ;


INSERT INTO `HerediVar_ahdoebm1`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`) VALUES ('clinvar', 'ClinVar variation ID', 'The Variation ID from ClinVar', 'int', '-', '2024-01-07', 'ID', '0');
