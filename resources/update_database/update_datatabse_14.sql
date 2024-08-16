ALTER TABLE `HerediVar.`user` 
ADD COLUMN `roles` TEXT NOT NULL AFTER `api_key`;
ALTER TABLE `HerediVar`.`user` 
CHANGE COLUMN `roles` `api_roles` TEXT NOT NULL ;
