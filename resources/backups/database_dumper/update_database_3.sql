ALTER TABLE `HerediVar_ahdoebm1`.`classification_scheme` 
ADD COLUMN `is_active` TINYINT(1) NOT NULL DEFAULT 1 AFTER `reference`;


ALTER TABLE `HerediVar_ahdoebm1`.`classification_scheme` 
ADD COLUMN `is_default` TINYINT(1) NOT NULL DEFAULT 0 AFTER `is_active`;


ALTER TABLE `HerediVar_ahdoebm1`.`classification_criterium_strength` 
ADD COLUMN `display_name` VARCHAR(45) NOT NULL AFTER `name`;


UPDATE classification_criterium_strength SET display_name = "vstr" WHERE name = "pvs";
UPDATE classification_criterium_strength SET display_name = "str" WHERE name = "ps" or name = "bs";
UPDATE classification_criterium_strength SET display_name = "mod" WHERE name = "pm" or name = "bm";
UPDATE classification_criterium_strength SET display_name = "sup" WHERE name = "pp" or name = "bp";
UPDATE classification_criterium_strength SET display_name = "alo" WHERE name = "ba";


ALTER TABLE `HerediVar_ahdoebm1`.`annotation_queue` 
CHANGE COLUMN `status` `status` ENUM('pending', 'success', 'error', 'retry', 'aborted') NOT NULL DEFAULT 'pending' ;
