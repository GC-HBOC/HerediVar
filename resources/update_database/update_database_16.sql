ALTER TABLE `HerediVar`.`publish_clinvar_queue` 
ADD COLUMN `manually_added` TINYINT(1) NOT NULL DEFAULT 0 AFTER `consensus_classification_id`;
