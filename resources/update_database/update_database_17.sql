ALTER TABLE `HerediVar_ahdoebm1`.`consensus_classification` 
CHANGE COLUMN `classification` `classification` ENUM('1', '2', '3', '4', '5', '3+', '3-', '4M', '5M', 'R') NOT NULL ;

ALTER TABLE `HerediVar_ahdoebm1`.`user_classification` 
CHANGE COLUMN `classification` `classification` ENUM('1', '2', '3', '4', '5', '3-', '3+', '4M', '5M', 'R') NOT NULL ;
