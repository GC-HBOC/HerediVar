INSERT INTO `HerediVar`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`, `is_deleted`) VALUES ('heredicare', 'HerediCare', 'The HerediCaRe annotation. Including LR scores and n_pat and n_fam', 'text', '-', '2023-01-01', 'None', '0', '0');
INSERT INTO `HerediVar`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`, `is_deleted`) VALUES ('heredicare', 'HerediCare', 'The HerediCaRe annotation. Including LR scores and n_pat and n_fam', 'text', '-', '2024-07-24', 'None', '0', '0');



ALTER TABLE `HerediVar`.`variant_heredicare_annotation` 
ADD COLUMN `annotation_type_id` INT UNSIGNED NOT NULL AFTER `lr_family`,
ADD INDEX `FK_variant_heredicare_annotation_annotation_type_id_idx` (`annotation_type_id` ASC);
;

UPDATE variant_heredicare_annotation SET annotation_type_id = (SELECT MIN(id) FROM annotation_type WHERE title = "heredicare") WHERE annotation_type_id = 0;


ALTER TABLE `HerediVar`.`variant_heredicare_annotation` 
DROP INDEX `vid_variant_id_unique` ;
;

ALTER TABLE `HerediVar`.`variant_heredicare_annotation` 
ADD UNIQUE INDEX `variant_id_annotation_type_id_unique` (`annotation_type_id` ASC, `variant_id` ASC, `vid` ASC);

ALTER TABLE `HerediVar`.`variant_heredicare_annotation` 
ADD CONSTRAINT `FK_variant_heredicare_annotation_annotation_type_id`
  FOREIGN KEY (`annotation_type_id`)
  REFERENCES `HerediVar`.`annotation_type` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;