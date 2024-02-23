ALTER TABLE `HerediVar`.`user_classification_criteria_applied` 
ADD COLUMN `state` ENUM('selected', 'unselected') NOT NULL AFTER `is_selected`;

UPDATE HerediVar.user_classification_criteria_applied SET state = 'unselected' WHERE is_selected = 0;
UPDATE HerediVar.user_classification_criteria_applied SET state = 'selected' WHERE is_selected = 1;

ALTER TABLE `HerediVar`.`user_classification_criteria_applied` 
DROP COLUMN `is_selected`;


ALTER TABLE `HerediVar`.`automatic_classification_criteria_applied` 
ADD COLUMN `state` ENUM('selected', 'unselected') NOT NULL AFTER `is_selected`;

UPDATE HerediVar.automatic_classification_criteria_applied SET state = 'unselected' WHERE is_selected = 0;
UPDATE HerediVar.automatic_classification_criteria_applied SET state = 'selected' WHERE is_selected = 1;

ALTER TABLE `HerediVar`.`automatic_classification_criteria_applied` 
DROP COLUMN `is_selected`;


ALTER TABLE `HerediVar`.`consensus_classification_criteria_applied` 
ADD COLUMN `state` ENUM('selected', 'unselected') NOT NULL AFTER `is_selected`;

UPDATE HerediVar.consensus_classification_criteria_applied SET state = 'unselected' WHERE is_selected = 0;
UPDATE HerediVar.consensus_classification_criteria_applied SET state = 'selected' WHERE is_selected = 1;

ALTER TABLE `HerediVar`.`consensus_classification_criteria_applied` 
DROP COLUMN `is_selected`;
