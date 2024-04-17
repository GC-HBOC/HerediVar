ALTER TABLE `HerediVar_ahdoebm1`.`annotation_queue` 
CHANGE COLUMN `status` `status` ENUM('pending', 'success', 'error', 'retry', 'aborted', 'progress') NOT NULL DEFAULT 'pending' ;
