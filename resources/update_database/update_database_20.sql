ALTER TABLE `HerediVar`.`user_classification` 
ADD COLUMN `point_score` INT NOT NULL AFTER `deleted_date`;
ALTER TABLE `HerediVar`.`user_classification` 
ADD COLUMN `point_classification` ENUM('-', '1', '2', '3', '4', '5') NOT NULL AFTER `point_score`;
ALTER TABLE `HerediVar`.`user_classification` 
CHANGE COLUMN `point_classification` `point_class` ENUM('-', '1', '2', '3', '4', '5') NOT NULL ;


ALTER TABLE `HerediVar`.`consensus_classification` 
ADD COLUMN `point_score` INT NOT NULL AFTER `needs_clinvar_upload`,
ADD COLUMN `point_class` ENUM('-', '1', '2', '3', '4', '5') NOT NULL AFTER `point_score`;

ALTER TABLE `HerediVar`.`automatic_classification` 
ADD COLUMN `point_class_splicing` ENUM('1', '2', '3', '4', '5') NOT NULL AFTER `tool_version`,
ADD COLUMN `point_score_splicing` INT NOT NULL AFTER `point_class_splicing`,
ADD COLUMN `point_class_protein` ENUM('1', '2', '3', '4', '5') NOT NULL AFTER `point_score_splicing`,
ADD COLUMN `point_score_protein` INT NOT NULL AFTER `point_class_protein`;
