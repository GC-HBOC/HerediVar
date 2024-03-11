INSERT INTO `HerediVar_ahdoebm1`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`, `is_deleted`) VALUES ('gnomad_ac_nc', 'AC', 'The gnomAD allele count of the non-cancer subset', 'int', 'v3.1.2', '2021-10-22', 'gnomAD non-cancer', '0', '0');
INSERT INTO `HerediVar_ahdoebm1`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`, `is_deleted`) VALUES ('gnomad_af_nc', 'AF', 'The gnomAD allele frequency of the non-cancer subset', 'float', 'v3.1.2', '2021-10-22', 'gnomAD non-cancer', '0', '0');
INSERT INTO `HerediVar_ahdoebm1`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`, `is_deleted`) VALUES ('gnomad_hom_nc', 'hom', 'The number of homozygotes in the gnomAD non-cancer subset', 'int', 'v3.1.2', '2021-10-22', 'gnomAD non-cancer', '0', '0');
INSERT INTO `HerediVar_ahdoebm1`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`, `is_deleted`) VALUES ('gnomad_hemi_nc', 'hemi', 'The number of hemizygotes in the gnomAD non-cancer subset', 'int', 'v3.1.2', '2021-10-22', 'gnomAD non-cancer', '0', '0');
INSERT INTO `HerediVar_ahdoebm1`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`, `is_deleted`) VALUES ('gnomad_het_nc', 'het', 'The number of heterozygotes in the gnomAD non-cancer subset', 'int', 'v3.1.2', '2021-10-22', 'gnomAD non-cancer', '0', '0');
INSERT INTO `HerediVar_ahdoebm1`.`annotation_type` (`title`, `display_title`, `description`, `value_type`, `version`, `version_date`, `group_name`, `is_transcript_specific`, `is_deleted`) VALUES ('faf95_popmax', 'popmax faf95', 'Filtering allele frequency (using Poisson 95% CI) for the population with the maximum allele frequency', 'float', 'v3.1.2', '2021-10-22', 'gnomAD', '0', '0');


ALTER TABLE `HerediVar_ahdoebm1`.`variant_heredicare_annotation` 
ADD UNIQUE INDEX `vid_variant_id_unique` (`variant_id` ASC, `vid` ASC);
;
ALTER TABLE `HerediVar_ahdoebm1`.`heredicare_center_classification` 
ADD UNIQUE INDEX `heredicare_center_unique` (`variant_heredicare_annotation_id` ASC, `heredicare_ZID` ASC);
;

GRANT UPDATE ON HerediVar_ahdoebm1.heredicare_center_classification TO 'HerediVar_annotation';
GRANT UPDATE ON HerediVar_ahdoebm1.variant_heredicare_annotation TO 'HerediVar_annotation';

GRANT DELETE ON HerediVar_ahdoebm1.heredicare_center_classification TO 'HerediVar_annotation';
