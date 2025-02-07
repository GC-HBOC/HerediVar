ALTER TABLE `HerediVar`.`heredicare_center_classification` 
CHANGE COLUMN `classification` `classification` ENUM('1', '2', '3', '11', '12', '32', '13', '34', '14', '15', '20', '21', '4', '16', '17', '18') NOT NULL ;

ALTER TABLE `HerediVar`.`variant_literature` 
CHARACTER SET = utf8mb4 ;
ALTER TABLE `HerediVar`.`variant_literature` MODIFY title TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
ALTER TABLE `HerediVar`.`variant_literature` MODIFY authors TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
ALTER TABLE `HerediVar`.`variant_literature` MODIFY journal_publisher TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

ALTER TABLE `HerediVar`.`user_classification` MODIFY comment TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
ALTER TABLE `HerediVar`.`user_classification_criteria_applied` MODIFY evidence TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
ALTER TABLE `HerediVar`.`user_classification_selected_literature` MODIFY text_passage TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;


ALTER TABLE `HerediVar`.`consensus_classification` MODIFY comment TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
ALTER TABLE `HerediVar`.`consensus_classification_criteria_applied` MODIFY evidence TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
ALTER TABLE `HerediVar`.`consensus_classification_selected_literature` MODIFY text_passage TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

ALTER TABLE `HerediVar`.`heredicare_center_classification` MODIFY comment TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

