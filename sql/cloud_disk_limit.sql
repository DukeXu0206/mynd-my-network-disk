DROP TABLE IF EXISTS `disk_limit`;

CREATE TABLE `disk_limit` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `remark` longtext NOT NULL,
  `limit_name` varchar(50) NOT NULL,
  `limit_key` varchar(50) NOT NULL,
  `create_by_id` int DEFAULT NULL,
  `update_by_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `limit_key` (`limit_key`),
  KEY `disk_limit_create_by_id_1658fc3e_fk_auth_user_id` (`create_by_id`),
  KEY `disk_limit_update_by_id_7c9d389d_fk_auth_user_id` (`update_by_id`),
  CONSTRAINT `disk_limit_create_by_id_1658fc3e_fk_auth_user_id` FOREIGN KEY (`create_by_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `disk_limit_update_by_id_7c9d389d_fk_auth_user_id` FOREIGN KEY (`update_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



LOCK TABLES `disk_limit` WRITE;
INSERT INTO `disk_limit` VALUES
(1, NOW(6), NOW(6), '', 'Cloud Storage Capacity', 'storage', 1, 1),
(5, NOW(6), NOW(6), '', 'Preview Limit', 'preview', 1, 1);
UNLOCK TABLES;

