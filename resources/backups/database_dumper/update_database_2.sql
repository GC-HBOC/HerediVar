CREATE TABLE `HerediVar_ahdoebm1`.`variant_transcript_annotation` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `variant_id` INT UNSIGNED NOT NULL,
  `annotation_type_id` INT UNSIGNED NOT NULL,
  `transcript` VARCHAR(45) NOT NULL,
  `value` TEXT NOT NULL,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  PRIMARY KEY (`id`),
  INDEX `FK_variant_transcript_annotation_variant_idx` (`variant_id` ASC),
  INDEX `FK_variant_transcript_annotation_annotation_type_idx` (`annotation_type_id` ASC),
  CONSTRAINT `FK_variant_transcript_annotation_variant`
    FOREIGN KEY (`variant_id`)
    REFERENCES `HerediVar_ahdoebm1`.`variant` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `FK_variant_transcript_annotation_annotation_type`
    FOREIGN KEY (`annotation_type_id`)
    REFERENCES `HerediVar_ahdoebm1`.`annotation_type` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


ALTER TABLE `HerediVar_ahdoebm1`.`variant_transcript_annotation` 
ADD UNIQUE INDEX `UNIQUE_variant_transcript_annotation` (`variant_id` ASC, `annotation_type_id` ASC, `transcript` ASC),
DROP INDEX `id_UNIQUE` ;


INSERT INTO `HerediVar_ahdoebm1`.`annotation_type` (`id`, `title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`) VALUES (53, 'maxentscan', 'MaxEntScan', 'The transcript specific MaxEntScan scores calculated from ngs-bits. Each value is of the form: ref|alt', 'text', 'v1.0.0', '2023-09-27', 'Splicing', 1);
INSERT INTO `HerediVar_ahdoebm1`.`annotation_type` (`id`, `title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`) VALUES (54, 'maxentscan_swa', 'MaxEntScan SWA', 'The transcript specific MaxEntScan SWA scores calculated from ngs-bits. A special application of the MaxEntScan algorithm to discover de-novo spliceing variants. Each value is of the form maxentscan_ref_donor|maxentscan_alt_donor|maxentscan_donor_comp|maxentscan_ref_acceptor|maxentscan_alt_acceptor|maxentscan_acceptor_comp', 'text', 'v1.0.0', '2023-09-27', 'Splicing', 1);


ALTER TABLE `HerediVar_ahdoebm1`.`annotation_type` 
ADD COLUMN `is_transcript_specific` TINYINT(1) NOT NULL DEFAULT 0 AFTER `group_name`;




GRANT SELECT, INSERT, UPDATE ON HerediVar.variant_transcript_annotation TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar.variant_transcript_annotation TO 'HerediVar_user';
GRANT SELECT ON HerediVar.variant_transcript_annotation TO 'HerediVar_superuser';
GRANT SELECT ON HerediVar.variant_transcript_annotation TO 'HerediVar_read_only';




UPDATE `HerediVar_ahdoebm1`.`annotation_type` SET `group_name` = 'Protein Domain' WHERE (`id` = '36');
UPDATE `HerediVar_ahdoebm1`.`annotation_type` SET `group_name` = 'Protein Domain' WHERE (`id` = '37');
UPDATE `HerediVar_ahdoebm1`.`annotation_type` SET `group_name` = 'None' WHERE (`id` = '9');
UPDATE `HerediVar_ahdoebm1`.`annotation_type` SET `group_name` = 'None' WHERE (`id` = '10');




ALTER TABLE `HerediVar_ahdoebm1`.`variant_heredicare_annotation` 
ADD INDEX `FK_variant_heredicare_annotation_variant_idx` (`variant_id` ASC);
;
ALTER TABLE `HerediVar_ahdoebm1`.`variant_heredicare_annotation` 
ADD CONSTRAINT `FK_variant_heredicare_annotation_variant`
  FOREIGN KEY (`variant_id`)
  REFERENCES `HerediVar_ahdoebm1`.`variant` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


ALTER TABLE `HerediVar_ahdoebm1`.`annotation_queue` 
CHANGE COLUMN `error_message` `error_message` TEXT NULL DEFAULT '' ;
