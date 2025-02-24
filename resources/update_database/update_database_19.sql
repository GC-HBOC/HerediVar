ALTER TABLE `HerediVar`.`variant_heredicare_annotation` 
CHANGE COLUMN `consensus_class` `consensus_class` ENUM('1', '2', '3', '11', '12', '32', '13', '34', '14', '15', '20', '21', '4', '16', '17', '18') NULL DEFAULT NULL ;
