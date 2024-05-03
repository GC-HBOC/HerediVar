ALTER TABLE `HerediVar_ahdoebm1`.`annotation_queue` 
CHANGE COLUMN `status` `status` ENUM('pending', 'success', 'error', 'retry', 'aborted', 'progress') NOT NULL DEFAULT 'pending' ;

UPDATE HerediVar_ahdoebm1.annotation_type SET is_deleted = 1 WHERE title = "maxentscan_ref" OR title = "maxentscan_alt";