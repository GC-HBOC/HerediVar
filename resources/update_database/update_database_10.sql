ALTER TABLE `HerediVar_ahdoebm1`.`classification_scheme_alias` 
ADD COLUMN `version` VARCHAR(45) NOT NULL AFTER `alias`;

ALTER TABLE `HerediVar_ahdoebm1`.`classification_scheme_alias` 
ADD UNIQUE INDEX `classification_scheme_alias_unique` (`alias` ASC, `version` ASC);
;
