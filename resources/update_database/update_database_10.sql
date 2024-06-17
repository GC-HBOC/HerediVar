ALTER TABLE `HerediVar`.`classification_scheme_alias` 
ADD COLUMN `version` VARCHAR(45) NOT NULL AFTER `alias`;

ALTER TABLE `HerediVar`.`classification_scheme_alias` 
ADD UNIQUE INDEX `classification_scheme_alias_unique` (`alias` ASC, `version` ASC);
;

ALTER TABLE `HerediVar`.`user` 
ADD COLUMN `api_key` VARCHAR(64) NULL AFTER `affiliation`;
